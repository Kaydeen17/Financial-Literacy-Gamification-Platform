# Contains endpoints for Fixed Deposits, buying Bonds, and trading Stocks.
import random
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import (
    User, 
    FixedDeposit, 
    AvailableBond, 
    AvailableStock, 
    UserPortfolio, 
    CoinTransaction
)
from datetime import datetime, timedelta
from decimal import Decimal

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/bonds/market', methods=['GET'])
@jwt_required()
def get_bond_market():
    # Allow users to browse available bonds
    bonds = AvailableBond.query.all()
    market_data = []
    for b in bonds:
        market_data.append({
            "id": b.bond_id,
            "issuer": b.issuer_name,
            "price": float(b.face_value),
            "coupon_rate": f"{float(b.coupon_rate * 100)}%", # e.g. 8.5%
            "duration_hours": b.maturity_hours,
            "risk": b.risk_rating
        })
    return jsonify(market_data), 200

@finance_bp.route('/bonds/purchase', methods=['POST'])
@jwt_required()
def purchase_bond():
    user_id = get_jwt_identity()
    bond_id = request.json.get('bond_id')
    quantity = request.json.get('quantity', 1) # Usually 1 for bonds
    
    user = User.query.get(user_id)
    bond = AvailableBond.query.get(bond_id)
    
    if not bond: return jsonify({"msg": "Bond not found"}), 404
    
    total_cost = bond.face_value * quantity
    
    # Check if user can afford it
    if user.coin_balance < total_cost:
        return jsonify({"msg": "Insufficient coins"}), 400
        
    # 1. Deduct Coins & Log Transaction (Requirement 1.4)
    user.coin_balance -= total_cost
    tx = CoinTransaction(
        user_id=user_id,
        amount=-total_cost,
        activity_type=f"Bond Purchase: {bond.issuer_name}"
    )
    
    # 2. Add to Portfolio (Requirement 1.8)
    new_holding = UserPortfolio(
        user_id=user_id,
        asset_id=bond.bond_id,
        asset_type='Bond',
        quantity=quantity,
        purchase_price=bond.face_value,
        purchased_at=datetime.utcnow()
    )
    
    db.session.add(tx)
    db.session.add(new_holding)
    db.session.commit()
    
    return jsonify({
        "msg": "Bond purchased successfully!",
        "new_balance": float(user.coin_balance)
    }), 200
# Helper to calculate Margin of Safety
def calculate_mos(current, intrinsic):
    if not intrinsic or intrinsic <= 0: return 0
    # Formula: ((Intrinsic - Current) / Intrinsic) * 100
    mos = ((intrinsic - current) / intrinsic) * 100
    return round(float(mos), 2)

@finance_bp.route('/stocks/market', methods=['GET'])
@jwt_required()
def get_stock_market():
    stocks = AvailableStock.query.all()
    market_data = []
    
    for s in stocks:
        market_data.append({
            "id": s.stock_id,
            "ticker": s.ticker,
            "company": s.company_name,
            "price": float(s.current_price),
            "metrics": {
                "roe": f"{s.roe_percentage}%",
                "debt_to_equity": float(s.debt_to_equity),
                "profit_margin": f"{s.profit_margin}%",
                "moat": s.moat_description
            },
            "margin_of_safety": calculate_mos(s.current_price, s.intrinsic_value),
            "intrinsic_value": float(s.intrinsic_value)
        })
    return jsonify(market_data), 200

@finance_bp.route('/stocks/trade', methods=['POST'])
@jwt_required()
def trade_stock():
    user_id = get_jwt_identity()
    data = request.json
    stock_id = data.get('stock_id')
    action = data.get('action') # 'BUY' or 'SELL'
    quantity = Decimal(str(data.get('quantity', 0)))
    
    user = User.query.get(user_id)
    stock = AvailableStock.query.get(stock_id)
    
    if not stock or quantity <= 0:
        return jsonify({"msg": "Invalid trade parameters"}), 400

    total_value = stock.current_price * quantity

    if action == 'BUY':
        if user.coin_balance < total_value:
            return jsonify({"msg": "Insufficient coins"}), 400
        
        user.coin_balance -= total_value
        # Add to Portfolio
        new_holding = UserPortfolio(
            user_id=user_id, asset_id=stock_id, asset_type='Stock',
            quantity=quantity, purchase_price=stock.current_price
        )
        db.session.add(new_transaction(user_id, -total_value, f"Bought {stock.ticker}"))
        db.session.add(new_holding)

    elif action == 'SELL':
        # Check if they own enough shares
        holding = UserPortfolio.query.filter_by(
            user_id=user_id, asset_id=stock_id, asset_type='Stock'
        ).first()
        
        if not holding or holding.quantity < quantity:
            return jsonify({"msg": "Not enough shares to sell"}), 400
        
        user.coin_balance += total_value
        holding.quantity -= quantity
        
        if holding.quantity == 0:
            db.session.delete(holding)
            
        db.session.add(new_transaction(user_id, total_value, f"Sold {stock.ticker}"))

    db.session.commit()
    return jsonify({"msg": f"Successfully {action.lower()}ed {quantity} shares"}), 200

# Helper for transactions
def new_transaction(u_id, amt, act):
    return CoinTransaction(user_id=u_id, amount=amt, activity_type=act)

@finance_bp.route('/portfolio/summary', methods=['GET'])
@jwt_required()
def get_portfolio_summary():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    holdings = UserPortfolio.query.filter_by(user_id=user_id).all()
    
    stock_value = 0
    bond_value = 0
    
    for h in holdings:
        if h.asset_type == 'Stock':
            s = AvailableStock.query.get(h.asset_id)
            stock_value += (s.current_price * h.quantity)
        else:
            b = AvailableBond.query.get(h.asset_id)
            bond_value += (b.face_value * h.quantity)
            
    total_value = Decimal(user.coin_balance) + stock_value + bond_value
    
    return jsonify({
        "cash_balance": float(user.coin_balance),
        "stock_holdings_value": float(stock_value),
        "bond_holdings_value": float(bond_value),
        "total_portfolio_value": float(total_value)
    }), 200

@finance_bp.route('/stocks/tick', methods=['POST'])
def market_tick():
    stocks = AvailableStock.query.all()
    for s in stocks:
        # Random change between -2% and +2%
        change = Decimal(random.uniform(0.98, 1.02))
        s.current_price = round(s.current_price * change, 2)
    db.session.commit()
    return jsonify({"msg": "Market prices updated"}), 200

@finance_bp.route('/fd/status', methods=['GET'])
@jwt_required()
def get_fd_status():
    user_id = get_jwt_identity()
    fds = FixedDeposit.query.filter_by(user_id=user_id, is_matured=False).all()
    
    status_report = []
    now = datetime.utcnow()
    
    for fd in fds:
        # Calculate elapsed time in hours
        time_diff = now - fd.start_time
        hours_passed = time_diff.total_seconds() / 3600
        
        # Apply Compound Interest: A = P(1 + r)^t
        # Note: We cap 't' at the duration_hours so interest stops at maturity
        t = min(hours_passed, fd.duration_hours)
        current_value = float(fd.principal) * ((1 + float(fd.interest_rate)) ** t)
        
        status_report.append({
            "id": fd.fd_id,
            "principal": float(fd.principal),
            "current_value": round(current_value, 2),
            "remaining_hours": max(0, fd.duration_hours - hours_passed),
            "can_withdraw": hours_passed >= fd.duration_hours
        })
        
    return jsonify(status_report), 200

@finance_bp.route('/fd/create', methods=['POST'])
@jwt_required()
def create_fd():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.json
    
    amount = Decimal(str(data.get('amount')))
    duration = int(data.get('duration')) 
    
    # Define our tier constraints
    tier_rules = {
        24: {"rate": 0.01, "min": 500},
        72: {"rate": 0.03, "min": 2000},
        168: {"rate": 0.08, "min": 10000}
    }
    
    rule = tier_rules.get(duration)
    
    if not rule:
        return jsonify({"msg": "Invalid duration selected"}), 400
    
    if amount < rule['min']:
        return jsonify({
            "msg": f"Minimum deposit for {duration}h is {rule['min']} coins. Keep saving!"
        }), 400
        
    # Standard Balance Check
    if user.coin_balance < amount:
        return jsonify({"msg": "Insufficient coins"}), 400
        
    # Process the deposit
    user.coin_balance -= amount
    
    new_fd = FixedDeposit(
        user_id=user_id, 
        principal=amount, 
        interest_rate=rule['rate'], 
        duration_hours=duration
    )
    
    # Requirement 1.4: Log the transaction
    db.session.add(CoinTransaction(
        user_id=user_id, 
        amount=-amount, 
        activity_type=f"Fixed Deposit ({duration}h)"
    ))
    db.session.add(new_fd)
    db.session.commit()
    
    return jsonify({
        "msg": "Investment locked!", 
        "amount": float(amount),
        "target_maturity": duration
    }), 201

@finance_bp.route('/fd/withdraw', methods=['POST'])
@jwt_required()
def withdraw_fd():
    user_id = get_jwt_identity()
    fd_id = request.json.get('fd_id')
    fd = FixedDeposit.query.get(fd_id)
    user = User.query.get(user_id)
    
    now = datetime.utcnow()
    hours_passed = (now - fd.start_time).total_seconds() / 3600
    
    if hours_passed >= fd.duration_hours:
        # MATURED: Full Principal + Compound Interest
        final_val = float(fd.principal) * ((1 + float(fd.interest_rate)) ** fd.duration_hours)
        msg = "Goal reached! Interest paid."
    else:
        # EARLY: Penalty (Return only 90% of principal)
        final_val = float(fd.principal) * 0.90
        msg = "Early withdrawal penalty applied (10%). No interest earned."

    user.coin_balance += Decimal(str(final_val))
    db.session.delete(fd) # Remove the FD record
    db.session.add(CoinTransaction(user_id=user_id, amount=final_val, activity_type="FD Withdrawal"))
    db.session.commit()
    
    return jsonify({"msg": msg, "received": round(final_val, 2)}), 200