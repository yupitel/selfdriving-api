from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class PipelineDataBase(BaseModel):
    """Base pipelinedata schema"""
    name: Optional[str] = None
    type: int = Field(..., description="Type of pipeline data")
    data_stream_id: Optional[UUID] = Field(None, description="Associated datastream ID")
    scene_id: Optional[UUID] = Field(None, description="Associated scene ID")
    source: Optional[str] = Field(None, description="Data source information")
    data_path: Optional[str] = Field(None, description="Path to the data file")
    params: Optional[str] = Field(None, description="Parameters as JSON string")


class PipelineDataCreate(PipelineDataBase):
    """Schema for creating pipeline data"""
    pass


class PipelineDataUpdate(BaseModel):
    """Schema for updating pipeline data"""
    name: Optional[str] = None
    type: Optional[int] = Field(None, description="Type of pipeline data")
    data_stream_id: Optional[UUID] = Field(None, description="Associated datastream ID")
    scene_id: Optional[UUID] = Field(None, description="Associated scene ID")
    source: Optional[str] = Field(None, description="Data source information")
    data_path: Optional[str] = Field(None, description="Path to the data file")
    params: Optional[str] = Field(None, description="Parameters as JSON string")


class PipelineDataResponse(PipelineDataBase):
    """Schema for pipeline data response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: int
    updated_at: int


class PipelineDataListResponse(BaseModel):
    """Schema for pipeline data list response"""
    pipeline_data: List[PipelineDataResponse]
    total: int
    page: int
    per_page: int


class PipelineDataFilter(BaseModel):
    """Schema for pipeline data filtering"""
    type: Optional[int] = None
    data_stream_id: Optional[UUID] = None
    scene_id: Optional[UUID] = None
    source: Optional[str] = None
    offset: int = 0
    limit: int = 20


class PipelineDataBulkCreate(BaseModel):
    """Schema for bulk creating pipeline data"""
    pipeline_data: List[PipelineDataCreate]