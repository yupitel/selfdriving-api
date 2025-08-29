from typing import Optional
from uuid import UUID

from app.cores.tablename import PIPELINE
from app.models.base import BaseSQLModel

from sqlmodel import Field, Column, SmallInteger

class PipelineModel(BaseSQLModel, table=True):
    __tablename__ = PIPELINE

    name: str = Field(..., nullable=False)
    type: int = Field(..., sa_column=Column(SmallInteger, nullable=False))
    group: int = Field(..., sa_column=Column(SmallInteger, nullable=False))
    is_available: int = Field(..., sa_column=Column(SmallInteger, nullable=False))
    version: int = Field(..., sa_column=Column(SmallInteger, nullable=False))
    options: Optional[str] = Field(..., nullable=True)
    params: str = Field(..., nullable=False)
