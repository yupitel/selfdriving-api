from fastapi import APIRouter, Depends
from sqlmodel import Session, text
from app.cores.database import get_session
from app.schemas.base import BaseResponse

router = APIRouter(
    prefix="/api/v1",
    tags=["Health"]
)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return BaseResponse(
        success=True,
        message="API is healthy",
        data={"status": "ok"}
    )


@router.get("/health/db")
async def database_health_check(session: Session = Depends(get_session)):
    """Database health check endpoint"""
    try:
        # Test database connection
        result = session.exec(text("SELECT 1"))
        result.first()
        
        return BaseResponse(
            success=True,
            message="Database connection is healthy",
            data={"status": "ok", "database": "connected"}
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message="Database connection failed",
            error=str(e),
            data={"status": "error", "database": "disconnected"}
        )