@echo off
echo 🐳 TrustAI Docker Test Script
echo ============================

echo.
echo 🔍 Checking Docker installation...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not in PATH
    echo.
    echo 📥 Please install Docker Desktop from:
    echo    https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is installed
docker --version

echo.
echo 🔍 Checking if Docker is running...

REM Check if Docker daemon is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running
    echo.
    echo 🚀 Please start Docker Desktop and try again
    echo    - Open Docker Desktop application
    echo    - Wait for it to fully start
    echo    - Look for the green "running" status
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is running

echo.
echo 🔍 Checking Docker Compose...

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not available
    echo.
    echo 📥 Docker Compose should be included with Docker Desktop
    echo    Please reinstall Docker Desktop if this error persists
    echo.
    pause
    exit /b 1
)

echo ✅ Docker Compose is available
docker-compose --version

echo.
echo 🔍 Testing Docker functionality...

REM Test basic Docker functionality
docker run --rm hello-world >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker test failed
    echo.
    echo 🔧 Troubleshooting steps:
    echo    1. Restart Docker Desktop
    echo    2. Check Windows features (Hyper-V, WSL2)
    echo    3. Run Docker Desktop as administrator
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is working correctly

echo.
echo 🎉 All Docker checks passed!
echo.
echo 🚀 You can now build and run TrustAI with Docker:
echo.
echo    1. Build images:     docker-build.bat
echo    2. Start services:   docker-start.bat
echo    3. Or use compose:   docker-compose up -d
echo.
echo 🌐 After starting, access:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:5000
echo.
pause
