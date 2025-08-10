from flask import current_app
from bson.objectid import ObjectId
from datetime import datetime

def init_db(app):
    # This function is not strictly necessary if app.db is initialized in app.py
    # but can be kept for consistency.
    app.db = app.db

def add_question(user_id, question_data):
    """Adds a question document to the database for a given user."""
    try:
        db = current_app.db
        questions_collection = db['questions']
        question = {
            'user_id': ObjectId(user_id),
            'title': question_data.get('title', question_data.get('url', '')),
            'url': question_data.get('url'),
            'difficulty': question_data.get('difficulty'),
            'topic': question_data.get('topic'),
            'solved': question_data.get('solved'),
            'needs_revision': question_data.get('needs_revision'),
            'code': question_data.get('code', ''),
            'date_solved': question_data.get('date_solved', ''),
            'timestamp': question_data.get('timestamp')
        }
        result = questions_collection.insert_one(question)
        return str(result.inserted_id)
    except Exception as e:
        # Log the exception for debugging
        current_app.logger.error(f"Database error in add_question: {e}")
        raise Exception(f"Failed to add question: {str(e)}")

def get_questions_by_user(user_id, query):
    """Retrieves a list of questions for a user, based on a filter query."""
    try:
        db = current_app.db
        questions_collection = db['questions']
        # Add the user_id to the query to ensure user data isolation
        query['user_id'] = ObjectId(user_id)
        
        # Find questions and sort by most recent timestamp
        questions = list(questions_collection.find(query).sort("timestamp", -1))
        
        # Convert ObjectId to string for JSON serialization
        for q in questions:
            q['_id'] = str(q['_id'])
            q['user_id'] = str(q['user_id']) # Also convert user_id
        return questions
    except Exception as e:
        current_app.logger.error(f"Database error in get_questions_by_user: {e}")
        raise Exception(f"Failed to retrieve questions: {str(e)}")