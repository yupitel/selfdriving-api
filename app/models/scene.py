from typing import Optional
from uuid import UUID

from app.cores.tablename import SCENE 
from app.models.base import BaseSQLModel

from sqlmodel import Field, Column, SmallInteger

class SceneDataModel(BaseSQLModel, table=True):
    __tablename__ = SCENE

    name: Optional[str] = Field(default=None, nullable=True)
    type: Optional[int] = Field(..., sa_column=Column(SmallInteger, nullable=True))
    state: Optional[int] = Field(..., sa_column=Column(SmallInteger, nullable=True))
    data_stream_id: Optional[UUID] = Field(default=None, nullable=True)
    start_idx: int = Field(..., nullable=False)
    end_idx: int = Field(..., nullable=False)
    data_path: Optional[str] = Field(default=None, nullable=True)
