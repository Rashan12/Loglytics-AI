from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.analysis import Analysis
from app.models.log_entry import LogEntry
from app.schemas.analysis import Analysis as AnalysisSchema, AnalysisCreate
from app.services.auth.dependencies import get_current_user
from app.services.analytics.analytics_service import AnalyticsService
from app.services.analytics.analytics_engine import AnalyticsEngine

router = APIRouter()


@router.post("/", response_model=AnalysisSchema)
async def create_analysis(
    analysis: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new analysis"""
    analytics_service = AnalyticsService(db)
    return await analytics_service.create_analysis(analysis, current_user.id)


@router.get("/", response_model=List[AnalysisSchema])
async def get_analyses(
    skip: int = 0,
    limit: int = 100,
    analysis_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's analyses"""
    query = db.query(Analysis).filter(Analysis.user_id == current_user.id)
    
    if analysis_type:
        query = query.filter(Analysis.analysis_type == analysis_type)
    
    analyses = query.offset(skip).limit(limit).all()
    return analyses


@router.get("/{analysis_id}", response_model=AnalysisSchema)
async def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific analysis"""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    return analysis


@router.post("/patterns")
async def analyze_patterns(
    log_file_id: int,
    pattern_type: str = "error",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze log patterns"""
    analytics_service = AnalyticsService(db)
    return await analytics_service.analyze_patterns(log_file_id, pattern_type, current_user.id)


@router.post("/anomalies")
async def detect_anomalies(
    log_file_id: int,
    threshold: float = 0.8,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detect anomalies in logs"""
    analytics_service = AnalyticsService(db)
    return await analytics_service.detect_anomalies(log_file_id, threshold, current_user.id)


@router.get("/stats/overview")
async def get_overview_stats(
    log_file_id: Optional[int] = None,
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overview statistics"""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_overview_stats(log_file_id, days, current_user.id)


# New Analytics Engine Endpoints

@router.get("/anomalies/{project_id}")
async def get_anomaly_detection(
    project_id: str,
    log_file_id: Optional[str] = Query(None),
    threshold: float = Query(2.0, ge=1.0, le=5.0),
    force_refresh: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get anomaly detection results for a project"""
    try:
        engine = AnalyticsEngine(db)
        result = await engine.get_or_compute_analytics(
            project_id=project_id,
            analytics_type="anomalies",
            log_file_id=log_file_id,
            force_refresh=force_refresh
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/{project_id}")
async def get_performance_metrics(
    project_id: str,
    log_file_id: Optional[str] = Query(None),
    force_refresh: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get performance metrics for a project"""
    try:
        engine = AnalyticsEngine(db)
        result = await engine.get_or_compute_analytics(
            project_id=project_id,
            analytics_type="performance",
            log_file_id=log_file_id,
            force_refresh=force_refresh
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns/{project_id}")
async def get_pattern_analysis(
    project_id: str,
    log_file_id: Optional[str] = Query(None),
    force_refresh: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get NLP-based pattern analysis for a project"""
    try:
        engine = AnalyticsEngine(db)
        result = await engine.get_or_compute_analytics(
            project_id=project_id,
            analytics_type="patterns",
            log_file_id=log_file_id,
            force_refresh=force_refresh
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/{project_id}")
async def get_ai_insights(
    project_id: str,
    log_file_id: Optional[str] = Query(None),
    force_refresh: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-generated insights and recommendations for a project"""
    try:
        engine = AnalyticsEngine(db)
        result = await engine.get_or_compute_analytics(
            project_id=project_id,
            analytics_type="insights",
            log_file_id=log_file_id,
            force_refresh=force_refresh
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/{log_file_id}")
async def trigger_analytics_generation(
    log_file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger background analytics generation for a log file"""
    try:
        # TODO: Integrate with Celery for background task processing
        # For now, return a placeholder response
        return {
            "message": "Analytics generation triggered",
            "status": "processing",
            "log_file_id": log_file_id,
            "user_id": current_user.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# New Dashboard Analytics Endpoints

@router.get("/overview/{project_id}")
async def get_analytics_overview(
    project_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    log_levels: Optional[str] = Query(None),  # Comma-separated log levels
    force_refresh: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive analytics overview for dashboard"""
    try:
        from app.services.analytics.metrics_calculator import MetricsCalculator
        
        calculator = MetricsCalculator(db)
        
        # Parse date range
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Parse log levels filter
        log_level_filter = None
        if log_levels:
            log_level_filter = [level.strip().upper() for level in log_levels.split(',')]
        
        # Get overview data
        overview_data = await calculator.calculate_overview(project_id)
        
        # Get error analysis
        error_data = await calculator.calculate_error_analysis(project_id)
        
        # Get anomaly data
        from app.services.analytics.anomaly_detector import AnomalyDetector
        anomaly_detector = AnomalyDetector(db)
        anomaly_data = await anomaly_detector.detect_anomalies(project_id)
        
        return {
            "overview": overview_data,
            "errors": error_data,
            "anomalies": anomaly_data,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline/{project_id}")
async def get_log_timeline(
    project_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    granularity: str = Query("hour", regex="^(hour|day)$"),
    log_levels: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get log timeline data for charts"""
    try:
        from app.services.analytics.metrics_calculator import MetricsCalculator
        
        calculator = MetricsCalculator(db)
        timeline_data = await calculator._get_timeline_data(project_id)
        
        return {
            "timeline": timeline_data,
            "granularity": granularity,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/errors/{project_id}")
async def get_error_analysis(
    project_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get error analysis data"""
    try:
        from app.services.analytics.metrics_calculator import MetricsCalculator
        
        calculator = MetricsCalculator(db)
        error_data = await calculator.calculate_error_analysis(project_id)
        
        return {
            "errors": error_data,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/{project_id}")
async def get_performance_analysis(
    project_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get performance metrics and analysis"""
    try:
        from app.services.analytics.performance_analyzer import PerformanceAnalyzer
        
        analyzer = PerformanceAnalyzer(db)
        performance_data = await analyzer.analyze_performance(project_id)
        
        return {
            "performance": performance_data,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/{project_id}")
async def get_ai_insights_enhanced(
    project_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get enhanced AI insights and recommendations"""
    try:
        # This would integrate with the LLM service to generate insights
        # For now, return mock data
        mock_insights = [
            {
                "id": "1",
                "type": "insight",
                "title": "Error Rate Spike Detected",
                "description": "Errors increased by 35% in the last 24 hours, primarily between 2-4 AM. This pattern suggests a possible cron job or scheduled task issue.",
                "severity": "high",
                "confidence": 0.87,
                "actionable": True,
                "category": "Error Analysis",
                "timestamp": datetime.utcnow().isoformat(),
                "related_metrics": ["Error Rate", "Timeline Analysis"]
            },
            {
                "id": "2",
                "type": "recommendation",
                "title": "Database Connection Pool Optimization",
                "description": "Consider increasing the database connection pool size. Current timeout errors suggest insufficient connections during peak hours.",
                "severity": "medium",
                "confidence": 0.72,
                "actionable": True,
                "category": "Performance",
                "timestamp": datetime.utcnow().isoformat(),
                "related_metrics": ["Response Time", "Database Errors"]
            }
        ]
        
        return {
            "insights": mock_insights,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/{project_id}")
async def export_analytics_data(
    project_id: str,
    format: str = Query(..., regex="^(pdf|csv|json|png)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export analytics data in various formats"""
    try:
        # This would generate the actual export files
        # For now, return a placeholder response
        return {
            "message": f"Export in {format} format initiated",
            "project_id": project_id,
            "format": format,
            "download_url": f"/api/v1/analytics/download/{project_id}/{format}",
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))