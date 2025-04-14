import uuid
from datetime import datetime

from app import db

class Product(db.Model):
    """Product model for storing product/service details"""
    __tablename__ = 'products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=False)
    
    # Product information
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)  # Can be null for "contact for price"
    currency = db.Column(db.String(3), default='USD')
    
    # Product type
    type = db.Column(db.String(20), default='physical')  # physical, digital
    
    # Product source
    source = db.Column(db.String(20), nullable=True)  # instagram, tiktok, etsy, manual
    source_id = db.Column(db.String(100), nullable=True)  # ID from the source platform
    
    # Product images
    image_url = db.Column(db.String(255), nullable=True)
    gallery_urls = db.Column(db.Text, nullable=True)  # JSON array of image URLs
    
    # External links
    external_link = db.Column(db.String(255), nullable=True)  # Link to buy on Etsy, Gumroad, etc.
    
    # Categories and tags
    category = db.Column(db.String(50), nullable=True)
    tags = db.Column(db.Text, nullable=True)  # JSON array of tags
    
    # Featured status
    is_featured = db.Column(db.Boolean, default=False)
    
    # Stock status
    in_stock = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'site_id': self.site_id,
            'title': self.title,
            'description': self.description,
            'price': float(self.price) if self.price is not None else None,
            'currency': self.currency,
            'type': self.type,
            'source': self.source,
            'image_url': self.image_url,
            'gallery_urls': self.gallery_urls,
            'external_link': self.external_link,
            'category': self.category,
            'tags': self.tags,
            'is_featured': self.is_featured,
            'in_stock': self.in_stock,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Product {self.title}>' 