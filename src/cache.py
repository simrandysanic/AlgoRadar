import json
from flask import current_app

def cache_get_questions(user_email, query_params):
    try:
        redis_client = current_app.redis_client
        cache_key = f"questions:{user_email}:{json.dumps(query_params, sort_keys=True)}"
        
        # Check cache
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data), True
        
        return None, False
    except Exception as e:
        current_app.logger.error(f"Cache get error: {str(e)}")
        return None, False

def cache_set_questions(user_email, query_params, questions):
    try:
        redis_client = current_app.redis_client
        cache_key = f"questions:{user_email}:{json.dumps(query_params, sort_keys=True)}"
        
        # Cache for 1 hour
        redis_client.setex(cache_key, 3600, json.dumps(questions))
    except Exception as e:
        current_app.logger.error(f"Cache set error: {str(e)}")