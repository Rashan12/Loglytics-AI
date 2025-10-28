from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, text
from app.database.session import get_db
from app.models.user import User
from app.models.rag_vector import RAGVector
from app.models.log_file import LogFile
from app.services.auth.jwt_handler import get_current_user
from app.services.rag.rag_service import RAGService
from app.schemas.user import UserResponse
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

from fastapi import Body

async def _get_or_create_default_project(db: AsyncSession, user_id: str):
    """Get or create a default project for direct uploads"""
    from app.models.project import Project
    
    # Try to find existing default project
    result = await db.execute(
        select(Project).where(
            Project.user_id == user_id,
            Project.name == "Default Project"
        )
    )
    default_project = result.scalar_one_or_none()
    
    if not default_project:
        # Create default project
        default_project = Project(
            user_id=user_id,
            name="Default Project",
            description="Default project for direct log file uploads"
        )
        db.add(default_project)
        await db.commit()
        await db.refresh(default_project)
        logger.info(f"Created default project for user {user_id}")
    
    return default_project

@router.post("/search")
async def rag_search(
    request: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search RAG vectors for relevant content"""
    try:
        # Extract query and parameters from request
        query = request.get("query", "")
        project_id = request.get("project_id", "default")
        limit = request.get("limit", 20)
        similarity_threshold = request.get("similarity_threshold", 0.7)
        filters = request.get("filters", {})
        
        if not query:
            raise HTTPException(400, "Query is required")
        
        # If project_id is "default", search across all user's projects
        if project_id == "default":
            # Get all project IDs for this user
            from app.models.project import Project
            projects_result = await db.execute(
                select(Project.id).where(Project.user_id == current_user.id)
            )
            user_project_ids = [str(pid) for pid in projects_result.scalars().all()]
            logger.info(f"🔍 Searching across {len(user_project_ids)} projects for user {current_user.id}")
        else:
            user_project_ids = [project_id]
        
        # Initialize RAG service
        rag_service = RAGService(db)
        await rag_service.initialize()
        
        # Convert user to UserResponse format
        user_response = UserResponse(
            id=current_user.id,
            email=current_user.email,
            subscription_tier=current_user.subscription_tier,
            selected_llm_model="maverick",
            is_active=current_user.is_active,
            created_at=current_user.created_at
        )
        
        # Much lower similarity threshold for actual results
        effective_threshold = min(similarity_threshold, 0.05)  # Cap at 0.05 for much better results
        
        # Search across all user projects
        all_results = []
        for pid in user_project_ids:
            try:
                rag_response = await rag_service.query(
                    question=query,
                    project_id=pid,
                    user=user_response,
                    max_chunks=limit,
                    similarity_threshold=effective_threshold,
                    filters=filters
                )
                all_results.extend(rag_response.sources)
            except Exception as e:
                logger.warning(f"Error searching project {pid}: {e}")
                continue
        
        # Sort all results by similarity score and take top results
        all_results.sort(key=lambda x: x['similarity_score'], reverse=True)
        top_results = all_results[:limit]
        
        # Format results
        results = []
        for source in top_results:
            # Parse metadata if it's a string
            metadata = source['metadata']
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            
            results.append({
                "id": str(source['vector_id']) if source['vector_id'] else None,
                "content": source['content_preview'],
                "source": metadata.get("source", "Log Entry") if metadata else "Log Entry",
                "timestamp": metadata.get("timestamp") if metadata else None,
                "score": source['similarity_score'],
                "metadata": metadata
            })
        
        logger.info(f"🔍 RAG search for '{query}': {len(results)} results")
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"❌ RAG search error: {e}", exc_info=True)
        raise HTTPException(500, f"RAG search failed: {str(e)}")

@router.get("/vectors")
async def get_rag_vectors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    project_id: str = Query(None, description="Filter by project ID"),
    skip: int = Query(0, description="Number of results to skip"),
    limit: int = Query(50, description="Maximum number of results")
):
    """Get all RAG vectors for the RAG search page"""
    try:
        # Build query
        query = select(RAGVector).where(RAGVector.user_id == current_user.id)
        
        if project_id:
            query = query.where(RAGVector.project_id == project_id)
        
        query = query.order_by(desc(RAGVector.created_at)).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        vectors = result.scalars().all()
        
        # Format results
        vectors_data = []
        for vector in vectors:
            vectors_data.append({
                "id": vector.id,
                "project_id": vector.project_id,
                "log_file_id": vector.log_file_id,
                "content": vector.content[:200] + "..." if len(vector.content) > 200 else vector.content,
                "content_preview": vector.content[:100] + "..." if len(vector.content) > 100 else vector.content,
                "metadata": vector.metadata,
                "created_at": vector.created_at.isoformat() if vector.created_at else None,
                "embedding_dimension": len(vector.embedding) if vector.embedding else 0
            })
        
        # Get total count
        count_query = select(func.count(RAGVector.id)).where(RAGVector.user_id == current_user.id)
        if project_id:
            count_query = count_query.where(RAGVector.project_id == project_id)
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0
        
        logger.info(f"🔍 Retrieved {len(vectors_data)} RAG vectors for user {current_user.id}")
        
        return {
            "vectors": vectors_data,
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "project_id": project_id
        }
        
    except Exception as e:
        logger.error(f"❌ Get RAG vectors error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get RAG vectors: {str(e)}")

@router.get("/vectors/{vector_id}")
async def get_rag_vector_details(
    vector_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed RAG vector information"""
    try:
        # Get specific vector
        vector_result = await db.execute(
            select(RAGVector).where(
                RAGVector.id == vector_id,
                RAGVector.user_id == current_user.id
            )
        )
        vector = vector_result.scalar_one_or_none()
        
        if not vector:
            raise HTTPException(404, "RAG vector not found")
        
        # Get associated log file info if available
        log_file_info = None
        if vector.log_file_id:
            log_file_result = await db.execute(
                select(LogFile).where(LogFile.id == vector.log_file_id)
            )
            log_file = log_file_result.scalar_one_or_none()
            if log_file:
                log_file_info = {
                    "id": log_file.id,
                    "filename": log_file.filename,
                    "file_size": log_file.file_size,
                    "file_type": log_file.file_type,
                    "created_at": log_file.created_at.isoformat() if log_file.created_at else None
                }
        
        logger.info(f"🔍 Retrieved RAG vector {vector_id} for user {current_user.id}")
        
        return {
            "id": vector.id,
            "project_id": vector.project_id,
            "log_file_id": vector.log_file_id,
            "content": vector.content,
            "metadata": vector.metadata,
            "created_at": vector.created_at.isoformat() if vector.created_at else None,
            "embedding_dimension": len(vector.embedding) if vector.embedding else 0,
            "log_file_info": log_file_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get RAG vector details error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get RAG vector details: {str(e)}")

@router.get("/stats")
async def get_rag_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get RAG statistics for the dashboard"""
    try:
        # Get total vectors count
        total_vectors_result = await db.execute(
            select(func.count(RAGVector.id)).where(RAGVector.user_id == current_user.id)
        )
        total_vectors = total_vectors_result.scalar() or 0
        
        # Get unique log files count
        log_files_result = await db.execute(
            select(func.count(func.distinct(RAGVector.log_file_id)))
            .where(RAGVector.user_id == current_user.id)
        )
        estimated_files = log_files_result.scalar() or 0
        
        logger.info(f"📊 RAG stats for user {current_user.id}: {total_vectors} total vectors, {estimated_files} files")
        
        # Determine status based on whether we have any data
        status = "ready" if total_vectors > 0 else "no_data"
        
        return {
            "indexedChunks": total_vectors,
            "estimatedFiles": estimated_files,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"❌ Get RAG stats error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get RAG stats: {str(e)}")

@router.post("/reindex-all")
async def reindex_all_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Re-index all log files for RAG"""
    try:
        from app.services.rag.rag_service import RAGService
        from app.models.log_file import LogFile
        
        # Get all log files for the user
        log_files_result = await db.execute(
            select(LogFile).where(LogFile.user_id == current_user.id)
        )
        log_files = log_files_result.scalars().all()
        
        if not log_files:
            return {"message": "No log files found", "indexed": 0}
        
        # Initialize RAG service
        rag_service = RAGService(db)
        await rag_service.initialize()
        
        indexed_count = 0
        skipped_count = 0
        errors = []
        
        for log_file in log_files:
            try:
                # Check if already indexed (skip if already processed)
                existing_vectors = await db.execute(
                    select(RAGVector).where(
                        RAGVector.log_file_id == str(log_file.id),
                        RAGVector.user_id == current_user.id
                    )
                )
                if existing_vectors.scalars().first():
                    skipped_count += 1
                    logger.info(f"⏭️ Skipped (already indexed): {log_file.filename}")
                    continue
                
                # Construct file path
                import os
                if log_file.project_id:
                    file_path = os.path.join("uploads", str(log_file.project_id), log_file.filename)
                else:
                    file_path = os.path.join("uploads", log_file.filename)
                
                # Check if file exists
                if not os.path.exists(file_path):
                    errors.append(f"File not found: {log_file.filename}")
                    continue
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Determine project_id - use actual project_id or create/use default
                if log_file.project_id:
                    project_id = str(log_file.project_id)
                else:
                    # Get or create default project
                    default_project = await _get_or_create_default_project(db, current_user.id)
                    project_id = str(default_project.id)
                
                # Index the file
                await rag_service.index_log_file(
                    log_file_id=str(log_file.id),
                    project_id=project_id,
                    user_id=current_user.id,
                    content=content,
                    file_type=log_file.file_type or "log"
                )
                
                indexed_count += 1
                logger.info(f"✅ Re-indexed: {log_file.filename}")
                
            except Exception as e:
                error_msg = f"Error indexing {log_file.filename}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return {
            "message": f"Re-indexing completed",
            "indexed": indexed_count,
            "skipped": skipped_count,
            "total_files": len(log_files),
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"❌ Re-index error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to re-index files: {str(e)}")

@router.get("/health")
async def rag_health_check(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check RAG system health"""
    try:
        # Initialize RAG service
        rag_service = RAGService(db)
        await rag_service.initialize()
        
        # Test a simple query
        user_response = UserResponse(
            id=current_user.id,
            email=current_user.email,
            subscription_tier=current_user.subscription_tier,
            selected_llm_model="maverick",
            is_active=current_user.is_active,
            created_at=current_user.created_at
        )
        
        # Perform a test query
        test_response = await rag_service.query(
            question="test",
            project_id="default",
            user=user_response,
            max_chunks=1,
            similarity_threshold=0.1
        )
        
        logger.info(f"🔍 RAG health check passed for user {current_user.id}")
        
        return {
            "status": "healthy",
            "total_vectors": len(test_response.sources) if test_response.sources else 0,
            "response_time": test_response.metadata.get("search_time", 0),
            "message": "RAG system is operational"
        }
        
    except Exception as e:
        logger.error(f"❌ RAG health check error: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "RAG system is not operational"
        }