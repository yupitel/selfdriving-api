from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.cores.database import get_session
from app.schemas.base import BaseResponse, PaginatedResponse
from app.schemas.measurement import (
    MeasurementCreate,
    MeasurementUpdate,
    MeasurementResponse,
    MeasurementListResponse,
    MeasurementFilter,
    MeasurementBulkCreate
)
from app.services.measurement import MeasurementService

router = APIRouter(
    prefix="/api/v1/measurements",
    tags=["Measurements"]
)


@router.post("/", response_model=BaseResponse[MeasurementResponse], status_code=status.HTTP_201_CREATED)
async def create_measurement(
    measurement_data: MeasurementCreate,
    session: Session = Depends(get_session)
):
    """Create a new measurement"""
    try:
        service = MeasurementService(session)
        measurement = await service.create_measurement(measurement_data)
        
        return BaseResponse(
            success=True,
            message="Measurement created successfully",
            data=MeasurementResponse.model_validate(measurement)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{measurement_id}", response_model=BaseResponse[MeasurementResponse])
async def get_measurement(
    measurement_id: UUID,
    session: Session = Depends(get_session)
):
    """Get measurement by ID"""
    service = MeasurementService(session)
    measurement = await service.get_measurement(measurement_id)
    
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement with ID {measurement_id} not found"
        )
    
    return BaseResponse(
        success=True,
        data=MeasurementResponse.model_validate(measurement)
    )


@router.get("/", response_model=MeasurementListResponse)
async def get_measurements(
    vehicle_id: Optional[UUID] = Query(None, description="Filter by vehicle ID"),
    area_id: Optional[UUID] = Query(None, description="Filter by area ID"),
    start_time: Optional[datetime] = Query(None, description="Filter by start time"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    session: Session = Depends(get_session)
):
    """Get measurements with filtering and pagination"""
    filter_params = MeasurementFilter(
        vehicle_id=vehicle_id,
        area_id=area_id,
        start_time=start_time,
        end_time=end_time
    )
    
    skip = (page - 1) * per_page
    
    service = MeasurementService(session)
    measurements, total = await service.get_measurements(
        filter_params=filter_params,
        skip=skip,
        limit=per_page
    )
    
    measurement_responses = [
        MeasurementResponse.model_validate(m) for m in measurements
    ]
    
    return MeasurementListResponse(
        measurements=measurement_responses,
        total=total,
        page=page,
        per_page=per_page
    )


@router.put("/{measurement_id}", response_model=BaseResponse[MeasurementResponse])
async def update_measurement(
    measurement_id: UUID,
    measurement_update: MeasurementUpdate,
    session: Session = Depends(get_session)
):
    """Update measurement"""
    try:
        service = MeasurementService(session)
        measurement = await service.update_measurement(measurement_id, measurement_update)
        
        if not measurement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Measurement with ID {measurement_id} not found"
            )
        
        return BaseResponse(
            success=True,
            message="Measurement updated successfully",
            data=MeasurementResponse.model_validate(measurement)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{measurement_id}", response_model=BaseResponse[None])
async def delete_measurement(
    measurement_id: UUID,
    session: Session = Depends(get_session)
):
    """Delete measurement"""
    try:
        service = MeasurementService(session)
        deleted = await service.delete_measurement(measurement_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Measurement with ID {measurement_id} not found"
            )
        
        return BaseResponse(
            success=True,
            message="Measurement deleted successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/bulk", response_model=BaseResponse[list[MeasurementResponse]], status_code=status.HTTP_201_CREATED)
async def bulk_create_measurements(
    bulk_data: MeasurementBulkCreate,
    session: Session = Depends(get_session)
):
    """Bulk create measurements"""
    try:
        service = MeasurementService(session)
        measurements = await service.bulk_create_measurements(bulk_data)
        
        measurement_responses = [
            MeasurementResponse.model_validate(m) for m in measurements
        ]
        
        return BaseResponse(
            success=True,
            message=f"Successfully created {len(measurements)} measurements",
            data=measurement_responses
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )