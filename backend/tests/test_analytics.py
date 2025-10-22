import pytest
from httpx import AsyncClient
from app.main import app
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.log_file import LogFile
from app.models.log_entry import LogEntry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime, timedelta

# Test data fixtures
@pytest.fixture
async def test_user(db: AsyncSession):
    """Create a test user"""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User",
        subscription_tier="pro",
        selected_llm_model="local",
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@pytest.fixture
async def test_project(db: AsyncSession, test_user: User):
    """Create a test project"""
    project = Project(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        name="Test Project",
        description="Test project for analytics"
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

@pytest.fixture
async def test_log_file(db: AsyncSession, test_user: User, test_project: Project):
    """Create a test log file"""
    log_file = LogFile(
        id=str(uuid.uuid4()),
        project_id=test_project.id,
        user_id=test_user.id,
        filename="test.log",
        file_size=1024,
        file_type="text/plain",
        upload_status="completed"
    )
    db.add(log_file)
    await db.commit()
    await db.refresh(log_file)
    return log_file

@pytest.fixture
async def test_log_entries(db: AsyncSession, test_user: User, test_project: Project, test_log_file: LogFile):
    """Create test log entries"""
    log_entries = []
    base_time = datetime.utcnow() - timedelta(hours=24)
    
    # Create various log entries for testing
    test_data = [
        ("ERROR", "Database connection failed", "database.py:123"),
        ("WARN", "High memory usage detected", "memory_monitor.py:45"),
        ("INFO", "User login successful", "auth.py:67"),
        ("ERROR", "Timeout occurred in API call", "api_client.py:89"),
        ("CRITICAL", "System shutdown initiated", "system.py:12"),
        ("INFO", "Cache cleared successfully", "cache.py:34"),
        ("WARN", "Slow query detected", "query_optimizer.py:156"),
        ("ERROR", "File not found: config.json", "config_loader.py:23"),
        ("INFO", "Background job completed", "scheduler.py:78"),
        ("ERROR", "Network timeout", "network.py:45")
    ]
    
    for i, (level, message, source) in enumerate(test_data):
        entry = LogEntry(
            id=str(uuid.uuid4()),
            log_file_id=test_log_file.id,
            project_id=test_project.id,
            user_id=test_user.id,
            timestamp=base_time + timedelta(minutes=i*30),
            log_level=level,
            message=message,
            source=source,
            raw_content=f"{level}: {message}"
        )
        db.add(entry)
        log_entries.append(entry)
    
    await db.commit()
    return log_entries

@pytest.fixture
async def auth_headers(test_user: User):
    """Create authentication headers for test user"""
    # This would normally involve JWT token generation
    # For testing, we'll use a mock approach
    return {"Authorization": f"Bearer test_token_{test_user.id}"}

# Test functions
@pytest.mark.asyncio
async def test_overview_analytics(
    client: AsyncClient, 
    test_user: User, 
    test_project: Project, 
    test_log_entries: list,
    auth_headers: dict
):
    """Test overview analytics endpoint"""
    response = await client.get(
        f"/api/v1/analytics/overview/{test_project.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total_count" in data
    assert "log_level_distribution" in data
    assert "date_range" in data
    assert "timeline" in data
    assert data["total_count"] == len(test_log_entries)

@pytest.mark.asyncio
async def test_error_analytics(
    client: AsyncClient, 
    test_user: User, 
    test_project: Project, 
    test_log_entries: list,
    auth_headers: dict
):
    """Test error analysis endpoint"""
    response = await client.get(
        f"/api/v1/analytics/errors/{test_project.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "mtbf_hours" in data
    assert "error_timeline" in data
    assert "errors_by_service" in data
    assert "error_hotspots" in data
    assert "error_categories" in data
    assert "error_recurrence" in data

@pytest.mark.asyncio
async def test_anomaly_detection(
    client: AsyncClient, 
    test_user: User, 
    test_project: Project, 
    test_log_entries: list,
    auth_headers: dict
):
    """Test anomaly detection endpoint"""
    response = await client.get(
        f"/api/v1/analytics/anomalies/{test_project.id}?threshold=2.0",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "statistical_anomalies" in data
    assert "volume_anomalies" in data
    assert "temporal_anomalies" in data
    assert "pattern_anomalies" in data
    assert "anomaly_scores" in data
    assert "summary" in data
    assert "threshold" in data
    assert data["threshold"] == 2.0

@pytest.mark.asyncio
async def test_performance_metrics(
    client: AsyncClient, 
    test_user: User, 
    test_project: Project, 
    test_log_entries: list,
    auth_headers: dict
):
    """Test performance metrics endpoint"""
    response = await client.get(
        f"/api/v1/analytics/performance/{test_project.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "response_time_analysis" in data
    assert "throughput_metrics" in data
    assert "slow_operations" in data
    assert "endpoint_performance" in data
    assert "resource_usage" in data

@pytest.mark.asyncio
async def test_pattern_analysis(
    client: AsyncClient, 
    test_user: User, 
    test_project: Project, 
    test_log_entries: list,
    auth_headers: dict
):
    """Test pattern analysis endpoint"""
    response = await client.get(
        f"/api/v1/analytics/patterns/{test_project.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "common_patterns" in data
    assert "potential_root_causes" in data
    assert "error_correlations" in data
    assert "message_clusters" in data
    assert "total_analyzed" in data

@pytest.mark.asyncio
async def test_insights_generation(
    client: AsyncClient, 
    test_user: User, 
    test_project: Project, 
    test_log_entries: list,
    auth_headers: dict
):
    """Test AI insights generation endpoint"""
    response = await client.get(
        f"/api/v1/analytics/insights/{test_project.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "insights" in data
    assert "recommendations" in data
    assert "summary" in data
    assert "health_score" in data["summary"]
    
    health_score = data["summary"]["health_score"]
    assert isinstance(health_score, int)
    assert 0 <= health_score <= 100

@pytest.mark.asyncio
async def test_force_refresh(
    client: AsyncClient, 
    test_user: User, 
    test_project: Project, 
    test_log_entries: list,
    auth_headers: dict
):
    """Test force refresh parameter"""
    response = await client.get(
        f"/api/v1/analytics/overview/{test_project.id}?force_refresh=true",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data

@pytest.mark.asyncio
async def test_log_file_filtering(
    client: AsyncClient, 
    test_user: User, 
    test_project: Project, 
    test_log_file: LogFile,
    test_log_entries: list,
    auth_headers: dict
):
    """Test filtering by log file ID"""
    response = await client.get(
        f"/api/v1/analytics/overview/{test_project.id}?log_file_id={test_log_file.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data

@pytest.mark.asyncio
async def test_analytics_generation_trigger(
    client: AsyncClient, 
    test_user: User, 
    test_log_file: LogFile,
    auth_headers: dict
):
    """Test analytics generation trigger endpoint"""
    response = await client.post(
        f"/api/v1/analytics/generate/{test_log_file.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert "status" in data
    assert "log_file_id" in data
    assert data["log_file_id"] == test_log_file.id

@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient, test_project: Project):
    """Test that endpoints require authentication"""
    response = await client.get(f"/api/v1/analytics/overview/{test_project.id}")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_invalid_project_id(
    client: AsyncClient, 
    test_user: User, 
    auth_headers: dict
):
    """Test with invalid project ID"""
    invalid_project_id = str(uuid.uuid4())
    response = await client.get(
        f"/api/v1/analytics/overview/{invalid_project_id}",
        headers=auth_headers
    )
    
    # Should return 200 but with empty results
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 0

@pytest.mark.asyncio
async def test_threshold_validation(
    client: AsyncClient, 
    test_user: User, 
    test_project: Project, 
    auth_headers: dict
):
    """Test threshold parameter validation"""
    # Test valid threshold
    response = await client.get(
        f"/api/v1/analytics/anomalies/{test_project.id}?threshold=3.0",
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Test invalid threshold (should be handled by FastAPI validation)
    response = await client.get(
        f"/api/v1/analytics/anomalies/{test_project.id}?threshold=10.0",
        headers=auth_headers
    )
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_analytics_caching(
    client: AsyncClient, 
    test_user: User, 
    test_project: Project, 
    test_log_entries: list,
    auth_headers: dict
):
    """Test that analytics results are cached"""
    # First request
    response1 = await client.get(
        f"/api/v1/analytics/overview/{test_project.id}",
        headers=auth_headers
    )
    assert response1.status_code == 200
    
    # Second request (should use cache)
    response2 = await client.get(
        f"/api/v1/analytics/overview/{test_project.id}",
        headers=auth_headers
    )
    assert response2.status_code == 200
    
    # Results should be identical (cached)
    assert response1.json() == response2.json()

@pytest.mark.asyncio
async def test_all_analytics_types(
    client: AsyncClient, 
    test_user: User, 
    test_project: Project, 
    test_log_entries: list,
    auth_headers: dict
):
    """Test all analytics types in sequence"""
    analytics_types = ["overview", "errors", "anomalies", "performance", "patterns", "insights"]
    
    for analytics_type in analytics_types:
        response = await client.get(
            f"/api/v1/analytics/{analytics_type}/{test_project.id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed for analytics type: {analytics_type}"
        
        data = response.json()
        assert isinstance(data, dict), f"Response should be dict for {analytics_type}"
        assert len(data) > 0, f"Response should not be empty for {analytics_type}"

# Performance test
@pytest.mark.asyncio
async def test_analytics_performance(
    client: AsyncClient, 
    test_user: User, 
    test_project: Project, 
    test_log_entries: list,
    auth_headers: dict
):
    """Test analytics performance with multiple requests"""
    import time
    
    start_time = time.time()
    
    # Make multiple concurrent requests
    tasks = []
    for _ in range(5):
        task = client.get(
            f"/api/v1/analytics/overview/{test_project.id}",
            headers=auth_headers
        )
        tasks.append(task)
    
    responses = await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # All requests should succeed
    for response in responses:
        assert response.status_code == 200
    
    # Should complete within reasonable time (5 seconds)
    assert duration < 5.0, f"Analytics took too long: {duration:.2f}s"

# Helper function for async test setup
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
