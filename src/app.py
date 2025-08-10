from flask import Flask, redirect
from routes import questions_bp
from auth import auth_bp
from config import Config
from db import init_db
from cache import init_redis

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)
    init_redis(app)
    app.register_blueprint(questions_bp)
    app.register_blueprint(auth_bp)
    
    @app.route('/')
    def index():
        return redirect('/api/dashboard')
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)