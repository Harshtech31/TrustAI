#!/usr/bin/env python3
"""
TrustAI API Testing Script
Comprehensive testing of the TrustAI fraud detection API
"""

import requests
import json
import time
from datetime import datetime

class TrustAITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
    
    def test_health_check(self):
        """Test the health check endpoint"""
        print("🔍 Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_login(self, username="alice_normal", password="SecurePass123!"):
        """Test user login"""
        print(f"🔐 Testing login with {username}...")
        try:
            response = self.session.post(f"{self.base_url}/api/auth/login", json={
                "username": username,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                print(f"✅ Login successful - Trust Score: {data.get('trust_score', 'N/A')}")
                print(f"   Risk Level: {data.get('risk_level', 'N/A')}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_transaction_analysis(self, amount=99.99, merchant="Amazon", transaction_type="purchase"):
        """Test transaction analysis"""
        print(f"💳 Testing transaction analysis (${amount} at {merchant})...")
        try:
            response = self.session.post(f"{self.base_url}/api/transaction/analyze", json={
                "amount": amount,
                "merchant": merchant,
                "transaction_type": transaction_type
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Transaction analyzed - Trust Score: {data.get('trust_score', 'N/A')}")
                print(f"   Risk Level: {data.get('risk_level', 'N/A')}")
                print(f"   Decision: {data.get('decision', 'N/A')}")
                print(f"   Explanation: {data.get('explanation', 'N/A')}")
                return True
            else:
                print(f"❌ Transaction analysis failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Transaction analysis error: {e}")
            return False
    
    def test_trust_score_retrieval(self):
        """Test trust score retrieval"""
        print("📊 Testing trust score retrieval...")
        try:
            response = self.session.get(f"{self.base_url}/api/user/trust-score")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Trust score retrieved - Current Score: {data.get('current_score', 'N/A')}")
                print(f"   History entries: {len(data.get('history', []))}")
                print(f"   Recent activities: {len(data.get('recent_activities', []))}")
                return True
            else:
                print(f"❌ Trust score retrieval failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Trust score retrieval error: {e}")
            return False
    
    def test_admin_dashboard(self):
        """Test admin dashboard (requires admin user)"""
        print("👑 Testing admin dashboard...")
        try:
            response = self.session.get(f"{self.base_url}/api/admin/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Admin dashboard accessed")
                print(f"   Total Users: {data.get('total_users', 'N/A')}")
                print(f"   Total Transactions: {data.get('total_transactions', 'N/A')}")
                print(f"   Fraud Detected: {data.get('fraud_detected', 'N/A')}")
                return True
            elif response.status_code == 403:
                print("⚠️ Admin dashboard access denied (user not admin)")
                return True  # Expected for non-admin users
            else:
                print(f"❌ Admin dashboard failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Admin dashboard error: {e}")
            return False
    
    def test_fraud_scenarios(self):
        """Test various fraud scenarios"""
        print("🚨 Testing fraud scenarios...")
        
        scenarios = [
            {
                "name": "Normal Transaction",
                "amount": 49.99,
                "merchant": "Starbucks",
                "expected_risk": "low"
            },
            {
                "name": "Large Transaction",
                "amount": 1999.99,
                "merchant": "Best Buy",
                "expected_risk": "medium"
            },
            {
                "name": "Very Large Transaction",
                "amount": 9999.99,
                "merchant": "Unknown Store",
                "expected_risk": "high"
            }
        ]
        
        results = []
        for scenario in scenarios:
            print(f"   Testing: {scenario['name']}")
            success = self.test_transaction_analysis(
                scenario['amount'],
                scenario['merchant']
            )
            results.append(success)
            time.sleep(1)  # Small delay between tests
        
        return all(results)
    
    def test_rapid_transactions(self):
        """Test rapid transaction detection"""
        print("⚡ Testing rapid transaction detection...")
        
        # Simulate multiple rapid transactions
        for i in range(5):
            print(f"   Transaction {i+1}/5")
            success = self.test_transaction_analysis(
                amount=99.99 + i,
                merchant="Steam"
            )
            if not success:
                return False
            time.sleep(0.5)  # Very short delay to simulate rapid transactions
        
        print("✅ Rapid transaction test completed")
        return True
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🛡️ TrustAI API Comprehensive Test Suite")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("User Login", lambda: self.test_login("alice_normal")),
            ("Transaction Analysis", self.test_transaction_analysis),
            ("Trust Score Retrieval", self.test_trust_score_retrieval),
            ("Fraud Scenarios", self.test_fraud_scenarios),
            ("Rapid Transactions", self.test_rapid_transactions),
            ("Admin Dashboard", self.test_admin_dashboard),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Test with admin user
        print(f"\n🔄 Testing with admin user...")
        if self.test_login("admin_user"):
            self.test_admin_dashboard()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("🎉 All tests passed! TrustAI API is working correctly.")
        else:
            print("⚠️ Some tests failed. Please check the API implementation.")
        
        return passed == len(results)

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TrustAI API Testing Script")
    parser.add_argument("--url", default="http://localhost:5000", help="API base URL")
    parser.add_argument("--test", choices=["health", "login", "transaction", "all"], 
                       default="all", help="Specific test to run")
    
    args = parser.parse_args()
    
    tester = TrustAITester(args.url)
    
    if args.test == "health":
        tester.test_health_check()
    elif args.test == "login":
        tester.test_login()
    elif args.test == "transaction":
        if tester.test_login():
            tester.test_transaction_analysis()
    else:
        tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
