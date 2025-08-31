from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class SceneBase(BaseModel):
    """Base schema for Scene"""
    name: Optional[str] = Field(None, max_length=255, description="Name of the scene segment")
    type: int = Field(..., ge=0, le=32767, description="Scene type (application-defined, 0-32767)")
    state: int = Field(..., ge=0, le=32767, description="Scene state (application-defined, 0-32767)")
    datastream_id: Optional[UUID] = Field(None, description="Associated datastream ID")
    start_idx: int = Field(..., ge=0, description="Inclusive start index within the stream")
    end_idx: int = Field(..., ge=0, description="Inclusive end index within the stream")
    data_path: Optional[str] = Field(None, max_length=500, description="Path to scene data or artifacts")


class SceneCreate(SceneBase):
    """Schema for creating a Scene"""
    pass


class SceneUpdate(BaseModel):
    """Schema for updating a Scene"""
    name: Optional[str] = Field(None, max_length=255)
    type: Optional[int] = Field(None, ge=0, le=32767)
    state: Optional[int] = Field(None, ge=0, le=32767)
    datastream_id: Optional[UUID] = None
    start_idx: Optional[int] = Field(None, ge=0)
    end_idx: Optional[int] = Field(None, ge=0)
    data_path: Optional[str] = Field(None, max_length=500)


class SceneResponse(SceneBase):
    """Schema for Scene response"""
    id: UUID
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)


class SceneFilter(BaseModel):
    """Schema for filtering Scenes"""
    type: Optional[int] = Field(None, ge=0, le=32767, description="Filter by type")
    state: Optional[int] = Field(None, ge=0, le=32767, description="Filter by state")
    datastream_id: Optional[UUID] = Field(None, description="Filter by associated datastream ID")
    name: Optional[str] = Field(None, description="Filter by name (partial match)")
    start_time: Optional[datetime] = Field(None, description="Filter by creation time (after)")
    end_time: Optional[datetime] = Field(None, description="Filter by creation time (before)")
    limit: int = Field(100, gt=0, le=1000, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")

