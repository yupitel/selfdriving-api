from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.cores.database import get_session
from app.schemas.base import BaseResponse
from app.schemas.pipelinedata import (
    PipelineDataUpdate,
    PipelineDataResponse,
    PipelineDataListResponse,
    PipelineDataFilter,
    PipelineDataBulkCreate
)
from app.services.pipelinedata import PipelineDataService

router = APIRouter(
    prefix="/api/v1/pipelinedata",
    tags=["Pipeline Data"]
)


@router.post("/", response_model=BaseResponse[list[PipelineDataResponse]], status_code=status.HTTP_201_CREATED)
async def create_pipeline_data(
    bulk_data: PipelineDataBulkCreate,
    session: Session = Depends(get_session)
):
    """Bulk create pipeline data entries"""
    try:
        service = PipelineDataService(session)
        pipeline_data_entries = await service.bulk_create_pipeline_data(bulk_data)

        pipeline_data_responses = [
            PipelineDataResponse.model_validate(pd) for pd in pipeline_data_entries
        ]

        return BaseResponse(
            success=True,
            message=f"Successfully created {len(pipeline_data_entries)} pipeline data entries",
            data=pipeline_data_responses
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


@router.get("/{pipeline_data_id}", response_model=BaseResponse[PipelineDataResponse])
async def get_pipeline_data(
    pipeline_data_id: UUID,
    session: Session = Depends(get_session)
):
    """Get pipeline data by ID"""
    service = PipelineDataService(session)
    pipeline_data = await service.get_pipeline_data(pipeline_data_id)
    
    if not pipeline_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline data with ID {pipeline_data_id} not found"
        )
    
    return BaseResponse(
        success=True,
        data=PipelineDataResponse.model_validate(pipeline_data)
    )


@router.get("/", response_model=PipelineDataListResponse)
async def get_pipeline_data_list(
    type: Optional[int] = Query(None, description="Filter by type"),
    datastream_id: Optional[UUID] = Query(None, description="Filter by datastream ID"),
    scene_id: Optional[UUID] = Query(None, description="Filter by scene ID"),
    source: Optional[str] = Query(None, description="Filter by source"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    session: Session = Depends(get_session)
):
    """Get pipeline data list with filtering and pagination"""
    offset = (page - 1) * per_page
    
    filter_params = PipelineDataFilter(
        type=type,
        datastream_id=datastream_id,
        scene_id=scene_id,
        source=source,
        offset=offset,
        limit=per_page
    )
    
    service = PipelineDataService(session)
    pipeline_data_list, total = await service.get_pipeline_data_list(filter_params)
    
    pipeline_data_responses = [
        PipelineDataResponse.model_validate(pd) for pd in pipeline_data_list
    ]
    
    return PipelineDataListResponse(
        pipeline_data=pipeline_data_responses,
        total=total,
        page=page,
        per_page=per_page
    )


@router.put("/{pipeline_data_id}", response_model=BaseResponse[PipelineDataResponse])
async def update_pipeline_data(
    pipeline_data_id: UUID,
    pipeline_data_update: PipelineDataUpdate,
    session: Session = Depends(get_session)
):
    """Update pipeline data"""
    try:
        service = PipelineDataService(session)
        pipeline_data = await service.update_pipeline_data(pipeline_data_id, pipeline_data_update)
        
        if not pipeline_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline data with ID {pipeline_data_id} not found"
            )
        
        return BaseResponse(
            success=True,
            message="Pipeline data updated successfully",
            data=PipelineDataResponse.model_validate(pipeline_data)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{pipeline_data_id}", response_model=BaseResponse[None])
async def delete_pipeline_data(
    pipeline_data_id: UUID,
    session: Session = Depends(get_session)
):
    """Delete pipeline data"""
    try:
        service = PipelineDataService(session)
        deleted = await service.delete_pipeline_data(pipeline_data_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline data with ID {pipeline_data_id} not found"
            )
        
        return BaseResponse(
            success=True,
            message="Pipeline data deleted successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

