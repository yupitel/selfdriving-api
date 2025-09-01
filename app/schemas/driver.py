from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class DriverBase(BaseModel):
    """Base schema for Driver"""
    email: Optional[str] = Field(None, description="Driver email address")
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the driver")
    name_kana: Optional[str] = Field(None, max_length=100, description="Name in Katakana")
    
    # License information
    license_number: Optional[str] = Field(None, max_length=50, description="Driving license number")
    license_type: Optional[str] = Field(None, max_length=50, description="Type of driving license")
    license_expiry_date: Optional[date] = Field(None, description="License expiration date")
    
    # Certification information
    certification_level: int = Field(0, ge=0, le=3, description="Certification level (0=TRAINEE, 1=BASIC, 2=ADVANCED, 3=EXPERT)")
    certification_date: Optional[date] = Field(None, description="Date when certification was obtained")
    training_completed_date: Optional[date] = Field(None, description="Date when training was completed")
    
    # Status
    status: int = Field(1, ge=0, le=3, description="Driver status (0=INACTIVE, 1=ACTIVE, 2=ON_LEAVE, 3=RETIRED)")
    employment_type: int = Field(1, ge=0, le=3, description="Employment type (0=FULL_TIME, 1=CONTRACT, 2=PART_TIME, 3=EXTERNAL)")
    
    # Organization
    department: Optional[str] = Field(None, max_length=100, description="Department the driver belongs to")
    team: Optional[str] = Field(None, max_length=100, description="Team the driver belongs to")
    supervisor_id: Optional[UUID] = Field(None, description="Reference to supervisor")
    
    # Statistics (read-only in base, will be calculated)
    total_drives: int = Field(0, ge=0, description="Total number of driving sessions")
    total_distance: Optional[Decimal] = Field(None, ge=0, description="Total distance driven in kilometers")
    total_duration: int = Field(0, ge=0, description="Total driving time in seconds")
    last_drive_date: Optional[date] = Field(None, description="Date of last driving session")
    
    # Scores
    safety_score: Optional[Decimal] = Field(None, ge=0, le=1, description="Safety performance score (0.00-1.00)")
    efficiency_score: Optional[Decimal] = Field(None, ge=0, le=1, description="Efficiency score (0.00-1.00)")
    data_quality_score: Optional[Decimal] = Field(None, ge=0, le=1, description="Data collection quality score (0.00-1.00)")
    
    # Contact information
    phone_number: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    emergency_contact: Optional[str] = Field(None, max_length=200, description="Emergency contact information")
    
    # Metadata
    notes: Optional[str] = Field(None, description="Additional notes about the driver")
    extra_metadata: Optional[str] = Field(None, description="Additional metadata as JSON string")


class DriverCreate(DriverBase):
    """Schema for creating a new Driver"""
    # Override some fields to make them required for creation
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the driver")
    
    # Don't allow setting statistics on creation
    total_drives: int = Field(0, description="Will be calculated automatically")
    total_distance: Optional[Decimal] = Field(None, description="Will be calculated automatically")
    total_duration: int = Field(0, description="Will be calculated automatically")
    last_drive_date: Optional[date] = Field(None, description="Will be updated automatically")


class DriverUpdate(BaseModel):
    """Schema for updating a Driver"""
    email: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_kana: Optional[str] = Field(None, max_length=100)
    
    # License information
    license_number: Optional[str] = Field(None, max_length=50)
    license_type: Optional[str] = Field(None, max_length=50)
    license_expiry_date: Optional[date] = None
    
    # Certification information
    certification_level: Optional[int] = Field(None, ge=0, le=3)
    certification_date: Optional[date] = None
    training_completed_date: Optional[date] = None
    
    # Status
    status: Optional[int] = Field(None, ge=0, le=3)
    employment_type: Optional[int] = Field(None, ge=0, le=3)
    
    # Organization
    department: Optional[str] = Field(None, max_length=100)
    team: Optional[str] = Field(None, max_length=100)
    supervisor_id: Optional[UUID] = None
    
    # Contact information
    phone_number: Optional[str] = Field(None, max_length=20)
    emergency_contact: Optional[str] = Field(None, max_length=200)
    
    # Metadata
    notes: Optional[str] = None
    extra_metadata: Optional[str] = None
    
    # Note: Statistics are not updateable directly, they are calculated


class DriverResponse(DriverBase):
    """Schema for Driver response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DriverFilter(BaseModel):
    """Schema for filtering Drivers"""
    email: Optional[str] = Field(None, description="Filter by email (exact match)")
    name: Optional[str] = Field(None, description="Filter by name (partial match)")
    certification_level: Optional[int] = Field(None, ge=0, le=3, description="Filter by certification level")
    status: Optional[int] = Field(None, ge=0, le=3, description="Filter by driver status")
    employment_type: Optional[int] = Field(None, ge=0, le=3, description="Filter by employment type")
    department: Optional[str] = Field(None, description="Filter by department (exact match)")
    team: Optional[str] = Field(None, description="Filter by team (exact match)")
    supervisor_id: Optional[UUID] = Field(None, description="Filter by supervisor ID")
    
    # Date filters
    license_expiring_before: Optional[date] = Field(None, description="Filter drivers whose license expires before this date")
    last_drive_after: Optional[date] = Field(None, description="Filter drivers who drove after this date")
    last_drive_before: Optional[date] = Field(None, description="Filter drivers who drove before this date")
    
    # Score filters
    min_safety_score: Optional[Decimal] = Field(None, ge=0, le=1, description="Minimum safety score")
    min_efficiency_score: Optional[Decimal] = Field(None, ge=0, le=1, description="Minimum efficiency score")
    min_data_quality_score: Optional[Decimal] = Field(None, ge=0, le=1, description="Minimum data quality score")
    
    # Pagination parameters
    offset: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")


class DriverBulkCreate(BaseModel):
    """Schema for bulk creating Drivers"""
    drivers: List[DriverCreate] = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="List of drivers to create"
    )


class DriverBulkResponse(BaseModel):
    """Response for bulk operations"""
    created: int = Field(..., description="Number of successfully created items")
    failed: int = Field(..., description="Number of failed items")
    ids: List[UUID] = Field(..., description="IDs of created items")
    errors: List[dict] = Field(default_factory=list, description="Error details for failed items")


class DriverStatistics(BaseModel):
    """Statistics about drivers"""
    total: int = Field(..., description="Total number of drivers")
    by_status: dict = Field(..., description="Count by status")
    by_certification_level: dict = Field(..., description="Count by certification level")
    by_employment_type: dict = Field(..., description="Count by employment type")
    by_department: dict = Field(..., description="Count by department")
    active_drivers: int = Field(..., description="Number of active drivers")
    license_expiring_soon: int = Field(..., description="Number of drivers with licenses expiring within 30 days")


# Enums for reference
class CertificationLevelEnum:
    """Enumeration of certification levels"""
    TRAINEE = 0
    BASIC = 1
    ADVANCED = 2
    EXPERT = 3
    
    @classmethod
    def get_name(cls, level: int) -> str:
        """Get the name of a certification level"""
        level_map = {
            0: "TRAINEE",
            1: "BASIC",
            2: "ADVANCED",
            3: "EXPERT"
        }
        return level_map.get(level, "UNKNOWN")


class DriverStatusEnum:
    """Enumeration of driver statuses"""
    INACTIVE = 0
    ACTIVE = 1
    ON_LEAVE = 2
    RETIRED = 3
    
    @classmethod
    def get_name(cls, status: int) -> str:
        """Get the name of a driver status"""
        status_map = {
            0: "INACTIVE",
            1: "ACTIVE",
            2: "ON_LEAVE",
            3: "RETIRED"
        }
        return status_map.get(status, "UNKNOWN")


class EmploymentTypeEnum:
    """Enumeration of employment types"""
    FULL_TIME = 0
    CONTRACT = 1
    PART_TIME = 2
    EXTERNAL = 3
    
    @classmethod
    def get_name(cls, emp_type: int) -> str:
        """Get the name of an employment type"""
        type_map = {
            0: "FULL_TIME",
            1: "CONTRACT",
            2: "PART_TIME",
            3: "EXTERNAL"
        }
        return type_map.get(emp_type, "UNKNOWN")
