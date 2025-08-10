from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime

# Import cache utilities and database functions
from cache import cache_get_questions, cache_set_questions
from db import add_question as db_add_question, get_questions_by_user

questions_bp = Blueprint('questions', __name__, url_prefix="/api")

@questions_bp.route('/questions', methods=['POST'])
@jwt_required()
def add_question():
    """API endpoint to add a new question to the database."""
    user_id = get_jwt_identity()
    data = request.get_json()

    # --- Validation ---
    required_fields = ["url", "difficulty", "topic", "solved", "needs_revision"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    if data["difficulty"] not in ["Easy", "Medium", "Hard"]:
        return jsonify({"error": "Invalid difficulty"}), 400

    # Auto set date_solved if solved = True
    if data.get("solved"):
        data["date_solved"] = datetime.utcnow().isoformat()

    data["timestamp"] = datetime.utcnow()

    # --- Call database layer to add question ---
    try:
        question_id = db_add_question(user_id, data)
    except Exception as e:
        current_app.logger.error(f"Error adding question via db layer: {str(e)}")
        return jsonify({"error": "Failed to add question"}), 500

    # --- Clear relevant Redis caches for this user ---
    try:
        if current_app.redis:
            # Delete dashboard cache
            current_app.redis.delete(f"dashboard:{user_id}")
            # Delete all question list caches for the user
            pattern = f"questions:{user_id}:*"
            keys_to_delete = current_app.redis.keys(pattern)
            if keys_to_delete:
                current_app.redis.delete(*keys_to_delete)
                current_app.logger.info(f"Cleared {len(keys_to_delete)} cache entries for user {user_id}")
    except Exception as e:
        current_app.logger.error(f"Error clearing cache for user {user_id}: {str(e)}")

    return jsonify({"message": "Question added successfully", "id": question_id}), 201


@questions_bp.route('/questions', methods=['GET'])
@jwt_required()
def get_questions():
    """API endpoint to get questions with optional filters."""
    user_id = get_jwt_identity()
    difficulty = request.args.get("difficulty")
    topic = request.args.get("topic")

    # Build query for caching and DB lookup
    query_params = {}
    if difficulty:
        query_params["difficulty"] = difficulty
    if topic:
        query_params["topic"] = topic

    # --- Try Redis cache first ---
    cached_data, cached = cache_get_questions(str(user_id), query_params)
    if cached:
        current_app.logger.info(f"Questions cache hit for user {user_id} with params {query_params}")
        return jsonify({"questions": cached_data, "cached": True}), 200

    # --- If cache miss, fetch from MongoDB via db layer ---
    current_app.logger.info(f"Questions cache miss for user {user_id} with params {query_params}")
    try:
        problems = get_questions_by_user(user_id, query_params)
    except Exception as e:
        current_app.logger.error(f"Error getting questions via db layer: {str(e)}")
        return jsonify({"error": "Failed to retrieve questions"}), 500

    # --- Store in Redis for 1 hour ---
    cache_set_questions(str(user_id), query_params, problems)

    return jsonify({"questions": problems, "cached": False}), 200