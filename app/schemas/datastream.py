from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


class DataStreamBase(BaseModel):
    """Base schema for DataStream"""
    type: int = Field(..., ge=0, le=32767, description="DataStream type (0-32767)")
    measurement_id: UUID = Field(..., description="Associated measurement ID")
    name: Optional[str] = Field(None, max_length=255, description="Name of the datastream")
    data_path: Optional[str] = Field(None, max_length=500, description="Path to the data file")
    src_path: Optional[str] = Field(None, max_length=500, description="Source path of the data")
    sequence_number: Optional[int] = Field(None, ge=1, description="Sequence number within measurement")
    start_time: Optional[datetime] = Field(None, description="Start time of this segment")
    end_time: Optional[datetime] = Field(None, description="End time of this segment")
    duration: Optional[int] = Field(None, ge=0, description="Duration in milliseconds")
    video_url: Optional[str] = Field(None, description="URL to video file for this segment")
    has_data_loss: bool = Field(False, description="Whether data loss occurred in this segment")
    data_loss_duration: Optional[int] = Field(None, ge=0, description="Duration of data loss in milliseconds")
    processing_status: int = Field(0, ge=0, le=3, description="Processing status (0=PENDING, 1=PROCESSING, 2=COMPLETED, 3=FAILED)")
    state: Optional[int] = Field(None, ge=0, description="Custom state indicator for the datastream")
    frame_count: Optional[int] = Field(None, ge=0, description="Total number of frames captured for this segment")
    valid_frame_count: Optional[int] = Field(None, ge=0, description="Number of frames without data loss in this segment")
    pipeline_state_id: Optional[UUID] = Field(None, description="Pipeline state identifier when generated via pipeline")


class DataStreamCreate(DataStreamBase):
    """Schema for creating a new DataStream"""
    pass


class DataStreamUpdate(BaseModel):
    """Schema for updating a DataStream"""
    type: Optional[int] = Field(None, ge=0, le=32767, description="DataStream type")
    measurement_id: Optional[UUID] = Field(None, description="Associated measurement ID")
    name: Optional[str] = Field(None, max_length=255, description="Name of the datastream")
    data_path: Optional[str] = Field(None, max_length=500, description="Path to the data file")
    src_path: Optional[str] = Field(None, max_length=500, description="Source path of the data")
    sequence_number: Optional[int] = Field(None, ge=1, description="Sequence number within measurement")
    start_time: Optional[datetime] = Field(None, description="Start time of this segment")
    end_time: Optional[datetime] = Field(None, description="End time of this segment")
    duration: Optional[int] = Field(None, ge=0, description="Duration in milliseconds")
    video_url: Optional[str] = Field(None, description="URL to video file for this segment")
    has_data_loss: Optional[bool] = Field(None, description="Whether data loss occurred in this segment")
    data_loss_duration: Optional[int] = Field(None, ge=0, description="Duration of data loss in milliseconds")
    processing_status: Optional[int] = Field(None, ge=0, le=3, description="Processing status (0=PENDING, 1=PROCESSING, 2=COMPLETED, 3=FAILED)")
    state: Optional[int] = Field(None, ge=0, description="Custom state indicator for the datastream")
    frame_count: Optional[int] = Field(None, ge=0, description="Total number of frames captured for this segment")
    valid_frame_count: Optional[int] = Field(None, ge=0, description="Number of frames without data loss in this segment")
    pipeline_state_id: Optional[UUID] = Field(None, description="Pipeline state identifier when generated via pipeline")


class DataStreamResponse(DataStreamBase):
    """Schema for DataStream response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DataStreamFilter(BaseModel):
    """Schema for filtering DataStreams"""
    type: Optional[int] = Field(None, ge=0, le=32767, description="Filter by type")
    measurement_id: Optional[UUID] = Field(None, description="Filter by measurement ID")
    name: Optional[str] = Field(None, description="Filter by name (partial match)")
    data_path: Optional[str] = Field(None, description="Filter by data path (partial match)")
    src_path: Optional[str] = Field(None, description="Filter by source path (partial match)")
    sequence_number: Optional[int] = Field(None, ge=1, description="Filter by sequence number")
    processing_status: Optional[int] = Field(None, ge=0, le=3, description="Filter by processing status")
    has_data_loss: Optional[bool] = Field(None, description="Filter by data loss flag")
    state: Optional[int] = Field(None, ge=0, description="Filter by custom datastream state")
    pipeline_state_id: Optional[UUID] = Field(None, description="Filter by pipeline state identifier")
    segment_start_time: Optional[datetime] = Field(None, description="Filter by segment start time (after)")
    segment_end_time: Optional[datetime] = Field(None, description="Filter by segment end time (before)")
    start_time: Optional[datetime] = Field(None, description="Filter by creation time (after)")
    end_time: Optional[datetime] = Field(None, description="Filter by creation time (before)")
    limit: int = Field(100, gt=0, le=1000, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class DataStreamBulkCreate(BaseModel):
    """Schema for bulk creating DataStreams"""
    datastreams: List[DataStreamCreate] = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="List of datastreams to create"
    )


class DataStreamBulkResponse(BaseModel):
    """Response for bulk operations"""
    created: int = Field(..., description="Number of successfully created items")
    failed: int = Field(..., description="Number of failed items")
    ids: List[UUID] = Field(..., description="IDs of created items")
    errors: List[dict] = Field(default_factory=list, description="Error details for failed items")


class DataStreamTypeEnum:
    """Enumeration of DataStream types"""
    CAMERA = 0
    LIDAR = 1
    RADAR = 2
    IMU = 3
    GPS = 4
    CAN = 5
    ULTRASONIC = 6
    THERMAL = 7
    MICROPHONE = 8
    OTHER = 99
    
    @classmethod
    def get_name(cls, type_value: int) -> str:
        """Get the name of a datastream type"""
        type_map = {
            0: "CAMERA",
            1: "LIDAR",
            2: "RADAR",
            3: "IMU",
            4: "GPS",
            5: "CAN",
            6: "ULTRASONIC",
            7: "THERMAL",
            8: "MICROPHONE",
            99: "OTHER"
        }
        return type_map.get(type_value, "UNKNOWN")
    
    @classmethod
    def is_valid(cls, type_value: int) -> bool:
        """Check if a type value is valid"""
        return 0 <= type_value <= 32767


class ProcessingStatusEnum:
    """Enumeration of processing statuses"""
    PENDING = 0
    PROCESSING = 1
    COMPLETED = 2
    FAILED = 3
    
    @classmethod
    def get_name(cls, status_value: int) -> str:
        """Get the name of a processing status"""
        status_map = {
            0: "PENDING",
            1: "PROCESSING", 
            2: "COMPLETED",
            3: "FAILED"
        }
        return status_map.get(status_value, "UNKNOWN")
    
    @classmethod
    def is_valid(cls, status_value: int) -> bool:
        """Check if a status value is valid"""
        return 0 <= status_value <= 3
