from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.cores.database import get_session
from app.schemas.scene import (
    SceneCreate,
    SceneUpdate,
    SceneResponse,
    SceneFilter,
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


@router.post("/", response_model=SceneResponse, status_code=status.HTTP_201_CREATED)
async def create_scene(
    scene: SceneCreate, session: Session = Depends(get_session)
) -> SceneResponse:
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
        return SceneResponse.model_validate(created)
    except (BadRequestException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scene: {str(e)}",
        )


@router.get("/", response_model=List[SceneResponse])
async def list_scenes(
    type: Optional[int] = Query(None, ge=0, le=32767, description="Filter by type"),
    state: Optional[int] = Query(None, ge=0, le=32767, description="Filter by state"),
    datastream_id: Optional[UUID] = Query(None, description="Filter by datastream ID"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    start_time: Optional[str] = Query(None, description="Filter by creation time (after)"),
    end_time: Optional[str] = Query(None, description="Filter by creation time (before)"),
    limit: int = Query(100, gt=0, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    session: Session = Depends(get_session),
) -> List[SceneResponse]:
    """List scenes with optional filters."""
    try:
        filters = SceneFilter(
            type=type,
            state=state,
            datastream_id=datastream_id,
            name=name,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
        )

        service = SceneService(session)
        scenes = await service.list_scenes(filters)
        return [SceneResponse.model_validate(s) for s in scenes]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scenes: {str(e)}",
        )


@router.get("/{scene_id}", response_model=SceneResponse)
async def get_scene(scene_id: UUID, session: Session = Depends(get_session)) -> SceneResponse:
    """Get a specific scene by ID."""
    try:
        service = SceneService(session)
        scene = await service.get_scene(scene_id)
        return SceneResponse.model_validate(scene)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scene: {str(e)}",
        )


@router.put("/{scene_id}", response_model=SceneResponse)
async def update_scene(
    scene_id: UUID, scene_update: SceneUpdate, session: Session = Depends(get_session)
) -> SceneResponse:
    """Update a scene."""
    try:
        service = SceneService(session)
        updated = await service.update_scene(scene_id, scene_update)
        return SceneResponse.model_validate(updated)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (BadRequestException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scene: {str(e)}",
        )


@router.delete("/{scene_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scene(scene_id: UUID, session: Session = Depends(get_session)) -> None:
    """Delete a scene."""
    try:
        service = SceneService(session)
        await service.delete_scene(scene_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scene: {str(e)}",
        )

