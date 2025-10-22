#!/bin/bash

echo "=========================================="
echo "Loglytics AI - Test Coverage Analysis"
echo "=========================================="
echo ""

# Check if backend is running
echo "Checking if backend is running..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend is not running!"
    echo "Please start the backend first:"
    echo "  python -m uvicorn app.main:app --reload"
    exit 1
fi

echo "✅ Backend is running"
echo ""

# Install test dependencies
echo "Installing test dependencies..."
pip install -r requirements-test.txt
echo ""

# Run tests with coverage
echo "Running tests with coverage analysis..."
pytest tests/test_end_to_end.py --cov=app --cov-report=html --cov-report=term-missing -v

# Display results
echo ""
echo "=========================================="
echo "Coverage Report Generated: htmlcov/index.html"
echo "Test Results Saved to: TEST_RESULTS.md"
echo "=========================================="
