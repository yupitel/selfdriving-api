
from __future__ import annotations

import logging
import json
from typing import List, Optional, Tuple, Set, Any
from uuid import UUID

from sqlalchemy import func, and_, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel import Session

from app.models.dataset import DatasetModel, DatasetMemberModel, DatasetSourceType, DatasetStatus
from app.models.datastream import DataStreamModel
from app.models.scene import SceneDataModel
from app.schemas.dataset import (
    DatasetCreate, DatasetUpdate, DatasetFilter, DatasetItem, DatasetItemsAddRequest, DatasetItemsDeleteRequest,
)
from app.utils.exceptions import (
    BadRequestException,
    ConflictException,
    InternalServerException,
    NotFoundException,
)

logger = logging.getLogger(__name__)


class DatasetService:
    def __init__(self, session: Session):
        self.session = session

    # ---------- Helpers ----------

    def _get_dataset_or_404(self, dataset_id: UUID) -> DatasetModel:
        dataset = self.session.get(DatasetModel, dataset_id)
        if not dataset:
            raise NotFoundException(f"Dataset {dataset_id} not found")
        return dataset

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

    def _normalize_meta(self, value: Any) -> Optional[dict]:
        """Normalize meta payloads to dictionary-or-None for schema validation."""
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

    def _validate_members_exist(self, items: List[DatasetItem]) -> None:
        """Ensure referenced items exist in their respective tables."""
        if not items:
            return
        # Group by type
        ds_ids = [i.item_id for i in items if i.item_type == 0]
        sc_ids = [i.item_id for i in items if i.item_type == 1]
        dt_ids = [i.item_id for i in items if i.item_type == 2]

        # Datastreams and scenes may live in external services; warn but continue if missing
        def _warn_missing(model, ids, typename: str) -> None:
            if not ids:
                return
            unique_ids = list(set(ids))
            q = select(model.id).where(model.id.in_(unique_ids))
            existing = {row[0] for row in self.session.exec(q).all()}
            missing = [str(uid) for uid in unique_ids if uid not in existing]
            if missing:
                logger.warning("Dataset creation: missing %s references: %s", typename, missing)

        _warn_missing(DataStreamModel, ds_ids, "datastream")
        _warn_missing(SceneDataModel, sc_ids, "scene")

        # Nested dataset references must exist
        if dt_ids:
            unique_ids = list(set(dt_ids))
            q = select(func.count()).where(DatasetModel.id.in_(unique_ids))
            count = int(self.session.exec(q).scalar_one())
            if count < len(unique_ids):
                raise BadRequestException("Some dataset IDs do not exist")

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
                raise BadRequestException("Adding this nested dataset would create a cycle")


    # ---------- CRUD ----------

    async def create(self, payload: DatasetCreate) -> DatasetModel:
        if payload.source_type == DatasetSourceType.EXTERNAL_FILE:
            file_path = (payload.file_path or "").strip()
            if not file_path:
                raise BadRequestException("EXTERNAL_FILE datasets require a non-empty file_path")
            if payload.items:
                raise BadRequestException("EXTERNAL_FILE datasets do not support items")
            payload.file_path = file_path
        else:
            # Normalise optional strings
            if payload.file_path is not None and not payload.file_path.strip():
                payload.file_path = None
        if payload.file_format is not None and not payload.file_format.strip():
            payload.file_format = None

        dataset = DatasetModel(
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

        try:
            with self.session.begin():
                self.session.add(dataset)
                self.session.flush()  # ensure dataset.id available

                if dataset.source_type == DatasetSourceType.COMPOSED:
                    items = payload.items or []
                    if items:
                        self._validate_members_exist(items)
                        self._detect_cycle(dataset.id, items)
                        for item in items:
                            self.session.add(
                                DatasetMemberModel(
                                    dataset_id=dataset.id,
                                    item_type=item.item_type,
                                    item_id=item.item_id,
                                    meta=self._normalize_meta(item.meta),
                                )
                            )
                        self.session.flush()
                    self._touch_counts(dataset.id)
                    dataset.status = DatasetStatus.READY
                    self.session.add(dataset)

            self.session.refresh(dataset)
            return dataset
        except BadRequestException:
            self.session.rollback()
            raise
        except IntegrityError as exc:
            self.session.rollback()
            logger.warning("Dataset creation conflict: %s", exc)
            raise ConflictException("Dataset membership already exists") from exc
        except SQLAlchemyError as exc:
            self.session.rollback()
            logger.exception("Failed to create dataset: %s", exc)
            raise InternalServerException("Failed to create dataset") from exc

    async def get(self, dataset_id: UUID) -> Tuple[Optional[DatasetModel], List[DatasetItem]]:
        try:
            dataset = self.session.get(DatasetModel, dataset_id)
            if not dataset:
                return None, []
            q = (
                select(DatasetMemberModel)
                .where(DatasetMemberModel.dataset_id == dataset_id)
                .order_by(DatasetMemberModel.created_at.asc())
            )
            result = self.session.exec(q)
            members = result.scalars().all()
            items = [
                DatasetItem(
                    item_type=m.item_type,
                    item_id=m.item_id,
                    meta=self._normalize_meta(m.meta),
                )
                for m in members
            ]
            return dataset, items
        except SQLAlchemyError as exc:
            logger.exception("Failed to fetch dataset %s: %s", dataset_id, exc)
            raise InternalServerException("Failed to fetch dataset") from exc

    def _build_filter_conditions(self, filters: DatasetFilter) -> list:
        conditions: list = []

        if filters.search:
            term = filters.search.strip()
            if term:
                conditions.append(DatasetModel.name.ilike(f"%{term}%"))
        if filters.purpose:
            conditions.append(DatasetModel.purpose == filters.purpose)
        if filters.status is not None:
            conditions.append(DatasetModel.status == filters.status)
        if filters.source_type is not None:
            conditions.append(DatasetModel.source_type == filters.source_type)
        if filters.created_by:
            conditions.append(DatasetModel.created_by == filters.created_by)
        if filters.created_from:
            conditions.append(DatasetModel.created_at >= int(filters.created_from.timestamp()))
        if filters.created_to:
            conditions.append(DatasetModel.created_at <= int(filters.created_to.timestamp()))

        return conditions

    async def list(self, filters: DatasetFilter) -> Tuple[List[DatasetModel], int]:
        stmt = select(DatasetModel)
        conditions = self._build_filter_conditions(filters)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        count_stmt = select(func.count()).select_from(DatasetModel)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))

        try:
            total = int(self.session.exec(count_stmt).scalar_one())
            limit = filters.limit if filters.limit is not None else 20
            if limit <= 0:
                limit = 20
            offset = filters.offset if filters.offset is not None else 0
            if offset < 0:
                offset = 0
            stmt = (
                stmt.order_by(DatasetModel.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            result = self.session.exec(stmt)
            rows = result.scalars().all()
            return rows, total
        except SQLAlchemyError as exc:
            logger.exception("Failed to list datasets: %s", exc)
            raise InternalServerException("Failed to list datasets") from exc

    async def count(self, filters: DatasetFilter) -> int:
        conditions = self._build_filter_conditions(filters)
        count_stmt = select(func.count()).select_from(DatasetModel)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))

        try:
            return int(self.session.exec(count_stmt).scalar_one())
        except SQLAlchemyError as exc:
            logger.exception("Failed to count datasets: %s", exc)
            raise InternalServerException("Failed to count datasets") from exc

    async def update(self, dataset_id: UUID, payload: DatasetUpdate) -> DatasetModel:
        dataset = self._get_dataset_or_404(dataset_id)

        try:
            with self.session.begin():
                if payload.name is not None:
                    dataset.name = payload.name
                if payload.description is not None:
                    dataset.description = payload.description
                if payload.purpose is not None:
                    dataset.purpose = payload.purpose
                if payload.status is not None:
                    dataset.status = payload.status
                if payload.algorithm_config is not None:
                    dataset.algorithm_config = payload.algorithm_config
                if payload.file_path is not None:
                    cleaned = payload.file_path.strip() if payload.file_path else ""
                    if dataset.source_type == DatasetSourceType.EXTERNAL_FILE:
                        if not cleaned:
                            raise BadRequestException("file_path cannot be empty for an EXTERNAL_FILE dataset")
                        dataset.file_path = cleaned
                    else:
                        dataset.file_path = cleaned or None
                if payload.file_format is not None:
                    dataset.file_format = payload.file_format.strip() if payload.file_format else None

                if payload.replace_items is not None:
                    if dataset.source_type != DatasetSourceType.COMPOSED:
                        raise BadRequestException("Cannot modify items of an EXTERNAL_FILE dataset")

                    items = payload.replace_items or []
                    if items:
                        self._validate_members_exist(items)
                        self._detect_cycle(dataset.id, items)

                    delete_stmt = DatasetMemberModel.__table__.delete().where(
                        DatasetMemberModel.dataset_id == dataset.id
                    )
                    self.session.exec(delete_stmt)

                    for item in items:
                        self.session.add(
                            DatasetMemberModel(
                                dataset_id=dataset.id,
                                item_type=item.item_type,
                                item_id=item.item_id,
                                meta=item.meta,
                            )
                        )
                    self.session.flush()
                    self._touch_counts(dataset.id)

                self.session.add(dataset)

            self.session.refresh(dataset)
            return dataset
        except BadRequestException:
            self.session.rollback()
            raise
        except IntegrityError as exc:
            self.session.rollback()
            logger.warning("Dataset update conflict for %s: %s", dataset_id, exc)
            raise ConflictException("Dataset membership already exists") from exc
        except SQLAlchemyError as exc:
            self.session.rollback()
            logger.exception("Failed to update dataset %s: %s", dataset_id, exc)
            raise InternalServerException("Failed to update dataset") from exc

    async def add_items(self, dataset_id: UUID, req: DatasetItemsAddRequest) -> DatasetModel:
        dataset = self._get_dataset_or_404(dataset_id)
        if dataset.source_type != DatasetSourceType.COMPOSED:
            raise BadRequestException("Cannot add items to an EXTERNAL_FILE dataset")

        items = req.items or []
        if not items:
            return dataset

        try:
            self._validate_members_exist(items)
            self._detect_cycle(dataset.id, items)

            for item in items:
                self.session.add(
                    DatasetMemberModel(
                        dataset_id=dataset.id,
                        item_type=item.item_type,
                        item_id=item.item_id,
                        meta=item.meta,
                    )
                )

            self.session.flush()
            self._touch_counts(dataset.id)
            self.session.add(dataset)
            self.session.commit()
            self.session.refresh(dataset)
            return dataset
        except BadRequestException:
            self.session.rollback()
            raise
        except IntegrityError as exc:
            self.session.rollback()
            logger.warning("Dataset add_items conflict for %s: %s", dataset_id, exc)
            raise ConflictException("Dataset membership already exists") from exc
        except SQLAlchemyError as exc:
            self.session.rollback()
            logger.exception("Failed to add items to dataset %s: %s", dataset_id, exc)
            raise InternalServerException("Failed to add items to dataset") from exc

    async def remove_items(self, dataset_id: UUID, req: DatasetItemsDeleteRequest) -> DatasetModel:
        dataset = self._get_dataset_or_404(dataset_id)
        if dataset.source_type != DatasetSourceType.COMPOSED:
            raise BadRequestException("Cannot remove items from an EXTERNAL_FILE dataset")

        items = req.items or []
        if not items:
            return dataset

        try:
            for item in items:
                self.session.exec(
                    DatasetMemberModel.__table__.delete().where(
                        and_(
                            DatasetMemberModel.dataset_id == dataset.id,
                            DatasetMemberModel.item_type == item.item_type,
                            DatasetMemberModel.item_id == item.item_id,
                        )
                    )
                )

            self.session.flush()
            self._touch_counts(dataset.id)
            self.session.add(dataset)
            self.session.commit()
            self.session.refresh(dataset)
            return dataset
        except SQLAlchemyError as exc:
            self.session.rollback()
            logger.exception("Failed to remove items from dataset %s: %s", dataset_id, exc)
            raise InternalServerException("Failed to remove items from dataset") from exc
