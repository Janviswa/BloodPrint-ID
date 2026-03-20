# routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)
TOKEN_EXPIRY = timedelta(hours=24)

@auth_bp.route('/register', methods=['POST'])
def register():
    data      = request.get_json()
    username  = (data.get('username') or '').strip()   # email
    full_name = (data.get('full_name') or '').strip()   # display name
    password  = data.get('password') or ''

    if not username or not password:
        return jsonify(error='Email and password are required.'), 400
    if not full_name:
        return jsonify(error='Full name is required.'), 400
    if len(password) < 6:
        return jsonify(error='Password must be at least 6 characters.'), 400
    if User.query.filter_by(username=username).first():
        return jsonify(error='Email already registered.'), 409

    user = User(
        username      = username,
        full_name     = full_name,
        password_hash = generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id), expires_delta=TOKEN_EXPIRY)
    return jsonify(token=token, username=user.username, full_name=user.full_name), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data     = request.get_json()
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify(error='Invalid email or password.'), 401

    token = create_access_token(identity=str(user.id), expires_delta=TOKEN_EXPIRY)
    return jsonify(token=token, username=user.username, full_name=user.full_name or user.username), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user = User.query.get_or_404(int(get_jwt_identity()))
    return jsonify(user.to_dict()), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user = User.query.get_or_404(int(get_jwt_identity()))
    data = request.get_json()
    if not check_password_hash(user.password_hash, data.get('old_password','')):
        return jsonify(error='Current password is incorrect.'), 400
    new = data.get('new_password','')
    if len(new) < 6:
        return jsonify(error='New password must be at least 6 characters.'), 400
    user.password_hash = generate_password_hash(new)
    db.session.commit()
    return jsonify(message='Password updated.'), 200


@auth_bp.route('/update-name', methods=['POST'])
@jwt_required()
def update_name():
    user = User.query.get_or_404(int(get_jwt_identity()))
    name = (request.get_json().get('full_name') or '').strip()
    if not name:
        return jsonify(error='Name cannot be empty.'), 400
    user.full_name = name
    db.session.commit()
    return jsonify(message='Name updated.', full_name=name), 200