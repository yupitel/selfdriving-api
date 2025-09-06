from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlmodel import Session

from app.cores.database import get_session
from app.schemas.pipeline import (
    PipelineUpdate,
    PipelineResponse,
    PipelineFilter,
    PipelineBulkCreate,
    PipelineBulkResponse,
    PipelineStatistics
)
from app.services.pipeline import PipelineService
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
    InternalServerException
)

router = APIRouter(
    prefix="/api/v1/pipelines",
    tags=["pipelines"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        409: {"description": "Conflict"},
        500: {"description": "Internal server error"}
    }
)


@router.post("/", response_model=PipelineBulkResponse, status_code=status.HTTP_201_CREATED)
async def create_pipelines(
    bulk_data: PipelineBulkCreate,
    session: Session = Depends(get_session)
) -> PipelineBulkResponse:
    """
    Bulk create pipelines.

    - **pipelines**: List of pipelines to create (max 1000)

    Returns:
    - **created**: Number of successfully created pipelines
    - **failed**: Number of failed creations
    - **ids**: List of created pipeline IDs
    - **errors**: List of error details for failed creations
    """
    try:
        service = PipelineService(session)
        result = await service.bulk_create_pipelines(bulk_data)
        return PipelineBulkResponse(**result)
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk create pipelines: {str(e)}"
        )


@router.get("/", response_model=List[PipelineResponse])
async def list_pipelines(
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    type: Optional[int] = Query(None, ge=0, le=32767, description="Filter by type"),
    group: Optional[int] = Query(None, ge=0, le=32767, description="Filter by group"),
    is_available: Optional[int] = Query(None, ge=0, le=1, description="Filter by availability"),
    version: Optional[int] = Query(None, ge=0, le=32767, description="Filter by exact version"),
    min_version: Optional[int] = Query(None, ge=0, le=32767, description="Filter by minimum version"),
    max_version: Optional[int] = Query(None, ge=0, le=32767, description="Filter by maximum version"),
    start_time: Optional[str] = Query(None, description="Filter by creation time (after)"),
    end_time: Optional[str] = Query(None, description="Filter by creation time (before)"),
    limit: int = Query(100, gt=0, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    session: Session = Depends(get_session)
) -> List[PipelineResponse]:
    """
    List pipelines with optional filters.
    
    Query parameters:
    - **name**: Filter by name (partial match)
    - **type**: Filter by pipeline type
    - **group**: Filter by pipeline group
    - **is_available**: Filter by availability (0=unavailable, 1=available)
    - **version**: Filter by exact version
    - **min_version**: Filter by minimum version
    - **max_version**: Filter by maximum version
    - **start_time**: Filter by creation time (after)
    - **end_time**: Filter by creation time (before)
    - **limit**: Maximum number of results (default: 100, max: 1000)
    - **offset**: Number of results to skip (default: 0)
    """
    try:
        # Build filter object
        filters = PipelineFilter(
            name=name,
            type=type,
            group=group,
            is_available=is_available,
            version=version,
            min_version=min_version,
            max_version=max_version,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset
        )
        
        service = PipelineService(session)
        pipelines = await service.list_pipelines(filters)
        return [PipelineResponse.model_validate(p) for p in pipelines]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list pipelines: {str(e)}"
        )


@router.get("/statistics", response_model=PipelineStatistics)
async def get_pipeline_statistics(
    session: Session = Depends(get_session)
) -> PipelineStatistics:
    """
    Get statistics about pipelines.
    
    Returns:
    - **total**: Total number of pipelines
    - **by_type**: Count of pipelines by type
    - **by_group**: Count of pipelines by group
    - **available**: Count of available pipelines
    - **unavailable**: Count of unavailable pipelines
    - **by_version**: Count of pipelines by version
    """
    try:
        service = PipelineService(session)
        stats = await service.get_pipeline_statistics()
        return PipelineStatistics(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/available", response_model=List[PipelineResponse])
async def get_available_pipelines(
    limit: int = Query(100, gt=0, le=1000, description="Maximum number of results"),
    session: Session = Depends(get_session)
) -> List[PipelineResponse]:
    """
    Get all available pipelines.
    
    - **limit**: Maximum number of results (default: 100, max: 1000)
    """
    try:
        service = PipelineService(session)
        pipelines = await service.get_available_pipelines(limit)
        return [PipelineResponse.model_validate(p) for p in pipelines]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pipelines: {str(e)}"
        )


@router.get("/type/{type_value}", response_model=List[PipelineResponse])
async def get_pipelines_by_type(
    type_value: int,
    limit: int = Query(100, gt=0, le=1000, description="Maximum number of results"),
    session: Session = Depends(get_session)
) -> List[PipelineResponse]:
    """
    Get all pipelines for a specific type.
    
    - **type_value**: Pipeline type value
    - **limit**: Maximum number of results (default: 100, max: 1000)
    """
    try:
        service = PipelineService(session)
        pipelines = await service.get_pipelines_by_type(type_value, limit)
        return [PipelineResponse.model_validate(p) for p in pipelines]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pipelines: {str(e)}"
        )


@router.get("/group/{group}", response_model=List[PipelineResponse])
async def get_pipelines_by_group(
    group: int,
    limit: int = Query(100, gt=0, le=1000, description="Maximum number of results"),
    session: Session = Depends(get_session)
) -> List[PipelineResponse]:
    """
    Get all pipelines for a specific group.
    
    - **group**: Pipeline group value
    - **limit**: Maximum number of results (default: 100, max: 1000)
    """
    try:
        service = PipelineService(session)
        pipelines = await service.get_pipelines_by_group(group, limit)
        return [PipelineResponse.model_validate(p) for p in pipelines]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pipelines: {str(e)}"
        )


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: UUID,
    session: Session = Depends(get_session)
) -> PipelineResponse:
    """
    Get a specific pipeline by ID.
    
    - **pipeline_id**: UUID of the pipeline
    """
    try:
        service = PipelineService(session)
        pipeline = await service.get_pipeline(pipeline_id)
        return PipelineResponse.model_validate(pipeline)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pipeline: {str(e)}"
        )


@router.put("/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: UUID,
    pipeline_update: PipelineUpdate,
    session: Session = Depends(get_session)
) -> PipelineResponse:
    """
    Update a pipeline.
    
    - **pipeline_id**: UUID of the pipeline to update
    - **body**: Fields to update (all fields are optional)
    """
    try:
        service = PipelineService(session)
        updated_pipeline = await service.update_pipeline(pipeline_id, pipeline_update)
        return PipelineResponse.model_validate(updated_pipeline)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (BadRequestException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update pipeline: {str(e)}"
        )


@router.delete("/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline(
    pipeline_id: UUID,
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a pipeline.
    
    - **pipeline_id**: UUID of the pipeline to delete
    """
    try:
        service = PipelineService(session)
        await service.delete_pipeline(pipeline_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete pipeline: {str(e)}"
        )




@router.post("/{pipeline_id}/execute", response_model=Dict[str, Any])
async def execute_pipeline(
    pipeline_id: UUID,
    input_params: Dict[str, Any] = Body(..., description="Input parameters for pipeline execution"),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Execute a pipeline with given parameters.
    
    This is a placeholder endpoint for pipeline execution logic.
    In a real implementation, this would trigger actual pipeline processing.
    
    - **pipeline_id**: UUID of the pipeline to execute
    - **input_params**: Input parameters for the pipeline
    
    Returns:
    - Execution result (mock response for now)
    """
    try:
        service = PipelineService(session)
        result = await service.execute_pipeline(pipeline_id, input_params)
        return result
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute pipeline: {str(e)}"
        )
