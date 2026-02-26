from app import db

class Cosmetic(db.Model):
    __tablename__ = 'cosmetics'
    
    cosmetic_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bg_name = db.Column(db.String(100), nullable=False)  # Theme name
    image_url = db.Column(db.String(255), nullable=False) # Path to the asset
    cost = db.Column(db.Integer, nullable=False)         # Price in coins

class UserCosmetic(db.Model):
    __tablename__ = 'user_cosmetics'
    
    # Linking table for ownership
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    cosmetic_id = db.Column(db.Integer, db.ForeignKey('cosmetics.cosmetic_id'), primary_key=True)
    is_equipped = db.Column(db.Boolean, default=False)   # If currently active