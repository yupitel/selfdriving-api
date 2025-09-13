from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.cores.database import get_session
from app.schemas.base import BaseResponse
from app.schemas.datastream import (
    DataStreamUpdate,
    DataStreamResponse,
    DataStreamFilter,
    DataStreamBulkCreate,
    DataStreamBulkResponse
)
from app.services.datastream import DataStreamService
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
    InternalServerException
)

router = APIRouter(
    prefix="/api/v1/datastreams",
    tags=["datastreams"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        409: {"description": "Conflict"},
        500: {"description": "Internal server error"}
    }
)


@router.post("/", response_model=BaseResponse[DataStreamBulkResponse], status_code=status.HTTP_201_CREATED)
async def create_datastreams(
    bulk_data: DataStreamBulkCreate,
    session: Session = Depends(get_session)
) -> BaseResponse[DataStreamBulkResponse]:
    """
    Bulk create datastreams.

    - **datastreams**: List of datastreams to create (max 1000)

    Returns:
    - **created**: Number of successfully created datastreams
    - **failed**: Number of failed creations
    - **ids**: List of created datastream IDs
    - **errors**: List of error details for failed creations
    """
    try:
        service = DataStreamService(session)
        result = await service.create_datastreams(bulk_data)
        return BaseResponse(success=True, data=DataStreamBulkResponse(**result))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk create datastreams: {str(e)}"
        )


@router.get("/", response_model=BaseResponse[list[DataStreamResponse]])
async def list_datastreams(
    type: Optional[int] = Query(None, ge=0, le=32767, description="Filter by type"),
    measurement_id: Optional[UUID] = Query(None, description="Filter by measurement ID"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    data_path: Optional[str] = Query(None, description="Filter by data path (partial match)"),
    src_path: Optional[str] = Query(None, description="Filter by source path (partial match)"),
    start_time: Optional[str] = Query(None, description="Filter by creation time (after)"),
    end_time: Optional[str] = Query(None, description="Filter by creation time (before)"),
    limit: int = Query(100, gt=0, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    session: Session = Depends(get_session)
) -> BaseResponse[list[DataStreamResponse]]:
    """
    List datastreams with optional filters.
    
    Query parameters:
    - **type**: Filter by datastream type
    - **measurement_id**: Filter by measurement ID
    - **name**: Filter by name (partial match)
    - **data_path**: Filter by data path (partial match)
    - **src_path**: Filter by source path (partial match)
    - **start_time**: Filter by creation time (after)
    - **end_time**: Filter by creation time (before)
    - **limit**: Maximum number of results (default: 100, max: 1000)
    - **offset**: Number of results to skip (default: 0)
    """
    try:
        # Build filter object
        filters = DataStreamFilter(
            type=type,
            measurement_id=measurement_id,
            name=name,
            data_path=data_path,
            src_path=src_path,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset
        )
        
        service = DataStreamService(session)
        datastreams = await service.list_datastreams(filters)
        return BaseResponse(success=True, data=[DataStreamResponse.model_validate(ds) for ds in datastreams])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list datastreams: {str(e)}"
        )


@router.get("/statistics", response_model=BaseResponse[dict])
async def get_datastream_statistics(
    session: Session = Depends(get_session)
) -> BaseResponse[dict]:
    """
    Get statistics about datastreams.
    
    Returns:
    - **total**: Total number of datastreams
    - **by_type**: Count of datastreams by type
    - **with_data_path**: Count of datastreams with data_path
    - **with_src_path**: Count of datastreams with src_path
    """
    try:
        service = DataStreamService(session)
        stats = await service.get_datastream_statistics()
        return BaseResponse(success=True, data=stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/count", response_model=BaseResponse[dict])
async def count_datastreams(
    type: Optional[int] = Query(None, ge=0, le=32767, description="Filter by type"),
    measurement_id: Optional[UUID] = Query(None, description="Filter by measurement ID"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    data_path: Optional[str] = Query(None, description="Filter by data path (partial match)"),
    src_path: Optional[str] = Query(None, description="Filter by source path (partial match)"),
    start_time: Optional[str] = Query(None, description="Filter by creation time (after)"),
    end_time: Optional[str] = Query(None, description="Filter by creation time (before)"),
    session: Session = Depends(get_session)
) -> BaseResponse[dict]:
    """
    Return count of datastreams matching filters.
    Accepts same filters as list endpoint (excluding pagination).
    """
    try:
        filters = DataStreamFilter(
            type=type,
            measurement_id=measurement_id,
            name=name,
            data_path=data_path,
            src_path=src_path,
            start_time=start_time,
            end_time=end_time,
            limit=1,
            offset=0,
        )
        service = DataStreamService(session)
        total = await service.count_datastreams(filters)
        return BaseResponse(success=True, data={"count": total})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to count datastreams: {str(e)}"
        )


@router.get("/measurement/{measurement_id}", response_model=BaseResponse[list[DataStreamResponse]])
async def get_datastreams_by_measurement(
    measurement_id: UUID,
    limit: int = Query(100, gt=0, le=1000, description="Maximum number of results"),
    session: Session = Depends(get_session)
) -> BaseResponse[list[DataStreamResponse]]:
    """
    Get all datastreams for a specific measurement.
    
    - **measurement_id**: UUID of the measurement
    - **limit**: Maximum number of results (default: 100, max: 1000)
    """
    try:
        service = DataStreamService(session)
        datastreams = await service.get_datastreams_by_measurement(measurement_id, limit)
        return BaseResponse(success=True, data=[DataStreamResponse.model_validate(ds) for ds in datastreams])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get datastreams: {str(e)}"
        )


@router.get("/{datastream_id}", response_model=BaseResponse[list[DataStreamResponse]])
async def get_datastream(
    datastream_id: UUID,
    session: Session = Depends(get_session)
) -> BaseResponse[list[DataStreamResponse]]:
    """
    Get datastream(s) by ID as a list.
    - Returns [] when not found (200 OK).
    """
    try:
        service = DataStreamService(session)
        datastreams = await service.get_datastreams_by_id(datastream_id)
        return BaseResponse(success=True, data=[DataStreamResponse.model_validate(ds) for ds in datastreams])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get datastream: {str(e)}"
        )


@router.put("/{datastream_id}", response_model=BaseResponse[DataStreamResponse])
async def update_datastream(
    datastream_id: UUID,
    datastream_update: DataStreamUpdate,
    session: Session = Depends(get_session)
) -> BaseResponse[DataStreamResponse]:
    """
    Update a datastream.
    
    - **datastream_id**: UUID of the datastream to update
    - **body**: Fields to update (all fields are optional)
    """
    try:
        service = DataStreamService(session)
        updated_datastream = await service.update_datastream(datastream_id, datastream_update)
        return BaseResponse(success=True, data=DataStreamResponse.model_validate(updated_datastream))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (BadRequestException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update datastream: {str(e)}"
        )


@router.delete("/{datastream_id}", response_model=BaseResponse[None])
async def delete_datastream(
    datastream_id: UUID,
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a datastream.
    
    - **datastream_id**: UUID of the datastream to delete
    """
    try:
        service = DataStreamService(session)
        await service.delete_datastream(datastream_id)
        return BaseResponse(success=True, message="Datastream deleted")
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete datastream: {str(e)}"
        )
