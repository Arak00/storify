from flask import jsonify, request, current_app, abort
from flask_login import login_required, current_user
import uuid

from app import db
from app.models import Site
from app.routes.api import api

@api.route('/sites', methods=['GET'])
@login_required
def get_sites():
    """Get all sites owned by the current user"""
    sites = current_user.sites.all()
    return jsonify([site.to_dict() for site in sites])

@api.route('/sites/<site_id>', methods=['GET'])
@login_required
def get_site(site_id):
    """Get a specific site by ID"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    return jsonify(site.to_dict())

@api.route('/sites', methods=['POST'])
@login_required
def create_site():
    """Create a new site"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('name')
    subdomain = data.get('subdomain')
    
    if not name or not subdomain:
        return jsonify({'error': 'Name and subdomain are required'}), 400
    
    # Check if subdomain is already taken
    if Site.query.filter_by(subdomain=subdomain).first():
        return jsonify({'error': 'Subdomain is already taken'}), 400
    
    # Create site
    site = Site(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=name,
        subdomain=subdomain,
        description=data.get('description'),
        theme_json=data.get('theme', {}),
        content_json=data.get('content', {})
    )
    
    db.session.add(site)
    db.session.commit()
    
    return jsonify(site.to_dict()), 201

@api.route('/sites/<site_id>', methods=['PUT'])
@login_required
def update_site(site_id):
    """Update a site"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update site fields
    if 'name' in data:
        site.name = data['name']
    
    if 'description' in data:
        site.description = data['description']
    
    if 'logo_url' in data:
        site.logo_url = data['logo_url']
    
    if 'hero_image_url' in data:
        site.hero_image_url = data['hero_image_url']
    
    if 'theme' in data:
        site.theme_json = data['theme']
    
    if 'content' in data:
        site.content_json = data['content']
    
    if 'seo_title' in data:
        site.seo_title = data['seo_title']
    
    if 'seo_description' in data:
        site.seo_description = data['seo_description']
    
    if 'seo_keywords' in data:
        site.seo_keywords = data['seo_keywords']
    
    if 'custom_domain' in data and current_user.is_premium():
        site.custom_domain = data['custom_domain']
    
    db.session.commit()
    
    return jsonify(site.to_dict())

@api.route('/sites/<site_id>', methods=['DELETE'])
@login_required
def delete_site(site_id):
    """Delete a site"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(site)
    db.session.commit()
    
    return '', 204

@api.route('/sites/<site_id>/publish', methods=['POST'])
@login_required
def publish_site(site_id):
    """Publish a site"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    
    if not site.is_published:
        from datetime import datetime
        site.is_published = True
        site.published_at = datetime.utcnow()
        db.session.commit()
    
    return jsonify(site.to_dict())

@api.route('/sites/<site_id>/unpublish', methods=['POST'])
@login_required
def unpublish_site(site_id):
    """Unpublish a site"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    
    if site.is_published:
        site.is_published = False
        db.session.commit()
    
    return jsonify(site.to_dict())

@api.route('/sites/<site_id>/import/<platform>', methods=['POST'])
@login_required
def import_content(site_id, platform):
    """Import content from a social platform"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    
    if platform not in ['instagram', 'tiktok', 'etsy']:
        return jsonify({'error': 'Invalid platform'}), 400
    
    if platform == 'instagram' and not current_user.instagram_token:
        return jsonify({'error': 'Instagram account not connected'}), 400
    
    if platform == 'tiktok' and not current_user.tiktok_token:
        return jsonify({'error': 'TikTok account not connected'}), 400
    
    if platform == 'etsy' and not current_user.etsy_token:
        return jsonify({'error': 'Etsy account not connected'}), 400
    
    # Import content from the platform
    # This is a simplified placeholder - in a real app, you would fetch content and create products
    
    if platform == 'instagram':
        from app.services.instagram import InstagramService
        
        instagram_service = InstagramService(
            client_id=current_app.config['INSTAGRAM_CLIENT_ID'],
            client_secret=current_app.config['INSTAGRAM_CLIENT_SECRET']
        )
        
        # Get posts from Instagram
        posts = instagram_service.get_posts(current_user.instagram_token)
        
        # Create products from posts
        for post in posts:
            from app.models import Product
            
            # Check if product already exists
            if Product.query.filter_by(site_id=site.id, source='instagram', source_id=post['id']).first():
                continue
            
            # Create product
            product = Product(
                id=str(uuid.uuid4()),
                site_id=site.id,
                title=post.get('caption', 'Instagram Post'),
                description=post.get('caption'),
                image_url=post.get('media_url'),
                source='instagram',
                source_id=post['id']
            )
            
            db.session.add(product)
    
    # Implement similar imports for TikTok and Etsy
    
    db.session.commit()
    
    return jsonify(site.to_dict()) 