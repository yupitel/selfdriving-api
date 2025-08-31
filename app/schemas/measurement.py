from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

from .datastream import DataStreamResponse


class MeasurementBase(BaseModel):
    """Base measurement schema"""
    vehicle_id: UUID
    area_id: UUID
    driver_id: Optional[UUID] = None
    local_time: datetime
    measured_at: int
    name: Optional[str] = None
    data_path: Optional[str] = None
    distance: Optional[Decimal] = Field(None, ge=0, description="Total distance in kilometers")
    duration: Optional[int] = Field(None, ge=0, description="Total duration in seconds")
    start_location: Optional[str] = Field(None, description="Starting location as JSON string")
    end_location: Optional[str] = Field(None, description="Ending location as JSON string")
    weather_condition: Optional[str] = None
    road_condition: Optional[str] = None


class MeasurementCreate(MeasurementBase):
    """Schema for creating measurement"""
    pass


class MeasurementUpdate(BaseModel):
    """Schema for updating measurement"""
    vehicle_id: Optional[UUID] = None
    area_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    local_time: Optional[datetime] = None
    measured_at: Optional[int] = None
    name: Optional[str] = None
    data_path: Optional[str] = None
    distance: Optional[Decimal] = Field(None, ge=0, description="Total distance in kilometers")
    duration: Optional[int] = Field(None, ge=0, description="Total duration in seconds")
    start_location: Optional[str] = Field(None, description="Starting location as JSON string")
    end_location: Optional[str] = Field(None, description="Ending location as JSON string")
    weather_condition: Optional[str] = None
    road_condition: Optional[str] = None


class MeasurementResponse(MeasurementBase):
    """Schema for measurement response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: int
    updated_at: int


class MeasurementListResponse(BaseModel):
    """Schema for measurement list response"""
    measurements: List[MeasurementResponse]
    total: int
    page: int
    per_page: int


class MeasurementFilter(BaseModel):
    """Filter parameters for measurements"""
    vehicle_id: Optional[UUID] = None
    area_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    weather_condition: Optional[str] = None
    road_condition: Optional[str] = None
    min_distance: Optional[Decimal] = Field(None, ge=0, description="Minimum distance in kilometers")
    max_distance: Optional[Decimal] = Field(None, ge=0, description="Maximum distance in kilometers")
    min_duration: Optional[int] = Field(None, ge=0, description="Minimum duration in seconds")
    max_duration: Optional[int] = Field(None, ge=0, description="Maximum duration in seconds")
    
    # Pagination parameters
    offset: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")
    
    
class MeasurementDetailResponse(MeasurementResponse):
    """Schema for measurement detail response with embedded datastreams"""
    datastreams: Optional[List[DataStreamResponse]] = Field(default_factory=list, description="Associated datastreams")
    total_segments: int = Field(0, description="Total number of datastream segments")
    processing_status: str = Field("pending", description="Aggregate processing status")


class MeasurementBulkCreate(BaseModel):
    """Schema for bulk creating measurements"""
    measurements: List[MeasurementCreate]