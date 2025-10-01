# E2E Tests for Self-driving Data Collection API

## Overview

This directory contains end-to-end (E2E) tests for the measurement data collection API using Playwright and a JSON-driven test framework.

## Architecture

### JSON-Driven Testing
The testing framework uses JSON configuration files (`testplan.json`) to define test scenarios, making tests:
- **Declarative**: Tests are defined as data, not code
- **Maintainable**: Non-developers can understand and modify tests
- **Reusable**: Common patterns can be extracted and reused
- **Extensible**: New test types can be added without changing the runner

### Components

1. **`json-runner.spec.ts`**: The Playwright test runner that interprets JSON test plans
2. **`testplan.json`**: Test configuration files defining test scenarios
3. **`run-tests.sh`**: Shell script to orchestrate test execution

## Test Plan Structure

```json
{
  "title": "Test Suite Name",
  "baseUrl": "http://localhost:8000",
  "headers": {
    "content-type": "application/json"
  },
  "preprocess": [
    // Setup steps before tests
  ],
  "tests": [
    {
      "name": "Test Case Name",
      "assertions": [
        {
          "description": "What this test does",
          "api": "/endpoint",
          "method": "POST",
          "input": { /* request body */ },
          "expected": {
            "status": 200,
            "result": { /* expected response */ }
          },
          "postprocess": [
            // Steps after assertion (e.g., capture variables)
          ]
        }
      ]
    }
  ]
}
```

## Features

### 1. Variable Capture and Reuse
Capture values from API responses and use them in subsequent tests:
```json
{
  "postprocess": [{
    "type": "capture",
    "from": "id",
    "to": "global.measurementId"
  }]
},
{
  "api": "/measurements/${global.measurementId}"
}
```

### 2. Parallel Testing
Test API performance with concurrent requests:
```json
{
  "parallel": 50,
  "expected": { "status": 200 }
}
```

### 3. Preprocessing
Set up test data before running tests:
```json
"preprocess": [
  { "type": "db", "script": "setup.sql" },
  { "type": "api", "api": "/reset", "method": "POST" }
]
```

### 4. Deep Object Validation
Validate nested response structures with partial matching:
```json
"expected": {
  "result": {
    "user": {
      "name": "John",
      "permissions": ["read", "write"]
    }
  }
}
```

## Available Test Plans

### 1. `testplan.json` (Default)
Basic sample test configuration for demonstration.

### 2. `measurement-api.testplan.json`
Comprehensive test suite for the measurement API including:
- CRUD operations
- Bulk operations
- Error handling
- Performance testing
- Filtering and pagination

### 3. `dataset-api.testplan.json`
Dataset API coverage exercising composed dataset creation, retrieval of dataset details and items, and validation failures for external datasets without required metadata.

## Running Tests

### Quick Start
```bash
# Run with default test plan
./tests/e2e/run-tests.sh

# Run specific test plan
./tests/e2e/run-tests.sh --test-plan measurement-api.testplan.json

# Run in headed mode (visible browser)
./tests/e2e/run-tests.sh --headed

# Run with test environment
./tests/e2e/run-tests.sh --env test
```

### Manual Execution
```bash
# Install dependencies
npm install

# Install Playwright browsers
npx playwright install chromium

# Start API server
docker-compose up -d

# Run tests
TEST_PLAN_PATH=./tests/e2e/measurement-api.testplan.json \
BASE_URL=http://localhost:8000 \
npx playwright test tests/e2e/json-runner.spec.ts

# View test report
npx playwright show-report
```

### Environment Variables
- `TEST_PLAN_PATH`: Path to the test plan JSON file
- `BASE_URL`: Override the base URL for API calls

## Writing New Tests

### 1. Create a Test Plan
Create a new JSON file following the structure:
```json
{
  "title": "Your API Tests",
  "baseUrl": "http://localhost:8000",
  "tests": [
    // Your test cases
  ]
}
```

### 2. Define Test Cases
Each test case should have:
- Clear, descriptive name
- Meaningful assertion descriptions
- Proper expected values
- Necessary postprocessing steps

### 3. Best Practices
- **Test Independence**: Each test should be runnable independently
- **Clear Naming**: Use descriptive names for tests and assertions
- **Error Cases**: Include negative test cases
- **Performance**: Add parallel tests for load testing
- **Cleanup**: Ensure tests clean up after themselves

## Extending the Framework

### Adding New Preprocessing Types
Edit `json-runner.spec.ts` and add to the `executePreprocess` function:
```typescript
case 'custom':
  // Your custom preprocessing logic
  break;
```

### Adding New Postprocessing Types
Edit `json-runner.spec.ts` and add to the `executePostprocess` function:
```typescript
case 'validate-custom':
  // Your custom validation logic
  break;
```

### Adding New Assertion Types
Modify the assertion execution logic in the main test loop to handle new assertion patterns.

## Troubleshooting

### API Not Starting
```bash
# Check Docker logs
docker-compose logs api

# Verify containers are running
docker ps

# Test API health
curl http://localhost:8000/health
```

### Tests Failing
```bash
# Run with debug output
npx playwright test --debug

# View detailed test report
npx playwright show-report

# Check API logs during test
docker-compose logs -f api
```

### Playwright Issues
```bash
# Reinstall browsers
npx playwright install --force chromium

# Clear Playwright cache
rm -rf ~/.cache/ms-playwright
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run E2E Tests
  run: |
    cd api
    npm ci
    npx playwright install chromium
    docker-compose up -d
    ./tests/e2e/run-tests.sh --test-plan measurement-api.testplan.json
```

### Jenkins Example
```groovy
stage('E2E Tests') {
  steps {
    sh 'cd api && ./tests/e2e/run-tests.sh --env test'
  }
  post {
    always {
      publishHTML([
        reportDir: 'api/playwright-report',
        reportFiles: 'index.html',
        reportName: 'E2E Test Report'
      ])
    }
  }
}
```

## Performance Metrics

The framework captures:
- Response times
- Success/failure rates
- Parallel request handling
- Error patterns

Results are available in:
- Console output
- HTML report (`playwright-report/`)
- JSON report (`test-results/results.json`)

## Contributing

When adding new features:
1. Update this README
2. Add example test cases
3. Ensure backward compatibility
4. Test with existing test plans
