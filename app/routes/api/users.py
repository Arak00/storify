from flask import jsonify, request, current_app
from flask_login import login_required, current_user

from app import db
from app.models import User
from app.routes.api import api

@api.route('/users/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    return jsonify(current_user.to_dict())

@api.route('/users/me', methods=['PUT'])
@login_required
def update_current_user():
    """Update current user information"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update user fields
    if 'first_name' in data:
        current_user.first_name = data['first_name']
    
    if 'last_name' in data:
        current_user.last_name = data['last_name']
    
    if 'bio' in data:
        current_user.bio = data['bio']
    
    db.session.commit()
    
    return jsonify(current_user.to_dict())

@api.route('/users/me/password', methods=['PUT'])
@login_required
def update_password():
    """Update user password"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new passwords are required'}), 400
    
    if not current_user.verify_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    current_user.password = new_password
    db.session.commit()
    
    return jsonify({'message': 'Password updated successfully'})

@api.route('/users/me/social/connect/<platform>', methods=['POST'])
@login_required
def connect_social_account(platform):
    """Connect a social account to the current user"""
    if platform not in ['instagram', 'tiktok', 'etsy']:
        return jsonify({'error': 'Invalid platform'}), 400
    
    data = request.get_json()
    access_token = data.get('access_token')
    
    if not access_token:
        return jsonify({'error': 'Access token is required'}), 400
    
    if platform == 'instagram':
        from app.services.instagram import InstagramService
        
        instagram_service = InstagramService(
            client_id=current_app.config['INSTAGRAM_CLIENT_ID'],
            client_secret=current_app.config['INSTAGRAM_CLIENT_SECRET']
        )
        
        user_info = instagram_service.get_user_info(access_token)
        
        current_user.instagram_id = user_info['id']
        current_user.instagram_token = access_token
    
    elif platform == 'tiktok':
        from app.services.tiktok import TikTokService
        
        tiktok_service = TikTokService(
            client_key=current_app.config['TIKTOK_CLIENT_KEY'],
            client_secret=current_app.config['TIKTOK_CLIENT_SECRET']
        )
        
        user_info = tiktok_service.get_user_info(access_token)
        
        current_user.tiktok_id = user_info['id']
        current_user.tiktok_token = access_token
    
    elif platform == 'etsy':
        from app.services.etsy import EtsyService
        
        etsy_service = EtsyService(
            api_key=current_app.config['ETSY_API_KEY'],
            api_secret=current_app.config['ETSY_API_SECRET']
        )
        
        user_info = etsy_service.get_user_info(access_token)
        
        current_user.etsy_id = user_info['id']
        current_user.etsy_token = access_token
    
    db.session.commit()
    
    return jsonify(current_user.to_dict())

@api.route('/users/me/social/disconnect/<platform>', methods=['POST'])
@login_required
def disconnect_social_account(platform):
    """Disconnect a social account from the current user"""
    if platform not in ['instagram', 'tiktok', 'etsy']:
        return jsonify({'error': 'Invalid platform'}), 400
    
    if platform == 'instagram':
        current_user.instagram_id = None
        current_user.instagram_token = None
    
    elif platform == 'tiktok':
        current_user.tiktok_id = None
        current_user.tiktok_token = None
    
    elif platform == 'etsy':
        current_user.etsy_id = None
        current_user.etsy_token = None
    
    db.session.commit()
    
    return jsonify(current_user.to_dict()) 