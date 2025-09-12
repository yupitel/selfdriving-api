from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.cores.database import get_session
from app.schemas.base import BaseResponse
from app.schemas.measurement import (
    MeasurementUpdate,
    MeasurementResponse,
    MeasurementFilter,
    MeasurementBulkCreate,
    MeasurementDetailResponse
)
from app.services.measurement import MeasurementService

router = APIRouter(
    prefix="/api/v1/measurements",
    tags=["Measurements"]
)


@router.post("/", response_model=BaseResponse[list[MeasurementResponse]], status_code=status.HTTP_201_CREATED)
async def create_measurements(
    bulk_data: MeasurementBulkCreate,
    session: Session = Depends(get_session)
):
    """Bulk create measurements"""
    try:
        service = MeasurementService(session)
        measurements = await service.create_measurements(bulk_data)

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


@router.get("/{measurement_id}", response_model=BaseResponse[list[MeasurementResponse]])
async def get_measurement(
    measurement_id: UUID,
    session: Session = Depends(get_session)
):
    """Get measurement(s) by ID as a list. Returns [] when not found"""
    service = MeasurementService(session)
    measurements = await service.get_measurements_by_id(measurement_id)
    measurement_responses = [MeasurementResponse.model_validate(m) for m in measurements]
    return BaseResponse(
        success=True,
        data=measurement_responses
    )


@router.get("/{measurement_id}/detail", response_model=BaseResponse[MeasurementDetailResponse])
async def get_measurement_detail(
    measurement_id: UUID,
    session: Session = Depends(get_session)
):
    """Get measurement with detailed datastream information"""
    service = MeasurementService(session)
    measurement_detail = await service.get_measurement_detail(measurement_id)
    
    if not measurement_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement with ID {measurement_id} not found"
        )
    
    return BaseResponse(
        success=True,
        data=measurement_detail
    )


@router.get("/", response_model=BaseResponse[list[MeasurementResponse]])
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
    offset = (page - 1) * per_page
    
    filter_params = MeasurementFilter(
        vehicle_id=vehicle_id,
        area_id=area_id,
        start_time=start_time,
        end_time=end_time,
        offset=offset,
        limit=per_page
    )
    
    service = MeasurementService(session)
    measurements, total = await service.get_measurements(filter_params)
    
    measurement_responses = [
        MeasurementResponse.model_validate(m) for m in measurements
    ]
    
    return BaseResponse(
        success=True,
        data=measurement_responses
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
