@echo off
echo 🛡️ TrustAI Docker Startup Script
echo ================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo.
echo 🚀 Starting TrustAI with Docker Compose...

REM Start the services
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start TrustAI services
    pause
    exit /b 1
)

echo.
echo ✅ TrustAI is starting up!
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
echo 📊 To check status: docker-compose ps
echo 📋 To view logs:    docker-compose logs -f
echo 🛑 To stop:        docker-compose down
echo.
pause
