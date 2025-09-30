
from __future__ import annotations

import logging
from typing import List, Optional, Tuple, Set
from uuid import UUID

from sqlalchemy import func, and_, or_, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel import Session

from app.cores.config import SCHEMA
from app.models.dataset import DatasetModel, DatasetMemberModel, DatasetSourceType, DatasetStatus
from app.models.datastream import DataStreamModel
from app.models.scene import SceneDataModel
from app.schemas.dataset import (
    DatasetCreate, DatasetUpdate, DatasetFilter, DatasetItem, DatasetItemsAddRequest, DatasetItemsDeleteRequest,
)

logger = logging.getLogger(__name__)


class DatasetService:
    def __init__(self, session: Session):
        self.session = session

    # ---------- Helpers ----------

    def _touch_counts(self, dataset_id: UUID) -> None:
        """Recompute and persist member counts for a dataset."""
        ds = self.session.get(DatasetModel, dataset_id)
        if not ds:
            return

        # Count by type
        q = select(DatasetMemberModel.item_type, func.count()).where(DatasetMemberModel.dataset_id == dataset_id).group_by(DatasetMemberModel.item_type)
        counts = {row[0]: row[1] for row in self.session.exec(q).all()}
        ds.datastream_count = counts.get(0, 0)
        ds.scene_count = counts.get(1, 0)
        ds.dataset_count = counts.get(2, 0)
        ds.save()
        self.session.add(ds)

    def _validate_members_exist(self, items: List[DatasetItem]) -> None:
        """Ensure referenced items exist in their respective tables."""
        if not items:
            return
        # Group by type
        ds_ids = [i.item_id for i in items if i.item_type == 0]
        sc_ids = [i.item_id for i in items if i.item_type == 1]
        dt_ids = [i.item_id for i in items if i.item_type == 2]

        def _check(model, ids, typename):
            if not ids:
                return
            q = select(func.count()).where(model.id.in_(ids))
            found = self.session.exec(q).one()
            if (found or 0) < len(set(ids)):
                raise ValueError(f"Some {typename} IDs do not exist")  # simple msg for client

        _check(DataStreamModel, ds_ids, "datastream")
        _check(SceneDataModel, sc_ids, "scene")
        _check(DatasetModel, dt_ids, "dataset")  # allow nested

    def _detect_cycle(self, parent_dataset_id: UUID, items: List[DatasetItem]) -> None:
        """Prevent cycles when adding nested dataset references."""
        nested_ids = [i.item_id for i in items if i.item_type == 2]
        if not nested_ids:
            return

        # Build ancestor set of parent (all datasets reachable via reverse edges)
        ancestors: Set[UUID] = set()

        def collect_ancestors(target_id: UUID) -> None:
            # Find datasets that contain target_id (reverse membership)
            q = select(DatasetMemberModel.dataset_id).where(
                and_(DatasetMemberModel.item_type == 2, DatasetMemberModel.item_id == target_id)
            )
            parents = [row[0] for row in self.session.exec(q).all()]
            for pid in parents:
                if pid not in ancestors:
                    ancestors.add(pid)
                    collect_ancestors(pid)

        collect_ancestors(parent_dataset_id)

        for nid in nested_ids:
            if nid == parent_dataset_id or nid in ancestors:
                raise ValueError("Adding this nested dataset would create a cycle")


    # ---------- CRUD ----------

    async def create(self, payload: DatasetCreate) -> DatasetModel:
        ds = DatasetModel(
            name=payload.name,
            description=payload.description,
            purpose=payload.purpose,
            source_type=payload.source_type,
            file_path=payload.file_path,
            file_format=payload.file_format,
            created_by=payload.created_by,
            algorithm_config=payload.algorithm_config,
            status=DatasetStatus.CREATING if payload.source_type == DatasetSourceType.COMPOSED else DatasetStatus.READY,
        )
        self.session.add(ds)
        self.session.commit()
        self.session.refresh(ds)

        # For composed datasets, validate and attach items
        if payload.source_type == DatasetSourceType.COMPOSED and payload.items:
            self._validate_members_exist(payload.items)
            self._detect_cycle(ds.id, payload.items)
            for it in payload.items:
                self.session.add(DatasetMemberModel(dataset_id=ds.id, item_type=it.item_type, item_id=it.item_id, meta=it.meta))
            self.session.commit()
            self._touch_counts(ds.id)
            self.session.commit()
            self.session.refresh(ds)

        # Mark ready after initial assembly
        if ds.source_type == DatasetSourceType.COMPOSED:
            ds.status = DatasetStatus.READY
            self.session.add(ds)
            self.session.commit()
            self.session.refresh(ds)

        return ds

    async def get(self, dataset_id: UUID) -> Tuple[Optional[DatasetModel], List[DatasetItem]]:
        ds = self.session.get(DatasetModel, dataset_id)
        if not ds:
            return None, []
        q = select(DatasetMemberModel).where(DatasetMemberModel.dataset_id == dataset_id).order_by(DatasetMemberModel.created_at.asc())
        members = self.session.exec(q).all()
        items = [DatasetItem(item_type=m.item_type, item_id=m.item_id, meta=m.meta) for m in members]
        return ds, items

    async def list(self, filters: DatasetFilter) -> Tuple[List[DatasetModel], int]:
        stmt = select(DatasetModel)
        conds = []
        if filters.search:
            # ILIKE for Postgres; for generic SQL use contains
            conds.append(DatasetModel.name.contains(filters.search))
        if filters.purpose:
            conds.append(DatasetModel.purpose == filters.purpose)
        if filters.status is not None:
            conds.append(DatasetModel.status == filters.status)
        if filters.source_type is not None:
            conds.append(DatasetModel.source_type == filters.source_type)
        if filters.created_by:
            conds.append(DatasetModel.created_by == filters.created_by)
        if filters.created_from:
            conds.append(DatasetModel.created_at >= int(filters.created_from.timestamp()))
        if filters.created_to:
            conds.append(DatasetModel.created_at <= int(filters.created_to.timestamp()))
        if conds:
            stmt = stmt.where(and_(*conds))

        total = self.session.exec(select(func.count()).select_from(stmt.subquery())).one()
        stmt = stmt.order_by(DatasetModel.created_at.desc()).offset((filters.page - 1) * filters.per_page).limit(filters.per_page)
        rows = self.session.exec(stmt).all()
        return rows, int(total or 0)

    async def update(self, dataset_id: UUID, payload: DatasetUpdate) -> Optional[DatasetModel]:
        ds = self.session.get(DatasetModel, dataset_id)
        if not ds:
            return None

        if payload.name is not None:
            ds.name = payload.name
        if payload.description is not None:
            ds.description = payload.description
        if payload.purpose is not None:
            ds.purpose = payload.purpose
        if payload.status is not None:
            ds.status = payload.status
        if payload.algorithm_config is not None:
            ds.algorithm_config = payload.algorithm_config

        self.session.add(ds)

        if payload.replace_items is not None:
            if ds.source_type != DatasetSourceType.COMPOSED:
                raise ValueError("Cannot modify items of an EXTERNAL_FILE dataset")
            # Delete existing
            self.session.exec(select(DatasetMemberModel).where(DatasetMemberModel.dataset_id == ds.id))
            # Easiest: delete via SQL then re-insert
            self.session.exec(
                DatasetMemberModel.__table__.delete().where(DatasetMemberModel.dataset_id == ds.id)
            )
            items = payload.replace_items
            self._validate_members_exist(items)
            self._detect_cycle(ds.id, items)
            for it in items:
                self.session.add(DatasetMemberModel(dataset_id=ds.id, item_type=it.item_type, item_id=it.item_id, meta=it.meta))
            self._touch_counts(ds.id)

        self.session.commit()
        self.session.refresh(ds)
        return ds

    async def add_items(self, dataset_id: UUID, req: DatasetItemsAddRequest) -> DatasetModel:
        ds = self.session.get(DatasetModel, dataset_id)
        if not ds:
            raise ValueError("Dataset not found")
        if ds.source_type != DatasetSourceType.COMPOSED:
            raise ValueError("Cannot add items to an EXTERNAL_FILE dataset" )

        items = req.items or []
        self._validate_members_exist(items)
        self._detect_cycle(ds.id, items)

        for it in items:
            self.session.add(DatasetMemberModel(dataset_id=ds.id, item_type=it.item_type, item_id=it.item_id, meta=it.meta))
        self.session.commit()
        self._touch_counts(ds.id)
        self.session.commit()
        self.session.refresh(ds)
        return ds

    async def remove_items(self, dataset_id: UUID, req: DatasetItemsDeleteRequest) -> DatasetModel:
        ds = self.session.get(DatasetModel, dataset_id)
        if not ds:
            raise ValueError("Dataset not found")
        if ds.source_type != DatasetSourceType.COMPOSED:
            raise ValueError("Cannot remove items from an EXTERNAL_FILE dataset" )

        for it in (req.items or []):
            self.session.exec(
                DatasetMemberModel.__table__.delete().where(
                    and_(
                        DatasetMemberModel.dataset_id == ds.id,
                        DatasetMemberModel.item_type == it.item_type,
                        DatasetMemberModel.item_id == it.item_id,
                    )
                )
            )
        self.session.commit()
        self._touch_counts(ds.id)
        self.session.commit()
        self.session.refresh(ds)
        return ds
