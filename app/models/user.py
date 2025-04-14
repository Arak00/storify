import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db, login_manager

class User(UserMixin, db.Model):
    """User model for storing user related details"""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # Social accounts
    instagram_id = db.Column(db.String(64), nullable=True)
    tiktok_id = db.Column(db.String(64), nullable=True)
    etsy_id = db.Column(db.String(64), nullable=True)
    
    # OAuth tokens
    instagram_token = db.Column(db.String(255), nullable=True)
    tiktok_token = db.Column(db.String(255), nullable=True)
    etsy_token = db.Column(db.String(255), nullable=True)
    
    # User info
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    
    # Subscription
    plan = db.Column(db.String(20), default='free')  # free, creator, studio
    plan_started_at = db.Column(db.DateTime, nullable=True)
    plan_ends_at = db.Column(db.DateTime, nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sites = db.relationship('Site', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def password(self):
        """Prevent password from being accessed"""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Set password to a hashed password"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Check if password matches"""
        return check_password_hash(self.password_hash, password)
    
    def is_premium(self):
        """Check if user has a premium plan"""
        return self.plan in ['creator', 'studio'] and self.plan_ends_at > datetime.utcnow()
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'plan': self.plan,
            'is_premium': self.is_premium(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'social_accounts': {
                'instagram': bool(self.instagram_id),
                'tiktok': bool(self.tiktok_id),
                'etsy': bool(self.etsy_id)
            }
        }

    def __repr__(self):
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    """Callback to reload a user from the session"""
    return User.query.get(user_id) 