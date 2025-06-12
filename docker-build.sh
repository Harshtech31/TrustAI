#!/bin/bash

# TrustAI Docker Build Script

echo "🛡️ TrustAI Docker Build Script"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "📦 Building TrustAI Docker images..."

# Build backend image
echo "🔧 Building backend image..."
docker build -f Dockerfile.backend -t trustai-backend:latest .

if [ $? -eq 0 ]; then
    echo "✅ Backend image built successfully"
else
    echo "❌ Failed to build backend image"
    exit 1
fi

# Build frontend image
echo "🎨 Building frontend image..."
cd frontend
docker build -f Dockerfile -t trustai-frontend:latest .

if [ $? -eq 0 ]; then
    echo "✅ Frontend image built successfully"
else
    echo "❌ Failed to build frontend image"
    exit 1
fi

cd ..

echo "🎉 All Docker images built successfully!"
echo ""
echo "🚀 To start TrustAI with Docker:"
echo "   docker-compose up -d"
echo ""
echo "🌐 Access points:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo "   Nginx:    http://localhost:80 (production profile)"
