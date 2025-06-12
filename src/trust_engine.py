"""
TrustAI Trust Engine - Core fraud detection and trust scoring logic
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
import hashlib
import json

logger = logging.getLogger(__name__)

class TrustEngine:
    """
    Core trust scoring and fraud detection engine
    """
    
    def __init__(self, database):
        self.db = database
        self.risk_thresholds = {
            'low': 70,      # Score >= 70: Low risk
            'medium': 40,   # Score 40-69: Medium risk  
            'high': 0       # Score < 40: High risk
        }
        
        # Scoring weights for different factors
        self.scoring_weights = {
            'device_consistency': 0.25,
            'transaction_velocity': 0.20,
            'geolocation_risk': 0.20,
            'behavioral_pattern': 0.15,
            'account_history': 0.10,
            'time_pattern': 0.10
        }
    
    def analyze_activity(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for analyzing user activity
        """
        try:
            # Calculate individual risk factors
            risk_factors = self._calculate_risk_factors(context)
            
            # Calculate overall trust score
            trust_score = self._calculate_trust_score(risk_factors)
            
            # Determine risk level and decision
            risk_level = self._determine_risk_level(trust_score)
            decision = self._make_decision(trust_score, risk_level, context)
            
            # Generate explanation
            explanation = self._generate_explanation(risk_factors, trust_score)
            
            result = {
                'score': round(trust_score, 2),
                'risk_level': risk_level,
                'decision': decision['action'],
                'explanation': explanation,
                'risk_factors': risk_factors,
                'requires_mfa': decision.get('requires_mfa', False),
                'requires_verification': decision.get('requires_verification', False),
                'recommended_actions': decision.get('recommended_actions', []),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Store the result
            self._store_trust_result(context['user_id'], result)
            
            return result
            
        except Exception as e:
            logger.error(f"Trust analysis error: {str(e)}")
            # Return safe default for errors
            return {
                'score': 50.0,
                'risk_level': 'medium',
                'decision': 'review',
                'explanation': 'Unable to complete analysis',
                'requires_verification': True
            }
    
    def _calculate_risk_factors(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Calculate individual risk factor scores"""
        factors = {}
        
        # Device consistency analysis
        factors['device_consistency'] = self._analyze_device_consistency(context)
        
        # Transaction velocity analysis
        factors['transaction_velocity'] = self._analyze_transaction_velocity(context)
        
        # Geolocation risk analysis
        factors['geolocation_risk'] = self._analyze_geolocation_risk(context)
        
        # Behavioral pattern analysis
        factors['behavioral_pattern'] = self._analyze_behavioral_pattern(context)
        
        # Account history analysis
        factors['account_history'] = self._analyze_account_history(context)
        
        # Time pattern analysis
        factors['time_pattern'] = self._analyze_time_pattern(context)
        
        return factors
    
    def _analyze_device_consistency(self, context: Dict[str, Any]) -> float:
        """Analyze device fingerprint consistency"""
        user_id = context['user_id']
        current_fingerprint = self._generate_device_fingerprint(context)
        
        # Get recent device fingerprints
        recent_devices = self.db.get_user_devices(user_id, days=30)
        
        if not recent_devices:
            # New user or no device history - moderate risk
            return 60.0
        
        # Check if current device matches any recent devices
        for device in recent_devices:
            if device['fingerprint'] == current_fingerprint:
                return 90.0  # Known device - low risk
        
        # Check for similar devices (partial matches)
        similarity_scores = []
        for device in recent_devices:
            similarity = self._calculate_device_similarity(
                current_fingerprint, device['fingerprint']
            )
            similarity_scores.append(similarity)
        
        if similarity_scores:
            max_similarity = max(similarity_scores)
            if max_similarity > 0.8:
                return 75.0  # Similar device - low-medium risk
            elif max_similarity > 0.5:
                return 50.0  # Somewhat similar - medium risk
        
        return 30.0  # New/unknown device - higher risk
    
    def _analyze_transaction_velocity(self, context: Dict[str, Any]) -> float:
        """Analyze transaction frequency and velocity"""
        if context['action'] != 'transaction':
            return 80.0  # Not a transaction, return neutral score
        
        user_id = context['user_id']
        current_time = context['timestamp']
        amount = context.get('amount', 0)
        
        # Get recent transactions (last 24 hours)
        recent_transactions = self.db.get_user_transactions(user_id, limit=100)
        
        if not recent_transactions:
            return 85.0  # First transaction - generally safe
        
        # Calculate velocity metrics
        transaction_count = len(recent_transactions)
        total_amount = sum(t['amount'] for t in recent_transactions) + amount
        
        # Check for suspicious patterns
        risk_score = 100.0
        
        # Too many transactions in short time
        if transaction_count > 10:
            risk_score -= 30
        elif transaction_count > 5:
            risk_score -= 15
        
        # Large amounts
        if amount > 1000:
            risk_score -= 20
        elif amount > 500:
            risk_score -= 10
        
        # High total daily amount
        if total_amount > 5000:
            risk_score -= 25
        elif total_amount > 2000:
            risk_score -= 15
        
        # Check for rapid-fire transactions (within minutes)
        recent_minutes = [
            t for t in recent_transactions 
            if (current_time - t['timestamp']).total_seconds() < 300
        ]
        if len(recent_minutes) > 3:
            risk_score -= 40
        
        return max(0, risk_score)
    
    def _analyze_geolocation_risk(self, context: Dict[str, Any]) -> float:
        """Analyze geolocation-based risk"""
        user_id = context['user_id']
        current_ip = context.get('ip_address')
        
        if not current_ip:
            return 70.0  # No IP info - moderate risk
        
        # Get user's location history
        location_history = self.db.get_user_locations(user_id, days=30)
        current_location = self._get_location_from_ip(current_ip)
        
        if not location_history:
            return 60.0  # No location history - moderate risk
        
        # Check if location is familiar
        for location in location_history:
            distance = self._calculate_distance(current_location, location)
            if distance < 50:  # Within 50km
                return 90.0  # Familiar location - low risk
        
        # Check for impossible travel
        latest_location = max(location_history, key=lambda x: x['timestamp'])
        time_diff = (context['timestamp'] - latest_location['timestamp']).total_seconds()
        distance = self._calculate_distance(current_location, latest_location)
        
        # Calculate maximum possible travel speed (km/h)
        if time_diff > 0:
            speed = (distance / 1000) / (time_diff / 3600)  # km/h
            if speed > 1000:  # Impossible travel speed
                return 20.0
            elif speed > 500:  # Very fast travel (likely plane)
                return 40.0
        
        # New location but reasonable travel
        return 55.0
    
    def _analyze_behavioral_pattern(self, context: Dict[str, Any]) -> float:
        """Analyze user behavioral patterns"""
        user_id = context['user_id']
        
        # Get user's behavioral history
        behavior_history = self.db.get_user_behavior_patterns(user_id)
        
        if not behavior_history:
            return 70.0  # No history - moderate score
        
        current_behavior = self._extract_behavior_features(context)
        
        # Compare with historical patterns
        similarity_score = self._calculate_behavior_similarity(
            current_behavior, behavior_history
        )
        
        # Convert similarity to risk score (higher similarity = lower risk)
        return min(100, 30 + (similarity_score * 70))
    
    def _analyze_account_history(self, context: Dict[str, Any]) -> float:
        """Analyze account age and history"""
        user_id = context['user_id']
        user_info = self.db.get_user(user_id)
        
        if not user_info:
            return 30.0  # No user info - high risk
        
        # Account age factor
        try:
            if isinstance(user_info['created_at'], str):
                created_at = datetime.fromisoformat(user_info['created_at'].replace('Z', '+00:00'))
            else:
                created_at = user_info['created_at']
            account_age = (datetime.utcnow() - created_at).days
        except:
            account_age = 1  # Default to 1 day if parsing fails
        age_score = min(50, account_age * 2)  # Max 50 points for age
        
        # Previous incidents
        incidents = self.db.get_user_incidents(user_id)
        incident_penalty = len(incidents) * 10
        
        # Verification status
        verification_bonus = 20 if user_info.get('verified') else 0
        
        # Activity level
        activity_score = min(30, self.db.get_user_activity_score(user_id))
        
        total_score = age_score + verification_bonus + activity_score - incident_penalty
        return max(0, min(100, total_score))
    
    def _analyze_time_pattern(self, context: Dict[str, Any]) -> float:
        """Analyze timing patterns"""
        current_time = context['timestamp']
        user_id = context['user_id']
        
        # Get user's typical activity hours
        activity_patterns = self.db.get_user_time_patterns(user_id)
        
        if not activity_patterns:
            return 70.0  # No pattern data
        
        current_hour = current_time.hour
        
        # Check if current time matches user's typical patterns
        typical_hours = activity_patterns.get('typical_hours', [])
        
        if current_hour in typical_hours:
            return 85.0  # Normal time for user
        
        # Check for unusual hours (late night/early morning)
        if current_hour < 6 or current_hour > 23:
            return 45.0  # Unusual hours - higher risk
        
        return 65.0  # Outside normal pattern but reasonable hours
    
    def _calculate_trust_score(self, risk_factors: Dict[str, float]) -> float:
        """Calculate weighted trust score from risk factors"""
        total_score = 0.0
        total_weight = 0.0
        
        for factor, score in risk_factors.items():
            weight = self.scoring_weights.get(factor, 0.1)
            total_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 50.0  # Default neutral score
        
        return total_score / total_weight
    
    def _determine_risk_level(self, trust_score: float) -> str:
        """Determine risk level based on trust score"""
        if trust_score >= self.risk_thresholds['low']:
            return 'low'
        elif trust_score >= self.risk_thresholds['medium']:
            return 'medium'
        else:
            return 'high'
    
    def _make_decision(self, trust_score: float, risk_level: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision based on trust score and risk level"""
        decision = {
            'action': 'allow',
            'requires_mfa': False,
            'requires_verification': False,
            'recommended_actions': []
        }
        
        if risk_level == 'high':
            decision['action'] = 'block'
            decision['recommended_actions'] = [
                'Contact customer support',
                'Verify identity through alternative method',
                'Review account security settings'
            ]
        elif risk_level == 'medium':
            if context['action'] == 'login':
                decision['requires_mfa'] = True
                decision['action'] = 'challenge'
            elif context['action'] == 'transaction':
                decision['requires_verification'] = True
                decision['action'] = 'verify'
            
            decision['recommended_actions'] = [
                'Complete additional verification',
                'Review transaction details'
            ]
        
        return decision
    
    def _generate_explanation(self, risk_factors: Dict[str, float], trust_score: float) -> str:
        """Generate human-readable explanation for the trust score"""
        explanations = []
        
        # Find the most significant risk factors
        sorted_factors = sorted(risk_factors.items(), key=lambda x: x[1])
        
        for factor, score in sorted_factors[:3]:  # Top 3 factors
            if score < 50:
                explanations.append(self._get_factor_explanation(factor, score))
        
        if not explanations:
            return f"Trust score: {trust_score:.1f}/100. All security checks passed normally."
        
        return f"Trust score: {trust_score:.1f}/100. " + " ".join(explanations)
    
    def _get_factor_explanation(self, factor: str, score: float) -> str:
        """Get explanation for a specific risk factor"""
        explanations = {
            'device_consistency': "Unrecognized device detected.",
            'transaction_velocity': "Unusual transaction frequency or amounts.",
            'geolocation_risk': "Login from new or distant location.",
            'behavioral_pattern': "Activity doesn't match typical user behavior.",
            'account_history': "Account has limited history or previous incidents.",
            'time_pattern': "Activity at unusual time for this user."
        }
        return explanations.get(factor, f"Elevated risk in {factor}.")
    
    # Helper methods
    def _generate_device_fingerprint(self, context: Dict[str, Any]) -> str:
        """Generate device fingerprint from context"""
        user_agent = context.get('user_agent', '')
        ip_address = context.get('ip_address', '')
        
        # Simple fingerprint based on available data
        fingerprint_data = f"{user_agent}:{ip_address}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    def _calculate_device_similarity(self, fp1: str, fp2: str) -> float:
        """Calculate similarity between device fingerprints"""
        # Simple similarity based on string comparison
        # In production, this would be more sophisticated
        if fp1 == fp2:
            return 1.0
        
        # Basic similarity check
        common_chars = sum(1 for a, b in zip(fp1, fp2) if a == b)
        return common_chars / max(len(fp1), len(fp2))
    
    def _get_location_from_ip(self, ip_address: str) -> Dict[str, float]:
        """Get approximate location from IP address"""
        # Simplified geolocation - in production use GeoIP2 or similar
        # For demo, return mock coordinates
        return {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'city': 'New York',
            'country': 'US'
        }
    
    def _calculate_distance(self, loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
        """Calculate distance between two locations in km"""
        # Simplified distance calculation
        lat_diff = abs(loc1['latitude'] - loc2['latitude'])
        lon_diff = abs(loc1['longitude'] - loc2['longitude'])
        
        # Rough approximation: 1 degree ≈ 111 km
        return ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111
    
    def _extract_behavior_features(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract behavioral features from context"""
        return {
            'action_type': context['action'],
            'hour_of_day': context['timestamp'].hour,
            'day_of_week': context['timestamp'].weekday(),
            'amount': context.get('amount', 0),
            'merchant': context.get('merchant', ''),
            'transaction_type': context.get('transaction_type', '')
        }
    
    def _calculate_behavior_similarity(self, current: Dict[str, Any], history: List[Dict[str, Any]]) -> float:
        """Calculate behavioral similarity score"""
        if not history:
            return 0.5
        
        # Simple similarity calculation
        # In production, this would use ML models
        similarities = []
        
        for past_behavior in history[-10:]:  # Last 10 behaviors
            similarity = 0.0
            
            if current['action_type'] == past_behavior['action_type']:
                similarity += 0.3
            
            hour_diff = abs(current['hour_of_day'] - past_behavior['hour_of_day'])
            if hour_diff <= 2:
                similarity += 0.2
            
            if current['day_of_week'] == past_behavior['day_of_week']:
                similarity += 0.1
            
            similarities.append(similarity)
        
        return max(similarities) if similarities else 0.5
    
    def get_user_trust_score(self, user_id: int) -> float:
        """Get current trust score for a user"""
        recent_scores = self.db.get_recent_trust_scores(user_id, limit=5)
        if not recent_scores:
            return 70.0  # Default score for new users
        
        # Return weighted average of recent scores
        weights = [0.4, 0.3, 0.2, 0.1]  # More weight on recent scores
        weighted_sum = sum(score * weight for score, weight in zip(recent_scores, weights))
        return weighted_sum / sum(weights[:len(recent_scores)])
    
    def get_score_factors(self, user_id: int) -> Dict[str, Any]:
        """Get detailed score factors for a user"""
        return {
            'device_trust': self.db.get_user_device_trust(user_id),
            'location_trust': self.db.get_user_location_trust(user_id),
            'behavior_trust': self.db.get_user_behavior_trust(user_id),
            'account_age_days': self.db.get_user_account_age(user_id),
            'verification_status': self.db.get_user_verification_status(user_id)
        }
    
    def _store_trust_result(self, user_id: int, result: Dict[str, Any]) -> None:
        """Store trust analysis result"""
        self.db.store_trust_score(user_id, result)

        # Store device fingerprint if available
        if 'device_fingerprint' in result.get('context', {}):
            self.db.store_device_fingerprint(user_id, result['context']['device_fingerprint'])
