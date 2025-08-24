from datetime import datetime
from typing import Optional
from uuid import UUID

from app.cores.table_name import DATASTREAM
from app.models.base import BaseSQLModel

from sqlmodel import Field, Column, SmallInteger

class DataStreamModel(BaseSQLModel, table=True):
    __tablename__ = DATASTREAM
    
    type: int = Field(..., sa_column=Column(SmallInteger), nullable=False)
    measurement_id: UUID = Field(..., nullable=False)
    data_path: Optional[str] = Field(default=None, nullable=True)
    src_path: Optional[str] = Field(default=None, nullable=True)
