from typing import Optional
from uuid import UUID

from app.cores.tablename import PIPELINE_STATE
from app.models.base import BaseSQLModel

from sqlmodel import Field, Column, SmallInteger

class PipelineStateModel(BaseSQLModel, table=True):
    __tablename__ = PIPELINE_STATE

    pipelinedata_id: UUID = Field(..., nullable=False)
    pipeline_id: UUID = Field(..., nullable=False)
    input: str = Field(..., nullable=False)
    output: str = Field(..., nullable=False)
    state: int = Field(..., sa_column=Column(SmallInteger, nullable=False))
