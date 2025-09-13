import logging
import json
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlmodel import Session, select, and_, or_
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.pipeline import PipelineModel
from app.schemas.pipeline import (
    PipelineUpdate,
    PipelineFilter,
    PipelineBulkCreate,
    PipelineTypeEnum
)
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
    InternalServerException
)
from app.cores.config import BULK_INSERT_MAX_NUM

logger = logging.getLogger(__name__)


class PipelineService:
    """Service class for Pipeline operations"""
    
    def __init__(self, db_session: Session):
        self.session = db_session
    
    # Note: Single create is removed in favor of bulk-at-root API usage.
    
    async def get_pipeline(self, pipeline_id: UUID) -> PipelineModel:
        """Get a pipeline by ID"""
        try:
            statement = select(PipelineModel).where(PipelineModel.id == pipeline_id)
            pipeline = self.session.exec(statement).first()
            
            if not pipeline:
                raise NotFoundException(f"Pipeline with ID {pipeline_id} not found")
            
            return pipeline
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching pipeline {pipeline_id}: {str(e)}")
            raise InternalServerException(f"Failed to fetch pipeline: {str(e)}")

    async def get_pipelines_by_id(self, pipeline_id: UUID) -> List[PipelineModel]:
        """Get pipeline(s) by ID as a list (0 or 1 items)."""
        try:
            statement = select(PipelineModel).where(PipelineModel.id == pipeline_id)
            pipelines = self.session.exec(statement).all()
            return list(pipelines)
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching pipeline list {pipeline_id}: {str(e)}")
            raise InternalServerException(f"Failed to fetch pipelines: {str(e)}")
    
    async def list_pipelines(self, filters: PipelineFilter) -> List[PipelineModel]:
        """List pipelines with optional filters"""
        try:
            statement = select(PipelineModel)
            
            # Build filter conditions
            conditions = []
            
            if filters.name:
                conditions.append(PipelineModel.name.contains(filters.name))
            
            if filters.type is not None:
                conditions.append(PipelineModel.type == filters.type)
            
            if filters.group is not None:
                conditions.append(PipelineModel.group == filters.group)
            
            if filters.is_available is not None:
                conditions.append(PipelineModel.is_available == filters.is_available)
            
            if filters.version is not None:
                conditions.append(PipelineModel.version == filters.version)
            
            if filters.min_version is not None:
                conditions.append(PipelineModel.version >= filters.min_version)
            
            if filters.max_version is not None:
                conditions.append(PipelineModel.version <= filters.max_version)
            
            if filters.start_time:
                conditions.append(PipelineModel.created_at >= filters.start_time)
            
            if filters.end_time:
                conditions.append(PipelineModel.created_at <= filters.end_time)
            
            # Apply filters
            if conditions:
                statement = statement.where(and_(*conditions))
            
            # Apply ordering and pagination
            statement = statement.order_by(PipelineModel.created_at.desc())
            statement = statement.limit(filters.limit).offset(filters.offset)
            
            # Execute query
            pipelines = self.session.exec(statement).all()
            
            logger.info(f"Listed {len(pipelines)} pipelines with filters")
            return list(pipelines)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error listing pipelines: {str(e)}")
            raise InternalServerException(f"Failed to list pipelines: {str(e)}")

    async def count_pipelines(self, filters: PipelineFilter) -> int:
        """Count pipelines matching filters using SELECT COUNT(*)"""
        try:
            statement = select(func.count()).select_from(PipelineModel)

            conditions = []
            if filters.name:
                conditions.append(PipelineModel.name.contains(filters.name))
            if filters.type is not None:
                conditions.append(PipelineModel.type == filters.type)
            if filters.group is not None:
                conditions.append(PipelineModel.group == filters.group)
            if filters.is_available is not None:
                conditions.append(PipelineModel.is_available == filters.is_available)
            if filters.version is not None:
                conditions.append(PipelineModel.version == filters.version)
            if filters.min_version is not None:
                conditions.append(PipelineModel.version >= filters.min_version)
            if filters.max_version is not None:
                conditions.append(PipelineModel.version <= filters.max_version)
            if filters.start_time:
                conditions.append(PipelineModel.created_at >= filters.start_time)
            if filters.end_time:
                conditions.append(PipelineModel.created_at <= filters.end_time)

            if conditions:
                statement = statement.where(and_(*conditions))

            result = self.session.exec(statement).one()
            return int(result[0] if isinstance(result, tuple) else result)
        except SQLAlchemyError as e:
            logger.error(f"Database error counting pipelines: {str(e)}")
            raise InternalServerException(f"Failed to count pipelines: {str(e)}")
    
    async def update_pipeline(
        self, 
        pipeline_id: UUID, 
        update_data: PipelineUpdate
    ) -> PipelineModel:
        """Update a pipeline"""
        try:
            # Get existing pipeline
            pipeline = await self.get_pipeline(pipeline_id)
            
            # Update fields
            update_dict = update_data.model_dump(exclude_unset=True)
            
            # Validate type if being updated
            if 'type' in update_dict and not PipelineTypeEnum.is_valid(update_dict['type']):
                raise BadRequestException(f"Invalid pipeline type: {update_dict['type']}")
            
            for field, value in update_dict.items():
                setattr(pipeline, field, value)
            
            # Update timestamp
            pipeline.updated_at = datetime.utcnow()
            
            # Commit changes
            self.session.add(pipeline)
            self.session.commit()
            self.session.refresh(pipeline)
            
            logger.info(f"Updated pipeline {pipeline_id}")
            return pipeline
            
        except IntegrityError as e:
            self.session.rollback()
            raise ConflictException(f"Update conflict: {str(e)}")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error updating pipeline {pipeline_id}: {str(e)}")
            raise InternalServerException(f"Failed to update pipeline: {str(e)}")
    
    async def delete_pipeline(self, pipeline_id: UUID) -> None:
        """Delete a pipeline"""
        try:
            # Get existing pipeline
            pipeline = await self.get_pipeline(pipeline_id)
            
            # Delete from database
            self.session.delete(pipeline)
            self.session.commit()
            
            logger.info(f"Deleted pipeline {pipeline_id}")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error deleting pipeline {pipeline_id}: {str(e)}")
            raise InternalServerException(f"Failed to delete pipeline: {str(e)}")
    
    async def create_pipelines(
        self, 
        bulk_data: PipelineBulkCreate
    ) -> dict:
        """Bulk create pipelines"""
        if len(bulk_data.pipelines) > BULK_INSERT_MAX_NUM:
            raise BadRequestException(
                f"Too many pipelines. Maximum allowed: {BULK_INSERT_MAX_NUM}"
            )
        
        created_ids = []
        errors = []
        
        try:
            for idx, pipeline_data in enumerate(bulk_data.pipelines):
                try:
                    # Validate type
                    if not PipelineTypeEnum.is_valid(pipeline_data.type):
                        errors.append({
                            "index": idx,
                            "error": f"Invalid pipeline type: {pipeline_data.type}",
                            "data": pipeline_data.model_dump()
                        })
                        continue
                    
                    # Create pipeline
                    pipeline = PipelineModel(**pipeline_data.model_dump())
                    self.session.add(pipeline)
                    self.session.flush()  # Flush to get ID without committing
                    created_ids.append(pipeline.id)
                    
                except IntegrityError as e:
                    errors.append({
                        "index": idx,
                        "error": str(e),
                        "data": pipeline_data.model_dump()
                    })
                except Exception as e:
                    errors.append({
                        "index": idx,
                        "error": str(e),
                        "data": pipeline_data.model_dump()
                    })
            
            # Commit all successful creations
            if created_ids:
                self.session.commit()
                logger.info(f"Bulk created {len(created_ids)} pipelines")
            else:
                self.session.rollback()
            
            return {
                "created": len(created_ids),
                "failed": len(errors),
                "ids": created_ids,
                "errors": errors
            }
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error in bulk create: {str(e)}")
            raise InternalServerException(f"Failed to bulk create pipelines: {str(e)}")
    
    async def get_pipelines_by_type(
        self, 
        type_value: int,
        limit: int = 100
    ) -> List[PipelineModel]:
        """Get all pipelines for a specific type"""
        try:
            statement = select(PipelineModel).where(
                PipelineModel.type == type_value
            ).limit(limit)
            
            pipelines = self.session.exec(statement).all()
            
            logger.info(f"Found {len(pipelines)} pipelines for type {type_value}")
            return list(pipelines)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching pipelines for type {type_value}: {str(e)}")
            raise InternalServerException(f"Failed to fetch pipelines: {str(e)}")
    
    async def get_pipelines_by_group(
        self, 
        group: int,
        limit: int = 100
    ) -> List[PipelineModel]:
        """Get all pipelines for a specific group"""
        try:
            statement = select(PipelineModel).where(
                PipelineModel.group == group
            ).limit(limit)
            
            pipelines = self.session.exec(statement).all()
            
            logger.info(f"Found {len(pipelines)} pipelines for group {group}")
            return list(pipelines)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching pipelines for group {group}: {str(e)}")
            raise InternalServerException(f"Failed to fetch pipelines: {str(e)}")
    
    async def get_available_pipelines(
        self,
        limit: int = 100
    ) -> List[PipelineModel]:
        """Get all available pipelines"""
        try:
            statement = select(PipelineModel).where(
                PipelineModel.is_available == 1
            ).limit(limit)
            
            pipelines = self.session.exec(statement).all()
            
            logger.info(f"Found {len(pipelines)} available pipelines")
            return list(pipelines)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching available pipelines: {str(e)}")
            raise InternalServerException(f"Failed to fetch pipelines: {str(e)}")
    
    async def get_pipeline_statistics(self) -> dict:
        """Get statistics about pipelines"""
        try:
            # Get all pipelines for statistics
            all_pipelines = self.session.exec(select(PipelineModel)).all()
            
            # Count by type
            type_counts = {}
            for pipeline in all_pipelines:
                type_counts[pipeline.type] = type_counts.get(pipeline.type, 0) + 1
            
            # Count by group
            group_counts = {}
            for pipeline in all_pipelines:
                group_counts[pipeline.group] = group_counts.get(pipeline.group, 0) + 1
            
            # Count by version
            version_counts = {}
            for pipeline in all_pipelines:
                version_counts[pipeline.version] = version_counts.get(pipeline.version, 0) + 1
            
            # Count available/unavailable
            available = len([p for p in all_pipelines if p.is_available == 1])
            unavailable = len([p for p in all_pipelines if p.is_available == 0])
            
            return {
                "total": len(all_pipelines),
                "by_type": type_counts,
                "by_group": group_counts,
                "available": available,
                "unavailable": unavailable,
                "by_version": version_counts
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting statistics: {str(e)}")
            raise InternalServerException(f"Failed to get statistics: {str(e)}")
    
    async def execute_pipeline(
        self,
        pipeline_id: UUID,
        input_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a pipeline with given parameters (placeholder for actual execution logic)"""
        try:
            # Get pipeline
            pipeline = await self.get_pipeline(pipeline_id)
            
            # Check if pipeline is available
            if pipeline.is_available != 1:
                raise BadRequestException(f"Pipeline {pipeline_id} is not available")
            
            # Parse pipeline parameters
            try:
                pipeline_params = json.loads(pipeline.params)
            except json.JSONDecodeError:
                raise InternalServerException("Invalid pipeline parameters")
            
            # Here you would implement actual pipeline execution logic
            # For now, return a mock response
            result = {
                "pipeline_id": str(pipeline_id),
                "pipeline_name": pipeline.name,
                "status": "executed",
                "input_params": input_params,
                "pipeline_params": pipeline_params,
                "result": "Pipeline execution completed successfully (mock)"
            }
            
            logger.info(f"Executed pipeline {pipeline_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing pipeline {pipeline_id}: {str(e)}")
            raise InternalServerException(f"Failed to execute pipeline: {str(e)}")
