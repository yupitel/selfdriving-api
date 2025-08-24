from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class MeasurementBase(BaseModel):
    """Base measurement schema"""
    vehicle_id: UUID
    area_id: UUID
    local_time: datetime
    measured_at: int
    data_path: Optional[str] = None


class MeasurementCreate(MeasurementBase):
    """Schema for creating measurement"""
    pass


class MeasurementUpdate(BaseModel):
    """Schema for updating measurement"""
    vehicle_id: Optional[UUID] = None
    area_id: Optional[UUID] = None
    local_time: Optional[datetime] = None
    measured_at: Optional[int] = None
    data_path: Optional[str] = None


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
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    
class MeasurementBulkCreate(BaseModel):
    """Schema for bulk creating measurements"""
    measurements: List[MeasurementCreate]