from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.cores.database import get_session
from app.schemas.base import BaseResponse
from app.schemas.vehicle import (
    VehicleUpdate,
    VehicleResponse,
    VehicleFilter,
    VehicleBulkCreate,
    VehicleBulkResponse,
    VehicleStatistics
)
from app.services.vehicle import VehicleService
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
    InternalServerException
)

router = APIRouter(
    prefix="/api/v1/vehicles",
    tags=["vehicles"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        409: {"description": "Conflict"},
        500: {"description": "Internal server error"}
    }
)


@router.post("/", response_model=BaseResponse[VehicleBulkResponse], status_code=status.HTTP_201_CREATED)
async def create_vehicles(
    bulk_data: VehicleBulkCreate,
    session: Session = Depends(get_session)
) -> BaseResponse[VehicleBulkResponse]:
    """
    Bulk create vehicles.

    - **vehicles**: List of vehicles to create (max 1000)

    Returns:
    - **created**: Number of successfully created vehicles
    - **failed**: Number of failed creations
    - **ids**: List of created vehicle IDs
    - **errors**: List of error details for failed creations
    """
    try:
        service = VehicleService(session)
        result = await service.create_vehicles(bulk_data)
        return BaseResponse(success=True, data=VehicleBulkResponse(**result))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk create vehicles: {str(e)}"
        )


@router.get("/", response_model=BaseResponse[list[VehicleResponse]])
async def list_vehicles(
    country: Optional[str] = Query(None, description="Filter by country (exact match)"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    data_path: Optional[str] = Query(None, description="Filter by data path (partial match)"),
    start_time: Optional[str] = Query(None, description="Filter by creation time (after)"),
    end_time: Optional[str] = Query(None, description="Filter by creation time (before)"),
    limit: int = Query(100, gt=0, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    session: Session = Depends(get_session)
) -> BaseResponse[list[VehicleResponse]]:
    """
    List vehicles with optional filters.
    
    Query parameters:
    - **country**: Filter by country (exact match)
    - **name**: Filter by name (partial match)
    - **data_path**: Filter by data path (partial match)
    - **start_time**: Filter by creation time (after)
    - **end_time**: Filter by creation time (before)
    - **limit**: Maximum number of results (default: 100, max: 1000)
    - **offset**: Number of results to skip (default: 0)
    """
    try:
        # Build filter object
        filters = VehicleFilter(
            country=country,
            name=name,
            data_path=data_path,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset
        )
        
        service = VehicleService(session)
        vehicles = await service.list_vehicles(filters)
        return BaseResponse(success=True, data=[VehicleResponse.model_validate(v) for v in vehicles])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list vehicles: {str(e)}"
        )


@router.get("/statistics", response_model=BaseResponse[VehicleStatistics])
async def get_vehicle_statistics(
    session: Session = Depends(get_session)
) -> BaseResponse[VehicleStatistics]:
    """
    Get statistics about vehicles.
    
    Returns:
    - **total**: Total number of vehicles
    - **by_country**: Count of vehicles by country
    - **with_data_path**: Count of vehicles with data_path
    """
    try:
        service = VehicleService(session)
        stats = await service.get_vehicle_statistics()
        return BaseResponse(success=True, data=VehicleStatistics(**stats))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/country/{country}", response_model=BaseResponse[list[VehicleResponse]])
async def get_vehicles_by_country(
    country: str,
    limit: int = Query(100, gt=0, le=1000, description="Maximum number of results"),
    session: Session = Depends(get_session)
) -> BaseResponse[list[VehicleResponse]]:
    """
    Get all vehicles for a specific country.
    
    - **country**: Country code
    - **limit**: Maximum number of results (default: 100, max: 1000)
    """
    try:
        service = VehicleService(session)
        vehicles = await service.get_vehicles_by_country(country, limit)
        return BaseResponse(success=True, data=[VehicleResponse.model_validate(v) for v in vehicles])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vehicles: {str(e)}"
        )


@router.get("/name/{name}", response_model=BaseResponse[VehicleResponse])
async def get_vehicle_by_name(
    name: str,
    session: Session = Depends(get_session)
) -> BaseResponse[VehicleResponse]:
    """
    Get a vehicle by name.
    
    - **name**: Exact name of the vehicle
    """
    try:
        service = VehicleService(session)
        vehicle = await service.get_vehicle_by_name(name)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehicle with name '{name}' not found"
            )
        return BaseResponse(success=True, data=VehicleResponse.model_validate(vehicle))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vehicle: {str(e)}"
        )


@router.get("/{vehicle_id}", response_model=BaseResponse[list[VehicleResponse]])
async def get_vehicle(
    vehicle_id: UUID,
    session: Session = Depends(get_session)
) -> BaseResponse[list[VehicleResponse]]:
    """
    Get vehicle(s) by ID as a list. Returns [] when not found.
    """
    try:
        service = VehicleService(session)
        vehicles = await service.get_vehicles_by_id(vehicle_id)
        return BaseResponse(success=True, data=[VehicleResponse.model_validate(v) for v in vehicles])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vehicle: {str(e)}"
        )


@router.put("/{vehicle_id}", response_model=BaseResponse[VehicleResponse])
async def update_vehicle(
    vehicle_id: UUID,
    vehicle_update: VehicleUpdate,
    session: Session = Depends(get_session)
) -> BaseResponse[VehicleResponse]:
    """
    Update a vehicle.
    
    - **vehicle_id**: UUID of the vehicle to update
    - **body**: Fields to update (all fields are optional)
    """
    try:
        service = VehicleService(session)
        updated_vehicle = await service.update_vehicle(vehicle_id, vehicle_update)
        return BaseResponse(success=True, data=VehicleResponse.model_validate(updated_vehicle))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (BadRequestException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update vehicle: {str(e)}"
        )


@router.delete("/{vehicle_id}", response_model=BaseResponse[None])
async def delete_vehicle(
    vehicle_id: UUID,
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a vehicle.
    
    - **vehicle_id**: UUID of the vehicle to delete
    """
    try:
        service = VehicleService(session)
        await service.delete_vehicle(vehicle_id)
        return BaseResponse(success=True, message="Vehicle deleted")
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete vehicle: {str(e)}"
        )
