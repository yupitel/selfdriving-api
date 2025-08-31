from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class PipelineStateBase(BaseModel):
    """Base pipelinestate schema"""
    pipelinedata_id: UUID = Field(..., description="Associated pipeline data ID")
    pipeline_id: UUID = Field(..., description="Associated pipeline ID")
    input: str = Field(..., description="Input data or parameters")
    output: str = Field(..., description="Output data or results")
    state: int = Field(..., description="State of the pipeline execution")


class PipelineStateCreate(PipelineStateBase):
    """Schema for creating pipeline state"""
    pass


class PipelineStateUpdate(BaseModel):
    """Schema for updating pipeline state"""
    pipelinedata_id: Optional[UUID] = Field(None, description="Associated pipeline data ID")
    pipeline_id: Optional[UUID] = Field(None, description="Associated pipeline ID")
    input: Optional[str] = Field(None, description="Input data or parameters")
    output: Optional[str] = Field(None, description="Output data or results")
    state: Optional[int] = Field(None, description="State of the pipeline execution")


class PipelineStateResponse(PipelineStateBase):
    """Schema for pipeline state response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: int
    updated_at: int


class PipelineStateListResponse(BaseModel):
    """Schema for pipeline state list response"""
    pipeline_states: List[PipelineStateResponse]
    total: int
    page: int
    per_page: int


class PipelineStateFilter(BaseModel):
    """Schema for pipeline state filtering"""
    pipelinedata_id: Optional[UUID] = None
    pipeline_id: Optional[UUID] = None
    state: Optional[int] = None
    offset: int = 0
    limit: int = 20


class PipelineStateBulkCreate(BaseModel):
    """Schema for bulk creating pipeline states"""
    pipeline_states: List[PipelineStateCreate]


class PipelineStateDetailResponse(BaseModel):
    """Schema for detailed pipeline state response with related data"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    pipelinedata_id: UUID
    pipeline_id: UUID
    input: str
    output: str
    state: int
    created_at: int
    updated_at: int
    
    # Related data (if needed for job management)
    pipelinedata_info: Optional[dict] = Field(None, description="Pipeline data information")
    pipeline_info: Optional[dict] = Field(None, description="Pipeline information")