@echo off
echo 🛡️ Starting TrustAI System
echo ==========================

echo.
echo 🚀 Starting backend server...
start "TrustAI Backend" cmd /k "python app.py"

echo.
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo 🎨 Starting frontend server...
cd frontend
start "TrustAI Frontend" cmd /k "npm start"
cd ..

echo.
echo ✅ TrustAI is starting up!
echo.
echo 🌐 Access points:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:5000
echo.
echo 👥 Demo accounts:
echo    alice_normal / SecurePass123!
echo    bob_suspicious / SecurePass123!
echo    charlie_fraudster / SecurePass123!
echo    admin_user / AdminPass123!
echo.
echo Press any key to close this window...
pause > nul
