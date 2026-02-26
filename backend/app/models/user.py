from app import db 
from flask_bcrypt import generate_password_hash, check_password_hash

class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(50), nullable=False) 
    
    users = db.relationship('User', backref='role', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    f_name = db.Column(db.String(50), nullable=False)
    l_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False) 
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False) # Increased for safety
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    xp_total = db.Column(db.Integer, default=0)
    current_level = db.Column(db.Integer, default=1)
    
    # Changed to Numeric for financial precision in Postgres
    coin_balance = db.Column(db.Numeric(12, 2), default=0.00)

    # A "Property" that calculates level on the fly
    @property
    def level(self):
        # Floor division: 250 // 100 = 2. Adding 1 makes it Level 3.
        return (self.xp // 100) + 1
    
    @property
    def xp_in_current_level(self):
        # 250 % 100 = 50 XP into the current level
        return self.xp % 100
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)