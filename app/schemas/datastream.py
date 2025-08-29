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