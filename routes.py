from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import add_or_update_question, get_questions_by_user, delete_question_by_id, get_unique_tags

questions_bp = Blueprint('questions', __name__, url_prefix="/api")

@questions_bp.route('/questions', methods=['POST'])
@jwt_required()
def handle_add_question():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data.get('url'):
        return jsonify({"error": "URL is required"}), 400
    question_id = add_or_update_question(user_id, data)
    return jsonify({"message": "Question added", "id": question_id}), 201

@questions_bp.route('/questions/<string:question_id>', methods=['PUT'])
@jwt_required()
def handle_update_question(question_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    data['_id'] = question_id
    updated_id = add_or_update_question(user_id, data)
    return jsonify({"message": "Question updated", "id": updated_id}), 200

@questions_bp.route('/questions', methods=['GET'])
@jwt_required()
def handle_get_questions():
    """Handles getting questions with filters and search."""
    user_id = get_jwt_identity()
    # Collect all query parameters, including the new 'search'
    filters = {k: v for k, v in request.args.items() if v}
    problems = get_questions_by_user(user_id, filters)
    return jsonify({"questions": problems}), 200

@questions_bp.route('/questions/<string:question_id>', methods=['DELETE'])
@jwt_required()
def handle_delete_question(question_id):
    user_id = get_jwt_identity()
    delete_question_by_id(user_id, question_id)
    return jsonify({"message": "Question deleted"}), 200

@questions_bp.route('/tags', methods=['GET'])
@jwt_required()
def handle_get_tags():
    user_id = get_jwt_identity()
    tags = get_unique_tags(user_id)
    return jsonify({"tags": tags}), 200
