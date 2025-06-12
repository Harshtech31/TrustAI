"""
TrustAI - Real-Time Fraud Detection & Trust Scoring System
Main Flask Application
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from datetime import datetime, timedelta
import logging

from src.trust_engine import TrustEngine
from src.database import Database
from src.auth import AuthManager
from src.utils import setup_logging, validate_input
from src.demo_data import DemoDataGenerator

# Initialize Flask app
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
CORS(app)
jwt = JWTManager(app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

# Initialize components
db = Database()
trust_engine = TrustEngine(db)
auth_manager = AuthManager(db)
demo_generator = DemoDataGenerator(db)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """User authentication endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        if not validate_input(data, ['username', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Authenticate user
        user = auth_manager.authenticate(data['username'], data['password'])
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user['id']))
        
        # Analyze login for fraud detection
        context = {
            'user_id': user['id'],
            'action': 'login',
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'timestamp': datetime.utcnow()
        }
        
        trust_result = trust_engine.analyze_activity(context)
        
        # Log the activity
        db.log_activity(user['id'], 'login', trust_result, context)
        
        response = {
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            },
            'trust_score': trust_result['score'],
            'risk_level': trust_result['risk_level'],
            'requires_mfa': trust_result.get('requires_mfa', False)
        }

        if trust_result.get('requires_mfa', False):
            response['mfa_challenge'] = auth_manager.generate_mfa_challenge(user['id'])
        
        return jsonify(response)

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/verify-mfa', methods=['POST'])
@limiter.limit("10 per minute")
def verify_mfa():
    """Verify MFA code"""
    try:
        data = request.get_json()

        # Validate input
        if not validate_input(data, ['challenge_id', 'code']):
            return jsonify({'error': 'Missing required fields'}), 400

        # Debug logging
        logger.info(f"MFA verification attempt - Challenge ID: {data['challenge_id']}, Code: {data['code']}")
        logger.info(f"Available challenges: {list(auth_manager.mfa_challenges.keys())}")

        # Get user from challenge BEFORE verification (since verification deletes the challenge)
        challenge = auth_manager.mfa_challenges.get(data['challenge_id'])
        if not challenge:
            logger.warning(f"Challenge not found: {data['challenge_id']}")
            return jsonify({'error': 'Invalid challenge'}), 400

        user_id = challenge['user_id']

        # Verify MFA code
        is_valid = auth_manager.verify_mfa_challenge(data['challenge_id'], data['code'])

        if not is_valid:
            logger.warning(f"MFA verification failed for challenge {data['challenge_id']}")
            return jsonify({'error': 'Invalid or expired MFA code'}), 400

        user = auth_manager.db.get_user(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Create access token
        access_token = create_access_token(identity=str(user['id']))

        response = {
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            },
            'message': 'MFA verification successful'
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"MFA verification error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/transaction/analyze', methods=['POST'])
@jwt_required()
@limiter.limit("100 per minute")
def analyze_transaction():
    """Analyze transaction for fraud detection"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate input
        required_fields = ['amount', 'merchant', 'transaction_type']
        if not validate_input(data, required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Build context
        context = {
            'user_id': user_id,
            'action': 'transaction',
            'amount': float(data['amount']),
            'merchant': data['merchant'],
            'transaction_type': data['transaction_type'],
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'timestamp': datetime.utcnow()
        }
        
        # Analyze with trust engine
        trust_result = trust_engine.analyze_activity(context)
        
        # Log the activity
        db.log_activity(user_id, 'transaction', trust_result, context)
        
        response = {
            'transaction_id': trust_result.get('transaction_id'),
            'trust_score': trust_result['score'],
            'risk_level': trust_result['risk_level'],
            'decision': trust_result['decision'],
            'explanation': trust_result['explanation'],
            'requires_verification': trust_result.get('requires_verification', False),
            'recommended_actions': trust_result.get('recommended_actions', [])
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Transaction analysis error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/user/trust-score', methods=['GET'])
@jwt_required()
def get_user_trust_score():
    """Get current user's trust score and history"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get current trust score
        current_score = trust_engine.get_user_trust_score(user_id)
        
        # Get trust score history
        history = db.get_trust_score_history(user_id, limit=30)
        
        # Get recent activities
        activities = db.get_user_activities(user_id, limit=10)
        
        return jsonify({
            'current_score': current_score,
            'history': history,
            'recent_activities': activities,
            'score_factors': trust_engine.get_score_factors(user_id)
        })
        
    except Exception as e:
        logger.error(f"Trust score retrieval error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    """Admin dashboard data"""
    try:
        user_id = int(get_jwt_identity())

        # Check if user is admin (simplified for demo)
        user = db.get_user(user_id)
        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get dashboard metrics
        metrics = {
            'total_users': db.get_total_users(),
            'total_transactions': db.get_total_transactions(),
            'fraud_detected': db.get_fraud_count(),
            'avg_trust_score': db.get_average_trust_score(),
            'recent_alerts': db.get_recent_alerts(limit=20),
            'risk_distribution': db.get_risk_distribution(),
            'hourly_activity': db.get_hourly_activity_stats()
        }
        
        return jsonify(metrics)
        
    except Exception as e:
        logger.error(f"Admin dashboard error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/demo/generate-data', methods=['POST'])
@jwt_required()
def generate_demo_data():
    """Generate demo data for presentation"""
    try:
        user_id = int(get_jwt_identity())

        # Check if user is admin
        user = db.get_user(user_id)
        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Generate demo data
        demo_generator.generate_demo_scenarios()
        
        return jsonify({
            'message': 'Demo data generated successfully',
            'scenarios_created': 5
        })
        
    except Exception as e:
        logger.error(f"Demo data generation error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded', 'message': str(e.description)}), 429

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database
    db.init_db()
    
    # Create demo admin user
    demo_generator.create_demo_users()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
