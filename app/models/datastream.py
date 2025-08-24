from datetime import datetime
from typing import Optional
from uuid import UUID

from app.cores.tablename import DATASTREAM
from app.models.base import BaseSQLModel

from sqlmodel import Field, Column, SmallInteger

class DataStreamModel(BaseSQLModel, table=True):
    __tablename__ = DATASTREAM
    
    # When using sa_column, set nullability on the SQLAlchemy Column, not Field()
    type: int = Field(sa_column=Column(SmallInteger, nullable=False))
    measurement_id: UUID = Field(..., nullable=False)
    data_path: Optional[str] = Field(default=None, nullable=True)
    src_path: Optional[str] = Field(default=None, nullable=True)
