from typing import Optional
from uuid import UUID

from app.cores.tablename import PIPELINE_DEPENDENCY
from app.models.base import BaseSQLModel

from sqlmodel import Field, Column, SmallInteger

class PipelineDependencyModel(BaseSQLModel, table=True):
    __tablename__ = PIPELINE_DEPENDENCY

    parent_id: UUID = Field(..., nullable=False)
    child_id: UUID = Field(..., nullable=False)
