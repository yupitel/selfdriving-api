from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class SceneBase(BaseModel):
    """Base schema for Scene"""
    name: Optional[str] = Field(None, max_length=255, description="Name of the scene segment")
    type: Optional[int] = Field(..., ge=0, le=32767, description="Scene type (application-defined, 0-32767)")
    state: Optional[int] = Field(..., ge=0, le=32767, description="Scene state (application-defined, 0-32767)")
    data_stream_id: Optional[UUID] = Field(None, description="Associated datastream ID")
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
    data_stream_id: Optional[UUID] = None
    start_idx: Optional[int] = Field(None, ge=0)
    end_idx: Optional[int] = Field(None, ge=0)
    data_path: Optional[str] = Field(None, max_length=500)


class SceneResponse(SceneBase):
    """Schema for Scene response"""
    id: UUID
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)


class SceneListItemResponse(SceneResponse):
    """Schema for Scene list item with basic metadata"""
    vehicle_id: Optional[UUID] = Field(None, description="Vehicle ID from measurement")
    driver_id: Optional[UUID] = Field(None, description="Driver ID from measurement")
    measurement_name: Optional[str] = Field(None, description="Measurement name")
    datastream_name: Optional[str] = Field(None, description="DataStream name")


class SceneDetailResponse(SceneResponse):
    """Schema for Scene detail with full metadata from JOINs"""
    # DataStream fields
    datastream_name: Optional[str] = Field(None, description="DataStream name")
    video_url: Optional[str] = Field(None, description="Video URL from datastream")
    datastream_start_time: Optional[datetime] = Field(None, description="DataStream start time")
    datastream_end_time: Optional[datetime] = Field(None, description="DataStream end time")
    
    # Measurement fields
    measurement_id: Optional[UUID] = Field(None, description="Measurement ID")
    measurement_name: Optional[str] = Field(None, description="Measurement name")
    vehicle_id: Optional[UUID] = Field(None, description="Vehicle ID")
    driver_id: Optional[UUID] = Field(None, description="Driver ID")
    area_id: Optional[UUID] = Field(None, description="Area ID")
    local_time: Optional[datetime] = Field(None, description="Local time of measurement")
    distance: Optional[float] = Field(None, description="Distance traveled")
    duration: Optional[int] = Field(None, description="Duration in seconds")
    start_location: Optional[str] = Field(None, description="Start location JSON")
    end_location: Optional[str] = Field(None, description="End location JSON")
    weather_condition: Optional[str] = Field(None, description="Weather condition")
    road_condition: Optional[str] = Field(None, description="Road condition")
    
    # Vehicle fields
    vehicle_name: Optional[str] = Field(None, description="Vehicle name")
    vehicle_model: Optional[str] = Field(None, description="Vehicle model")
    
    # Driver fields
    driver_name: Optional[str] = Field(None, description="Driver name")


class SceneFilter(BaseModel):
    """Schema for filtering Scenes"""
    type: Optional[int] = Field(None, ge=0, le=32767, description="Filter by type")
    state: Optional[int] = Field(None, ge=0, le=32767, description="Filter by state")
    data_stream_id: Optional[UUID] = Field(None, description="Filter by associated datastream ID")
    vehicle_id: Optional[UUID] = Field(None, description="Filter by vehicle ID")
    driver_id: Optional[UUID] = Field(None, description="Filter by driver ID")
    name: Optional[str] = Field(None, description="Filter by name (partial match)")
    start_time: Optional[datetime] = Field(None, description="Filter by creation time (after)")
    end_time: Optional[datetime] = Field(None, description="Filter by creation time (before)")
    limit: int = Field(100, gt=0, le=1000, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    include_metadata: bool = Field(True, description="Include vehicle/driver metadata in response")

