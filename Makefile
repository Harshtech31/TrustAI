# TrustAI Docker Makefile

.PHONY: help build start stop restart logs clean test dev prod

# Default target
help:
	@echo "🛡️ TrustAI Docker Commands"
	@echo "=========================="
	@echo ""
	@echo "Development:"
	@echo "  make dev      - Start development environment"
	@echo "  make build    - Build all Docker images"
	@echo "  make start    - Start all services"
	@echo "  make stop     - Stop all services"
	@echo "  make restart  - Restart all services"
	@echo "  make logs     - View logs"
	@echo ""
	@echo "Production:"
	@echo "  make prod     - Start production environment"
	@echo "  make prod-build - Build production images"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean    - Clean up containers and images"
	@echo "  make test     - Test Docker setup"
	@echo "  make status   - Show service status"
	@echo ""

# Development environment
dev:
	@echo "🚀 Starting TrustAI development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Development environment started!"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:5000"

# Build all images
build:
	@echo "📦 Building TrustAI Docker images..."
	docker-compose -f docker-compose.dev.yml build
	@echo "✅ Images built successfully!"

# Start services
start:
	@echo "🚀 Starting TrustAI services..."
	docker-compose up -d
	@echo "✅ Services started!"

# Stop services
stop:
	@echo "🛑 Stopping TrustAI services..."
	docker-compose down
	@echo "✅ Services stopped!"

# Restart services
restart: stop start

# View logs
logs:
	docker-compose logs -f

# Production environment
prod:
	@echo "🚀 Starting TrustAI production environment..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Production environment started!"
	@echo "   Application: http://localhost"

# Build production images
prod-build:
	@echo "📦 Building TrustAI production images..."
	docker-compose -f docker-compose.prod.yml build
	@echo "✅ Production images built!"

# Test Docker setup
test:
	@echo "🔍 Testing Docker setup..."
	docker --version
	docker-compose --version
	docker run --rm hello-world
	@echo "✅ Docker setup is working!"

# Show service status
status:
	@echo "📊 TrustAI Service Status:"
	docker-compose ps

# Clean up
clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup completed!"

# Database operations
db-init:
	@echo "📊 Initializing database..."
	docker-compose exec backend python init_db.py
	@echo "✅ Database initialized!"

db-backup:
	@echo "💾 Backing up database..."
	docker-compose exec backend python -c "import shutil; shutil.copy('trustai.db', 'trustai_backup.db')"
	@echo "✅ Database backed up to trustai_backup.db"

# Development helpers
shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh

# Monitoring
monitor:
	@echo "📊 Starting monitoring stack..."
	docker-compose -f docker-compose.prod.yml --profile monitoring up -d
	@echo "✅ Monitoring started!"
	@echo "   Prometheus: http://localhost:9090"
	@echo "   Grafana:    http://localhost:3001"
