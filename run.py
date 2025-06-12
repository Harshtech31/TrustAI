#!/usr/bin/env python3
"""
TrustAI Application Runner
Convenient script to run the TrustAI application
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def run_backend():
    """Run the Flask backend server"""
    print("🚀 Starting TrustAI Backend Server...")
    
    # Initialize database if it doesn't exist
    if not os.path.exists('trustai.db'):
        print("📊 Initializing database...")
        subprocess.run([sys.executable, 'init_db.py'], check=True)
    
    # Start Flask server
    env = os.environ.copy()
    env['FLASK_APP'] = 'app.py'
    env['FLASK_ENV'] = 'development'
    
    return subprocess.Popen([
        sys.executable, 'app.py'
    ], env=env)

def run_frontend():
    """Run the React frontend server"""
    print("🎨 Starting TrustAI Frontend Server...")
    
    frontend_dir = Path('frontend')
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return None
    
    # Check if node_modules exists
    if not (frontend_dir / 'node_modules').exists():
        print("📦 Installing frontend dependencies...")
        subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
    
    # Start React development server
    return subprocess.Popen([
        'npm', 'start'
    ], cwd=frontend_dir)

def main():
    """Main application runner"""
    print("🛡️ TrustAI - Real-Time Fraud Detection System")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'backend':
            backend_process = run_backend()
            try:
                backend_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping backend server...")
                backend_process.terminate()
                
        elif command == 'frontend':
            frontend_process = run_frontend()
            if frontend_process:
                try:
                    frontend_process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping frontend server...")
                    frontend_process.terminate()
                    
        elif command == 'init':
            print("📊 Initializing TrustAI database...")
            subprocess.run([sys.executable, 'init_db.py'], check=True)
            
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: backend, frontend, init")
            sys.exit(1)
    else:
        # Run both backend and frontend
        print("🚀 Starting both backend and frontend servers...")
        
        backend_process = run_backend()
        time.sleep(3)  # Give backend time to start
        
        frontend_process = run_frontend()
        
        if not frontend_process:
            print("❌ Failed to start frontend server")
            backend_process.terminate()
            sys.exit(1)
        
        print("\n✅ TrustAI is running!")
        print("   Backend API: http://localhost:5000")
        print("   Frontend UI: http://localhost:3000")
        print("\n   Press Ctrl+C to stop both servers")
        
        try:
            # Wait for either process to exit
            while True:
                if backend_process.poll() is not None:
                    print("❌ Backend server stopped")
                    break
                if frontend_process.poll() is not None:
                    print("❌ Frontend server stopped")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping TrustAI servers...")
        finally:
            # Clean shutdown
            if backend_process.poll() is None:
                backend_process.terminate()
                backend_process.wait(timeout=5)
            
            if frontend_process and frontend_process.poll() is None:
                frontend_process.terminate()
                frontend_process.wait(timeout=5)
            
            print("✅ TrustAI stopped successfully")

if __name__ == "__main__":
    main()
