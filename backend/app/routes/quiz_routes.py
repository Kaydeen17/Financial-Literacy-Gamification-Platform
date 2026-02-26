from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import QuizQuestion, GameHistory, User, CoinTransaction
from sqlalchemy import func
from app import db

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/start', methods=['GET'])
@jwt_required() 
def start_quiz():
    # Only logged-in users get past this point
    current_user_id = get_jwt_identity()

    # Fetch 10 random questions from the database
    questions = QuizQuestion.query.order_by(func.random()).limit(10).all()
    
    quiz_data = []
    for q in questions:
        quiz_data.append({
            "id": q.question_id,
            "question": q.question_text,
            "options": {
                "A": q.option_a,
                "B": q.option_b,
                "C": q.option_c,
                "D": q.option_d
            },
            "answer": q.correct_answer
        })
    
    return jsonify(quiz_data), 200

@quiz_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_quiz():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 1. Fetch the user first so we can check their level
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    old_level = user.level # Storing level before adding XP
    
    # 2. Extract and Calculate
    total_attempts = data.get('total_attempts', 10) 
    questions_count = 10 
    accuracy = (questions_count / total_attempts) * 100
    
    # 3. Define Rewards
    coin_reward = 100
    xp_reward = 50
    
    # 4. Update User Model
    user.coin_balance += coin_reward
    user.xp_total += xp_reward 
    
    # 5. Requirement 1.4: Create the Coin Transaction record
    new_transaction = CoinTransaction(
        user_id=user_id,
        amount=coin_reward,
        activity_type='Quiz' # Tracks earned/spent as per requirement
    )
    
    # 6. Create Game History record
    history = GameHistory(
        user_id=user_id,
        game_type="Quiz",
        score=accuracy 
    )
    
    # 7. Add all to session and commit
    db.session.add(new_transaction)
    db.session.add(history)
    db.session.commit()
    
    return jsonify({
        "msg": "Quiz complete!",
        "xp_gained": xp_reward,
        "coins_earned": coin_reward,
        "new_xp_total": user.xp_total,
        "current_level": user.level,
        "leveled_up": user.level > old_level,
        "accuracy": round(accuracy, 2)
    }), 200