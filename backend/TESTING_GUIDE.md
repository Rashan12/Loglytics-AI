# Loglytics AI - Comprehensive Testing Guide

## Overview

This guide provides comprehensive instructions for testing the Loglytics AI backend application. The testing suite covers all aspects of the application including API endpoints, database operations, WebSocket connections, and code coverage.

## Test Suite Components

### 1. End-to-End API Tests (`test_end_to_end.py`)
- **Purpose**: Tests all API endpoints and business logic
- **Coverage**: Authentication, Projects, Log Processing, AI Analysis, RAG Search, Analytics, Security, Error Handling, Performance
- **Duration**: ~5-10 minutes
- **Dependencies**: Backend server running

### 2. Database Operations Tests (`test_database_operations.py`)
- **Purpose**: Tests database integrity, performance, and operations
- **Coverage**: Connection, CRUD operations, bulk operations, query performance, caching
- **Duration**: ~2-3 minutes
- **Dependencies**: Database connection

### 3. WebSocket Connection Tests (`test_websocket_connections.py`)
- **Purpose**: Tests real-time features and WebSocket functionality
- **Coverage**: Notifications, Live Logs, Chat, Authentication, Performance
- **Duration**: ~2-3 minutes
- **Dependencies**: WebSocket server running

## Prerequisites

### System Requirements
- Python 3.8+
- PostgreSQL database
- Redis server
- Backend server running on localhost:8000

### Dependencies
```bash
pip install -r requirements-test.txt
```

### Environment Setup
1. Start PostgreSQL database
2. Start Redis server
3. Start the backend server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

## Running Tests

### Option 1: Run All Tests (Recommended)
```bash
python run_all_tests.py
```

### Option 2: Run Individual Test Suites
```bash
# End-to-End API Tests
pytest tests/test_end_to_end.py -v -s

# Database Tests
pytest tests/test_database_operations.py -v -s

# WebSocket Tests
pytest tests/test_websocket_connections.py -v -s
```

### Option 3: Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -v
```

### Option 4: Windows Batch Script
```cmd
run_tests.bat
```

## Test Configuration

### Environment Variables
Create a `.env.test` file with test-specific configuration:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/loglytics_test
REDIS_URL=redis://localhost:6379/1
SECRET_KEY=test-secret-key
DEBUG=True
```

### Test Data
- Test users are created with email `test_e2e@example.com`
- Test projects are named "E2E Test Project"
- Test log files contain sample log entries
- All test data is cleaned up after tests complete

## Test Results

### Generated Reports
1. **TEST_RESULTS.md** - End-to-End API test results
2. **DATABASE_TEST_RESULTS.md** - Database operation test results
3. **WEBSOCKET_TEST_RESULTS.md** - WebSocket connection test results
4. **COMPREHENSIVE_TEST_REPORT.md** - Combined test report
5. **htmlcov/index.html** - Code coverage report

### Understanding Results
- ✅ **PASS**: Test completed successfully
- ❌ **FAIL**: Test failed with error
- ⚠️ **WARN**: Test completed but with warnings

### Success Criteria
- **End-to-End Tests**: >90% pass rate
- **Database Tests**: 100% pass rate
- **WebSocket Tests**: >80% pass rate
- **Code Coverage**: >80% coverage

## Troubleshooting

### Common Issues

#### 1. Backend Not Running
```
❌ Backend is not running!
```
**Solution**: Start the backend server
```bash
python -m uvicorn app.main:app --reload
```

#### 2. Database Connection Failed
```
❌ Database connection failed
```
**Solution**: 
- Check PostgreSQL is running
- Verify DATABASE_URL in configuration
- Ensure database exists

#### 3. Redis Connection Failed
```
❌ Redis connection failed
```
**Solution**:
- Check Redis is running
- Verify REDIS_URL in configuration
- Ensure Redis server is accessible

#### 4. WebSocket Connection Failed
```
❌ WebSocket connection failed
```
**Solution**:
- Check WebSocket server is running
- Verify WebSocket endpoints are configured
- Check authentication tokens

#### 5. Import Errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution**:
- Ensure you're running from the backend directory
- Check Python path includes the project root
- Install all dependencies

### Debug Mode
Run tests with debug output:
```bash
pytest tests/test_end_to_end.py -v -s --tb=long --log-cli-level=DEBUG
```

### Verbose Output
Get detailed test output:
```bash
pytest tests/ -v -s --tb=short --capture=no
```

## Test Categories

### Authentication Tests
- User registration
- User login
- JWT token validation
- API key creation
- Password reset (if implemented)

### Project Management Tests
- Project creation
- Project listing
- Project details
- Project updates
- Project deletion

### Log Processing Tests
- Log file upload
- Log parsing
- Log entry retrieval
- Log file listing
- Log analysis

### AI Analysis Tests
- AI-powered log analysis
- Chat assistant
- Chat session creation
- RAG search
- RAG indexing

### WebSocket Tests
- Notifications WebSocket
- Live logs WebSocket
- Chat WebSocket
- Message handling
- Authentication
- Reconnection

### Analytics Tests
- Dashboard analytics
- Project analytics
- Real-time metrics
- Data aggregation

### Security Tests
- Security headers
- Rate limiting
- Input validation
- Authentication bypass
- Authorization checks

### Performance Tests
- Response times
- Concurrent requests
- Database performance
- Memory usage
- CPU usage

### Error Handling Tests
- Invalid endpoints
- Unauthorized access
- Validation errors
- Network errors
- Server errors

## Continuous Integration

### GitHub Actions Example
```yaml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run tests
      run: python run_all_tests.py
```

## Best Practices

### Test Data Management
- Use unique test data to avoid conflicts
- Clean up test data after each test
- Use test-specific database/Redis instances
- Avoid hardcoded values

### Test Isolation
- Each test should be independent
- Use fixtures for common setup
- Mock external dependencies
- Reset state between tests

### Performance Testing
- Monitor response times
- Test with realistic data volumes
- Use appropriate timeouts
- Profile memory usage

### Error Testing
- Test error conditions
- Verify error messages
- Test edge cases
- Validate error responses

## Maintenance

### Regular Tasks
- Update test data regularly
- Review test coverage
- Update test documentation
- Monitor test performance

### Test Updates
- Update tests when APIs change
- Add tests for new features
- Remove obsolete tests
- Refactor test code

## Support

For issues with the testing suite:
1. Check this guide first
2. Review test logs
3. Check system requirements
4. Verify configuration
5. Contact the development team

---

*Last updated: 2024-10-16*
