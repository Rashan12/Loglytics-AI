from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database.session import get_db
from app.models.user import User
from app.models.project import Project
from app.models.log_file import LogFile
from app.models.analysis import Analysis
from app.models.log_entry import LogEntry
from app.services.auth.jwt_handler import get_current_user
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard analytics for the current user"""
    try:
        # Get project count
        project_result = await db.execute(
            select(func.count(Project.id)).where(Project.user_id == current_user.id)
        )
        project_count = project_result.scalar() or 0
        
        # Get log file count
        log_file_result = await db.execute(
            select(func.count(LogFile.id)).where(LogFile.user_id == current_user.id)
        )
        log_file_count = log_file_result.scalar() or 0
        
        # Get analysis count and recent analyses
        analysis_result = await db.execute(
            select(func.count(Analysis.id)).where(Analysis.user_id == current_user.id)
        )
        analysis_count = analysis_result.scalar() or 0
        
        # Get recent analyses
        recent_analyses_result = await db.execute(
            select(Analysis)
            .where(Analysis.user_id == current_user.id)
            .order_by(desc(Analysis.created_at))
            .limit(5)
        )
        recent_analyses = recent_analyses_result.scalars().all()
        
        # Process recent analyses
        analyses_data = []
        for analysis in recent_analyses:
            try:
                results = json.loads(analysis.results) if analysis.results else {}
            except:
                results = {}
            
            analyses_data.append({
                "id": analysis.id,
                "name": analysis.name,
                "description": analysis.description,
                "analysis_type": analysis.analysis_type,
                "status": analysis.status,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                "results": results
            })
        
        # Calculate error rate from analyses (if available)
        error_rate = 0.0
        if analyses_data:
            total_errors = 0
            total_entries = 0
            for analysis in analyses_data:
                if analysis["results"] and "level_distribution" in analysis["results"]:
                    level_dist = analysis["results"]["level_distribution"]
                    total_errors += level_dist.get("ERROR", 0) + level_dist.get("FATAL", 0)
                    total_entries += sum(level_dist.values())
            
            if total_entries > 0:
                error_rate = (total_errors / total_entries) * 100
        
        logger.info(f"📊 Dashboard analytics for user {current_user.id}: {project_count} projects, {log_file_count} log files, {analysis_count} analyses")
        
        return {
            "total_logs": log_file_count,
            "error_rate": round(error_rate, 2),
            "active_projects": project_count,
            "ai_insights": analysis_count,
            "recent_analyses": analyses_data,
            "total_analyses": analysis_count
        }
        
    except Exception as e:
        logger.error(f"❌ Dashboard analytics error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get dashboard analytics: {str(e)}")

@router.get("/analyses")
async def get_all_analyses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get all analyses for the Analytics page"""
    try:
        # Get analyses with pagination
        analyses_result = await db.execute(
            select(Analysis)
            .where(Analysis.user_id == current_user.id)
            .order_by(desc(Analysis.created_at))
            .offset(skip)
            .limit(limit)
        )
        analyses = analyses_result.scalars().all()
        
        # Process analyses data
        analyses_data = []
        for analysis in analyses:
            try:
                results = json.loads(analysis.results) if analysis.results else {}
            except:
                results = {}
            
            analyses_data.append({
                "id": analysis.id,
                "name": analysis.name,
                "description": analysis.description,
                "analysis_type": analysis.analysis_type,
                "status": analysis.status,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
                "execution_time": analysis.execution_time,
                "results": results,
                "log_file_id": analysis.log_file_id
            })
        
        # Get total count
        count_result = await db.execute(
            select(func.count(Analysis.id)).where(Analysis.user_id == current_user.id)
        )
        total_count = count_result.scalar() or 0
        
        logger.info(f"📊 Retrieved {len(analyses_data)} analyses for user {current_user.id}")
        
        return {
            "analyses": analyses_data,
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"❌ Get analyses error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get analyses: {str(e)}")

@router.get("/analyses/{analysis_id}")
async def get_analysis_details(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed analysis results"""
    try:
        # Get specific analysis
        analysis_result = await db.execute(
            select(Analysis).where(
                Analysis.id == analysis_id,
                Analysis.user_id == current_user.id
            )
        )
        analysis = analysis_result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(404, "Analysis not found")
        
        try:
            results = json.loads(analysis.results) if analysis.results else {}
        except:
            results = {}
        
        logger.info(f"📊 Retrieved analysis {analysis_id} for user {current_user.id}")
        
        return {
            "id": analysis.id,
            "name": analysis.name,
            "description": analysis.description,
            "analysis_type": analysis.analysis_type,
            "status": analysis.status,
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
            "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
            "execution_time": analysis.execution_time,
            "results": results,
            "log_file_id": analysis.log_file_id,
            "error_message": analysis.error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get analysis details error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get analysis details: {str(e)}")

@router.get("/log-files")
async def get_user_log_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all log files for the current user with their upload dates"""
    try:
        # Get all log files for this user, ordered by most recent first
        log_files_result = await db.execute(
            select(LogFile)
            .where(LogFile.user_id == current_user.id)
            .order_by(desc(LogFile.created_at))
        )
        log_files = log_files_result.scalars().all()
        
        # Process log files data and deduplicate by filename
        log_files_data = []
        seen_filenames = {}  # Track filenames we've seen
        
        for log_file in log_files:
            # Extract actual filename without UUID prefix
            actual_filename = log_file.filename
            if '_' in actual_filename:
                # Remove the UUID prefix (everything before the last underscore)
                parts = actual_filename.rsplit('_', 1)
                if len(parts) == 2 and len(parts[0]) > 10:
                    # Likely has UUID prefix, use the second part
                    actual_filename = parts[1]
                else:
                    # Just use the original
                    actual_filename = log_file.filename
            
            # Check for duplicates by actual filename
            if actual_filename in seen_filenames:
                # This is a duplicate, update the entry count but keep the most recent file
                existing_file = seen_filenames[actual_filename]
                try:
                    entry_count_result = await db.execute(
                        select(func.count(LogEntry.id)).where(LogEntry.log_file_id == log_file.id)
                    )
                    entry_count = entry_count_result.scalar() or 0
                    
                    # Add to existing file's entry count
                    for i, f in enumerate(log_files_data):
                        if f['id'] == str(existing_file.id):
                            f['entry_count'] += entry_count
                            f['duplicate_count'] = f.get('duplicate_count', 1) + 1
                            break
                except Exception as e:
                    logger.warning(f"Could not count entries for duplicate file: {e}")
                continue
            
            # This is a new unique file
            try:
                entry_count_result = await db.execute(
                    select(func.count(LogEntry.id)).where(LogEntry.log_file_id == log_file.id)
                )
                entry_count = entry_count_result.scalar() or 0
            except Exception as e:
                logger.warning(f"Could not count entries: {e}")
                entry_count = 0
            
            # Get analysis for this log file
            analysis_count_result = await db.execute(
                select(func.count(Analysis.id)).where(
                    Analysis.log_file_id == log_file.id,
                    Analysis.user_id == current_user.id
                )
            )
            analysis_count = analysis_count_result.scalar() or 0
            
            log_files_data.append({
                "id": str(log_file.id),
                "filename": actual_filename,  # Use cleaned filename
                "original_filename": log_file.filename,  # Keep original for reference
                "file_size": log_file.file_size,
                "file_type": log_file.file_type,
                "upload_status": log_file.upload_status,
                "created_at": log_file.created_at.isoformat() if log_file.created_at else None,
                "updated_at": log_file.updated_at.isoformat() if log_file.updated_at else None,
                "entry_count": entry_count,
                "analysis_count": analysis_count,
                "project_id": log_file.project_id,
            })
            
            seen_filenames[actual_filename] = log_file
        
        logger.info(f"📊 Retrieved {len(log_files_data)} log files for user {current_user.id}")
        
        return {
            "log_files": log_files_data,
            "total_count": len(log_files_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Get log files error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get log files: {str(e)}")

@router.get("/by-log-file/{log_file_id}")
async def get_analytics_by_log_file(
    log_file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a specific log file"""
    try:
        # Verify log file exists and belongs to user
        log_file_result = await db.execute(
            select(LogFile).where(
                LogFile.id == log_file_id,
                LogFile.user_id == current_user.id
            )
        )
        log_file = log_file_result.scalar_one_or_none()
        
        if not log_file:
            raise HTTPException(404, "Log file not found")
        
        # Get analysis for this log file
        analysis_result = await db.execute(
            select(Analysis)
            .where(
                Analysis.log_file_id == log_file.id,
                Analysis.user_id == current_user.id
            )
            .order_by(desc(Analysis.created_at))
            .limit(1)
        )
        analysis = analysis_result.scalar_one_or_none()
        
        # Get log entries for this log file
        try:
            entries_result = await db.execute(
                select(LogEntry)
                .where(LogEntry.log_file_id == log_file.id)
                .order_by(LogEntry.timestamp.desc())
            )
            entries = entries_result.scalars().all()
            
            # Calculate analytics from entries
            total_logs = len(entries)
            error_count = sum(1 for e in entries if e.log_level in ['ERROR', 'FATAL'])
            warn_count = sum(1 for e in entries if e.log_level in ['WARN'])
            info_count = sum(1 for e in entries if e.log_level in ['INFO'])
            
            error_rate = (error_count / total_logs * 100) if total_logs > 0 else 0
            
            # Get log level distribution
            level_distribution = {}
            for e in entries:
                level = e.log_level
                level_distribution[level] = level_distribution.get(level, 0) + 1
            
            log_levels = [
                {"name": level, "count": count}
                for level, count in level_distribution.items()
            ]
            
            # Generate timeline data (last 24 hours)
            timeline_data = []
            if entries:
                # Get current time (timezone-aware)
                current_time = datetime.now(timezone.utc)
                start_time = current_time - timedelta(hours=24)
                
                # Create time buckets
                time_buckets = defaultdict(int)
                for entry in entries:
                    if entry.timestamp:
                        entry_time = entry.timestamp
                        if isinstance(entry_time, str):
                            entry_time = datetime.fromisoformat(entry_time)
                        
                        # Make entry_time timezone-aware if it's naive
                        if entry_time.tzinfo is None:
                            # Assume UTC if timezone-naive
                            entry_time = entry_time.replace(tzinfo=timezone.utc)
                        
                        # Only include entries from last 24h
                        if entry_time >= start_time:
                            # Round to hour
                            bucket = entry_time.replace(minute=0, second=0, microsecond=0)
                            time_buckets[bucket] += 1
                
                # Sort and format
                for time, count in sorted(time_buckets.items()):
                    timeline_data.append({
                        "time": time.strftime("%H:%M"),
                        "count": count
                    })
            
        except Exception as e:
            logger.warning(f"Could not get log entries: {e}")
            total_logs = 0
            error_rate = 0
            log_levels = []
            timeline_data = []
        
        # Parse analysis results if available
        analysis_results = {}
        if analysis:
            try:
                analysis_results = json.loads(analysis.results) if analysis.results else {}
            except:
                pass
        
        logger.info(f"📊 Analytics for log file {log_file_id}: {total_logs} entries")
        
        # Generate error frequency data (by day)
        error_frequency = []
        if entries:
            error_entries = [e for e in entries if e.log_level in ['ERROR', 'FATAL']]
            error_by_day = defaultdict(int)
            for error in error_entries:
                if error.timestamp:
                    timestamp = error.timestamp
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp)
                    day = timestamp.strftime('%a')
                    error_by_day[day] += 1
            
            # Default order
            days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for day in days_order:
                if day in error_by_day:
                    error_frequency.append({"period": day, "errors": error_by_day[day]})
        
        # Generate top errors
        top_errors = []
        if entries and total_logs > 0:
            error_entries = [e for e in entries if e.log_level in ['ERROR', 'FATAL']]
            
            if error_entries:
                # Count error occurrences by message
                error_messages = defaultdict(int)
                last_seen_times = {}
                
                for e in error_entries:
                    if e.content:
                        msg = e.content[:100]  # First 100 chars
                        error_messages[msg] += 1
                        # Track last seen timestamp
                        if e.timestamp:
                            timestamp = e.timestamp
                            if isinstance(timestamp, str):
                                timestamp = datetime.fromisoformat(timestamp)
                            # Update last seen if newer
                            if msg not in last_seen_times or timestamp > last_seen_times[msg]:
                                last_seen_times[msg] = timestamp
                
                # Sort by frequency and take top 5
                sorted_errors = sorted(error_messages.items(), key=lambda x: x[1], reverse=True)[:5]
                
                top_errors = [
                    {
                        "severity": "high",
                        "count": count,
                        "message": msg,
                        "lastSeen": last_seen_times.get(msg)
                    }
                    for msg, count in sorted_errors
                ]
                
                logger.info(f"📊 Generated {len(top_errors)} top errors from {len(error_entries)} error entries")
        
        return {
            "log_file": {
                "id": str(log_file.id),
                "filename": log_file.filename,
                "file_size": log_file.file_size,
                "file_type": log_file.file_type,
                "upload_status": log_file.upload_status,
                "created_at": log_file.created_at.isoformat() if log_file.created_at else None,
            },
            "total_logs": total_logs,
            "error_rate": round(error_rate, 2),
            "log_levels": log_levels,
            "timeline": timeline_data,
            "error_frequency": error_frequency,
            "top_errors": top_errors,
            "analysis": analysis_results if analysis else {},
            "analysis_id": analysis.id if analysis else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get analytics by log file error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get analytics: {str(e)}")