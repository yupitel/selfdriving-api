from datetime import datetime, date
from typing import Optional
from uuid import UUID
from decimal import Decimal

from app.cores.tablename import DRIVER
from app.models.base import BaseSQLModel

from sqlmodel import Field, Column
from sqlalchemy import DECIMAL, SmallInteger, Integer, Boolean, Date, Text

class DriverModel(BaseSQLModel, table=True):
    __tablename__ = DRIVER
    
    # Driver identification
    email: Optional[str] = Field(default=None, nullable=True, unique=True)
    name: str = Field(..., nullable=False)
    name_kana: Optional[str] = Field(default=None, nullable=True)
    
    # License information
    license_number: Optional[str] = Field(default=None, nullable=True)
    license_type: Optional[str] = Field(default=None, nullable=True)
    license_expiry_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))
    
    # Certification information
    certification_level: int = Field(default=0, sa_column=Column(SmallInteger, nullable=False, default=0))  # 0=TRAINEE, 1=BASIC, 2=ADVANCED, 3=EXPERT
    certification_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))
    training_completed_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))
    
    # Status
    status: int = Field(default=1, sa_column=Column(SmallInteger, nullable=False, default=1))  # 0=INACTIVE, 1=ACTIVE, 2=ON_LEAVE, 3=RETIRED
    employment_type: int = Field(default=1, sa_column=Column(SmallInteger, nullable=False, default=1))  # 0=FULL_TIME, 1=CONTRACT, 2=PART_TIME, 3=EXTERNAL
    
    # Organization
    department: Optional[str] = Field(default=None, nullable=True)
    team: Optional[str] = Field(default=None, nullable=True)
    supervisor_id: Optional[UUID] = Field(default=None, nullable=True)  # Self-referencing foreign key
    
    # Statistics
    total_drives: int = Field(default=0, sa_column=Column(Integer, nullable=False, default=0))
    total_distance: Optional[Decimal] = Field(default=None, sa_column=Column(DECIMAL(10, 2), nullable=True, default=0))
    total_duration: int = Field(default=0, nullable=False)  # Total duration in seconds
    last_drive_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))
    
    # Scores
    safety_score: Optional[Decimal] = Field(default=None, sa_column=Column(DECIMAL(3, 2), nullable=True))
    efficiency_score: Optional[Decimal] = Field(default=None, sa_column=Column(DECIMAL(3, 2), nullable=True))
    data_quality_score: Optional[Decimal] = Field(default=None, sa_column=Column(DECIMAL(3, 2), nullable=True))
    
    # Contact information
    phone_number: Optional[str] = Field(default=None, nullable=True)
    emergency_contact: Optional[str] = Field(default=None, nullable=True)
    
    # Metadata
    notes: Optional[str] = Field(default=None, nullable=True)
    extra_metadata: Optional[str] = Field(default=None, sa_column=Column("metadata", Text, nullable=True))  # JSON string