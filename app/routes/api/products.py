from flask import jsonify, request, current_app, abort
from flask_login import login_required, current_user
import uuid
import json

from app import db
from app.models import Product, Site
from app.routes.api import api

@api.route('/sites/<site_id>/products', methods=['GET'])
@login_required
def get_products(site_id):
    """Get all products for a site"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    
    # Optional filtering
    category = request.args.get('category')
    featured = request.args.get('featured')
    
    query = Product.query.filter_by(site_id=site.id)
    
    if category:
        query = query.filter_by(category=category)
    
    if featured == 'true':
        query = query.filter_by(is_featured=True)
    
    products = query.all()
    
    return jsonify([product.to_dict() for product in products])

@api.route('/sites/<site_id>/products/<product_id>', methods=['GET'])
@login_required
def get_product(site_id, product_id):
    """Get a specific product"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    product = Product.query.filter_by(id=product_id, site_id=site.id).first_or_404()
    
    return jsonify(product.to_dict())

@api.route('/sites/<site_id>/products', methods=['POST'])
@login_required
def create_product(site_id):
    """Create a new product"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    title = data.get('title')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    # Check product limit based on plan
    if current_user.plan == 'free' and site.products.count() >= 3:
        return jsonify({'error': 'Free plan limited to 3 products. Upgrade to add more.'}), 403
    
    if current_user.plan == 'creator' and site.products.count() >= 15:
        return jsonify({'error': 'Creator plan limited to 15 products. Upgrade to add more.'}), 403
    
    # Create product
    product = Product(
        id=str(uuid.uuid4()),
        site_id=site.id,
        title=title,
        description=data.get('description'),
        price=data.get('price'),
        currency=data.get('currency', 'USD'),
        type=data.get('type', 'physical'),
        image_url=data.get('image_url'),
        gallery_urls=json.dumps(data.get('gallery_urls', [])) if data.get('gallery_urls') else None,
        external_link=data.get('external_link'),
        category=data.get('category'),
        tags=json.dumps(data.get('tags', [])) if data.get('tags') else None,
        is_featured=data.get('is_featured', False),
        in_stock=data.get('in_stock', True),
        source='manual'
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify(product.to_dict()), 201

@api.route('/sites/<site_id>/products/<product_id>', methods=['PUT'])
@login_required
def update_product(site_id, product_id):
    """Update a product"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    product = Product.query.filter_by(id=product_id, site_id=site.id).first_or_404()
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update product fields
    if 'title' in data:
        product.title = data['title']
    
    if 'description' in data:
        product.description = data['description']
    
    if 'price' in data:
        product.price = data['price']
    
    if 'currency' in data:
        product.currency = data['currency']
    
    if 'type' in data:
        product.type = data['type']
    
    if 'image_url' in data:
        product.image_url = data['image_url']
    
    if 'gallery_urls' in data:
        product.gallery_urls = json.dumps(data['gallery_urls'])
    
    if 'external_link' in data:
        product.external_link = data['external_link']
    
    if 'category' in data:
        product.category = data['category']
    
    if 'tags' in data:
        product.tags = json.dumps(data['tags'])
    
    if 'is_featured' in data:
        product.is_featured = data['is_featured']
    
    if 'in_stock' in data:
        product.in_stock = data['in_stock']
    
    db.session.commit()
    
    return jsonify(product.to_dict())

@api.route('/sites/<site_id>/products/<product_id>', methods=['DELETE'])
@login_required
def delete_product(site_id, product_id):
    """Delete a product"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    product = Product.query.filter_by(id=product_id, site_id=site.id).first_or_404()
    
    db.session.delete(product)
    db.session.commit()
    
    return '', 204

@api.route('/sites/<site_id>/products/featured', methods=['PUT'])
@login_required
def update_featured_products(site_id):
    """Update featured products"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    
    data = request.get_json()
    
    if not data or 'product_ids' not in data:
        return jsonify({'error': 'Product IDs are required'}), 400
    
    product_ids = data['product_ids']
    
    # Reset all featured products
    for product in site.products:
        product.is_featured = False
    
    # Set featured for specified products
    for product in Product.query.filter(Product.id.in_(product_ids), Product.site_id == site.id).all():
        product.is_featured = True
    
    db.session.commit()
    
    return jsonify([p.to_dict() for p in site.products.filter_by(is_featured=True).all()]) 