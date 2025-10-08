"""
Analytics helper functions for access log queries
Provides metrics like DAU, MAU, unique visitors, popular endpoints
"""
from datetime import datetime, timedelta
from sqlalchemy import func, distinct, and_
from models_analytics import AccessLog
from models import db


def get_daily_active_users(date=None):
    """
    Get Daily Active Users (DAU) for a specific date

    Args:
        date: datetime.date object (defaults to today)

    Returns:
        dict with:
            - total_unique: Total unique users (authenticated + anonymous)
            - authenticated: Unique authenticated users
            - anonymous: Unique anonymous visitors (by IP hash)
            - date: Date queried
    """
    if date is None:
        date = datetime.utcnow().date()

    # Start and end of day
    start_time = datetime.combine(date, datetime.min.time())
    end_time = datetime.combine(date, datetime.max.time())

    # Query unique authenticated users
    authenticated_users = db.session.query(
        func.count(distinct(AccessLog.user_id))
    ).filter(
        and_(
            AccessLog.timestamp.between(start_time, end_time),
            AccessLog.user_id.isnot(None)
        )
    ).scalar() or 0

    # Query unique anonymous visitors (by IP hash)
    anonymous_visitors = db.session.query(
        func.count(distinct(AccessLog.ip_hash))
    ).filter(
        and_(
            AccessLog.timestamp.between(start_time, end_time),
            AccessLog.user_id.is_(None),
            AccessLog.ip_hash.isnot(None)
        )
    ).scalar() or 0

    return {
        'date': date.isoformat(),
        'total_unique': authenticated_users + anonymous_visitors,
        'authenticated': authenticated_users,
        'anonymous': anonymous_visitors
    }


def get_monthly_active_users(year=None, month=None):
    """
    Get Monthly Active Users (MAU) for a specific month

    Args:
        year: Year (defaults to current year)
        month: Month (1-12, defaults to current month)

    Returns:
        dict with unique user counts
    """
    if year is None or month is None:
        now = datetime.utcnow()
        year = year or now.year
        month = month or now.month

    # Start and end of month
    start_time = datetime(year, month, 1)
    if month == 12:
        end_time = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_time = datetime(year, month + 1, 1) - timedelta(seconds=1)

    # Query unique authenticated users
    authenticated_users = db.session.query(
        func.count(distinct(AccessLog.user_id))
    ).filter(
        and_(
            AccessLog.timestamp.between(start_time, end_time),
            AccessLog.user_id.isnot(None)
        )
    ).scalar() or 0

    # Query unique anonymous visitors
    anonymous_visitors = db.session.query(
        func.count(distinct(AccessLog.ip_hash))
    ).filter(
        and_(
            AccessLog.timestamp.between(start_time, end_time),
            AccessLog.user_id.is_(None),
            AccessLog.ip_hash.isnot(None)
        )
    ).scalar() or 0

    return {
        'year': year,
        'month': month,
        'total_unique': authenticated_users + anonymous_visitors,
        'authenticated': authenticated_users,
        'anonymous': anonymous_visitors
    }


def get_unique_visitors_last_n_days(n=7):
    """
    Get unique visitors over the last N days

    Args:
        n: Number of days to look back (default: 7)

    Returns:
        dict with unique user counts and daily breakdown
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=n)

    # Get total unique users in period
    authenticated_users = db.session.query(
        func.count(distinct(AccessLog.user_id))
    ).filter(
        and_(
            AccessLog.timestamp >= start_date,
            AccessLog.user_id.isnot(None)
        )
    ).scalar() or 0

    anonymous_visitors = db.session.query(
        func.count(distinct(AccessLog.ip_hash))
    ).filter(
        and_(
            AccessLog.timestamp >= start_date,
            AccessLog.user_id.is_(None),
            AccessLog.ip_hash.isnot(None)
        )
    ).scalar() or 0

    # Get daily breakdown
    daily_breakdown = []
    for i in range(n):
        day_date = (end_date - timedelta(days=n - i - 1)).date()
        daily_data = get_daily_active_users(day_date)
        daily_breakdown.append(daily_data)

    return {
        'period_days': n,
        'start_date': start_date.date().isoformat(),
        'end_date': end_date.date().isoformat(),
        'total_unique': authenticated_users + anonymous_visitors,
        'authenticated': authenticated_users,
        'anonymous': anonymous_visitors,
        'daily_breakdown': daily_breakdown
    }


def get_popular_endpoints(start_date=None, end_date=None, limit=10):
    """
    Get most popular endpoints by request count

    Args:
        start_date: Start date for query (defaults to 7 days ago)
        end_date: End date for query (defaults to now)
        limit: Number of top endpoints to return (default: 10)

    Returns:
        list of dicts with endpoint stats
    """
    if end_date is None:
        end_date = datetime.utcnow()
    if start_date is None:
        start_date = end_date - timedelta(days=7)

    # Query endpoint usage
    results = db.session.query(
        AccessLog.endpoint,
        func.count(AccessLog.id).label('total_requests'),
        func.count(distinct(AccessLog.user_id)).label('unique_users'),
        func.count(distinct(AccessLog.ip_hash)).label('unique_ips'),
        func.avg(AccessLog.response_time_ms).label('avg_response_time')
    ).filter(
        AccessLog.timestamp.between(start_date, end_date)
    ).group_by(
        AccessLog.endpoint
    ).order_by(
        func.count(AccessLog.id).desc()
    ).limit(limit).all()

    endpoints = []
    for row in results:
        endpoints.append({
            'endpoint': row.endpoint,
            'total_requests': row.total_requests,
            'unique_users': row.unique_users or 0,
            'unique_ips': row.unique_ips or 0,
            'avg_response_time_ms': round(row.avg_response_time, 2) if row.avg_response_time else None
        })

    return {
        'start_date': start_date.date().isoformat(),
        'end_date': end_date.date().isoformat(),
        'endpoints': endpoints
    }


def get_device_breakdown(start_date=None, end_date=None):
    """
    Get breakdown of requests by device type and browser

    Args:
        start_date: Start date for query (defaults to 7 days ago)
        end_date: End date for query (defaults to now)

    Returns:
        dict with device and browser statistics
    """
    if end_date is None:
        end_date = datetime.utcnow()
    if start_date is None:
        start_date = end_date - timedelta(days=7)

    # Device type breakdown
    device_results = db.session.query(
        AccessLog.device_type,
        func.count(AccessLog.id).label('count')
    ).filter(
        and_(
            AccessLog.timestamp.between(start_date, end_date),
            AccessLog.device_type.isnot(None)
        )
    ).group_by(
        AccessLog.device_type
    ).all()

    devices = {row.device_type: row.count for row in device_results}

    # Browser breakdown
    browser_results = db.session.query(
        AccessLog.browser,
        func.count(AccessLog.id).label('count')
    ).filter(
        and_(
            AccessLog.timestamp.between(start_date, end_date),
            AccessLog.browser.isnot(None)
        )
    ).group_by(
        AccessLog.browser
    ).order_by(
        func.count(AccessLog.id).desc()
    ).limit(10).all()

    browsers = {row.browser: row.count for row in browser_results}

    # OS breakdown
    os_results = db.session.query(
        AccessLog.os,
        func.count(AccessLog.id).label('count')
    ).filter(
        and_(
            AccessLog.timestamp.between(start_date, end_date),
            AccessLog.os.isnot(None)
        )
    ).group_by(
        AccessLog.os
    ).order_by(
        func.count(AccessLog.id).desc()
    ).limit(10).all()

    operating_systems = {row.os: row.count for row in os_results}

    return {
        'start_date': start_date.date().isoformat(),
        'end_date': end_date.date().isoformat(),
        'devices': devices,
        'browsers': browsers,
        'operating_systems': operating_systems
    }


def get_response_time_stats(start_date=None, end_date=None):
    """
    Get response time statistics across all endpoints

    Args:
        start_date: Start date for query (defaults to 7 days ago)
        end_date: End date for query (defaults to now)

    Returns:
        dict with response time statistics
    """
    if end_date is None:
        end_date = datetime.utcnow()
    if start_date is None:
        start_date = end_date - timedelta(days=7)

    # Query response time stats
    stats = db.session.query(
        func.avg(AccessLog.response_time_ms).label('avg'),
        func.min(AccessLog.response_time_ms).label('min'),
        func.max(AccessLog.response_time_ms).label('max')
    ).filter(
        and_(
            AccessLog.timestamp.between(start_date, end_date),
            AccessLog.response_time_ms.isnot(None)
        )
    ).first()

    return {
        'start_date': start_date.date().isoformat(),
        'end_date': end_date.date().isoformat(),
        'avg_response_time_ms': round(stats.avg, 2) if stats.avg else None,
        'min_response_time_ms': stats.min,
        'max_response_time_ms': stats.max
    }


def get_overview_stats(days=7):
    """
    Get comprehensive overview of all analytics

    Args:
        days: Number of days to look back (default: 7)

    Returns:
        dict with comprehensive analytics overview
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Total requests
    total_requests = db.session.query(
        func.count(AccessLog.id)
    ).filter(
        AccessLog.timestamp >= start_date
    ).scalar() or 0

    return {
        'period_days': days,
        'start_date': start_date.date().isoformat(),
        'end_date': end_date.date().isoformat(),
        'total_requests': total_requests,
        'unique_visitors': get_unique_visitors_last_n_days(days),
        'popular_endpoints': get_popular_endpoints(start_date, end_date, limit=5),
        'device_breakdown': get_device_breakdown(start_date, end_date),
        'response_time_stats': get_response_time_stats(start_date, end_date)
    }
