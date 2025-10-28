from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.config import settings
from app.database.session import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Get token from credentials
        token = credentials.credentials
        
        if not token:
            logger.warning("No token provided")
            raise credentials_exception
        
        # Decode JWT
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            
            if user_id is None:
                logger.warning("Token has no user_id")
                raise credentials_exception
                
        except JWTError as e:
            logger.warning(f"JWT decode error: {e}")
            raise credentials_exception
        
        # Get user from database
        try:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user is None:
                logger.warning(f"User not found: {user_id}")
                raise credentials_exception
            
            return user
            
        except Exception as e:
            logger.error(f"Database error fetching user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected auth error: {e}")
        raise credentials_exception
