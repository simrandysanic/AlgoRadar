from flask import current_app
from bson.objectid import ObjectId

def add_question(user_email, question_data):
    try:
        db = current_app.db
        questions_collection = db['questions']
        question = {
            'user_email': user_email,
            'url': question_data['url'],
            'difficulty': question_data['difficulty'],
            'topic': question_data['topic'],
            'solved': question_data['solved'],
            'needs_revision': question_data['needs_revision'],
            'code': question_data.get('code', ''),
            'timestamp': question_data['timestamp']
        }
        result = questions_collection.insert_one(question)
        return str(result.inserted_id)
    except Exception as e:
        raise Exception(f"Failed to add question: {str(e)}")

def get_questions_by_user(user_email, query):
    try:
        db = current_app.db
        questions_collection = db['questions']
        questions = list(questions_collection.find(query))
        return questions
    except Exception as e:
        raise Exception(f"Failed to retrieve questions: {str(e)}")