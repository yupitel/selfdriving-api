from datetime import datetime
from typing import Optional
from uuid import UUID

from app.cores.tablename import DATASTREAM
from app.models.base import BaseSQLModel

from sqlmodel import Field, Column
from sqlalchemy import SmallInteger, Integer, Boolean

class DataStreamModel(BaseSQLModel, table=True):
    __tablename__ = DATASTREAM
    
    # When using sa_column, set nullability on the SQLAlchemy Column, not Field()
    type: int = Field(sa_column=Column(SmallInteger, nullable=False))
    measurement_id: UUID = Field(..., nullable=False)
    name: Optional[str] = Field(default=None, nullable=True)
    data_path: Optional[str] = Field(default=None, nullable=True)
    src_path: Optional[str] = Field(default=None, nullable=True)
    sequence_number: Optional[int] = Field(default=None, sa_column=Column(Integer, nullable=True))
    start_time: Optional[datetime] = Field(default=None, nullable=True)
    end_time: Optional[datetime] = Field(default=None, nullable=True)
    duration: Optional[int] = Field(default=None, nullable=True)  # Duration in milliseconds
    video_url: Optional[str] = Field(default=None, nullable=True)  # URL to video file
    has_data_loss: bool = Field(default=False, sa_column=Column(Boolean, nullable=False, default=False))
    data_loss_duration: Optional[int] = Field(default=None, nullable=True)  # Data loss duration in milliseconds
    processing_status: int = Field(default=0, sa_column=Column(SmallInteger, nullable=False, default=0))  # 0=PENDING, 1=PROCESSING, 2=COMPLETED, 3=FAILED
