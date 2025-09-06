import logging
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlmodel import Session, select, and_
from app.models.pipelinedata import PipelineDataModel
from app.schemas.pipelinedata import (
    PipelineDataUpdate,
    PipelineDataFilter,
    PipelineDataBulkCreate
)
from app.cores.config import BULK_INSERT_MAX_NUM

logger = logging.getLogger(__name__)


class PipelineDataService:
    """Service class for pipeline data operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    # Note: Single create is removed in favor of bulk-at-root API usage.
    
    async def get_pipeline_data(self, pipeline_data_id: UUID) -> Optional[PipelineDataModel]:
        """Get pipeline data by ID"""
        statement = select(PipelineDataModel).where(PipelineDataModel.id == pipeline_data_id)
        result = self.session.exec(statement)
        pipeline_data = result.first()
        
        if pipeline_data:
            logger.info(f"Retrieved pipeline data with ID: {pipeline_data_id}")
        else:
            logger.warning(f"Pipeline data not found with ID: {pipeline_data_id}")
        
        return pipeline_data
    
    async def get_pipeline_data_list(self, filter_params: PipelineDataFilter) -> Tuple[List[PipelineDataModel], int]:
        """Get list of pipeline data with filtering and pagination"""
        # Build the base query
        base_statement = select(PipelineDataModel)
        conditions = []
        
        # Apply filters
        if filter_params.type is not None:
            conditions.append(PipelineDataModel.type == filter_params.type)
        
        if filter_params.datastream_id:
            conditions.append(PipelineDataModel.datastream_id == filter_params.datastream_id)
            
        if filter_params.scene_id:
            conditions.append(PipelineDataModel.scene_id == filter_params.scene_id)
            
        if filter_params.source:
            conditions.append(PipelineDataModel.source.ilike(f"%{filter_params.source}%"))
        
        # Apply conditions if any
        if conditions:
            base_statement = base_statement.where(and_(*conditions))
        
        # Get total count
        count_statement = select(PipelineDataModel).where(and_(*conditions)) if conditions else select(PipelineDataModel)
        total_result = self.session.exec(count_statement)
        total = len(list(total_result))
        
        # Apply pagination
        statement = base_statement.offset(filter_params.offset).limit(filter_params.limit)
        result = self.session.exec(statement)
        pipeline_data_list = list(result)
        
        logger.info(f"Retrieved {len(pipeline_data_list)} pipeline data entries out of {total} total")
        return pipeline_data_list, total
    
    async def update_pipeline_data(self, pipeline_data_id: UUID, pipeline_data_update: PipelineDataUpdate) -> Optional[PipelineDataModel]:
        """Update pipeline data"""
        try:
            statement = select(PipelineDataModel).where(PipelineDataModel.id == pipeline_data_id)
            result = self.session.exec(statement)
            pipeline_data = result.first()
            
            if not pipeline_data:
                logger.warning(f"Pipeline data not found for update with ID: {pipeline_data_id}")
                return None
            
            # Update fields
            update_data = pipeline_data_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(pipeline_data, key, value)
            
            self.session.add(pipeline_data)
            self.session.commit()
            self.session.refresh(pipeline_data)
            logger.info(f"Updated pipeline data with ID: {pipeline_data_id}")
            return pipeline_data
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating pipeline data: {str(e)}")
            raise
    
    async def delete_pipeline_data(self, pipeline_data_id: UUID) -> bool:
        """Delete pipeline data"""
        try:
            statement = select(PipelineDataModel).where(PipelineDataModel.id == pipeline_data_id)
            result = self.session.exec(statement)
            pipeline_data = result.first()
            
            if not pipeline_data:
                logger.warning(f"Pipeline data not found for deletion with ID: {pipeline_data_id}")
                return False
            
            self.session.delete(pipeline_data)
            self.session.commit()
            logger.info(f"Deleted pipeline data with ID: {pipeline_data_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting pipeline data: {str(e)}")
            raise
    
    async def bulk_create_pipeline_data(self, bulk_data: PipelineDataBulkCreate) -> List[PipelineDataModel]:
        """Bulk create pipeline data entries"""
        if len(bulk_data.pipeline_data) > BULK_INSERT_MAX_NUM:
            raise ValueError(f"Bulk insert limit exceeded. Maximum {BULK_INSERT_MAX_NUM} items allowed.")
        
        try:
            pipeline_data_entries = []
            for data in bulk_data.pipeline_data:
                data_entry = PipelineDataModel(
                    id=uuid4(),
                    **data.model_dump()
                )
                pipeline_data_entries.append(data_entry)
            
            self.session.add_all(pipeline_data_entries)
            self.session.commit()
            
            # Refresh all entries
            for entry in pipeline_data_entries:
                self.session.refresh(entry)
                
            logger.info(f"Bulk created {len(pipeline_data_entries)} pipeline data entries")
            return pipeline_data_entries
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error bulk creating pipeline data: {str(e)}")
            raise
