from __future__ import annotations

from typing import List, Optional, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.cores.database import get_session
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationParams
from app.schemas.dataset import (
    DatasetCreate, DatasetUpdate, DatasetDetail, DatasetListItem, DatasetFilter,
    DatasetItemsAddRequest, DatasetItemsDeleteRequest, DatasetItem
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

@router.get("", response_model=PaginatedResponse[List[DatasetListItem]])
async def list_datasets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    search: Optional[str] = None,
    purpose: Optional[str] = None,
    status_: Optional[int] = Query(None, alias="status"),
    source_type: Optional[int] = None,
    created_by: Optional[str] = None,
    session: Session = Depends(get_session)
):
    try:
        filters = DatasetFilter(
            page=page, per_page=per_page, search=search, purpose=purpose,
            status=status_, source_type=source_type, created_by=created_by
        )
        service = DatasetService(session)
        rows, total = await service.list(filters)
        return PaginatedResponse[List[DatasetListItem]](
            success=True,
            data=[DatasetListItem.model_validate(r) for r in rows],
            pagination=PaginationParams(page=page, per_page=per_page, total=total)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{dataset_id}", response_model=BaseResponse[DatasetDetail])
async def get_dataset(dataset_id: UUID, session: Session = Depends(get_session)):
    try:
        service = DatasetService(session)
        ds, items = await service.get(dataset_id)
        if not ds:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        return BaseResponse(success=True, data=DatasetDetail.model_validate({**ds.model_dump(), "items": [it.model_dump() for it in items]}))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{dataset_id}/items", response_model=BaseResponse[list[DatasetItem]])
async def list_items(
    dataset_id: UUID,
    resolve: Literal["direct", "leaf", "all"] = Query("direct", description="direct: children only, leaf: recurse to scene/datastream, all: include nested datasets too"),
    item_type: Optional[int] = Query(None, ge=0, le=2, description="optional filter by 0=datastream,1=scene,2=dataset"),
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
                if it.item_type == 2:  # dataset
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
        return BaseResponse(success=True, data=DatasetDetail.model_validate({**ds2.model_dump(), "items": [it.model_dump() for it in items]}))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{dataset_id}", response_model=BaseResponse[DatasetDetail])
async def update_dataset(dataset_id: UUID, payload: DatasetUpdate, session: Session = Depends(get_session)):
    try:
        service = DatasetService(session)
        ds = await service.update(dataset_id, payload)
        if not ds:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        ds2, items = await service.get(dataset_id)
        return BaseResponse(success=True, data=DatasetDetail.model_validate({**ds2.model_dump(), "items": [it.model_dump() for it in items]}))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{dataset_id}/items", response_model=BaseResponse[DatasetDetail])
async def add_items(dataset_id: UUID, req: DatasetItemsAddRequest, session: Session = Depends(get_session)):
    try:
        service = DatasetService(session)
        ds = await service.add_items(dataset_id, req)
        ds2, items = await service.get(dataset_id)
        return BaseResponse(success=True, data=DatasetDetail.model_validate({**ds2.model_dump(), "items": [it.model_dump() for it in items]}))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{dataset_id}/items", response_model=BaseResponse[DatasetDetail])
async def remove_items(dataset_id: UUID, req: DatasetItemsDeleteRequest, session: Session = Depends(get_session)):
    try:
        service = DatasetService(session)
        ds = await service.remove_items(dataset_id, req)
        ds2, items = await service.get(dataset_id)
        return BaseResponse(success=True, data=DatasetDetail.model_validate({**ds2.model_dump(), "items": [it.model_dump() for it in items]}))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
