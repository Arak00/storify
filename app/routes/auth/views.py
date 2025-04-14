import os
from flask import render_template, redirect, url_for, flash, request, session, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
import json
import uuid

from app import db
from app.models import User
from app.routes.auth import auth
from app.services.instagram import InstagramService
from app.services.tiktok import TikTokService
from app.services.etsy import EtsyService

# Forms will be implemented separately

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Placeholder for form handling
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Simple validation
        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(id=str(uuid.uuid4()), email=email)
        user.password = password  # This will hash the password
        
        db.session.add(user)
        db.session.commit()
        
        # Log the user in
        login_user(user)
        
        # Redirect to onboarding
        return redirect(url_for('auth.onboarding'))
    
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Placeholder for form handling
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.verify_password(password):
            flash('Invalid email or password', 'danger')
            return render_template('auth/login.html')
        
        if not user.is_active:
            flash('Account is disabled', 'danger')
            return render_template('auth/login.html')
        
        # Log the user in
        login_user(user, remember=remember)
        
        # Redirect to the next page or dashboard
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        
        return redirect(next_page)
    
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    """Onboarding process after registration"""
    # Check if user has already completed onboarding
    if current_user.sites.first():
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        # Process onboarding form
        # This is a simplified placeholder - in a real app, you would handle form validation
        site_name = request.form.get('site_name')
        subdomain = request.form.get('subdomain')
        
        if not site_name or not subdomain:
            flash('Site name and subdomain are required', 'danger')
            return render_template('auth/onboarding.html')
        
        # Create the site
        from app.models import Site
        
        site = Site(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            name=site_name,
            subdomain=subdomain
        )
        
        db.session.add(site)
        db.session.commit()
        
        # Redirect to the dashboard
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/onboarding.html')

# Social authentication routes
@auth.route('/login/instagram')
def login_instagram():
    """Initiate Instagram OAuth flow"""
    # This is a simplified placeholder - in a real app, you would implement OAuth
    instagram_service = InstagramService(
        client_id=current_app.config['INSTAGRAM_CLIENT_ID'],
        client_secret=current_app.config['INSTAGRAM_CLIENT_SECRET'],
        redirect_uri=url_for('auth.instagram_callback', _external=True)
    )
    
    # Generate and store state to prevent CSRF
    state = str(uuid.uuid4())
    session['oauth_state'] = state
    
    # Redirect to Instagram authorization page
    auth_url = instagram_service.get_authorization_url(state)
    return redirect(auth_url)

@auth.route('/login/instagram/callback')
def instagram_callback():
    """Handle Instagram OAuth callback"""
    # This is a simplified placeholder - in a real app, you would handle errors
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Verify state to prevent CSRF
    if state != session.pop('oauth_state', None):
        flash('Authorization failed', 'danger')
        return redirect(url_for('auth.login'))
    
    instagram_service = InstagramService(
        client_id=current_app.config['INSTAGRAM_CLIENT_ID'],
        client_secret=current_app.config['INSTAGRAM_CLIENT_SECRET'],
        redirect_uri=url_for('auth.instagram_callback', _external=True)
    )
    
    # Exchange code for access token
    token_data = instagram_service.exchange_code_for_token(code)
    
    # Get user info from Instagram
    user_info = instagram_service.get_user_info(token_data['access_token'])
    
    # Check if a user with this Instagram ID already exists
    user = User.query.filter_by(instagram_id=user_info['id']).first()
    
    if user:
        # Update Instagram token
        user.instagram_token = token_data['access_token']
        db.session.commit()
        
        # Log the user in
        login_user(user)
        
        # Redirect to dashboard
        return redirect(url_for('dashboard.index'))
    else:
        # Check if a user with this email already exists
        email = user_info.get('email')
        if email:
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Link Instagram account to existing user
                user.instagram_id = user_info['id']
                user.instagram_token = token_data['access_token']
                db.session.commit()
                
                # Log the user in
                login_user(user)
                
                # Redirect to dashboard
                return redirect(url_for('dashboard.index'))
        
        # Create a new user
        user = User(
            id=str(uuid.uuid4()),
            email=email or f"{user_info['username']}@instagram.user",
            instagram_id=user_info['id'],
            instagram_token=token_data['access_token'],
            first_name=user_info.get('name', '').split(' ')[0],
            last_name=' '.join(user_info.get('name', '').split(' ')[1:]),
            avatar_url=user_info.get('profile_picture')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log the user in
        login_user(user)
        
        # Redirect to onboarding
        return redirect(url_for('auth.onboarding'))

# Similar routes can be implemented for TikTok and Etsy 