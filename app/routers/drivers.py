from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.cores.database import get_session
from app.services.driver import DriverService
from app.schemas.driver import (
    DriverCreate,
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


@router.post("/", response_model=DriverResponse, status_code=201)
async def create_driver(
    driver_data: DriverCreate,
    session: Session = Depends(get_session)
):
    """Create a new driver"""
    service = DriverService(session)
    try:
        driver = await service.create_driver(driver_data)
        return driver
    except (BadRequestException, ConflictException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[DriverResponse])
async def list_drivers(
    driver_code: str = Query(None, description="Filter by driver code"),
    email: str = Query(None, description="Filter by email"),
    name: str = Query(None, description="Filter by name (partial match)"),
    certification_level: int = Query(None, ge=0, le=3, description="Filter by certification level"),
    status: int = Query(None, ge=0, le=3, description="Filter by status"),
    employment_type: int = Query(None, ge=0, le=3, description="Filter by employment type"),
    department: str = Query(None, description="Filter by department"),
    team: str = Query(None, description="Filter by team"),
    supervisor_id: UUID = Query(None, description="Filter by supervisor ID"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
):
    """List drivers with optional filtering"""
    service = DriverService(session)
    try:
        filters = DriverFilter(
            driver_code=driver_code,
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
        return drivers
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(
    driver_id: UUID,
    session: Session = Depends(get_session)
):
    """Get a specific driver by ID"""
    service = DriverService(session)
    try:
        driver = await service.get_driver(driver_id)
        return driver
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{driver_id}", response_model=DriverResponse)
async def update_driver(
    driver_id: UUID,
    update_data: DriverUpdate,
    session: Session = Depends(get_session)
):
    """Update a driver"""
    service = DriverService(session)
    try:
        driver = await service.update_driver(driver_id, update_data)
        return driver
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (BadRequestException, ConflictException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{driver_id}", status_code=204)
async def delete_driver(
    driver_id: UUID,
    session: Session = Depends(get_session)
):
    """Delete a driver"""
    service = DriverService(session)
    try:
        await service.delete_driver(driver_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk", response_model=DriverBulkResponse)
async def bulk_create_drivers(
    bulk_data: DriverBulkCreate,
    session: Session = Depends(get_session)
):
    """Bulk create drivers"""
    service = DriverService(session)
    try:
        result = await service.bulk_create_drivers(bulk_data)
        return result
    except BadRequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/code/{driver_code}", response_model=DriverResponse)
async def get_driver_by_code(
    driver_code: str,
    session: Session = Depends(get_session)
):
    """Get a driver by driver code"""
    service = DriverService(session)
    try:
        driver = await service.get_driver_by_code(driver_code)
        if not driver:
            raise NotFoundException(f"Driver with code '{driver_code}' not found")
        return driver
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supervisor/{supervisor_id}/subordinates", response_model=List[DriverResponse])
async def get_drivers_by_supervisor(
    supervisor_id: UUID,
    session: Session = Depends(get_session)
):
    """Get all drivers under a specific supervisor"""
    service = DriverService(session)
    try:
        drivers = await service.get_drivers_by_supervisor(supervisor_id)
        return drivers
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/overview", response_model=DriverStatistics)
async def get_driver_statistics(
    session: Session = Depends(get_session)
):
    """Get driver statistics"""
    service = DriverService(session)
    try:
        stats = await service.get_driver_statistics()
        return stats
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{driver_id}/update-statistics", response_model=DriverResponse)
async def update_driver_statistics(
    driver_id: UUID,
    session: Session = Depends(get_session)
):
    """Update driver statistics from measurement data"""
    service = DriverService(session)
    try:
        driver = await service.update_driver_statistics(driver_id)
        return driver
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InternalServerException as e:
        raise HTTPException(status_code=500, detail=str(e))