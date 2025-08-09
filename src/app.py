from flask import Flask
from pymongo import MongoClient
from config import Config
from auth import auth_bp
from routes import questions_bp
import redis

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # MongoDB setup
    mongo_client = MongoClient(app.config['MONGO_URI'])
    app.db = mongo_client['dsa_tracker']

    # Redis setup
    app.redis_client = redis.Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=0,
        decode_responses=True
    )

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(questions_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)