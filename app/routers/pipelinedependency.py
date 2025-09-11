from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.cores.database import get_session
from app.schemas.base import BaseResponse
from app.schemas.pipelinedependency import (
    PipelineDependencyUpdate,
    PipelineDependencyResponse,
    PipelineDependencyListResponse,
    PipelineDependencyFilter,
    PipelineDependencyBulkCreate,
    PipelineDependencyDetailResponse
)
from app.services.pipelinedependency import PipelineDependencyService

router = APIRouter(
    prefix="/api/v1/pipelinedependencies",
    tags=["Pipeline Dependencies"]
)


@router.post("/", response_model=BaseResponse[list[PipelineDependencyResponse]], status_code=status.HTTP_201_CREATED)
async def create_pipeline_dependencies(
    bulk_data: PipelineDependencyBulkCreate,
    session: Session = Depends(get_session)
):
    """Bulk create pipeline dependencies"""
    try:
        service = PipelineDependencyService(session)
        dependencies = await service.create_pipeline_dependencies(bulk_data)

        dependency_responses = [
            PipelineDependencyResponse.model_validate(dep) for dep in dependencies
        ]

        return BaseResponse(
            success=True,
            message=f"Successfully created {len(dependencies)} pipeline dependencies",
            data=dependency_responses
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


@router.get("/{dependency_id}", response_model=BaseResponse[list[PipelineDependencyResponse]])
async def get_pipeline_dependency(
    dependency_id: UUID,
    session: Session = Depends(get_session)
):
    """Get pipeline dependency by ID as a list. Returns [] when not found"""
    service = PipelineDependencyService(session)
    dependencies = await service.get_pipeline_dependencies_by_id(dependency_id)
    responses = [PipelineDependencyResponse.model_validate(dep) for dep in dependencies]
    return BaseResponse(
        success=True,
        data=responses
    )


@router.get("/{dependency_id}/detail", response_model=BaseResponse[PipelineDependencyDetailResponse])
async def get_pipeline_dependency_detail(
    dependency_id: UUID,
    session: Session = Depends(get_session)
):
    """Get pipeline dependency with detailed information"""
    service = PipelineDependencyService(session)
    dependency_detail = await service.get_pipeline_dependency_detail(dependency_id)
    
    if not dependency_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline dependency with ID {dependency_id} not found"
        )
    
    return BaseResponse(
        success=True,
        data=dependency_detail
    )


@router.get("/", response_model=BaseResponse[PipelineDependencyListResponse])
async def get_pipeline_dependencies(
    parent_id: Optional[UUID] = Query(None, description="Filter by parent pipeline state ID"),
    child_id: Optional[UUID] = Query(None, description="Filter by child pipeline state ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    session: Session = Depends(get_session)
):
    """Get pipeline dependencies with filtering and pagination"""
    offset = (page - 1) * per_page
    
    filter_params = PipelineDependencyFilter(
        parent_id=parent_id,
        child_id=child_id,
        offset=offset,
        limit=per_page
    )
    
    service = PipelineDependencyService(session)
    dependencies, total = await service.get_pipeline_dependencies(filter_params)
    
    dependency_responses = [
        PipelineDependencyResponse.model_validate(dep) for dep in dependencies
    ]
    
    return BaseResponse(
        success=True,
        data=PipelineDependencyListResponse(
            pipeline_dependencies=dependency_responses,
            total=total,
            page=page,
            per_page=per_page
        )
    )


@router.put("/{dependency_id}", response_model=BaseResponse[PipelineDependencyResponse])
async def update_pipeline_dependency(
    dependency_id: UUID,
    dependency_update: PipelineDependencyUpdate,
    session: Session = Depends(get_session)
):
    """Update pipeline dependency"""
    try:
        service = PipelineDependencyService(session)
        dependency = await service.update_pipeline_dependency(dependency_id, dependency_update)
        
        if not dependency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline dependency with ID {dependency_id} not found"
            )
        
        return BaseResponse(
            success=True,
            message="Pipeline dependency updated successfully",
            data=PipelineDependencyResponse.model_validate(dependency)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{dependency_id}", response_model=BaseResponse[None])
async def delete_pipeline_dependency(
    dependency_id: UUID,
    session: Session = Depends(get_session)
):
    """Delete pipeline dependency"""
    try:
        service = PipelineDependencyService(session)
        deleted = await service.delete_pipeline_dependency(dependency_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline dependency with ID {dependency_id} not found"
            )
        
        return BaseResponse(
            success=True,
            message="Pipeline dependency deleted successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )




# Specialized dependency management endpoints
@router.get("/parent/{parent_id}/children", response_model=BaseResponse[list[PipelineDependencyResponse]])
async def get_dependencies_for_parent(
    parent_id: UUID,
    session: Session = Depends(get_session)
):
    """Get all child dependencies for a parent pipeline state"""
    service = PipelineDependencyService(session)
    dependencies = await service.get_dependencies_for_parent(parent_id)
    
    dependency_responses = [
        PipelineDependencyResponse.model_validate(dep) for dep in dependencies
    ]
    
    return BaseResponse(
        success=True,
        data=dependency_responses,
        message=f"Retrieved {len(dependency_responses)} child dependencies for parent {parent_id}"
    )


@router.get("/child/{child_id}/parents", response_model=BaseResponse[list[PipelineDependencyResponse]])
async def get_dependencies_for_child(
    child_id: UUID,
    session: Session = Depends(get_session)
):
    """Get all parent dependencies for a child pipeline state"""
    service = PipelineDependencyService(session)
    dependencies = await service.get_dependencies_for_child(child_id)
    
    dependency_responses = [
        PipelineDependencyResponse.model_validate(dep) for dep in dependencies
    ]
    
    return BaseResponse(
        success=True,
        data=dependency_responses,
        message=f"Retrieved {len(dependency_responses)} parent dependencies for child {child_id}"
    )


@router.get("/chain/{pipeline_state_id}", response_model=BaseResponse[list[PipelineDependencyResponse]])
async def get_dependency_chain(
    pipeline_state_id: UUID,
    session: Session = Depends(get_session)
):
    """Get full dependency chain for a pipeline state (both parents and children)"""
    service = PipelineDependencyService(session)
    chain_dependencies = await service.get_dependency_chain(pipeline_state_id)
    
    dependency_responses = [
        PipelineDependencyResponse.model_validate(dep) for dep in chain_dependencies
    ]
    
    return BaseResponse(
        success=True,
        data=dependency_responses,
        message=f"Retrieved {len(dependency_responses)} dependencies in chain for pipeline state {pipeline_state_id}"
    )
