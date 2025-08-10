from flask import Blueprint, request, jsonify, current_app, render_template
import jwt
from config import Config
from db import add_question, get_questions_by_user
from cache import cache_get_questions, cache_set_questions
import datetime
from bson import json_util
from datetime import timedelta

questions_bp = Blueprint('questions', __name__, url_prefix="/api")


def verify_jwt_token(token):
    try:
        decoded = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return decoded['email']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


@questions_bp.route('/questions', methods=['POST'])
def add_question_route():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401

        token = auth_header.split(' ')[1]
        user_email = verify_jwt_token(token)
        if not user_email:
            return jsonify({'error': 'Invalid or expired token'}), 401

        data = request.get_json()
        if not all(key in data for key in ['url', 'difficulty', 'topic', 'solved', 'needs_revision']):
            return jsonify({'error': 'Missing required fields'}), 400

        if data['difficulty'] not in ['Easy', 'Medium', 'Hard']:
            return jsonify({'error': 'Invalid difficulty'}), 400

        question_data = {
            'url': data['url'],
            'difficulty': data['difficulty'],
            'topic': data['topic'],
            'solved': data['solved'],
            'needs_revision': data['needs_revision'],
            'code': data.get('code', ''),
            'timestamp': datetime.datetime.utcnow()
        }

        question_id = add_question(user_email, question_data)
        return jsonify({'message': 'Question added successfully', 'question_id': question_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@questions_bp.route('/questions', methods=['GET'])
def get_questions():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401

        token = auth_header.split(' ')[1]
        user_email = verify_jwt_token(token)
        if not user_email:
            return jsonify({'error': 'Invalid or expired token'}), 401

        topic = request.args.get('topic')
        difficulty = request.args.get('difficulty')
        solved = request.args.get('solved')
        needs_revision = request.args.get('needs_revision')

        query = {'user_email': user_email}
        if topic:
            query['topic'] = topic
        if difficulty in ['Easy', 'Medium', 'Hard']:
            query['difficulty'] = difficulty
        if solved is not None:
            query['solved'] = solved.lower() == 'true'
        if needs_revision is not None:
            query['needs_revision'] = needs_revision.lower() == 'true'

        query_params = {
            'topic': topic,
            'difficulty': difficulty,
            'solved': solved,
            'needs_revision': needs_revision
        }

        cached_questions, is_cached = cache_get_questions(user_email, query_params)
        if is_cached:
            return jsonify({'questions': cached_questions, 'cached': True}), 200

        questions = get_questions_by_user(user_email, query)
        cache_set_questions(user_email, query_params, json_util.dumps(questions))

        return jsonify({'questions': json_util.dumps(questions), 'cached': False}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# @questions_bp.route('/dashboard', methods=['GET'])
# def dashboard():
#     user_email = "test@example.com"  # hardcode a valid email in your DB for now
#     try:
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith('Bearer '):
#             return jsonify({'error': 'Missing or invalid token'}), 401

#         token = auth_header.split(' ')[1]
#         user_email = verify_jwt_token(token)
#         if not user_email:
#             return jsonify({'error': 'Invalid or expired token'}), 401

#         # Get all questions for the user
#         questions = get_questions_by_user(user_email, {'user_email': user_email})
@questions_bp.route('/dashboard', methods=['GET'])
def dashboard():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        token = auth_header.split(' ')[1]
        user_email = verify_jwt_token(token)
        if not user_email:
            return jsonify({'error': 'Invalid or expired token'}), 401
        questions = get_questions_by_user(user_email, {'user_email': user_email})
        total_problems = len(questions)
        difficulty_counts = {'Easy': 0, 'Medium': 0, 'Hard': 0}
        for q in questions:
            difficulty_counts[q['difficulty']] += 1
        solved_dates = sorted([q['timestamp'].date() for q in questions if q['solved']])
        streak = 0
        if solved_dates:
            today = datetime.datetime.utcnow().date()
            current_date = solved_dates[-1]
            while current_date >= today - timedelta(days=streak):
                if current_date in solved_dates:
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
        chart_data = {
            'labels': ['Easy', 'Medium', 'Hard'],
            'datasets': [{
                'data': [difficulty_counts['Easy'], difficulty_counts['Medium'], difficulty_counts['Hard']],
                'backgroundColor': ['#36A2EB', '#FFCE56', '#FF6384']
            }]
        }
        return render_template('dashboard.html', total_problems=total_problems, streak=streak, chart_data=chart_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500