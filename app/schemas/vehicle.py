from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class VehicleBase(BaseModel):
    """Base schema for Vehicle"""
    country: Optional[str] = Field(None, max_length=100, description="Country of the vehicle")
    name: str = Field(..., min_length=1, max_length=255, description="Name of the vehicle")
    data_path: Optional[str] = Field(None, max_length=500, description="Path to vehicle data")
    type: int = Field(..., ge=0, le=32767, description="Vehicle type (0-32767)")
    status: int = Field(..., ge=0, le=32767, description="Vehicle status (0=inactive, 1=active, 2=maintenance, 3=testing)")


class VehicleCreate(VehicleBase):
    """Schema for creating a new Vehicle"""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating a Vehicle"""
    country: Optional[str] = Field(None, max_length=100, description="Country of the vehicle")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the vehicle")
    data_path: Optional[str] = Field(None, max_length=500, description="Path to vehicle data")
    type: Optional[int] = Field(None, ge=0, le=32767, description="Vehicle type")
    status: Optional[int] = Field(None, ge=0, le=32767, description="Vehicle status")


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
    type: Optional[int] = Field(None, ge=0, le=32767, description="Filter by type")
    status: Optional[int] = Field(None, ge=0, le=32767, description="Filter by status")
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
    by_type: dict = Field(..., description="Count of vehicles by type")
    by_status: dict = Field(..., description="Count of vehicles by status")


class VehicleType:
    """Vehicle type enumeration"""
    SEDAN = 0
    SUV = 1
    TRUCK = 2
    VAN = 3
    BUS = 4
    COMPACT = 5
    MINIVAN = 6
    EXPERIMENTAL = 99
    
    @classmethod
    def get_name(cls, type_value: int) -> str:
        """Get the name of a vehicle type"""
        type_map = {
            0: "SEDAN",
            1: "SUV",
            2: "TRUCK",
            3: "VAN",
            4: "BUS",
            5: "COMPACT",
            6: "MINIVAN",
            99: "EXPERIMENTAL"
        }
        return type_map.get(type_value, "UNKNOWN")


class VehicleStatusEnum:
    """Vehicle status enumeration"""
    INACTIVE = 0
    ACTIVE = 1
    MAINTENANCE = 2
    TESTING = 3
    OFFLINE = 4
    
    @classmethod
    def get_name(cls, status_value: int) -> str:
        """Get the name of a vehicle status"""
        status_map = {
            0: "INACTIVE",
            1: "ACTIVE",
            2: "MAINTENANCE",
            3: "TESTING",
            4: "OFFLINE"
        }
        return status_map.get(status_value, "UNKNOWN")