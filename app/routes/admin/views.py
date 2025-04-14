from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc

from app import db
from app.models import User, Site, Product, Analytics
from app.routes.admin import admin

# Admin authentication decorator
def admin_required(f):
    """Decorator to require admin privileges"""
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin privileges required', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin.route('/')
@admin_required
def index():
    """Admin dashboard index"""
    # Get counts for dashboard
    user_count = User.query.count()
    site_count = Site.query.count()
    product_count = Product.query.count()
    
    # Get recent users
    recent_users = User.query.order_by(desc(User.created_at)).limit(10).all()
    
    # Get recent sites
    recent_sites = Site.query.order_by(desc(Site.created_at)).limit(10).all()
    
    return render_template('admin/index.html', 
                          user_count=user_count,
                          site_count=site_count,
                          product_count=product_count,
                          recent_users=recent_users,
                          recent_sites=recent_sites)

# User management
@admin.route('/users')
@admin_required
def list_users():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filter parameters
    email = request.args.get('email')
    plan = request.args.get('plan')
    is_active = request.args.get('is_active')
    
    query = User.query
    
    if email:
        query = query.filter(User.email.like(f'%{email}%'))
    
    if plan:
        query = query.filter_by(plan=plan)
    
    if is_active is not None:
        is_active = is_active.lower() == 'true'
        query = query.filter_by(is_active=is_active)
    
    users = query.order_by(desc(User.created_at)).paginate(page=page, per_page=per_page)
    
    return render_template('admin/users/list.html', users=users)

@admin.route('/users/<user_id>')
@admin_required
def view_user(user_id):
    """View a specific user"""
    user = User.query.get_or_404(user_id)
    sites = user.sites.all()
    
    return render_template('admin/users/view.html', user=user, sites=sites)

@admin.route('/users/<user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle a user's active status"""
    user = User.query.get_or_404(user_id)
    
    # Don't allow deactivating your own account
    if user.id == current_user.id:
        flash('You cannot deactivate your own account', 'danger')
        return redirect(url_for('admin.view_user', user_id=user_id))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    flash(f'User {user.email} {"activated" if user.is_active else "deactivated"}', 'success')
    return redirect(url_for('admin.view_user', user_id=user_id))

@admin.route('/users/<user_id>/change-plan', methods=['POST'])
@admin_required
def change_user_plan(user_id):
    """Change a user's subscription plan"""
    user = User.query.get_or_404(user_id)
    
    plan = request.form.get('plan')
    if plan not in ['free', 'creator', 'studio']:
        flash('Invalid plan', 'danger')
        return redirect(url_for('admin.view_user', user_id=user_id))
    
    user.plan = plan
    
    # Update plan dates
    if plan != 'free':
        from datetime import datetime, timedelta
        user.plan_started_at = datetime.utcnow()
        user.plan_ends_at = datetime.utcnow() + timedelta(days=30)
    else:
        user.plan_started_at = None
        user.plan_ends_at = None
    
    db.session.commit()
    
    flash(f'User {user.email} plan changed to {plan}', 'success')
    return redirect(url_for('admin.view_user', user_id=user_id))

# Site management
@admin.route('/sites')
@admin_required
def list_sites():
    """List all sites"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filter parameters
    subdomain = request.args.get('subdomain')
    is_published = request.args.get('is_published')
    
    query = Site.query
    
    if subdomain:
        query = query.filter(Site.subdomain.like(f'%{subdomain}%'))
    
    if is_published is not None:
        is_published = is_published.lower() == 'true'
        query = query.filter_by(is_published=is_published)
    
    sites = query.order_by(desc(Site.created_at)).paginate(page=page, per_page=per_page)
    
    return render_template('admin/sites/list.html', sites=sites)

@admin.route('/sites/<site_id>')
@admin_required
def view_site(site_id):
    """View a specific site"""
    site = Site.query.get_or_404(site_id)
    products = site.products.all()
    
    return render_template('admin/sites/view.html', site=site, products=products)

# Analytics
@admin.route('/analytics')
@admin_required
def analytics():
    """View overall analytics"""
    # Get overall stats
    user_count = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    premium_users = User.query.filter(User.plan != 'free').count()
    site_count = Site.query.count()
    published_sites = Site.query.filter_by(is_published=True).count()
    product_count = Product.query.count()
    
    # Get signup trends (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Count users by day
    user_trends = db.session.query(
        db.func.date(User.created_at).label('date'),
        db.func.count(User.id).label('count')
    ).filter(User.created_at >= thirty_days_ago).group_by('date').all()
    
    # Count sites by day
    site_trends = db.session.query(
        db.func.date(Site.created_at).label('date'),
        db.func.count(Site.id).label('count')
    ).filter(Site.created_at >= thirty_days_ago).group_by('date').all()
    
    return render_template('admin/analytics.html',
                           user_count=user_count,
                           active_users=active_users,
                           premium_users=premium_users,
                           site_count=site_count,
                           published_sites=published_sites,
                           product_count=product_count,
                           user_trends=user_trends,
                           site_trends=site_trends)

# Support
@admin.route('/support')
@admin_required
def support():
    """View support tickets (placeholder)"""
    # This would be implemented in a real application with a ticket system
    return render_template('admin/support.html')

# API endpoints for admin (for AJAX calls)
@admin.route('/api/users/stats', methods=['GET'])
@admin_required
def api_user_stats():
    """Get user statistics"""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    free_users = User.query.filter_by(plan='free').count()
    creator_users = User.query.filter_by(plan='creator').count()
    studio_users = User.query.filter_by(plan='studio').count()
    
    return jsonify({
        'total': total_users,
        'active': active_users,
        'free': free_users,
        'creator': creator_users,
        'studio': studio_users
    })

@admin.route('/api/sites/stats', methods=['GET'])
@admin_required
def api_site_stats():
    """Get site statistics"""
    total_sites = Site.query.count()
    published_sites = Site.query.filter_by(is_published=True).count()
    
    return jsonify({
        'total': total_sites,
        'published': published_sites
    }) 