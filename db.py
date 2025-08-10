from flask import current_app
from bson.objectid import ObjectId
from datetime import datetime

def add_or_update_question(user_id, data):
    """Adds or updates a question document in the database."""
    db = current_app.db
    questions = db.questions
    
    doc = {
        'user_id': ObjectId(user_id),
        'title': data.get('title', data.get('url', '')),
        'url': data.get('url'),
        'difficulty': data.get('difficulty'),
        'tags': data.get('tags', []),
        'notes': data.get('notes', ''),
        'code': data.get('code', ''),
        'time_complexity': data.get('time_complexity', ''),
        'space_complexity': data.get('space_complexity', ''),
        'solved': data.get('solved', False),
        'needs_revision': data.get('needs_revision', False),
        'last_updated': datetime.utcnow()
    }

    if doc['solved']:
        doc['date_solved'] = data.get('date_solved', datetime.utcnow().isoformat())
    else:
        doc['date_solved'] = None

    problem_id = data.get('_id')
    if problem_id:
        questions.update_one(
            {'_id': ObjectId(problem_id), 'user_id': ObjectId(user_id)},
            {'$set': doc}
        )
        return str(problem_id)
    else:
        result = questions.insert_one(doc)
        return str(result.inserted_id)

def get_questions_by_user(user_id, filters):
    """Retrieves questions for a user based on multiple filters, including text search."""
    db = current_app.db
    query = {'user_id': ObjectId(user_id)}

    # Text search filter
    if filters.get('search'):
        query['$text'] = {'$search': filters['search']}

    # Other filters
    if filters.get('difficulty'):
        query['difficulty'] = filters['difficulty']
    status = filters.get('status')
    if status == 'solved_revision':
        query.update({'solved': True, 'needs_revision': True})
    elif status == 'solved_only':
        query.update({'solved': True, 'needs_revision': False})

    # Execute query
    questions = list(db.questions.find(query).sort("last_updated", -1))
    
    for q in questions:
        q['_id'] = str(q['_id'])
        q['user_id'] = str(q['user_id'])
    return questions

def delete_question_by_id(user_id, question_id):
    """Deletes a single question by its ID."""
    db = current_app.db
    db.questions.delete_one({'_id': ObjectId(question_id), 'user_id': ObjectId(user_id)})

def get_unique_tags(user_id):
    """Gets a list of all unique tags for a user."""
    db = current_app.db
    return db.questions.distinct("tags", {"user_id": ObjectId(user_id)})
