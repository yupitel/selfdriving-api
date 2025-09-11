from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.cores.database import get_session
from app.schemas.base import BaseResponse
from app.schemas.scene import (
    SceneCreate,
    SceneUpdate,
    SceneResponse,
    SceneFilter,
    SceneDetailResponse,
    SceneListItemResponse,
)
from app.services.scene import SceneService
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
    InternalServerException,
)

router = APIRouter(
    prefix="/api/v1/scenes",
    tags=["scenes"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        409: {"description": "Conflict"},
        500: {"description": "Internal server error"},
    },
)


@router.post("/", response_model=BaseResponse[SceneResponse], status_code=status.HTTP_201_CREATED)
async def create_scene(
    scene: SceneCreate, session: Session = Depends(get_session)
) -> BaseResponse[SceneResponse]:
    """
    Create a new scene.

    - type: Scene type (0-32767)
    - state: Scene state (0-32767)
    - datastream_id: Optional associated datastream
    - start_idx/end_idx: Segment indices within the stream
    """
    try:
        service = SceneService(session)
        created = await service.create_scene(scene)
        return BaseResponse(success=True, data=SceneResponse.model_validate(created))
    except (BadRequestException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scene: {str(e)}",
        )


@router.get("/", response_model=BaseResponse[list[Union[SceneListItemResponse, SceneResponse]]])
async def list_scenes(
    type: Optional[int] = Query(None, ge=0, le=32767, description="Filter by type"),
    state: Optional[int] = Query(None, ge=0, le=32767, description="Filter by state"),
    datastream_id: Optional[UUID] = Query(None, description="Filter by datastream ID"),
    vehicle_id: Optional[UUID] = Query(None, description="Filter by vehicle ID"),
    driver_id: Optional[UUID] = Query(None, description="Filter by driver ID"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    start_time: Optional[str] = Query(None, description="Filter by creation time (after)"),
    end_time: Optional[str] = Query(None, description="Filter by creation time (before)"),
    limit: int = Query(100, gt=0, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    include_metadata: bool = Query(True, description="Include vehicle/driver metadata"),
    session: Session = Depends(get_session),
) -> BaseResponse[list[Union[SceneListItemResponse, SceneResponse]]]:
    """List scenes with optional filters and metadata."""
    try:
        filters = SceneFilter(
            type=type,
            state=state,
            datastream_id=datastream_id,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            name=name,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
            include_metadata=include_metadata,
        )

        service = SceneService(session)
        
        if include_metadata:
            # Returns SceneListItemResponse objects with metadata
            data = await service.list_scenes_with_metadata(filters)
            return BaseResponse(success=True, data=data)
        else:
            scenes = await service.list_scenes(filters)
            return BaseResponse(success=True, data=[SceneResponse.model_validate(s) for s in scenes])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scenes: {str(e)}",
        )


@router.get("/{scene_id}", response_model=BaseResponse[list[SceneResponse]])
async def get_scene(scene_id: UUID, session: Session = Depends(get_session)) -> BaseResponse[list[SceneResponse]]:
    """Get scene(s) by ID as a list. Returns [] when not found."""
    try:
        service = SceneService(session)
        scenes = await service.get_scenes_by_id(scene_id)
        return BaseResponse(success=True, data=[SceneResponse.model_validate(s) for s in scenes])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scene: {str(e)}",
        )


@router.get("/{scene_id}/detail", response_model=BaseResponse[SceneDetailResponse])
async def get_scene_detail(scene_id: UUID, session: Session = Depends(get_session)) -> BaseResponse[SceneDetailResponse]:
    """Get a specific scene with full details including vehicle, driver, and measurement information."""
    try:
        service = SceneService(session)
        scene_detail = await service.get_scene_detail(scene_id)
        return BaseResponse(success=True, data=scene_detail)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scene detail: {str(e)}",
        )


@router.put("/{scene_id}", response_model=BaseResponse[SceneResponse])
async def update_scene(
    scene_id: UUID, scene_update: SceneUpdate, session: Session = Depends(get_session)
) -> BaseResponse[SceneResponse]:
    """Update a scene."""
    try:
        service = SceneService(session)
        updated = await service.update_scene(scene_id, scene_update)
        return BaseResponse(success=True, data=SceneResponse.model_validate(updated))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (BadRequestException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scene: {str(e)}",
        )


@router.delete("/{scene_id}", response_model=BaseResponse[None])
async def delete_scene(scene_id: UUID, session: Session = Depends(get_session)) -> BaseResponse[None]:
    """Delete a scene."""
    try:
        service = SceneService(session)
        await service.delete_scene(scene_id)
        return BaseResponse(success=True, message="Scene deleted")
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scene: {str(e)}",
        )
