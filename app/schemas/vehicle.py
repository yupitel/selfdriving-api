from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class VehicleBase(BaseModel):
    """Base schema for Vehicle"""
    country: Optional[str] = Field(None, max_length=100, description="Country of the vehicle")
    name: str = Field(..., min_length=1, max_length=255, description="Name of the vehicle")
    data_path: Optional[str] = Field(None, max_length=500, description="Path to vehicle data")


class VehicleCreate(VehicleBase):
    """Schema for creating a new Vehicle"""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating a Vehicle"""
    country: Optional[str] = Field(None, max_length=100, description="Country of the vehicle")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the vehicle")
    data_path: Optional[str] = Field(None, max_length=500, description="Path to vehicle data")


class VehicleResponse(VehicleBase):
    """Schema for Vehicle response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehicleFilter(BaseModel):
    """Schema for filtering Vehicles"""
    country: Optional[str] = Field(None, description="Filter by country (exact match)")
    name: Optional[str] = Field(None, description="Filter by name (partial match)")
    data_path: Optional[str] = Field(None, description="Filter by data path (partial match)")
    start_time: Optional[datetime] = Field(None, description="Filter by creation time (after)")
    end_time: Optional[datetime] = Field(None, description="Filter by creation time (before)")
    limit: int = Field(100, gt=0, le=1000, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class VehicleBulkCreate(BaseModel):
    """Schema for bulk creating Vehicles"""
    vehicles: List[VehicleCreate] = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="List of vehicles to create"
    )


class VehicleBulkResponse(BaseModel):
    """Response for bulk operations"""
    created: int = Field(..., description="Number of successfully created items")
    failed: int = Field(..., description="Number of failed items")
    ids: List[UUID] = Field(..., description="IDs of created items")
    errors: List[dict] = Field(default_factory=list, description="Error details for failed items")


class VehicleStatistics(BaseModel):
    """Vehicle statistics response"""
    total: int = Field(..., description="Total number of vehicles")
    by_country: dict = Field(..., description="Count of vehicles by country")
    with_data_path: int = Field(..., description="Count of vehicles with data path")