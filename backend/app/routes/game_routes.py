# Fetches quiz questions, validates crossword answers, and handles game completion logic.
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import VocabularyTerm, User, GameHistory, db, CoinTransaction
from sqlalchemy import func

game_bp = Blueprint('game', __name__)

@game_bp.route('/hangman/start', methods=['GET'])
@jwt_required()
def start_hangman():
    # 1. Randomly select a financial term [Requirement 1.3]
    term_entry = VocabularyTerm.query.order_by(func.random()).first()
    
    if not term_entry:
        return jsonify({"msg": "No terms found in database"}), 404

    # 2. Display Hidden Word & Hint
    # We send the word length and the definition (hint)
    return jsonify({
        "term_id": term_entry.term_id,
        "display_word": "-" * len(term_entry.term), # Hidden word e.g. "_____"
        "hint": term_entry.definition,
        "length": len(term_entry.term),
        "category": term_entry.category
    }), 200

@game_bp.route('/hangman/guess', methods=['POST'])
@jwt_required()
def guess_letter():
    data = request.get_json()
    term_id = data.get('term_id')
    guess = data.get('guess').lower()
    
    term_entry = VocabularyTerm.query.get(term_id)
    word = term_entry.term.lower()
    
    # Logic to check if guess is in word
    if guess in word:
        # Find positions of the letter
        indices = [i for i, letter in enumerate(word) if letter == guess]
        return jsonify({"correct": True, "indices": indices})
    else:
        return jsonify({"correct": False})
    

@game_bp.route('/hangman/result', methods=['POST'])
@jwt_required()
def hangman_result():
    user_id = get_jwt_identity()
    data = request.get_json()
    win = data.get('win')
    
    if win:
        user = User.query.get(user_id)
        reward_amount = 50
        
        # 1. Update Balance
        user.coin_balance += reward_amount
        user.xp += 20
        
        # 2. Record Transaction (Requirement 1.4)
        new_transaction = CoinTransaction(
            user_id=user_id,
            transaction_type='earned',
            activity_type='Hangman',
            amount=reward_amount
        )
        
        # 3. Log Game History
        history = GameHistory(user_id=user_id, game_type="Hangman", score=100.0)
        
        db.session.add(new_transaction)
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            "msg": "Success!",
            "earned": reward_amount,
            "new_total": float(user.coin_balance)
        })
    
    return jsonify({"msg": "No coins earned"})