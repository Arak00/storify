import uuid
import json
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

from app import db

class Site(db.Model):
    """Site model for storing boutique website details"""
    __tablename__ = 'sites'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Domain settings
    subdomain = db.Column(db.String(64), unique=True, nullable=False)
    custom_domain = db.Column(db.String(255), unique=True, nullable=True)
    
    # Site information
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(255), nullable=True)
    hero_image_url = db.Column(db.String(255), nullable=True)
    
    # Theme settings - storing as JSON for flexibility
    theme = db.Column(db.Text, default='{}')  # Fall back to Text for SQLite
    
    # Site content - sections and their configuration
    content = db.Column(db.Text, default='{}')  # Fall back to Text for SQLite
    
    # SEO settings
    seo_title = db.Column(db.String(100), nullable=True)
    seo_description = db.Column(db.String(255), nullable=True)
    seo_keywords = db.Column(db.String(255), nullable=True)
    
    # Status
    is_published = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    products = db.relationship('Product', backref='site', lazy='dynamic', cascade='all, delete-orphan')
    analytics = db.relationship('Analytics', backref='site', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def theme_json(self):
        """Get the theme as a dictionary"""
        try:
            return json.loads(self.theme)
        except (TypeError, json.JSONDecodeError):
            return {}
            
    @theme_json.setter
    def theme_json(self, value):
        """Set the theme from a dictionary"""
        self.theme = json.dumps(value)
        
    @property
    def content_json(self):
        """Get the content as a dictionary"""
        try:
            return json.loads(self.content)
        except (TypeError, json.JSONDecodeError):
            return {}
            
    @content_json.setter
    def content_json(self, value):
        """Set the content from a dictionary"""
        self.content = json.dumps(value)
    
    def get_url(self):
        """Get the public URL for this site"""
        if self.custom_domain:
            return f"https://{self.custom_domain}"
        else:
            return f"https://{self.subdomain}.storify.com"
    
    def to_dict(self):
        """Convert site to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'subdomain': self.subdomain,
            'custom_domain': self.custom_domain,
            'logo_url': self.logo_url,
            'hero_image_url': self.hero_image_url,
            'theme': self.theme_json,
            'content': self.content_json,
            'seo': {
                'title': self.seo_title,
                'description': self.seo_description,
                'keywords': self.seo_keywords
            },
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'url': self.get_url()
        }

    def __repr__(self):
        return f'<Site {self.name}>' 