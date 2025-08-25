#!/bin/bash

# E2E Test Runner Script for Measurement API

set -e

echo "==================================="
echo "Measurement API E2E Test Runner"
echo "==================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Parse command line arguments
TEST_PLAN="testplan.json"
ENVIRONMENT="development"
HEADED=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --test-plan)
            TEST_PLAN="$2"
            shift 2
            ;;
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --headed)
            HEADED="--headed"
            shift
            ;;
        --help)
            echo "Usage: ./run-tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  --test-plan <file>  Specify test plan JSON file (default: testplan.json)"
            echo "  --env <env>         Environment: development, test, production (default: development)"
            echo "  --headed            Run tests in headed mode (visible browser)"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Navigate to API directory
cd /home/shunsuke/works/selfdriving/api

echo -e "${YELLOW}Setting up test environment...${NC}"

# Start Docker containers based on environment
if [ "$ENVIRONMENT" = "test" ]; then
    echo "Starting test environment containers..."
    docker-compose -f docker-compose.test.yml up -d
    API_URL="http://localhost:8001"
elif [ "$ENVIRONMENT" = "production" ]; then
    echo "Using production configuration..."
    docker-compose -f docker-compose.prod.yml up -d
    API_URL="http://localhost:8000"
else
    echo "Starting development environment containers..."
    docker-compose up -d
    API_URL="http://localhost:8000"
fi

# Wait for API to be ready
echo -e "${YELLOW}Waiting for API to be ready...${NC}"
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s "$API_URL/api/v1/health" > /dev/null 2>&1; then
        echo -e "${GREEN}API is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 2
    ATTEMPT=$((ATTEMPT + 1))
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo -e "${RED}API failed to start after 60 seconds${NC}"
    docker-compose logs api
    exit 1
fi

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing npm dependencies...${NC}"
    npm install
fi

# Install Playwright browsers if needed
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
    echo -e "${YELLOW}Installing Playwright browsers...${NC}"
    npx playwright install chromium
fi

# Run E2E tests
echo -e "${YELLOW}Running E2E tests...${NC}"
echo "Test plan: $TEST_PLAN"
echo "API URL: $API_URL"

export TEST_PLAN_PATH="./tests/e2e/$TEST_PLAN"
export BASE_URL="$API_URL"

npx playwright test tests/e2e/json-runner.spec.ts $HEADED

TEST_EXIT_CODE=$?

# Generate test report
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed. Check the test report for details.${NC}"
    echo "Opening test report..."
    npx playwright show-report
fi

# Cleanup (optional)
read -p "Do you want to stop the Docker containers? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping containers..."
    if [ "$ENVIRONMENT" = "test" ]; then
        docker-compose -f docker-compose.test.yml down
    elif [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.prod.yml down
    else
        docker-compose down
    fi
fi

exit $TEST_EXIT_CODE