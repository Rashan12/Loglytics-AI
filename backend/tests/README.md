# Analytics Testing Suite

This directory contains comprehensive tests for the Loglytics AI analytics system.

## Test Structure

### `test_analytics.py`
Main test file containing all analytics endpoint tests:

- **Overview Analytics**: Tests basic log statistics and distribution
- **Error Analytics**: Tests error analysis and MTBF calculations
- **Anomaly Detection**: Tests statistical anomaly detection with configurable thresholds
- **Performance Metrics**: Tests response time analysis and throughput metrics
- **Pattern Analysis**: Tests NLP-based pattern recognition and clustering
- **AI Insights**: Tests AI-generated insights and health scoring
- **Caching**: Tests analytics caching and invalidation
- **Authentication**: Tests endpoint security and authorization

### `conftest.py`
Pytest configuration and fixtures:

- **Database Setup**: In-memory SQLite database for testing
- **Test Data**: Fixtures for users, projects, log files, and log entries
- **Authentication**: Mock authentication for testing
- **Client Setup**: HTTP client configuration

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install -r requirements-test.txt
```

### Run All Tests
```bash
# From backend directory
python run_tests.py

# Or directly with pytest
pytest tests/test_analytics.py -v
```

### Run Specific Tests
```bash
# Test only overview analytics
pytest tests/test_analytics.py::test_overview_analytics -v

# Test only error analytics
pytest tests/test_analytics.py::test_error_analytics -v

# Test with specific markers
pytest -m "not slow" -v
```

## Test Coverage

### Analytics Endpoints Tested
- ✅ `GET /api/v1/analytics/overview/{project_id}`
- ✅ `GET /api/v1/analytics/errors/{project_id}`
- ✅ `GET /api/v1/analytics/anomalies/{project_id}`
- ✅ `GET /api/v1/analytics/performance/{project_id}`
- ✅ `GET /api/v1/analytics/patterns/{project_id}`
- ✅ `GET /api/v1/analytics/insights/{project_id}`
- ✅ `POST /api/v1/analytics/generate/{log_file_id}`

### Test Scenarios
- **Happy Path**: Normal operation with valid data
- **Edge Cases**: Empty data, invalid parameters
- **Error Handling**: Authentication failures, invalid project IDs
- **Performance**: Concurrent requests, caching behavior
- **Validation**: Parameter validation and type checking

## Test Data

### Sample Log Entries
Tests use realistic log data including:
- Various log levels (ERROR, WARN, INFO, CRITICAL)
- Different sources (database.py, auth.py, etc.)
- Timestamps spanning 24 hours
- Realistic error messages and patterns

### Test Projects
- Sample projects with different configurations
- Users with different subscription tiers
- Log files with various formats and sizes

## Configuration

### Database
- Uses in-memory SQLite for fast, isolated tests
- Automatic table creation and cleanup
- No external database dependencies

### Authentication
- Mock JWT authentication for testing
- Configurable user roles and permissions
- Security testing for unauthorized access

## Continuous Integration

### GitHub Actions (if configured)
```yaml
- name: Run Analytics Tests
  run: |
    cd backend
    pip install -r requirements-test.txt
    python run_tests.py
```

### Local Development
```bash
# Run tests before committing
python run_tests.py

# Run with coverage
pytest tests/test_analytics.py --cov=app.services.analytics
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Errors**: Check SQLAlchemy configuration
3. **Authentication Errors**: Verify mock auth setup
4. **Timeout Errors**: Increase test timeout for slow operations

### Debug Mode
```bash
# Run with detailed output
pytest tests/test_analytics.py -v -s --tb=long

# Run single test with debugging
pytest tests/test_analytics.py::test_overview_analytics -v -s --pdb
```

## Performance Benchmarks

### Expected Response Times
- Overview Analytics: < 100ms
- Error Analytics: < 200ms
- Anomaly Detection: < 500ms
- Performance Metrics: < 300ms
- Pattern Analysis: < 400ms
- AI Insights: < 1000ms

### Load Testing
Tests include concurrent request simulation to verify:
- Caching effectiveness
- Database connection pooling
- Memory usage under load
- Response time consistency

## Contributing

### Adding New Tests
1. Follow existing naming conventions
2. Use appropriate fixtures for test data
3. Include both positive and negative test cases
4. Add performance assertions where relevant
5. Update this README with new test descriptions

### Test Data Guidelines
- Use realistic, representative data
- Include edge cases and boundary conditions
- Ensure data covers all code paths
- Keep test data minimal but comprehensive
