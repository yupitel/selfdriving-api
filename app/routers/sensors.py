from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.cores.database import get_session
from app.schemas.base import BaseResponse
from app.schemas.sensor import (
    SensorUpdate,
    SensorResponse,
    SensorFilter,
    SensorBulkCreate,
    SensorBulkResponse,
)
from app.services.sensor import SensorService
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
)

router = APIRouter(
    prefix="/api/v1/sensors",
    tags=["sensors"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        409: {"description": "Conflict"},
        500: {"description": "Internal server error"},
    },
)


@router.post("/", response_model=BaseResponse[SensorBulkResponse], status_code=status.HTTP_201_CREATED)
async def create_sensors(
    bulk_data: SensorBulkCreate, session: Session = Depends(get_session)
) -> BaseResponse[SensorBulkResponse]:
    """Bulk create sensor settings for vehicles."""
    try:
        service = SensorService(session)
        result = await service.create_sensors(bulk_data)
        return BaseResponse(success=True, data=SensorBulkResponse(**result))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk create sensors: {str(e)}",
        )


@router.get("/", response_model=BaseResponse[list[SensorResponse]])
async def list_sensors(
    vehicle_id: Optional[UUID] = Query(None, description="Filter by vehicle ID"),
    type: Optional[int] = Query(None, ge=0, le=32767, description="Filter by sensor type"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    start_time: Optional[str] = Query(None, description="Filter by creation time (after)"),
    end_time: Optional[str] = Query(None, description="Filter by creation time (before)"),
    limit: int = Query(100, gt=0, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    session: Session = Depends(get_session),
) -> BaseResponse[list[SensorResponse]]:
    """List sensor settings with optional filters."""
    try:
        filters = SensorFilter(
            vehicle_id=vehicle_id,
            type=type,
            name=name,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
        )
        service = SensorService(session)
        sensors = await service.list_sensors(filters)
        return BaseResponse(success=True, data=[SensorResponse.model_validate(s) for s in sensors])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sensors: {str(e)}",
        )


@router.get("/{sensor_id}", response_model=BaseResponse[list[SensorResponse]])
async def get_sensor(sensor_id: UUID, session: Session = Depends(get_session)) -> BaseResponse[list[SensorResponse]]:
    """Get sensor(s) by ID as a list. Returns [] when not found."""
    try:
        service = SensorService(session)
        sensors = await service.get_sensors_by_id(sensor_id)
        return BaseResponse(success=True, data=[SensorResponse.model_validate(s) for s in sensors])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sensor: {str(e)}",
        )


@router.put("/{sensor_id}", response_model=BaseResponse[SensorResponse])
async def update_sensor(
    sensor_id: UUID, sensor_update: SensorUpdate, session: Session = Depends(get_session)
) -> BaseResponse[SensorResponse]:
    """Update a sensor settings record."""
    try:
        service = SensorService(session)
        updated = await service.update_sensor(sensor_id, sensor_update)
        return BaseResponse(success=True, data=SensorResponse.model_validate(updated))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (BadRequestException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update sensor: {str(e)}",
        )


@router.delete("/{sensor_id}", response_model=BaseResponse[None])
async def delete_sensor(sensor_id: UUID, session: Session = Depends(get_session)) -> BaseResponse[None]:
    """Delete a sensor settings record."""
    try:
        service = SensorService(session)
        await service.delete_sensor(sensor_id)
        return BaseResponse(success=True, message="Sensor deleted")
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete sensor: {str(e)}",
        )

