from typing import Optional
from uuid import UUID

from app.cores.tablename import SENSOR
from app.models.base import BaseSQLModel

from sqlmodel import Field, Column
from sqlalchemy import SmallInteger


class SensorModel(BaseSQLModel, table=True):
    __tablename__ = SENSOR

    vehicle_id: UUID = Field(..., nullable=False)
    type: int = Field(..., sa_column=Column(SmallInteger, nullable=False))
    name: Optional[str] = Field(default=None, nullable=True)
    settings: str = Field(..., nullable=False)

