from typing import Optional, TypeVar, Generic
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Base response model"""
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None
    error: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    per_page: int = 20
    total: Optional[int] = None


class PaginatedResponse(BaseResponse[T]):
    """Paginated response model"""
    pagination: Optional[PaginationParams] = None