from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

from app.cores.tablename import MEASUREMENT
from app.models.base import BaseSQLModel

from sqlmodel import Field, Column
from sqlalchemy import DECIMAL

class MeasurementModel(BaseSQLModel, table=True):
    __tablename__ = MEASUREMENT
    
    vehicle_id: UUID = Field(..., nullable=False)
    area_id: UUID = Field(..., nullable=False)
    driver_id: Optional[UUID] = Field(default=None, nullable=True)
    local_time: datetime = Field(..., nullable=False)
    measured_at: int = Field(..., nullable=False)
    name: Optional[str] = Field(default=None, nullable=True)
    data_path: Optional[str] = Field(default=None, nullable=True)
    distance: Optional[Decimal] = Field(default=None, sa_column=Column(DECIMAL(10, 2), nullable=True))
    duration: Optional[int] = Field(default=None, nullable=True)  # Total duration in seconds
    start_location: Optional[str] = Field(default=None, nullable=True)  # JSON string
    end_location: Optional[str] = Field(default=None, nullable=True)  # JSON string
    weather_condition: Optional[str] = Field(default=None, nullable=True)
    road_condition: Optional[str] = Field(default=None, nullable=True)
