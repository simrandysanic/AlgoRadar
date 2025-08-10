from flask import Flask, redirect, render_template
from pymongo import MongoClient
from config import Config
from auth import auth_bp
from routes import questions_bp
import redis
from cache import init_redis

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

    # Homepage route
    @app.route("/")
    def home():
        # TODO: Replace with real DB logic
        total_problems = 0
        streak = 0
        chart_data = {"labels": [], "datasets": []}
        return render_template(
            "dashboard.html",
            total_problems=total_problems,
            streak=streak,
            chart_data=chart_data
        )

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
