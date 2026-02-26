# backend/app/models.py
from app import db

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    
    # Unique question ID 
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # The quiz question text [cite: 32, 34, 35]
    question_text = db.Column(db.Text, nullable=False)
    
    # Multiple choice options parsed from your text file 
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    
    # Validated against user input (A, B, C, or D) 
    correct_answer = db.Column(db.String(10), nullable=False)
    
    # 1-5 scale: 1 (very easy) to 5 (very hard) 
    difficulty_level = db.Column(db.Integer, default=1)

class VocabularyTerm(db.Model):
    __tablename__ = 'vocabulary_terms'
    
    # For Hangman/Term Matcher 
    term_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # The financial word (e.g., Inflation, Liquidity) [cite: 1, 2]
    term = db.Column(db.String(100), nullable=False)
    
    # Hint or match description [cite: 1, 2]
    definition = db.Column(db.Text, nullable=False)
    
    # Category of word (e.g., 'Investing', 'Budgeting') [cite: 2, 3, 5]
    category = db.Column(db.String(50))

class GameHistory(db.Model):
    __tablename__ = 'game_history'
    
    # Log of completed activities
    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # The player who completed the game
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    
    # Quiz, Crossword, Hangman, or Matcher
    game_type = db.Column(db.String(50), nullable=False)
    
    # Accuracy or points earned
    score = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Optional: timestamp for when the game was played
    # played_at = db.Column(db.DateTime, server_default=db.func.now())