"""
TrustAI Database Module - SQLite database operations
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)

class Database:
    """Database operations for TrustAI system"""
    
    def __init__(self, db_path: str = "trustai.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        try:
            # Users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    trust_score REAL DEFAULT 70.0
                )
            ''')
            
            # Activities table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    trust_score REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    context TEXT,  -- JSON
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Transactions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    merchant TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    trust_score REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Device fingerprints table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS device_fingerprints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    fingerprint TEXT NOT NULL,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    trust_level REAL DEFAULT 50.0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # User locations table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    ip_address TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    city TEXT,
                    country TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Trust scores history table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS trust_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    score REAL NOT NULL,
                    factors TEXT,  -- JSON
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Incidents table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    incident_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            conn.rollback()
        finally:
            conn.close()
    
    # User operations
    def create_user(self, username: str, email: str, password_hash: str, role: str = 'user') -> int:
        """Create a new user"""
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                (username, email, password_hash, role)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except Exception as e:
            logger.error(f"User creation error: {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        conn = self.get_connection()
        try:
            conn.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (user_id,)
            )
            conn.commit()
        finally:
            conn.close()
    
    # Activity logging
    def log_activity(self, user_id: int, action_type: str, trust_result: Dict[str, Any], context: Dict[str, Any]):
        """Log user activity"""
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT INTO activities 
                (user_id, action_type, trust_score, risk_level, decision, context, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                action_type,
                trust_result['score'],
                trust_result['risk_level'],
                trust_result['decision'],
                json.dumps(context, default=str),
                context.get('ip_address'),
                context.get('user_agent')
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Activity logging error: {str(e)}")
        finally:
            conn.close()
    
    def get_user_activities(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent user activities"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT * FROM activities 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            activities = []
            for row in cursor.fetchall():
                activity = dict(row)
                if activity['context']:
                    activity['context'] = json.loads(activity['context'])
                activities.append(activity)
            
            return activities
        finally:
            conn.close()
    
    # Transaction operations
    def log_transaction(self, user_id: int, amount: float, merchant: str, 
                       transaction_type: str, trust_score: float, risk_level: str) -> int:
        """Log a transaction"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                INSERT INTO transactions 
                (user_id, amount, merchant, transaction_type, trust_score, risk_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, amount, merchant, transaction_type, trust_score, risk_level))
            
            transaction_id = cursor.lastrowid
            conn.commit()
            return transaction_id
        except Exception as e:
            logger.error(f"Transaction logging error: {str(e)}")
            return None
        finally:
            conn.close()
    
    def get_user_transactions(self, user_id: int, since: datetime = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user transactions"""
        conn = self.get_connection()
        try:
            if since:
                cursor = conn.execute('''
                    SELECT * FROM transactions 
                    WHERE user_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (user_id, since, limit))
            else:
                cursor = conn.execute('''
                    SELECT * FROM transactions 
                    WHERE user_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (user_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # Device fingerprint operations
    def store_device_fingerprint(self, user_id: int, fingerprint: str):
        """Store or update device fingerprint"""
        conn = self.get_connection()
        try:
            # Check if fingerprint exists
            cursor = conn.execute(
                'SELECT id FROM device_fingerprints WHERE user_id = ? AND fingerprint = ?',
                (user_id, fingerprint)
            )
            
            if cursor.fetchone():
                # Update last seen
                conn.execute(
                    'UPDATE device_fingerprints SET last_seen = CURRENT_TIMESTAMP WHERE user_id = ? AND fingerprint = ?',
                    (user_id, fingerprint)
                )
            else:
                # Insert new fingerprint
                conn.execute(
                    'INSERT INTO device_fingerprints (user_id, fingerprint) VALUES (?, ?)',
                    (user_id, fingerprint)
                )
            
            conn.commit()
        except Exception as e:
            logger.error(f"Device fingerprint storage error: {str(e)}")
        finally:
            conn.close()
    
    def get_user_devices(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get user's recent devices"""
        conn = self.get_connection()
        try:
            since = datetime.utcnow() - timedelta(days=days)
            cursor = conn.execute('''
                SELECT * FROM device_fingerprints 
                WHERE user_id = ? AND last_seen >= ?
                ORDER BY last_seen DESC
            ''', (user_id, since))
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # Trust score operations
    def store_trust_score(self, user_id: int, result: Dict[str, Any]):
        """Store trust score result"""
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT INTO trust_scores (user_id, score, factors)
                VALUES (?, ?, ?)
            ''', (user_id, result['score'], json.dumps(result.get('risk_factors', {}))))
            
            # Update user's current trust score
            conn.execute(
                'UPDATE users SET trust_score = ? WHERE id = ?',
                (result['score'], user_id)
            )
            
            conn.commit()
        except Exception as e:
            logger.error(f"Trust score storage error: {str(e)}")
        finally:
            conn.close()
    
    def get_recent_trust_scores(self, user_id: int, limit: int = 5) -> List[float]:
        """Get recent trust scores for a user"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT score FROM trust_scores 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_trust_score_history(self, user_id: int, limit: int = 30) -> List[Dict[str, Any]]:
        """Get trust score history"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT score, timestamp FROM trust_scores 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            return [{'score': row[0], 'timestamp': row[1]} for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # Location operations
    def store_user_location(self, user_id: int, ip_address: str, location_data: Dict[str, Any]):
        """Store user location data"""
        conn = self.get_connection()
        try:
            # Check if location exists
            cursor = conn.execute(
                'SELECT id FROM user_locations WHERE user_id = ? AND ip_address = ?',
                (user_id, ip_address)
            )
            
            if cursor.fetchone():
                # Update last seen
                conn.execute(
                    'UPDATE user_locations SET last_seen = CURRENT_TIMESTAMP WHERE user_id = ? AND ip_address = ?',
                    (user_id, ip_address)
                )
            else:
                # Insert new location
                conn.execute('''
                    INSERT INTO user_locations 
                    (user_id, ip_address, latitude, longitude, city, country)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, ip_address,
                    location_data.get('latitude'),
                    location_data.get('longitude'),
                    location_data.get('city'),
                    location_data.get('country')
                ))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Location storage error: {str(e)}")
        finally:
            conn.close()
    
    def get_user_locations(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get user's recent locations"""
        conn = self.get_connection()
        try:
            since = datetime.utcnow() - timedelta(days=days)
            cursor = conn.execute('''
                SELECT * FROM user_locations 
                WHERE user_id = ? AND last_seen >= ?
                ORDER BY last_seen DESC
            ''', (user_id, since))
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # Admin dashboard methods
    def get_total_users(self) -> int:
        """Get total number of users"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('SELECT COUNT(*) FROM users')
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def get_total_transactions(self) -> int:
        """Get total number of transactions"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('SELECT COUNT(*) FROM transactions')
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def get_fraud_count(self) -> int:
        """Get number of high-risk activities detected"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('SELECT COUNT(*) FROM activities WHERE risk_level = "high"')
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def get_average_trust_score(self) -> float:
        """Get average trust score across all users"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('SELECT AVG(trust_score) FROM users')
            result = cursor.fetchone()[0]
            return round(result, 2) if result else 0.0
        finally:
            conn.close()

    def get_recent_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent high-risk activities"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT a.*, u.username
                FROM activities a
                JOIN users u ON a.user_id = u.id
                WHERE a.risk_level IN ('high', 'medium')
                ORDER BY a.timestamp DESC
                LIMIT ?
            ''', (limit,))

            alerts = []
            for row in cursor.fetchall():
                alert = dict(row)
                if alert['context']:
                    alert['context'] = json.loads(alert['context'])
                alerts.append(alert)

            return alerts
        finally:
            conn.close()

    def get_risk_distribution(self) -> Dict[str, int]:
        """Get distribution of risk levels"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT risk_level, COUNT(*) as count
                FROM activities
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY risk_level
            ''')

            distribution = {'low': 0, 'medium': 0, 'high': 0}
            for row in cursor.fetchall():
                distribution[row[0]] = row[1]

            return distribution
        finally:
            conn.close()

    def get_hourly_activity_stats(self) -> List[Dict[str, Any]]:
        """Get hourly activity statistics for the last 24 hours"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT
                    strftime('%H', timestamp) as hour,
                    COUNT(*) as total_activities,
                    SUM(CASE WHEN risk_level = 'high' THEN 1 ELSE 0 END) as high_risk,
                    AVG(trust_score) as avg_trust_score
                FROM activities
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY strftime('%H', timestamp)
                ORDER BY hour
            ''')

            stats = []
            for row in cursor.fetchall():
                stats.append({
                    'hour': int(row[0]),
                    'total_activities': row[1],
                    'high_risk': row[2],
                    'avg_trust_score': round(row[3], 2) if row[3] else 0
                })

            return stats
        finally:
            conn.close()

    # User behavior analysis methods
    def get_user_behavior_patterns(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's behavioral patterns"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT action_type, context, timestamp
                FROM activities
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 50
            ''', (user_id,))

            patterns = []
            for row in cursor.fetchall():
                pattern = {
                    'action_type': row[0],
                    'timestamp': row[2]
                }
                if row[1]:
                    context = json.loads(row[1])
                    pattern.update({
                        'hour_of_day': datetime.fromisoformat(row[2]).hour,
                        'day_of_week': datetime.fromisoformat(row[2]).weekday(),
                        'amount': context.get('amount', 0),
                        'merchant': context.get('merchant', ''),
                        'transaction_type': context.get('transaction_type', '')
                    })
                patterns.append(pattern)

            return patterns
        finally:
            conn.close()

    def get_user_time_patterns(self, user_id: int) -> Dict[str, Any]:
        """Get user's typical activity time patterns"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                FROM activities
                WHERE user_id = ?
                GROUP BY strftime('%H', timestamp)
                ORDER BY count DESC
            ''', (user_id,))

            hours_data = cursor.fetchall()
            if not hours_data:
                return {'typical_hours': []}

            # Get top 3 most active hours
            typical_hours = [int(row[0]) for row in hours_data[:3]]

            return {
                'typical_hours': typical_hours,
                'activity_distribution': {int(row[0]): row[1] for row in hours_data}
            }
        finally:
            conn.close()

    def get_user_incidents(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's security incidents"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT * FROM incidents
                WHERE user_id = ?
                ORDER BY timestamp DESC
            ''', (user_id,))

            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_user_activity_score(self, user_id: int) -> float:
        """Calculate user activity score based on engagement"""
        conn = self.get_connection()
        try:
            # Count activities in last 30 days
            cursor = conn.execute('''
                SELECT COUNT(*) FROM activities
                WHERE user_id = ? AND timestamp >= datetime('now', '-30 days')
            ''', (user_id,))

            activity_count = cursor.fetchone()[0]

            # Convert to score (max 30 points)
            return min(30, activity_count)
        finally:
            conn.close()

    def get_user_device_trust(self, user_id: int) -> float:
        """Get user's device trust level"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT AVG(trust_level) FROM device_fingerprints
                WHERE user_id = ?
            ''', (user_id,))

            result = cursor.fetchone()[0]
            return round(result, 2) if result else 50.0
        finally:
            conn.close()

    def get_user_location_trust(self, user_id: int) -> float:
        """Get user's location trust level"""
        conn = self.get_connection()
        try:
            # Simple calculation based on number of known locations
            cursor = conn.execute('''
                SELECT COUNT(*) FROM user_locations
                WHERE user_id = ?
            ''', (user_id,))

            location_count = cursor.fetchone()[0]

            # More known locations = higher trust (up to a point)
            if location_count == 0:
                return 30.0
            elif location_count <= 3:
                return 60.0 + (location_count * 10)
            else:
                return 90.0
        finally:
            conn.close()

    def get_user_behavior_trust(self, user_id: int) -> float:
        """Get user's behavioral trust level"""
        conn = self.get_connection()
        try:
            # Calculate based on consistency of recent activities
            cursor = conn.execute('''
                SELECT AVG(trust_score) FROM activities
                WHERE user_id = ? AND timestamp >= datetime('now', '-7 days')
            ''', (user_id,))

            result = cursor.fetchone()[0]
            return round(result, 2) if result else 70.0
        finally:
            conn.close()

    def get_user_account_age(self, user_id: int) -> int:
        """Get user account age in days"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT julianday('now') - julianday(created_at) as age_days
                FROM users
                WHERE id = ?
            ''', (user_id,))

            result = cursor.fetchone()
            return int(result[0]) if result else 0
        finally:
            conn.close()

    def get_user_verification_status(self, user_id: int) -> bool:
        """Get user verification status"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('SELECT verified FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            return bool(result[0]) if result else False
        finally:
            conn.close()
