#!/usr/bin/env python3
"""
TrustAI Database Initialization Script
"""

import os
import sys
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database import Database
from src.demo_data import DemoDataGenerator
from src.utils import setup_logging

def main():
    """Initialize the TrustAI database with demo data"""
    
    # Setup logging
    setup_logging()
    
    print("🛡️ TrustAI Database Initialization")
    print("=" * 50)
    
    # Initialize database
    print("📊 Initializing database...")
    db = Database()
    
    # Create demo data generator
    demo_generator = DemoDataGenerator(db)
    
    # Create demo users
    print("👥 Creating demo users...")
    users = demo_generator.create_demo_users()
    print(f"✅ Created {len(users)} demo users")
    
    # Generate demo scenarios
    print("🎭 Generating demo scenarios...")
    demo_generator.generate_demo_scenarios()
    print("✅ Demo scenarios generated")
    
    # Generate some real-time data
    print("⚡ Generating real-time demo data...")
    demo_generator.generate_real_time_demo_data()
    print("✅ Real-time demo data generated")
    
    # Display summary
    print("\n📈 Database Summary:")
    print(f"   Total Users: {db.get_total_users()}")
    print(f"   Total Transactions: {db.get_total_transactions()}")
    print(f"   Fraud Incidents: {db.get_fraud_count()}")
    print(f"   Average Trust Score: {db.get_average_trust_score()}")
    
    print("\n🎯 Demo User Accounts:")
    print("   Username: alice_normal    | Password: SecurePass123! | Behavior: Normal user")
    print("   Username: bob_suspicious  | Password: SecurePass123! | Behavior: Suspicious activity")
    print("   Username: charlie_fraudster | Password: SecurePass123! | Behavior: Fraudulent patterns")
    print("   Username: diana_traveler  | Password: SecurePass123! | Behavior: Frequent traveler")
    print("   Username: admin_user      | Password: AdminPass123!  | Role: Administrator")
    
    print("\n🚀 Database initialization complete!")
    print("   You can now start the TrustAI application with: python app.py")
    print("   Access the API at: http://localhost:5000")
    print("   Frontend will be available at: http://localhost:3000")

if __name__ == "__main__":
    main()
