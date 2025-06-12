"""
TrustAI Authentication Module
"""

import hashlib
import secrets
import string
from typing import Dict, Optional, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AuthManager:
    """Handle user authentication and MFA"""
    
    def __init__(self, database):
        self.db = database
        self.mfa_challenges = {}  # In production, use Redis or database
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, stored_hash = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return stored_hash == password_hash_check.hex()
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password"""
        try:
            user = self.db.get_user_by_username(username)
            if not user:
                return None
            
            if self.verify_password(password, user['password_hash']):
                # Update last login
                self.db.update_last_login(user['id'])
                
                # Return user info (without password hash)
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role'],
                    'verified': user['verified']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    
    def register_user(self, username: str, email: str, password: str, role: str = 'user') -> Optional[int]:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = self.db.get_user_by_username(username)
            if existing_user:
                return None
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Create user
            user_id = self.db.create_user(username, email, password_hash, role)
            return user_id
            
        except Exception as e:
            logger.error(f"User registration error: {str(e)}")
            return None
    
    def generate_mfa_challenge(self, user_id: int) -> Dict[str, str]:
        """Generate MFA challenge for user"""
        # Generate 6-digit code
        code = ''.join(secrets.choice(string.digits) for _ in range(6))
        
        # Store challenge (expires in 5 minutes)
        challenge_id = secrets.token_urlsafe(32)
        self.mfa_challenges[challenge_id] = {
            'user_id': user_id,
            'code': code,
            'expires_at': datetime.utcnow() + timedelta(minutes=5)
        }
        
        # In production, send code via SMS/email
        logger.info(f"MFA code for user {user_id}: {code}")
        
        return {
            'challenge_id': challenge_id,
            'message': 'MFA code sent to your registered device',
            'expires_in': 300  # 5 minutes
        }
    
    def verify_mfa_challenge(self, challenge_id: str, code: str) -> bool:
        """Verify MFA challenge code"""
        try:
            challenge = self.mfa_challenges.get(challenge_id)
            if not challenge:
                return False
            
            # Check if expired
            if datetime.utcnow() > challenge['expires_at']:
                del self.mfa_challenges[challenge_id]
                return False
            
            # Verify code
            if challenge['code'] == code:
                del self.mfa_challenges[challenge_id]
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"MFA verification error: {str(e)}")
            return False
    
    def cleanup_expired_challenges(self):
        """Clean up expired MFA challenges"""
        current_time = datetime.utcnow()
        expired_challenges = [
            challenge_id for challenge_id, challenge in self.mfa_challenges.items()
            if current_time > challenge['expires_at']
        ]
        
        for challenge_id in expired_challenges:
            del self.mfa_challenges[challenge_id]
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            user = self.db.get_user(user_id)
            if not user:
                return False
            
            # Verify old password
            if not self.verify_password(old_password, user['password_hash']):
                return False
            
            # Hash new password
            new_password_hash = self.hash_password(new_password)
            
            # Update in database
            conn = self.db.get_connection()
            try:
                conn.execute(
                    'UPDATE users SET password_hash = ? WHERE id = ?',
                    (new_password_hash, user_id)
                )
                conn.commit()
                return True
            finally:
                conn.close()
                
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            return False
    
    def reset_password_request(self, email: str) -> Optional[str]:
        """Request password reset"""
        try:
            # Find user by email
            conn = self.db.get_connection()
            cursor = conn.execute('SELECT id, username FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return None
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            
            # Store reset token (expires in 1 hour)
            # In production, store in database with expiration
            self.mfa_challenges[f"reset_{reset_token}"] = {
                'user_id': user[0],
                'type': 'password_reset',
                'expires_at': datetime.utcnow() + timedelta(hours=1)
            }
            
            # In production, send email with reset link
            logger.info(f"Password reset token for {email}: {reset_token}")
            
            return reset_token
            
        except Exception as e:
            logger.error(f"Password reset request error: {str(e)}")
            return None
    
    def reset_password(self, reset_token: str, new_password: str) -> bool:
        """Reset password with token"""
        try:
            challenge_key = f"reset_{reset_token}"
            challenge = self.mfa_challenges.get(challenge_key)
            
            if not challenge or challenge['type'] != 'password_reset':
                return False
            
            # Check if expired
            if datetime.utcnow() > challenge['expires_at']:
                del self.mfa_challenges[challenge_key]
                return False
            
            # Hash new password
            new_password_hash = self.hash_password(new_password)
            
            # Update password
            conn = self.db.get_connection()
            try:
                conn.execute(
                    'UPDATE users SET password_hash = ? WHERE id = ?',
                    (new_password_hash, challenge['user_id'])
                )
                conn.commit()
                
                # Remove reset token
                del self.mfa_challenges[challenge_key]
                
                return True
            finally:
                conn.close()
                
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return False
    
    def verify_user_email(self, user_id: int) -> bool:
        """Mark user email as verified"""
        try:
            conn = self.db.get_connection()
            try:
                conn.execute(
                    'UPDATE users SET verified = TRUE WHERE id = ?',
                    (user_id,)
                )
                conn.commit()
                return True
            finally:
                conn.close()
                
        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            return False
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        try:
            user = self.db.get_user(user_id)
            return user and user.get('role') == 'admin'
        except Exception as e:
            logger.error(f"Admin check error: {str(e)}")
            return False
