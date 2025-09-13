from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.cores.database import get_session
from app.services.driver import DriverService
from app.schemas.base import BaseResponse
from app.schemas.driver import (
    DriverUpdate,
    DriverResponse,
    DriverFilter,
    DriverBulkCreate,
    DriverBulkResponse,
    DriverStatistics
)
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
    InternalServerException
)

router = APIRouter(prefix="/api/v1/drivers", tags=["drivers"])


@router.post("/", response_model=BaseResponse[DriverBulkResponse], status_code=201)
async def create_drivers(
    bulk_data: DriverBulkCreate,
    session: Session = Depends(get_session)
):
    """Bulk create drivers"""
    service = DriverService(session)
    try:
        result = await service.create_drivers(bulk_data)
        return BaseResponse(success=True, data=result)
    except (BadRequestException, ConflictException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=BaseResponse[list[DriverResponse]])
async def list_drivers(
    email: Optional[str] = Query(None, description="Filter by email"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    certification_level: Optional[int] = Query(None, ge=0, le=3, description="Filter by certification level"),
    status: Optional[int] = Query(None, ge=0, le=3, description="Filter by status"),
    employment_type: Optional[int] = Query(None, ge=0, le=3, description="Filter by employment type"),
    department: Optional[str] = Query(None, description="Filter by department"),
    team: Optional[str] = Query(None, description="Filter by team"),
    supervisor_id: Optional[UUID] = Query(None, description="Filter by supervisor ID"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
):
    """List drivers with optional filtering"""
    service = DriverService(session)
    try:
        filters = DriverFilter(
            email=email,
            name=name,
            certification_level=certification_level,
            status=status,
            employment_type=employment_type,
            department=department,
            team=team,
            supervisor_id=supervisor_id,
            offset=offset,
            limit=limit
        )
        drivers, total = await service.list_drivers(filters)
        return BaseResponse(success=True, data=drivers)
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count", response_model=BaseResponse[dict])
async def count_drivers(
    email: Optional[str] = Query(None, description="Filter by email"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    certification_level: Optional[int] = Query(None, ge=0, le=3, description="Filter by certification level"),
    status: Optional[int] = Query(None, ge=0, le=3, description="Filter by status"),
    employment_type: Optional[int] = Query(None, ge=0, le=3, description="Filter by employment type"),
    department: Optional[str] = Query(None, description="Filter by department"),
    team: Optional[str] = Query(None, description="Filter by team"),
    supervisor_id: Optional[UUID] = Query(None, description="Filter by supervisor ID"),
    session: Session = Depends(get_session)
):
    service = DriverService(session)
    try:
        filters = DriverFilter(
            email=email,
            name=name,
            certification_level=certification_level,
            status=status,
            employment_type=employment_type,
            department=department,
            team=team,
            supervisor_id=supervisor_id,
            offset=0,
            limit=1
        )
        total = await service.count_drivers(filters)
        return BaseResponse(success=True, data={"count": total})
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{driver_id}", response_model=BaseResponse[list[DriverResponse]])
async def get_driver(
    driver_id: UUID,
    session: Session = Depends(get_session)
):
    """Get driver(s) by ID as a list. Returns [] when not found."""
    service = DriverService(session)
    try:
        drivers = await service.get_drivers_by_id(driver_id)
        return BaseResponse(success=True, data=drivers)
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{driver_id}", response_model=BaseResponse[DriverResponse])
async def update_driver(
    driver_id: UUID,
    update_data: DriverUpdate,
    session: Session = Depends(get_session)
):
    """Update a driver"""
    service = DriverService(session)
    try:
        driver = await service.update_driver(driver_id, update_data)
        return BaseResponse(success=True, data=driver)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (BadRequestException, ConflictException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{driver_id}", response_model=BaseResponse[None])
async def delete_driver(
    driver_id: UUID,
    session: Session = Depends(get_session)
):
    """Delete a driver"""
    service = DriverService(session)
    try:
        await service.delete_driver(driver_id)
        return BaseResponse(success=True, message="Driver deleted")
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))

 

@router.get("/supervisor/{supervisor_id}/subordinates", response_model=BaseResponse[list[DriverResponse]])
async def get_drivers_by_supervisor(
    supervisor_id: UUID,
    session: Session = Depends(get_session)
):
    """Get all drivers under a specific supervisor"""
    service = DriverService(session)
    try:
        drivers = await service.get_drivers_by_supervisor(supervisor_id)
        return BaseResponse(success=True, data=drivers)
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/overview", response_model=BaseResponse[DriverStatistics])
async def get_driver_statistics(
    session: Session = Depends(get_session)
):
    """Get driver statistics"""
    service = DriverService(session)
    try:
        stats = await service.get_driver_statistics()
        return BaseResponse(success=True, data=stats)
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{driver_id}/update-statistics", response_model=BaseResponse[DriverResponse])
async def update_driver_statistics(
    driver_id: UUID,
    session: Session = Depends(get_session)
):
    """Update driver statistics from measurement data"""
    service = DriverService(session)
    try:
        driver = await service.update_driver_statistics(driver_id)
        return BaseResponse(success=True, data=driver)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))
