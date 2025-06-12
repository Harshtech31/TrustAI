@echo off
echo 🛡️ TrustAI Setup Script
echo ========================

echo.
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo 📊 Initializing database...
python init_db.py
if %errorlevel% neq 0 (
    echo ❌ Failed to initialize database
    pause
    exit /b 1
)

echo.
echo 📦 Installing frontend dependencies...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo ✅ Setup completed successfully!
echo.
echo 🚀 To start TrustAI:
echo    python run.py
echo.
echo 🌐 Access points:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:5000
echo.
echo 👥 Demo accounts:
echo    alice_normal / SecurePass123!     (Normal user)
echo    bob_suspicious / SecurePass123!   (Suspicious activity)
echo    charlie_fraudster / SecurePass123! (Fraudulent patterns)
echo    admin_user / AdminPass123!        (Administrator)
echo.
pause
