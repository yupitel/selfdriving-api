from typing import Optional

from app.cores.tablename import VEHICLE 
from app.models.base import BaseSQLModel
from sqlmodel import Field, Column, SmallInteger

class VehicleModel(BaseSQLModel, table=True):
    __tablename__ = VEHICLE

    country: Optional[str] = Field(default=None, nullable=True)
    name: Optional[str] = Field(default=None, nullable=False)
    data_path: Optional[str] = Field(default=None, nullable=True)
    type: int = Field(..., sa_column=Column(SmallInteger, nullable=False))
    status: int = Field(..., sa_column=Column(SmallInteger, nullable=False))