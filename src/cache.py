import json
import redis
from flask import current_app

def init_redis(app):
    try:
        app.redis = redis.Redis(
            host=app.config.get('REDIS_HOST', 'localhost'),
            port=app.config.get('REDIS_PORT', 6379),
            decode_responses=True
        )
        app.redis.ping()  # Test connection
        app.logger.info("Redis connected successfully")
    except redis.ConnectionError as e:
        app.redis = None  # Fallback to no caching
        app.logger.warning(f"Redis unavailable, caching disabled: {str(e)}")

def cache_get_questions(user_email, query_params):
    try:
        if not current_app.redis:
            current_app.logger.info("No Redis, skipping cache")
            return None, False
        cache_key = f"questions:{user_email}:{json.dumps(query_params, sort_keys=True)}"
        
        # Check cache
        cached_data = current_app.redis.get(cache_key)
        if cached_data:
            return json.loads(cached_data), True
        
        return None, False
    except Exception as e:
        current_app.logger.error(f"Cache get error: {str(e)}")
        return None, False

def cache_set_questions(user_email, query_params, questions):
    try:
        if not current_app.redis:
            current_app.logger.info("No Redis, skipping cache set")
            return
        cache_key = f"questions:{user_email}:{json.dumps(query_params, sort_keys=True)}"
        
        # Cache for 1 hour
        current_app.redis.setex(cache_key, 3600, json.dumps(questions))
    except Exception as e:
        current_app.logger.error(f"Cache set error: {str(e)}")