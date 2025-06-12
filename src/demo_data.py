"""
TrustAI Demo Data Generator
Creates realistic demo data for presentations and testing
"""

import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
from faker import Faker

logger = logging.getLogger(__name__)

class DemoDataGenerator:
    """Generate demo data for TrustAI system"""
    
    def __init__(self, database):
        self.db = database
        self.fake = Faker()
        
        # Demo user personas
        self.user_personas = [
            {
                'username': 'alice_normal',
                'email': 'alice@example.com',
                'password': 'SecurePass123!',
                'role': 'user',
                'behavior': 'normal',
                'trust_level': 'high'
            },
            {
                'username': 'bob_suspicious',
                'email': 'bob@example.com', 
                'password': 'SecurePass123!',
                'role': 'user',
                'behavior': 'suspicious',
                'trust_level': 'medium'
            },
            {
                'username': 'charlie_fraudster',
                'email': 'charlie@example.com',
                'password': 'SecurePass123!',
                'role': 'user',
                'behavior': 'fraudulent',
                'trust_level': 'low'
            },
            {
                'username': 'diana_traveler',
                'email': 'diana@example.com',
                'password': 'SecurePass123!',
                'role': 'user',
                'behavior': 'traveling',
                'trust_level': 'medium'
            },
            {
                'username': 'admin_user',
                'email': 'admin@trustai.com',
                'password': 'AdminPass123!',
                'role': 'admin',
                'behavior': 'normal',
                'trust_level': 'high'
            }
        ]
        
        # Common merchants for transactions
        self.merchants = [
            'Amazon', 'Walmart', 'Target', 'Best Buy', 'Home Depot',
            'Starbucks', 'McDonald\'s', 'Uber', 'Netflix', 'Spotify',
            'Apple Store', 'Google Play', 'Steam', 'PayPal', 'Venmo'
        ]
        
        # Transaction types
        self.transaction_types = [
            'purchase', 'refund', 'transfer', 'subscription', 'withdrawal'
        ]
    
    def create_demo_users(self):
        """Create demo users with different personas"""
        from src.auth import AuthManager
        auth_manager = AuthManager(self.db)
        
        created_users = []
        
        for persona in self.user_personas:
            # Check if user already exists
            existing_user = self.db.get_user_by_username(persona['username'])
            if existing_user:
                logger.info(f"User {persona['username']} already exists")
                created_users.append(existing_user)
                continue
            
            # Create user
            user_id = auth_manager.register_user(
                persona['username'],
                persona['email'],
                persona['password'],
                persona['role']
            )
            
            if user_id:
                # Verify email for demo users
                auth_manager.verify_user_email(user_id)
                
                user = self.db.get_user(user_id)
                created_users.append(user)
                logger.info(f"Created demo user: {persona['username']}")
            else:
                logger.error(f"Failed to create user: {persona['username']}")
        
        return created_users
    
    def generate_demo_scenarios(self):
        """Generate comprehensive demo scenarios"""
        users = self.create_demo_users()
        
        # Generate historical data for each user
        for user in users:
            persona = next(p for p in self.user_personas if p['username'] == user['username'])
            self._generate_user_history(user, persona)
        
        logger.info("Demo scenarios generated successfully")
    
    def _generate_user_history(self, user: Dict[str, Any], persona: Dict[str, Any]):
        """Generate historical activity for a user based on their persona"""
        user_id = user['id']
        behavior = persona['behavior']
        
        # Generate activities over the last 30 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        if behavior == 'normal':
            self._generate_normal_behavior(user_id, start_date, end_date)
        elif behavior == 'suspicious':
            self._generate_suspicious_behavior(user_id, start_date, end_date)
        elif behavior == 'fraudulent':
            self._generate_fraudulent_behavior(user_id, start_date, end_date)
        elif behavior == 'traveling':
            self._generate_traveling_behavior(user_id, start_date, end_date)
    
    def _generate_normal_behavior(self, user_id: int, start_date: datetime, end_date: datetime):
        """Generate normal user behavior patterns"""
        current_date = start_date
        
        while current_date < end_date:
            # Normal users login 1-3 times per day during business hours
            if random.random() < 0.8:  # 80% chance of activity per day
                login_time = self._get_business_hours_time(current_date)
                self._create_login_activity(user_id, login_time, trust_score=85 + random.uniform(-10, 10))
                
                # 60% chance of making a transaction after login
                if random.random() < 0.6:
                    transaction_time = login_time + timedelta(minutes=random.randint(5, 60))
                    amount = random.uniform(853, 17056)  # Normal transaction amounts (₹853-₹17,056)
                    self._create_transaction_activity(user_id, transaction_time, amount, trust_score=80 + random.uniform(-15, 15))
            
            current_date += timedelta(days=1)
    
    def _generate_suspicious_behavior(self, user_id: int, start_date: datetime, end_date: datetime):
        """Generate suspicious behavior patterns"""
        current_date = start_date
        
        while current_date < end_date:
            if random.random() < 0.7:  # 70% chance of activity per day
                # Sometimes login at unusual hours
                if random.random() < 0.3:
                    login_time = self._get_unusual_hours_time(current_date)
                    trust_score = 45 + random.uniform(-15, 20)
                else:
                    login_time = self._get_business_hours_time(current_date)
                    trust_score = 60 + random.uniform(-20, 15)
                
                self._create_login_activity(user_id, login_time, trust_score=trust_score)
                
                # Higher chance of multiple transactions
                if random.random() < 0.8:
                    num_transactions = random.randint(1, 4)
                    for i in range(num_transactions):
                        transaction_time = login_time + timedelta(minutes=random.randint(1, 120))
                        # Sometimes large amounts
                        if random.random() < 0.3:
                            amount = random.uniform(42640, 170560)  # Large amounts (₹42,640-₹1,70,560)
                            transaction_trust = 35 + random.uniform(-15, 25)
                        else:
                            amount = random.uniform(1706, 25584)  # Medium amounts (₹1,706-₹25,584)
                            transaction_trust = 55 + random.uniform(-20, 20)
                        
                        self._create_transaction_activity(user_id, transaction_time, amount, trust_score=transaction_trust)
            
            current_date += timedelta(days=1)
    
    def _generate_fraudulent_behavior(self, user_id: int, start_date: datetime, end_date: datetime):
        """Generate fraudulent behavior patterns"""
        current_date = start_date
        
        while current_date < end_date:
            if random.random() < 0.4:  # Less frequent but more suspicious
                # Often login at unusual hours
                if random.random() < 0.7:
                    login_time = self._get_unusual_hours_time(current_date)
                else:
                    login_time = self._get_business_hours_time(current_date)
                
                trust_score = 25 + random.uniform(-15, 20)
                self._create_login_activity(user_id, login_time, trust_score=trust_score)
                
                # Multiple rapid transactions
                if random.random() < 0.9:
                    num_transactions = random.randint(3, 8)
                    for i in range(num_transactions):
                        transaction_time = login_time + timedelta(minutes=random.randint(0, 30))
                        # Large amounts
                        amount = random.uniform(68224, 426400)  # Fraudulent amounts (₹68,224-₹4,26,400)
                        transaction_trust = 15 + random.uniform(-10, 25)
                        
                        self._create_transaction_activity(user_id, transaction_time, amount, trust_score=transaction_trust)
            
            current_date += timedelta(days=1)
    
    def _generate_traveling_behavior(self, user_id: int, start_date: datetime, end_date: datetime):
        """Generate traveling user behavior (legitimate but triggers location alerts)"""
        current_date = start_date
        locations = ['New York', 'Los Angeles', 'Chicago', 'Miami', 'London', 'Paris']
        current_location = 0
        
        while current_date < end_date:
            # Change location every 3-5 days
            if random.random() < 0.3:
                current_location = (current_location + 1) % len(locations)
            
            if random.random() < 0.6:
                login_time = self._get_random_time(current_date)
                # Lower trust score due to location changes
                trust_score = 55 + random.uniform(-20, 25)
                self._create_login_activity(user_id, login_time, trust_score=trust_score)
                
                # Normal transaction amounts but flagged due to location
                if random.random() < 0.5:
                    transaction_time = login_time + timedelta(minutes=random.randint(10, 90))
                    amount = random.uniform(4264, 34112)  # Traveler amounts (₹4,264-₹34,112)
                    transaction_trust = 50 + random.uniform(-25, 20)
                    
                    self._create_transaction_activity(user_id, transaction_time, amount, trust_score=transaction_trust)
            
            current_date += timedelta(days=1)
    
    def _get_business_hours_time(self, date: datetime) -> datetime:
        """Get random time during business hours"""
        hour = random.randint(9, 17)
        minute = random.randint(0, 59)
        return date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def _get_unusual_hours_time(self, date: datetime) -> datetime:
        """Get random time during unusual hours"""
        unusual_hours = list(range(0, 6)) + list(range(22, 24))
        hour = random.choice(unusual_hours)
        minute = random.randint(0, 59)
        return date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def _get_random_time(self, date: datetime) -> datetime:
        """Get random time of day"""
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        return date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def _create_login_activity(self, user_id: int, timestamp: datetime, trust_score: float):
        """Create a login activity record"""
        context = {
            'user_id': user_id,
            'action': 'login',
            'ip_address': self.fake.ipv4(),
            'user_agent': self.fake.user_agent(),
            'timestamp': timestamp
        }
        
        risk_level = self._get_risk_level(trust_score)
        decision = 'allow' if risk_level == 'low' else ('challenge' if risk_level == 'medium' else 'block')
        
        trust_result = {
            'score': trust_score,
            'risk_level': risk_level,
            'decision': decision,
            'explanation': f"Trust score: {trust_score:.1f}/100"
        }
        
        self.db.log_activity(user_id, 'login', trust_result, context)
    
    def _create_transaction_activity(self, user_id: int, timestamp: datetime, amount: float, trust_score: float):
        """Create a transaction activity record"""
        merchant = random.choice(self.merchants)
        transaction_type = random.choice(self.transaction_types)
        
        context = {
            'user_id': user_id,
            'action': 'transaction',
            'amount': amount,
            'merchant': merchant,
            'transaction_type': transaction_type,
            'ip_address': self.fake.ipv4(),
            'user_agent': self.fake.user_agent(),
            'timestamp': timestamp
        }
        
        risk_level = self._get_risk_level(trust_score)
        decision = 'allow' if risk_level == 'low' else ('verify' if risk_level == 'medium' else 'block')
        
        trust_result = {
            'score': trust_score,
            'risk_level': risk_level,
            'decision': decision,
            'explanation': f"Trust score: {trust_score:.1f}/100"
        }
        
        self.db.log_activity(user_id, 'transaction', trust_result, context)
        
        # Also log in transactions table
        status = 'completed' if decision == 'allow' else ('pending' if decision == 'verify' else 'blocked')
        self.db.log_transaction(user_id, amount, merchant, transaction_type, trust_score, risk_level)
    
    def _get_risk_level(self, trust_score: float) -> str:
        """Convert trust score to risk level"""
        if trust_score >= 70:
            return 'low'
        elif trust_score >= 40:
            return 'medium'
        else:
            return 'high'
    
    def generate_real_time_demo_data(self):
        """Generate real-time demo data for live demonstrations"""
        users = self.db.get_total_users()
        if users < 3:
            self.create_demo_users()
        
        # Create some recent activities for demo
        demo_users = [
            self.db.get_user_by_username('alice_normal'),
            self.db.get_user_by_username('bob_suspicious'),
            self.db.get_user_by_username('charlie_fraudster')
        ]
        
        current_time = datetime.utcnow()
        
        for user in demo_users:
            if user:
                # Create a recent login
                login_time = current_time - timedelta(minutes=random.randint(1, 30))
                persona = next(p for p in self.user_personas if p['username'] == user['username'])
                
                if persona['behavior'] == 'normal':
                    trust_score = 85 + random.uniform(-5, 10)
                elif persona['behavior'] == 'suspicious':
                    trust_score = 55 + random.uniform(-15, 20)
                else:  # fraudulent
                    trust_score = 25 + random.uniform(-10, 15)
                
                self._create_login_activity(user['id'], login_time, trust_score)
        
        logger.info("Real-time demo data generated")
