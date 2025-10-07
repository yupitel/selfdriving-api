from __future__ import annotations

from typing import List, Optional, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.cores.database import get_session
from app.schemas.base import BaseResponse
from app.schemas.dataset import (
    DatasetCreate,
    DatasetUpdate,
    DatasetDetail,
    DatasetListItem,
    DatasetFilter,
    DatasetItemsAddRequest,
    DatasetItemsDeleteRequest,
    DatasetItem,
    DatasetItemKind,
)
from app.services.dataset import DatasetService

router = APIRouter(
    prefix="/api/v1/datasets",
    tags=["datasets"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        409: {"description": "Conflict"},
        500: {"description": "Internal server error"}
    }
)

@router.get("", response_model=BaseResponse[list[DatasetListItem]])
async def list_datasets(
    limit: int = Query(20, ge=1, le=200, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    search: Optional[str] = None,
    purpose: Optional[str] = None,
    status_: Optional[int] = Query(None, alias="status"),
    source_type: Optional[int] = None,
    created_by: Optional[str] = None,
    session: Session = Depends(get_session)
):
    try:
        filters = DatasetFilter(
            search=search,
            purpose=purpose,
            status=status_,
            source_type=source_type,
            created_by=created_by,
            offset=offset,
            limit=limit,
        )
        service = DatasetService(session)
        rows, _total = await service.list(filters)

        def _normalize_row(row: object) -> DatasetListItem:
            dataset_obj = row
            if isinstance(row, tuple):
                dataset_obj = row[0]

            if hasattr(dataset_obj, "model_dump"):
                payload = dataset_obj.model_dump()
            elif hasattr(dataset_obj, "dict") and callable(getattr(dataset_obj, "dict")):
                payload = dataset_obj.dict()
            elif hasattr(dataset_obj, "_mapping"):
                payload = dict(dataset_obj._mapping)
            else:
                payload = dataset_obj

            if isinstance(payload, tuple) and hasattr(payload, "_fields"):
                payload = payload._asdict()

            if not isinstance(payload, dict):
                try:
                    payload = dict(payload)  # type: ignore[arg-type]
                except Exception as exc:  # pragma: no cover - defensive
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Unable to normalize dataset row: {exc}",
                    ) from exc

            return DatasetListItem.model_validate(payload)

        normalized = [_normalize_row(row) for row in rows]

        return BaseResponse(success=True, data=normalized)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/count", response_model=BaseResponse[dict[str, int]])
async def count_datasets(
    search: Optional[str] = None,
    purpose: Optional[str] = None,
    status_: Optional[int] = Query(None, alias="status"),
    source_type: Optional[int] = None,
    created_by: Optional[str] = None,
    session: Session = Depends(get_session)
):
    try:
        filters = DatasetFilter(
            offset=0,
            limit=1,
            search=search,
            purpose=purpose,
            status=status_,
            source_type=source_type,
            created_by=created_by,
        )
        service = DatasetService(session)
        total = await service.count(filters)
        return BaseResponse(success=True, data={"count": total})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{dataset_id}", response_model=BaseResponse[DatasetDetail])
async def get_dataset(dataset_id: UUID, session: Session = Depends(get_session)):
    try:
        service = DatasetService(session)
        ds, items = await service.get(dataset_id)
        if not ds:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        base = DatasetListItem.model_validate(ds)
        detail = DatasetDetail.model_validate({**base.model_dump(), "items": [it.model_dump() for it in items]})
        return BaseResponse(success=True, data=detail)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{dataset_id}/items", response_model=BaseResponse[list[DatasetItem]])
async def list_items(
    dataset_id: UUID,
    resolve: Literal["direct", "leaf", "all"] = Query("direct", description="direct: children only, leaf: recurse to scene/datastream, all: include nested datasets too"),
    item_type: Optional[int] = Query(None, ge=1, le=3, description="optional filter by 1=datastream,2=scene,3=dataset"),
    dedupe: bool = Query(False, description="deduplicate by (item_type, item_id)"),
    session: Session = Depends(get_session),
):
    """Return dataset items.
    - resolve=direct: only direct children
    - resolve=leaf: recurse and return only scene/datastream
    - resolve=all: recurse and return all (dataset nodes included)
    """
    try:
        service = DatasetService(session)

        def _filter_and_dedupe(items: list[DatasetItem]) -> list[DatasetItem]:
            seq = items
            if item_type is not None:
                seq = [x for x in seq if x.item_type == item_type]
            if dedupe:
                seen = set()
                uniq = []
                for x in seq:
                    key = (x.item_type, x.item_id)
                    if key not in seen:
                        seen.add(key)
                        uniq.append(x)
                seq = uniq
            return seq

        if resolve == "direct":
            ds, items = await service.get(dataset_id)
            if not ds:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
            return BaseResponse(success=True, data=[i.model_dump() for i in _filter_and_dedupe(items)])

        visited: set[UUID] = set()
        out: list[DatasetItem] = []

        async def dfs(did: UUID):
            if did in visited:
                return
            visited.add(did)
            ds, items = await service.get(did)
            if not ds:
                return
            for it in items:
                if it.item_type == DatasetItemKind.DATASET:
                    if resolve == "all":
                        out.append(it)
                    await dfs(it.item_id)
                else:
                    out.append(it)

        await dfs(dataset_id)
        return BaseResponse(success=True, data=[i.model_dump() for i in _filter_and_dedupe(out)])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", response_model=BaseResponse[DatasetDetail], status_code=status.HTTP_201_CREATED)
async def create_dataset(payload: DatasetCreate, session: Session = Depends(get_session)):
    try:
        service = DatasetService(session)
        ds = await service.create(payload)
        ds2, items = await service.get(ds.id)
        base = DatasetListItem.model_validate(ds2)
        detail = DatasetDetail.model_validate({**base.model_dump(), "items": [it.model_dump() for it in items]})
        return BaseResponse(success=True, data=detail)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{dataset_id}", response_model=BaseResponse[DatasetDetail])
async def update_dataset(dataset_id: UUID, payload: DatasetUpdate, session: Session = Depends(get_session)):
    try:
        service = DatasetService(session)
        await service.update(dataset_id, payload)
        ds2, items = await service.get(dataset_id)
        if not ds2:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        base = DatasetListItem.model_validate(ds2)
        detail = DatasetDetail.model_validate({**base.model_dump(), "items": [it.model_dump() for it in items]})
        return BaseResponse(success=True, data=detail)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{dataset_id}/items", response_model=BaseResponse[DatasetDetail])
async def add_items(dataset_id: UUID, req: DatasetItemsAddRequest, session: Session = Depends(get_session)):
    try:
        service = DatasetService(session)
        await service.add_items(dataset_id, req)
        ds2, items = await service.get(dataset_id)
        base = DatasetListItem.model_validate(ds2)
        detail = DatasetDetail.model_validate({**base.model_dump(), "items": [it.model_dump() for it in items]})
        return BaseResponse(success=True, data=detail)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{dataset_id}/items", response_model=BaseResponse[DatasetDetail])
async def remove_items(dataset_id: UUID, req: DatasetItemsDeleteRequest, session: Session = Depends(get_session)):
    try:
        service = DatasetService(session)
        await service.remove_items(dataset_id, req)
        ds2, items = await service.get(dataset_id)
        base = DatasetListItem.model_validate(ds2)
        detail = DatasetDetail.model_validate({**base.model_dump(), "items": [it.model_dump() for it in items]})
        return BaseResponse(success=True, data=detail)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
