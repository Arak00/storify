import uuid
from datetime import datetime

from app import db

class Analytics(db.Model):
    """Analytics model for tracking site usage statistics"""
    __tablename__ = 'analytics'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=False)
    
    # Date for this record (used for daily aggregation)
    date = db.Column(db.Date, nullable=False)
    
    # Page views
    views = db.Column(db.Integer, default=0)
    unique_visitors = db.Column(db.Integer, default=0)
    
    # Engagement
    clicks = db.Column(db.Integer, default=0)  # Internal link clicks
    external_clicks = db.Column(db.Integer, default=0)  # External link clicks
    
    # Product engagement
    product_views = db.Column(db.Integer, default=0)
    
    # Referrers (stored as JSON)
    referrers = db.Column(db.Text, nullable=True)  # JSON with referrer counts
    
    # Device types (stored as JSON)
    devices = db.Column(db.Text, nullable=True)  # JSON with device counts
    
    # Country data (stored as JSON)
    countries = db.Column(db.Text, nullable=True)  # JSON with country counts
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert analytics to dictionary"""
        return {
            'id': self.id,
            'site_id': self.site_id,
            'date': self.date.isoformat() if self.date else None,
            'views': self.views,
            'unique_visitors': self.unique_visitors,
            'clicks': self.clicks,
            'external_clicks': self.external_clicks,
            'product_views': self.product_views,
            'referrers': self.referrers,
            'devices': self.devices,
            'countries': self.countries,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Analytics for {self.site_id} on {self.date}>' 