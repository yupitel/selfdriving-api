from datetime import datetime
from typing import Optional
from uuid import UUID

from app.cores.tablename import MEASUREMENT
from app.models.base import BaseSQLModel

from sqlmodel import Field

class MeasurementModel(BaseSQLModel, table=True):
    __tablename__ = MEASUREMENT
    
    vehicle_id: UUID = Field(..., nullable=False)
    area_id: UUID = Field(..., nullable=False)
    local_time: datetime = Field(..., nullable=False)
    measured_at: int = Field(..., nullable=False)
    data_path: Optional[str] = Field(default=None, nullable=True)
