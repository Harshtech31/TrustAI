@echo off
echo 🛡️ TrustAI Docker Build Script
echo ==============================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo.
echo 📦 Building TrustAI Docker images...

REM Build backend image
echo 🔧 Building backend image...
docker build -f Dockerfile.backend -t trustai-backend:latest .
if %errorlevel% neq 0 (
    echo ❌ Failed to build backend image
    pause
    exit /b 1
)
echo ✅ Backend image built successfully

REM Build frontend image
echo 🎨 Building frontend image...
cd frontend
docker build -f Dockerfile -t trustai-frontend:latest .
if %errorlevel% neq 0 (
    echo ❌ Failed to build frontend image
    pause
    exit /b 1
)
echo ✅ Frontend image built successfully
cd ..

echo.
echo 🎉 All Docker images built successfully!
echo.
echo 🚀 To start TrustAI with Docker:
echo    docker-compose up -d
echo.
echo 🌐 Access points:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:5000
echo    Nginx:    http://localhost:80 (production profile)
echo.
pause
