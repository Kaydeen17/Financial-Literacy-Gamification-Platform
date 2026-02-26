# Logic for browsing and purchasing activity backgrounds.
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Cosmetic, UserCosmetic, CoinTransaction

store_bp = Blueprint('store', __name__)

@store_bp.route('/available', methods=['GET'])
@jwt_required()
def get_store():
    user_id = get_jwt_identity()
    
    # Get all possible cosmetics
    all_cosmetics = Cosmetic.query.all()
    
    # Get the user's owned items to check status
    owned_items = UserCosmetic.query.filter_by(user_id=user_id).all()
    owned_dict = {item.cosmetic_id: item.is_equipped for item in owned_items}

    store_list = []
    for c in all_cosmetics:
        store_list.append({
            "id": c.cosmetic_id,
            "name": c.bg_name,
            "image": c.image_url,
            "cost": c.cost,
            "owned": c.cosmetic_id in owned_dict,
            "equipped": owned_dict.get(c.cosmetic_id, False)
        })
    
    return jsonify(store_list), 200

@store_bp.route('/purchase', methods=['POST'])
@jwt_required()
def buy_background():
    user_id = get_jwt_identity()
    cosmetic_id = request.json.get('cosmetic_id')
    
    user = User.query.get(user_id)
    item = Cosmetic.query.get(cosmetic_id)
    
    # 1. Validation
    if not item: return jsonify({"msg": "Item not found"}), 404
    
    already_owned = UserCosmetic.query.filter_by(user_id=user_id, cosmetic_id=cosmetic_id).first()
    if already_owned: return jsonify({"msg": "Already owned"}), 400
    
    if user.coin_balance < item.cost:
        return jsonify({"msg": "Insufficient coins"}), 400

    # 2. Deduction & Transaction Log (Requirement 1.4)
    user.coin_balance -= item.cost
    
    new_purchase = UserCosmetic(user_id=user_id, cosmetic_id=cosmetic_id, is_equipped=False)
    
    tx = CoinTransaction(
        user_id=user_id,
        amount=-item.cost, # Deducting
        activity_type=f"Store: {item.bg_name}"
    )
    
    db.session.add(new_purchase)
    db.session.add(tx)
    db.session.commit()
    
    return jsonify({"msg": "Purchase successful!", "balance": float(user.coin_balance)}), 200

@store_bp.route('/equip', methods=['POST'])
@jwt_required()
def equip_background():
    user_id = get_jwt_identity()
    cosmetic_id = request.json.get('cosmetic_id')
    
    # 1. Verify ownership
    target_item = UserCosmetic.query.filter_by(user_id=user_id, cosmetic_id=cosmetic_id).first()
    if not target_item:
        return jsonify({"msg": "You do not own this background"}), 400
    
    # 2. Unequip everything else for this user
    UserCosmetic.query.filter_by(user_id=user_id).update({UserCosmetic.is_equipped: False})
    
    # 3. Equip the target
    target_item.is_equipped = True
    db.session.commit()
    
    return jsonify({"msg": "Background equipped!"}), 200