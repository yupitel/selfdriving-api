from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class PipelineDependencyBase(BaseModel):
    parent_id: UUID
    child_id: UUID


class PipelineDependencyCreate(PipelineDependencyBase):
    pass


class PipelineDependencyUpdate(BaseModel):
    parent_id: Optional[UUID] = None
    child_id: Optional[UUID] = None


class PipelineDependencyResponse(PipelineDependencyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PipelineDependencyDetailResponse(PipelineDependencyResponse):
    parent_name: Optional[str] = None
    child_name: Optional[str] = None


class PipelineDependencyFilter(BaseModel):
    parent_id: Optional[UUID] = None
    child_id: Optional[UUID] = None
    offset: int = 0
    limit: int = 20


class PipelineDependencyListResponse(BaseModel):
    """Schema for pipeline dependency list response"""
    pipeline_dependencies: List[PipelineDependencyResponse]
    total: int
    page: int
    per_page: int


class PipelineDependencyBulkCreate(BaseModel):
    dependencies: List[PipelineDependencyCreate]
