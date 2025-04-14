from flask import render_template, redirect, url_for, current_app, request
from flask_login import current_user

from app.routes.main import main

@main.route('/')
def index():
    """Landing page"""
    return render_template('main/index.html')

@main.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')

@main.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('main/pricing.html')

@main.route('/features')
def features():
    """Features page"""
    return render_template('main/features.html')

@main.route('/contact')
def contact():
    """Contact page"""
    return render_template('main/contact.html')

@main.route('/faq')
def faq():
    """FAQ page"""
    return render_template('main/faq.html')

@main.route('/<subdomain>')
def view_site(subdomain):
    """View a boutique site by subdomain"""
    from app.models import Site
    
    site = Site.query.filter_by(subdomain=subdomain, is_published=True).first_or_404()
    
    # Track analytics (simplified for now)
    # In a real app, you would use a background task for this
    if not request.user_agent.string.lower().startswith('bot'):
        from app.models import Analytics
        from app import db
        from datetime import date
        
        # Get or create today's analytics record
        analytics = Analytics.query.filter_by(
            site_id=site.id, 
            date=date.today()
        ).first()
        
        if not analytics:
            analytics = Analytics(site_id=site.id, date=date.today())
            db.session.add(analytics)
        
        # Increment views
        analytics.views += 1
        db.session.commit()
    
    return render_template('boutique/index.html', site=site) 