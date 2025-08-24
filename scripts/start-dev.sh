#!/bin/bash
# Development environment startup script

echo "Starting development environment..."

# Clean up any existing containers
docker-compose down

# Start services
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check API health
echo "Checking API health..."
curl -f http://localhost:8000/api/v1/health || {
    echo "API health check failed"
    docker-compose logs api
    exit 1
}

echo "Development environment is ready!"
echo "- API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- PostgreSQL: localhost:5432"