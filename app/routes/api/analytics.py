from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json

from app import db
from app.models import Site, Analytics
from app.routes.api import api

@api.route('/sites/<site_id>/analytics', methods=['GET'])
@login_required
def get_analytics(site_id):
    """Get analytics for a site"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    
    # Check if user has premium plan for analytics
    if not current_user.is_premium():
        return jsonify({'error': 'Analytics are only available for premium plans'}), 403
    
    # Get date range from query parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
    else:
        # Default to 30 days ago
        start_date = (datetime.utcnow() - timedelta(days=30)).date()
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
    else:
        # Default to today
        end_date = datetime.utcnow().date()
    
    # Query analytics within date range
    analytics = Analytics.query.filter(
        Analytics.site_id == site.id,
        Analytics.date >= start_date,
        Analytics.date <= end_date
    ).order_by(Analytics.date.asc()).all()
    
    # Prepare response data
    response = {
        'site_id': site.id,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'total_views': sum(a.views for a in analytics),
        'total_unique_visitors': sum(a.unique_visitors for a in analytics),
        'total_product_views': sum(a.product_views for a in analytics),
        'daily': [a.to_dict() for a in analytics]
    }
    
    return jsonify(response)

@api.route('/sites/<site_id>/analytics/summary', methods=['GET'])
@login_required
def get_analytics_summary(site_id):
    """Get a summary of analytics for a site"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    
    # For free users, provide a limited summary
    if not current_user.is_premium():
        # Get today's analytics
        today = datetime.utcnow().date()
        analytics = Analytics.query.filter_by(site_id=site.id, date=today).first()
        
        if not analytics:
            return jsonify({
                'views_today': 0,
                'is_premium_required': True
            })
        
        return jsonify({
            'views_today': analytics.views,
            'is_premium_required': True
        })
    
    # For premium users, provide more detailed summary
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Today's analytics
    today_analytics = Analytics.query.filter_by(site_id=site.id, date=today).first()
    today_views = today_analytics.views if today_analytics else 0
    
    # Yesterday's analytics
    yesterday_analytics = Analytics.query.filter_by(site_id=site.id, date=yesterday).first()
    yesterday_views = yesterday_analytics.views if yesterday_analytics else 0
    
    # Last 7 days
    week_analytics = Analytics.query.filter(
        Analytics.site_id == site.id,
        Analytics.date >= week_ago,
        Analytics.date <= today
    ).all()
    week_views = sum(a.views for a in week_analytics)
    
    # Last 30 days
    month_analytics = Analytics.query.filter(
        Analytics.site_id == site.id,
        Analytics.date >= month_ago,
        Analytics.date <= today
    ).all()
    month_views = sum(a.views for a in month_analytics)
    
    return jsonify({
        'views_today': today_views,
        'views_yesterday': yesterday_views,
        'views_last_7_days': week_views,
        'views_last_30_days': month_views,
        'unique_visitors_last_30_days': sum(a.unique_visitors for a in month_analytics),
        'is_premium_required': False
    })

@api.route('/sites/<site_id>/analytics/referrers', methods=['GET'])
@login_required
def get_referrers(site_id):
    """Get referrer sources for a site"""
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first_or_404()
    
    # Check if user has premium plan for analytics
    if not current_user.is_premium():
        return jsonify({'error': 'Analytics are only available for premium plans'}), 403
    
    # Get date range from query parameters (default to last 30 days)
    start_date = (datetime.utcnow() - timedelta(days=30)).date()
    end_date = datetime.utcnow().date()
    
    # Query analytics within date range
    analytics = Analytics.query.filter(
        Analytics.site_id == site.id,
        Analytics.date >= start_date,
        Analytics.date <= end_date
    ).all()
    
    # Aggregate referrers
    referrers = {}
    for record in analytics:
        if record.referrers:
            try:
                record_referrers = json.loads(record.referrers)
                for source, count in record_referrers.items():
                    referrers[source] = referrers.get(source, 0) + count
            except json.JSONDecodeError:
                pass
    
    # Sort by count (descending)
    sorted_referrers = [
        {'source': source, 'count': count}
        for source, count in sorted(referrers.items(), key=lambda x: x[1], reverse=True)
    ]
    
    return jsonify(sorted_referrers) 