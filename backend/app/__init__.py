import os
from flask import Flask
from flask_cors import CORS
from config import Config
from app.extensions import db, bcrypt, jwt, migrate # Import from the new file
from flask_mail import Mail

mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Pulling from .env
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    mail.init_app(app)

    # 1. Configuration
    app.config.from_object(Config)

    # 2. Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

    # 3. Import models 
    with app.app_context():
        from app.models.user import User, Role
        from app.models.economy import CoinTransaction, Investment
        from app.models.game import QuizQuestion, VocabularyTerm, GameHistory
        from app.models.cosmetics import Cosmetic, UserCosmetic
        from app.models.market import AvailableStock, AvailableBond, UserPortfolio

    # 4. Register Blueprints
    # 1. Authentication (Login/Register/Tokens)
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 2. Educational Games (Quiz Logic & Rewards)
    from app.routes.quiz_routes import quiz_bp
    app.register_blueprint(quiz_bp, url_prefix='/quiz')

    # 3. Mini-Games (Hangman & Term Matcher)
    from app.routes.game_routes import game_bp
    app.register_blueprint(game_bp, url_prefix='/game')

    # 4. Investment Simulator (Stocks, Bonds, Fixed Deposits)
    from app.routes.finance_routes import finance_bp
    app.register_blueprint(finance_bp, url_prefix='/finance')

    # 5. Cosmetic Store (Backgrounds & Purchases)
    from app.routes.store_routes import store_bp
    app.register_blueprint(store_bp, url_prefix='/store')

    return app