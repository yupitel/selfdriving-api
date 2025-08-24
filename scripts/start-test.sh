#!/bin/bash
# Test environment startup script

echo "Starting test environment..."

# Clean up any existing test containers
docker-compose -f docker-compose.test.yml down

# Start test services
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 15

# Check API health
echo "Checking test API health..."
curl -f http://localhost:8001/api/v1/health || {
    echo "Test API health check failed"
    docker-compose -f docker-compose.test.yml logs api-test
    exit 1
}

echo "Test environment is ready!"
echo "- Test API: http://localhost:8001"
echo "- Test API Docs: http://localhost:8001/docs"
echo "- Test PostgreSQL: localhost:5433"

echo ""
echo "Running API tests..."
python test_api.py http://localhost:8001/api/v1