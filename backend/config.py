import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 1.1.5: Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:abc12345@127.0.0.1:5432/fin_quest_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 1.1.6: Security
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-key-123'
    
    # Requirement: 12-hour session duration
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12) 
    BCRYPT_LOG_ROUNDS = 13