from typing import Optional
from uuid import UUID

from app.cores.tablename import PIPELINE_DATA
from app.models.base import BaseSQLModel

from sqlmodel import Field, Column, SmallInteger

class PipelineDataModel(BaseSQLModel, table=True):
    __tablename__ = PIPELINE_DATA

    name: Optional[str] = Field(default=None, nullable=True)
    type: int = Field(..., sa_column=Column(SmallInteger, nullable=False))
    datastream_id: Optional[UUID] = Field(default=None, nullable=True)
    scene_id: Optional[UUID] = Field(default=None, nullable=True)
    source: Optional[str] = Field(default=None, nullable=True)
    data_path: Optional[str] = Field(default=None, nullable=True)
    params: Optional[str] = Field(default=None, nullable=True)
