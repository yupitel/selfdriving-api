
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal
import json
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator, AliasChoices

class DatasetItemKind:
    DATASTREAM = 1
    SCENE = 2
    DATASET = 3

class DatasetSourceKind:
    COMPOSED = 1
    EXTERNAL_FILE = 2


class DatasetStateKind:
    CREATING = 1
    READY = 2
    PROCESSING = 3
    FAILED = 4


class DatasetItem(BaseModel):
    item_type: Optional[int] = Field(
        None,
        ge=1,
        le=3,
        description="1=datastream, 2=scene, 3=dataset; null permitted for untyped entries",
    )
    item_id: UUID
    meta: Optional[dict] = Field(default=None, description="Optional membership metadata")

    @field_validator("meta", mode="before")
    @classmethod
    def normalize_meta(cls, value: Optional[dict]) -> Optional[dict]:
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "" or stripped.lower() == "null":
                return None
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                return None
            return parsed if isinstance(parsed, dict) else None
        return None


class DatasetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    purpose: Optional[str] = Field(None, max_length=64, description="training/validation/test/production etc.")
    source_type: int = Field(DatasetSourceKind.COMPOSED, ge=DatasetSourceKind.COMPOSED, le=DatasetSourceKind.EXTERNAL_FILE)
    file_path: Optional[str] = Field(None, description="S3 or local path (external file only)")
    file_format: Optional[str] = Field(None, description="pickle, parquet, tfrecord, etc.")
    algorithm_config: Optional[dict] = Field(None, description="JSON config for split ratios etc.")
    created_by: Optional[str] = Field(None, description="User identifier")


class DatasetCreate(DatasetBase):
    items: Optional[List[DatasetItem]] = Field(default=None, description="Members if COMPOSED")

    @field_validator("name")
    @classmethod
    def normalize_create_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("name cannot be empty")
        return trimmed


class DatasetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    purpose: Optional[str] = Field(None, max_length=64)
    state: Optional[int] = Field(
        None,
        ge=DatasetStateKind.CREATING,
        le=DatasetStateKind.FAILED,
        validation_alias=AliasChoices('state', 'status'),
        serialization_alias='state',
    )
    algorithm_config: Optional[dict] = None
    file_path: Optional[str] = Field(None, description="Update external dataset path")
    file_format: Optional[str] = Field(None, description="Update dataset file format")
    # Replace all items (COMPOSED only). Use item APIs for incremental ops.
    replace_items: Optional[List[DatasetItem]] = None

    @field_validator("name")
    @classmethod
    def normalize_update_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("name cannot be empty")
        return trimmed


class DatasetListItem(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    purpose: Optional[str] = None
    state: int = Field(
        ...,
        ge=DatasetStateKind.CREATING,
        le=DatasetStateKind.FAILED,
        validation_alias=AliasChoices('state', 'status'),
        serialization_alias='state',
    )
    source_type: int
    file_path: Optional[str] = None
    file_format: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    scene_count: int
    datastream_count: int
    dataset_count: int

    model_config = ConfigDict(from_attributes=True)


class DatasetDetail(DatasetListItem):
    items: List[DatasetItem] = Field(default_factory=list)


class DatasetFilter(BaseModel):
    search: Optional[str] = None
    purpose: Optional[str] = None
    state: Optional[int] = Field(
        None,
        ge=DatasetStateKind.CREATING,
        le=DatasetStateKind.FAILED,
        validation_alias=AliasChoices('state', 'status'),
        serialization_alias='state',
    )
    source_type: Optional[int] = Field(
        None,
        ge=DatasetSourceKind.COMPOSED,
        le=DatasetSourceKind.EXTERNAL_FILE,
    )
    created_by: Optional[str] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    offset: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=200)


class DatasetItemsAddRequest(BaseModel):
    items: List[DatasetItem]


class DatasetItemsDeleteRequest(BaseModel):
    # Either member_ids (UUIDs of dataset_member rows) or (item_type,item_id) pairs could be supported;
    # we keep it simple and allow (item_type,item_id) pairs.
    items: List[DatasetItem]
