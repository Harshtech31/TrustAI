"""
TrustAI Utility Functions
"""

import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('trustai.log'),
            logging.StreamHandler()
        ]
    )

def validate_input(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate that all required fields are present in input data"""
    if not data:
        return False
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            return False
    
    return True

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    result = {
        'valid': True,
        'errors': []
    }
    
    if len(password) < 8:
        result['valid'] = False
        result['errors'].append('Password must be at least 8 characters long')
    
    if not re.search(r'[A-Z]', password):
        result['valid'] = False
        result['errors'].append('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        result['valid'] = False
        result['errors'].append('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        result['valid'] = False
        result['errors'].append('Password must contain at least one digit')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result['valid'] = False
        result['errors'].append('Password must contain at least one special character')
    
    return result

def sanitize_input(data: str) -> str:
    """Sanitize input data to prevent injection attacks"""
    if not isinstance(data, str):
        return str(data)
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', data)
    
    # Limit length
    return sanitized[:1000]

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"

def calculate_risk_color(risk_level: str) -> str:
    """Get color code for risk level"""
    colors = {
        'low': '#4CAF50',      # Green
        'medium': '#FF9800',   # Orange
        'high': '#F44336'      # Red
    }
    return colors.get(risk_level, '#9E9E9E')  # Gray for unknown

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display"""
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    return timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')

def get_client_ip(request) -> str:
    """Get client IP address from request"""
    # Check for forwarded IP (behind proxy)
    forwarded_ip = request.headers.get('X-Forwarded-For')
    if forwarded_ip:
        return forwarded_ip.split(',')[0].strip()
    
    # Check for real IP
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Fall back to remote address
    return request.remote_addr or '127.0.0.1'

def generate_transaction_id() -> str:
    """Generate unique transaction ID"""
    import uuid
    return f"TXN_{uuid.uuid4().hex[:12].upper()}"

def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """Mask sensitive data (e.g., credit card numbers, emails)"""
    if not data or len(data) <= visible_chars:
        return data
    
    visible_start = data[:visible_chars//2] if visible_chars > 2 else data[:1]
    visible_end = data[-(visible_chars//2):] if visible_chars > 2 else data[-1:]
    masked_middle = mask_char * (len(data) - visible_chars)
    
    return f"{visible_start}{masked_middle}{visible_end}"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 100.0 if new_value > 0 else 0.0
    
    return ((new_value - old_value) / old_value) * 100

def is_business_hours(timestamp: datetime = None) -> bool:
    """Check if timestamp is during business hours (9 AM - 5 PM, Mon-Fri)"""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    # Monday = 0, Sunday = 6
    if timestamp.weekday() >= 5:  # Weekend
        return False
    
    hour = timestamp.hour
    return 9 <= hour <= 17

def get_time_of_day(timestamp: datetime = None) -> str:
    """Get time of day category"""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    hour = timestamp.hour
    
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    return {
        'database_url': os.getenv('DATABASE_URL', 'sqlite:///trustai.db'),
        'jwt_secret': os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production'),
        'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379'),
        'email_service': {
            'smtp_server': os.getenv('SMTP_SERVER', 'localhost'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME', ''),
            'password': os.getenv('EMAIL_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', 'noreply@trustai.com')
        },
        'security': {
            'max_login_attempts': int(os.getenv('MAX_LOGIN_ATTEMPTS', '5')),
            'lockout_duration': int(os.getenv('LOCKOUT_DURATION', '900')),  # 15 minutes
            'session_timeout': int(os.getenv('SESSION_TIMEOUT', '3600')),  # 1 hour
        },
        'fraud_detection': {
            'high_risk_threshold': float(os.getenv('HIGH_RISK_THRESHOLD', '40')),
            'medium_risk_threshold': float(os.getenv('MEDIUM_RISK_THRESHOLD', '70')),
            'max_transaction_amount': float(os.getenv('MAX_TRANSACTION_AMOUNT', '10000')),
            'max_daily_transactions': int(os.getenv('MAX_DAILY_TRANSACTIONS', '20'))
        }
    }

def export_data_to_json(data: Any, filename: str) -> bool:
    """Export data to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logging.error(f"Data export error: {str(e)}")
        return False

def import_data_from_json(filename: str) -> Optional[Any]:
    """Import data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Data import error: {str(e)}")
        return None

def calculate_trust_score_trend(scores: List[float]) -> str:
    """Calculate trust score trend"""
    if len(scores) < 2:
        return 'stable'
    
    recent_avg = sum(scores[:3]) / min(3, len(scores))
    older_avg = sum(scores[3:6]) / min(3, len(scores[3:]))
    
    if len(scores) < 4:
        return 'stable'
    
    diff = recent_avg - older_avg
    
    if diff > 5:
        return 'improving'
    elif diff < -5:
        return 'declining'
    else:
        return 'stable'

def get_risk_recommendation(risk_level: str, trust_score: float) -> List[str]:
    """Get risk-based recommendations"""
    recommendations = []
    
    if risk_level == 'high':
        recommendations.extend([
            'Block transaction immediately',
            'Require manual review',
            'Contact customer for verification',
            'Flag account for monitoring'
        ])
    elif risk_level == 'medium':
        recommendations.extend([
            'Require additional authentication',
            'Send notification to customer',
            'Monitor for unusual patterns',
            'Consider transaction limits'
        ])
    else:  # low risk
        recommendations.extend([
            'Allow transaction',
            'Continue normal monitoring',
            'Update user behavior profile'
        ])
    
    # Score-specific recommendations
    if trust_score < 30:
        recommendations.append('Consider account suspension')
    elif trust_score < 50:
        recommendations.append('Increase monitoring frequency')
    elif trust_score > 80:
        recommendations.append('Consider trusted user benefits')
    
    return recommendations

def anonymize_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Anonymize user data for analytics"""
    anonymized = data.copy()
    
    # Remove or mask PII
    if 'email' in anonymized:
        anonymized['email'] = mask_sensitive_data(anonymized['email'])
    
    if 'username' in anonymized:
        anonymized['username'] = f"user_{hash(anonymized['username']) % 10000}"
    
    if 'ip_address' in anonymized:
        ip_parts = anonymized['ip_address'].split('.')
        if len(ip_parts) == 4:
            anonymized['ip_address'] = f"{ip_parts[0]}.{ip_parts[1]}.xxx.xxx"
    
    return anonymized
