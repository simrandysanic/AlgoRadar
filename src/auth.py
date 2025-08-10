from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, url_prefix="/api")

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.form or request.get_json()
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        if current_app.db.users.find_one({'email': email}):
            return jsonify({'error': 'Email already exists'}), 409
        hashed_password = generate_password_hash(password)
        user = {'email': email, 'password': hashed_password}
        result = current_app.db.users.insert_one(user)
        return jsonify({'message': 'User created successfully', 'user_id': str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.form or request.get_json()
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        user = current_app.db.users.find_one({'email': email})
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        access_token = create_access_token(identity=str(user['_id']), expires_delta=timedelta(hours=24))
        return jsonify({'token': access_token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500