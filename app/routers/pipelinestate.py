from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.cores.database import get_session
from app.schemas.base import BaseResponse
from app.schemas.pipelinestate import (
    PipelineStateUpdate,
    PipelineStateResponse,
    PipelineStateListResponse,
    PipelineStateFilter,
    PipelineStateBulkCreate,
    PipelineStateDetailResponse
)
from app.services.pipelinestate import PipelineStateService

router = APIRouter(
    prefix="/api/v1/pipelinestates",
    tags=["Pipeline States"]
)


@router.post("/", response_model=BaseResponse[list[PipelineStateResponse]], status_code=status.HTTP_201_CREATED)
async def create_pipeline_states(
    bulk_data: PipelineStateBulkCreate,
    session: Session = Depends(get_session)
):
    """Bulk create pipeline state entries"""
    try:
        service = PipelineStateService(session)
        pipeline_state_entries = await service.create_pipeline_states(bulk_data)

        pipeline_state_responses = [
            PipelineStateResponse.model_validate(ps) for ps in pipeline_state_entries
        ]

        return BaseResponse(
            success=True,
            message=f"Successfully created {len(pipeline_state_entries)} pipeline state entries",
            data=pipeline_state_responses
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


@router.get("/{pipeline_state_id}", response_model=BaseResponse[list[PipelineStateResponse]])
async def get_pipeline_state(
    pipeline_state_id: UUID,
    session: Session = Depends(get_session)
):
    """Get pipeline state by ID as a list. Returns [] when not found"""
    service = PipelineStateService(session)
    pipeline_states = await service.get_pipeline_states_by_id(pipeline_state_id)
    responses = [PipelineStateResponse.model_validate(ps) for ps in pipeline_states]
    return BaseResponse(
        success=True,
        data=responses
    )


@router.get("/{pipeline_state_id}/detail", response_model=BaseResponse[PipelineStateDetailResponse])
async def get_pipeline_state_detail(
    pipeline_state_id: UUID,
    session: Session = Depends(get_session)
):
    """Get pipeline state with detailed information"""
    service = PipelineStateService(session)
    pipeline_state_detail = await service.get_pipeline_state_detail(pipeline_state_id)
    
    if not pipeline_state_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline state with ID {pipeline_state_id} not found"
        )
    
    return BaseResponse(
        success=True,
        data=pipeline_state_detail
    )


@router.get("/", response_model=BaseResponse[PipelineStateListResponse])
async def get_pipeline_states(
    pipeline_data_id: Optional[UUID] = Query(None, description="Filter by pipeline data ID"),
    pipeline_id: Optional[UUID] = Query(None, description="Filter by pipeline ID"),
    state: Optional[int] = Query(None, description="Filter by state"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    session: Session = Depends(get_session)
):
    """Get pipeline states with filtering and pagination"""
    offset = (page - 1) * per_page
    
    filter_params = PipelineStateFilter(
        pipeline_data_id=pipeline_data_id,
        pipeline_id=pipeline_id,
        state=state,
        offset=offset,
        limit=per_page
    )
    
    service = PipelineStateService(session)
    pipeline_states, total = await service.get_pipeline_states(filter_params)
    
    pipeline_state_responses = [
        PipelineStateResponse.model_validate(ps) for ps in pipeline_states
    ]
    
    return BaseResponse(
        success=True,
        data=PipelineStateListResponse(
            pipeline_states=pipeline_state_responses,
            total=total,
            page=page,
            per_page=per_page
        )
    )


@router.put("/{pipeline_state_id}", response_model=BaseResponse[PipelineStateResponse])
async def update_pipeline_state(
    pipeline_state_id: UUID,
    pipeline_state_update: PipelineStateUpdate,
    session: Session = Depends(get_session)
):
    """Update pipeline state"""
    try:
        service = PipelineStateService(session)
        pipeline_state = await service.update_pipeline_state(pipeline_state_id, pipeline_state_update)
        
        if not pipeline_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline state with ID {pipeline_state_id} not found"
            )
        
        return BaseResponse(
            success=True,
            message="Pipeline state updated successfully",
            data=PipelineStateResponse.model_validate(pipeline_state)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{pipeline_state_id}", response_model=BaseResponse[None])
async def delete_pipeline_state(
    pipeline_state_id: UUID,
    session: Session = Depends(get_session)
):
    """Delete pipeline state"""
    try:
        service = PipelineStateService(session)
        deleted = await service.delete_pipeline_state(pipeline_state_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline state with ID {pipeline_state_id} not found"
            )
        
        return BaseResponse(
            success=True,
            message="Pipeline state deleted successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )




# Job-specific endpoints for managing pipeline states as jobs
@router.get("/jobs/by-pipeline-data/{pipeline_data_id}", response_model=BaseResponse[list[PipelineStateResponse]])
async def get_jobs_by_pipeline_data(
    pipeline_data_id: UUID,
    session: Session = Depends(get_session)
):
    """Get all jobs (pipeline states) for a specific pipeline data"""
    service = PipelineStateService(session)
    job_states = await service.get_job_states_for_pipeline_data(pipeline_data_id)
    
    job_responses = [
        PipelineStateResponse.model_validate(js) for js in job_states
    ]
    
    return BaseResponse(
        success=True,
        data=job_responses,
        message=f"Retrieved {len(job_responses)} jobs for pipeline data {pipeline_data_id}"
    )
