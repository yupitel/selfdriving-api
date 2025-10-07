
from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import SmallInteger, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from app.cores.config import SCHEMA
from app.cores.tablename import DATASET, DATASET_MEMBER
from app.models.base import BaseSQLModel


class DatasetSourceType:
    COMPOSED = 0        # Made of items (datastream/scene/dataset)
    EXTERNAL_FILE = 1   # Prebuilt dataset file (pickle, parquet, etc.)


class DatasetStatus:
    CREATING = 0
    READY = 1
    PROCESSING = 2
    FAILED = 3


class DatasetModel(BaseSQLModel, table=True):
    """Dataset parent table."""
    __tablename__ = DATASET

    # Name and description
    name: str = Field(sa_column=Column(String(255), nullable=False, index=True))
    description: Optional[str] = Field(default=None, sa_column=Column(String(2000), nullable=True))

    # Business classification (training/validation/test/production, etc.)
    purpose: Optional[str] = Field(default=None, sa_column=Column(String(64), nullable=True))

    # Status and source
    status: int = Field(default=DatasetStatus.CREATING, sa_column=Column(SmallInteger, nullable=False, index=True))
    source_type: int = Field(default=DatasetSourceType.COMPOSED, sa_column=Column(SmallInteger, nullable=False))

    # For EXTERNAL_FILE source
    file_path: Optional[str] = Field(default=None, sa_column=Column(String(1024), nullable=True))
    file_format: Optional[str] = Field(default=None, sa_column=Column(String(64), nullable=True))

    # Audit
    created_by: Optional[str] = Field(default=None, sa_column=Column(String(128), nullable=True))

    # Aggregates
    scene_count: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    datastream_count: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    dataset_count: int = Field(default=0, sa_column=Column(Integer, nullable=False))

    # Optional JSON config (e.g., split ratios, stratification key)
    algorithm_config: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))

    @property
    def read_only(self) -> bool:
        return self.source_type == DatasetSourceType.EXTERNAL_FILE


class DatasetMemberModel(BaseSQLModel, table=True):
    """Child items that compose a dataset.
    An entry may point to a datastream, scene, or another dataset.
    """
    __tablename__ = DATASET_MEMBER
    __table_args__ = (
        UniqueConstraint("dataset_id", "item_type", "item_id", name="uq_dataset_member_unique"),
        {"schema": SCHEMA},
    )

    dataset_id: UUID = Field(
        sa_column=Column(ForeignKey(f"{SCHEMA}.{DATASET}.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    # 1=datastream, 2=scene, 3=dataset. Nullable for legacy/unknown entries.
    item_type: Optional[int] = Field(sa_column=Column(SmallInteger, nullable=True, index=True))
    item_id: UUID = Field(nullable=False, index=True)

    # Optional metadata per membership (weighting, notes, etc.)
    meta: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
