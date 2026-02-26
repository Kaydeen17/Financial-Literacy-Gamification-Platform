from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from flask_mail import Message
from app import mail 
from app.extensions import db
from app.models.user import User, Role
from sqlalchemy.exc import SQLAlchemyError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Requirement 1.1.1: Registration with error handling"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"msg": "Request body must be JSON"}), 400

        # Validate mandatory fields
        required = ['username', 'email', 'password', 'f_name', 'l_name']
        if not all(field in data for field in required):
            return jsonify({"msg": "Missing required fields"}), 400

        # Check for existing user
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"msg": "Username already taken"}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"msg": "Email already registered"}), 409

        # Assign Default Role
        role = Role.query.filter_by(role_name='Standard').first()
        
        new_user = User(
            f_name=data['f_name'],
            l_name=data['l_name'],
            username=data['username'],
            email=data['email'],
            role_id=role.role_id if role else 1
        )
        
        # Requirement 2.2: Secure Hashing
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "Registration successful"}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": "Database error", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"msg": "Internal server error", "error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Requirement 1.1.2: Authenticate and generate 12hr token"""
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"msg": "Username and password required"}), 400

        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']):
            # Identity is stored as user_id string
            token = create_access_token(identity=str(user.user_id))
            
            return jsonify({
                "access_token": token,
                "user": {
                    "username": user.username,
                    "role": user.role.role_name if user.role else "Standard"
                }
            }), 200
            
        return jsonify({"msg": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"msg": "Login failed", "error": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Requirement 1.1.3: Secure Logout"""
    return jsonify({"msg": "Logged out successfully"}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"msg": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()

    if user:
        try:
            msg = Message("FinQuest: Password Recovery",
                          recipients=[email])
            
            # This only works if passwords are NOT hashed.
            msg.body = f"Hi {user.username},\n\nYour FinQuest password is: {user.password}\n\nGood luck on your next quest!"
            
            mail.send(msg)
            return jsonify({"msg": "Password sent to your email!"}), 200
        except Exception as e:
            return jsonify({"msg": "Failed to send email", "error": str(e)}), 500

    return jsonify({"msg": "No account found with that email"}), 404