#Defines tables for CoinTransactions, Investments, AvailableStocks, and AvailableBonds.
from app import db # The only db import you need
from datetime import datetime

class CoinTransaction(db.Model):
    __tablename__ = 'coin_transactions'
    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False) # 'Quiz', 'Investment', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Investment(db.Model):
    __tablename__ = 'investments'
    investment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    principal_p = db.Column(db.Numeric(10, 2), nullable=False) # Principal (P)
    rate_r = db.Column(db.Numeric(5, 4), nullable=False)      # Rate (r)
    duration_t = db.Column(db.Integer, nullable=False)        # Time (t)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)

