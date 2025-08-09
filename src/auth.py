from flask import Blueprint, request, jsonify, current_app
import bcrypt
import jwt
import datetime
from config import Config

auth_bp = Blueprint('auth', __name__, url_prefix="/api")

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        db = current_app.db
        users_collection = db['users']

        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        if users_collection.find_one({'email': email}):
            return jsonify({'error': 'Email already exists'}), 409

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user = {
            'email': email,
            'password': hashed_password,
            'created_at': datetime.datetime.utcnow()
        }
        users_collection.insert_one(user)

        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        db = current_app.db
        users_collection = db['users']

        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user = users_collection.find_one({'email': email})
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            token = jwt.encode({
                'email': email,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, Config.SECRET_KEY, algorithm='HS256')

            return jsonify({'token': token}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500