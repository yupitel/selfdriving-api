from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
import json


class PipelineBase(BaseModel):
    """Base schema for Pipeline"""
    name: str = Field(..., min_length=1, max_length=255, description="Name of the pipeline")
    type: int = Field(..., ge=0, le=32767, description="Pipeline type (0-32767)")
    group: int = Field(..., ge=0, le=32767, description="Pipeline group (0-32767)")
    is_available: int = Field(..., ge=0, le=1, description="Availability status (0=unavailable, 1=available)")
    version: int = Field(..., ge=0, le=32767, description="Pipeline version")
    options: Optional[str] = Field(None, description="Pipeline options as JSON string")
    params: str = Field(..., description="Pipeline parameters as JSON string")

    @field_validator('params')
    @classmethod
    def validate_params_json(cls, v):
        """Validate that params is valid JSON"""
        try:
            json.loads(v)
        except json.JSONDecodeError:
            raise ValueError("params must be valid JSON string")
        return v

    @field_validator('options')
    @classmethod
    def validate_options_json(cls, v):
        """Validate that options is valid JSON if provided"""
        if v is not None:
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("options must be valid JSON string")
        return v


class PipelineCreate(PipelineBase):
    """Schema for creating a new Pipeline"""
    pass


class PipelineUpdate(BaseModel):
    """Schema for updating a Pipeline"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the pipeline")
    type: Optional[int] = Field(None, ge=0, le=32767, description="Pipeline type")
    group: Optional[int] = Field(None, ge=0, le=32767, description="Pipeline group")
    is_available: Optional[int] = Field(None, ge=0, le=1, description="Availability status")
    version: Optional[int] = Field(None, ge=0, le=32767, description="Pipeline version")
    options: Optional[str] = Field(None, description="Pipeline options as JSON string")
    params: Optional[str] = Field(None, description="Pipeline parameters as JSON string")

    @field_validator('params')
    @classmethod
    def validate_params_json(cls, v):
        """Validate that params is valid JSON if provided"""
        if v is not None:
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("params must be valid JSON string")
        return v

    @field_validator('options')
    @classmethod
    def validate_options_json(cls, v):
        """Validate that options is valid JSON if provided"""
        if v is not None:
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("options must be valid JSON string")
        return v


class PipelineResponse(PipelineBase):
    """Schema for Pipeline response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    params_parsed: Optional[Dict[str, Any]] = Field(None, description="Parsed parameters")
    options_parsed: Optional[Dict[str, Any]] = Field(None, description="Parsed options")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj: Any) -> 'PipelineResponse':
        """Custom validation to parse JSON fields"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        # Parse JSON strings to dicts
        if 'params' in data and data['params']:
            try:
                data['params_parsed'] = json.loads(data['params'])
            except json.JSONDecodeError:
                data['params_parsed'] = None
        
        if 'options' in data and data['options']:
            try:
                data['options_parsed'] = json.loads(data['options'])
            except json.JSONDecodeError:
                data['options_parsed'] = None
        
        return super().model_validate(data)


class PipelineFilter(BaseModel):
    """Schema for filtering Pipelines"""
    name: Optional[str] = Field(None, description="Filter by name (partial match)")
    type: Optional[int] = Field(None, ge=0, le=32767, description="Filter by type")
    group: Optional[int] = Field(None, ge=0, le=32767, description="Filter by group")
    is_available: Optional[int] = Field(None, ge=0, le=1, description="Filter by availability")
    version: Optional[int] = Field(None, ge=0, le=32767, description="Filter by version")
    min_version: Optional[int] = Field(None, ge=0, le=32767, description="Filter by minimum version")
    max_version: Optional[int] = Field(None, ge=0, le=32767, description="Filter by maximum version")
    start_time: Optional[datetime] = Field(None, description="Filter by creation time (after)")
    end_time: Optional[datetime] = Field(None, description="Filter by creation time (before)")
    limit: int = Field(100, gt=0, le=1000, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class PipelineBulkCreate(BaseModel):
    """Schema for bulk creating Pipelines"""
    pipelines: List[PipelineCreate] = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="List of pipelines to create"
    )


class PipelineBulkResponse(BaseModel):
    """Response for bulk operations"""
    created: int = Field(..., description="Number of successfully created items")
    failed: int = Field(..., description="Number of failed items")
    ids: List[UUID] = Field(..., description="IDs of created items")
    errors: List[dict] = Field(default_factory=list, description="Error details for failed items")


class PipelineStatistics(BaseModel):
    """Pipeline statistics response"""
    total: int = Field(..., description="Total number of pipelines")
    by_type: Dict[int, int] = Field(..., description="Count of pipelines by type")
    by_group: Dict[int, int] = Field(..., description="Count of pipelines by group")
    available: int = Field(..., description="Count of available pipelines")
    unavailable: int = Field(..., description="Count of unavailable pipelines")
    by_version: Dict[int, int] = Field(..., description="Count of pipelines by version")


class PipelineTypeEnum:
    """Enumeration of Pipeline types"""
    DATA_COLLECTION = 0
    DATA_PROCESSING = 1
    DATA_VALIDATION = 2
    ML_TRAINING = 3
    ML_INFERENCE = 4
    DATA_EXPORT = 5
    DATA_IMPORT = 6
    QUALITY_CHECK = 7
    ANNOTATION = 8
    OTHER = 99
    
    @classmethod
    def get_name(cls, type_value: int) -> str:
        """Get the name of a pipeline type"""
        type_map = {
            0: "DATA_COLLECTION",
            1: "DATA_PROCESSING",
            2: "DATA_VALIDATION",
            3: "ML_TRAINING",
            4: "ML_INFERENCE",
            5: "DATA_EXPORT",
            6: "DATA_IMPORT",
            7: "QUALITY_CHECK",
            8: "ANNOTATION",
            99: "OTHER"
        }
        return type_map.get(type_value, "UNKNOWN")
    
    @classmethod
    def is_valid(cls, type_value: int) -> bool:
        """Check if a type value is valid"""
        return 0 <= type_value <= 32767