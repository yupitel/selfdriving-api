import logging
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlmodel import Session, select, and_
from sqlalchemy import func
from app.models.pipelinestate import PipelineStateModel
from app.models.pipelinedata import PipelineDataModel
from app.models.pipeline import PipelineModel
from app.schemas.pipelinestate import (
    PipelineStateUpdate,
    PipelineStateFilter,
    PipelineStateBulkCreate,
    PipelineStateDetailResponse
)
from app.cores.config import BULK_INSERT_MAX_NUM

logger = logging.getLogger(__name__)


class PipelineStateService:
    """Service class for pipeline state operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    # Note: Single create is removed in favor of bulk-at-root API usage.
    
    async def get_pipeline_state(self, pipeline_state_id: UUID) -> Optional[PipelineStateModel]:
        """Get pipeline state by ID"""
        statement = select(PipelineStateModel).where(PipelineStateModel.id == pipeline_state_id)
        result = self.session.exec(statement)
        pipeline_state = result.first()
        
        if pipeline_state:
            logger.info(f"Retrieved pipeline state with ID: {pipeline_state_id}")
        else:
            logger.warning(f"Pipeline state not found with ID: {pipeline_state_id}")
        
        return pipeline_state

    async def get_pipeline_states_by_id(self, pipeline_state_id: UUID) -> List[PipelineStateModel]:
        """Get pipeline state by ID as a list (0 or 1 items)."""
        statement = select(PipelineStateModel).where(PipelineStateModel.id == pipeline_state_id)
        result = self.session.exec(statement)
        return result.all()
    
    async def get_pipeline_state_detail(self, pipeline_state_id: UUID) -> Optional[PipelineStateDetailResponse]:
        """Get pipeline state with detailed information"""
        # Get the pipeline state
        pipeline_state = await self.get_pipeline_state(pipeline_state_id)
        if not pipeline_state:
            return None
        
        # Get related pipeline data info
        pipelinedata_info = None
        if pipeline_state.pipeline_data_id:
            pipelinedata_statement = select(PipelineDataModel).where(
                PipelineDataModel.id == pipeline_state.pipeline_data_id
            )
            pipelinedata_result = self.session.exec(pipelinedata_statement)
            pipelinedata = pipelinedata_result.first()
            if pipelinedata:
                pipelinedata_info = {
                    "id": str(pipelinedata.id),
                    "name": pipelinedata.name,
                    "type": pipelinedata.type,
                    "source": pipelinedata.source,
                    "data_path": pipelinedata.data_path
                }
        
        # Get related pipeline info
        pipeline_info = None
        if pipeline_state.pipeline_id:
            pipeline_statement = select(PipelineModel).where(
                PipelineModel.id == pipeline_state.pipeline_id
            )
            pipeline_result = self.session.exec(pipeline_statement)
            pipeline = pipeline_result.first()
            if pipeline:
                pipeline_info = {
                    "id": str(pipeline.id),
                    "name": pipeline.name,
                    "type": pipeline.type,
                    "version": pipeline.version
                }
        
        # Create detailed response
        detail_response = PipelineStateDetailResponse(
            id=pipeline_state.id,
            pipeline_data_id=pipeline_state.pipeline_data_id,
            pipeline_id=pipeline_state.pipeline_id,
            input=pipeline_state.input,
            output=pipeline_state.output,
            state=pipeline_state.state,
            created_at=pipeline_state.created_at,
            updated_at=pipeline_state.updated_at,
            pipelinedata_info=pipelinedata_info,
            pipeline_info=pipeline_info
        )
        
        return detail_response
    
    async def get_pipeline_states(self, filter_params: PipelineStateFilter) -> Tuple[List[PipelineStateModel], int]:
        """Get list of pipeline states with filtering and pagination"""
        # Build the base query
        base_statement = select(PipelineStateModel)
        conditions = []
        
        # Apply filters
        if filter_params.pipeline_data_id:
            conditions.append(PipelineStateModel.pipeline_data_id == filter_params.pipeline_data_id)
        
        if filter_params.pipeline_id:
            conditions.append(PipelineStateModel.pipeline_id == filter_params.pipeline_id)
            
        if filter_params.state is not None:
            conditions.append(PipelineStateModel.state == filter_params.state)
        
        # Apply conditions if any
        if conditions:
            base_statement = base_statement.where(and_(*conditions))
        
        # Get total count
        count_statement = select(func.count()).select_from(PipelineStateModel)
        if conditions:
            count_statement = count_statement.where(and_(*conditions))
        total_result = self.session.exec(count_statement).one()
        total = int(total_result[0] if isinstance(total_result, tuple) else total_result)
        
        # Apply pagination
        statement = base_statement.offset(filter_params.offset).limit(filter_params.limit)
        result = self.session.exec(statement)
        pipeline_states = list(result)
        
        logger.info(f"Retrieved {len(pipeline_states)} pipeline states out of {total} total")
        return pipeline_states, total
    
    async def update_pipeline_state(self, pipeline_state_id: UUID, pipeline_state_update: PipelineStateUpdate) -> Optional[PipelineStateModel]:
        """Update pipeline state"""
        try:
            statement = select(PipelineStateModel).where(PipelineStateModel.id == pipeline_state_id)
            result = self.session.exec(statement)
            pipeline_state = result.first()
            
            if not pipeline_state:
                logger.warning(f"Pipeline state not found for update with ID: {pipeline_state_id}")
                return None
            
            # Update fields
            update_data = pipeline_state_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(pipeline_state, key, value)
            
            self.session.add(pipeline_state)
            self.session.commit()
            self.session.refresh(pipeline_state)
            logger.info(f"Updated pipeline state with ID: {pipeline_state_id}")
            return pipeline_state
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating pipeline state: {str(e)}")
            raise
    
    async def delete_pipeline_state(self, pipeline_state_id: UUID) -> bool:
        """Delete pipeline state"""
        try:
            statement = select(PipelineStateModel).where(PipelineStateModel.id == pipeline_state_id)
            result = self.session.exec(statement)
            pipeline_state = result.first()
            
            if not pipeline_state:
                logger.warning(f"Pipeline state not found for deletion with ID: {pipeline_state_id}")
                return False
            
            self.session.delete(pipeline_state)
            self.session.commit()
            logger.info(f"Deleted pipeline state with ID: {pipeline_state_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting pipeline state: {str(e)}")
            raise
    
    async def create_pipeline_states(self, bulk_data: PipelineStateBulkCreate) -> List[PipelineStateModel]:
        """Bulk create pipeline state entries"""
        if len(bulk_data.pipeline_states) > BULK_INSERT_MAX_NUM:
            raise ValueError(f"Bulk insert limit exceeded. Maximum {BULK_INSERT_MAX_NUM} items allowed.")
        
        try:
            pipeline_state_entries = []
            for state in bulk_data.pipeline_states:
                # Validate foreign keys where possible
                # Validate pipeline_data_id exists
                if state.pipeline_data_id:
                    pd_stmt = select(PipelineDataModel).where(PipelineDataModel.id == state.pipeline_data_id)
                    if self.session.exec(pd_stmt).first() is None:
                        raise ValueError(f"Invalid pipeline_data_id: {state.pipeline_data_id}")
                # Validate pipeline_id exists
                if state.pipeline_id:
                    pl_stmt = select(PipelineModel).where(PipelineModel.id == state.pipeline_id)
                    if self.session.exec(pl_stmt).first() is None:
                        raise ValueError(f"Invalid pipeline_id: {state.pipeline_id}")
                state_entry = PipelineStateModel(
                    id=uuid4(),
                    **state.model_dump()
                )
                pipeline_state_entries.append(state_entry)
            
            self.session.add_all(pipeline_state_entries)
            self.session.commit()
            
            # Refresh all entries
            for entry in pipeline_state_entries:
                self.session.refresh(entry)
                
            logger.info(f"Bulk created {len(pipeline_state_entries)} pipeline state entries")
            return pipeline_state_entries
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error bulk creating pipeline states: {str(e)}")
            raise
    
    async def get_job_states_for_pipeline_data(self, pipeline_data_id: UUID) -> List[PipelineStateModel]:
        """Get all pipeline states (jobs) for a specific pipeline data"""
        statement = select(PipelineStateModel).where(
            PipelineStateModel.pipeline_data_id == pipeline_data_id
        )
        result = self.session.exec(statement)
        states = list(result)
        
        logger.info(f"Retrieved {len(states)} job states for pipeline data ID: {pipeline_data_id}")
        return states

    async def count_pipeline_states(self, filter_params: PipelineStateFilter) -> int:
        """Count pipeline states matching filters using SELECT COUNT(*)"""
        base_statement = select(func.count()).select_from(PipelineStateModel)
        conditions = []
        if filter_params.pipeline_data_id:
            conditions.append(PipelineStateModel.pipeline_data_id == filter_params.pipeline_data_id)
        if filter_params.pipeline_id:
            conditions.append(PipelineStateModel.pipeline_id == filter_params.pipeline_id)
        if filter_params.state is not None:
            conditions.append(PipelineStateModel.state == filter_params.state)
        if conditions:
            base_statement = base_statement.where(and_(*conditions))
        total_result = self.session.exec(base_statement).one()
        return int(total_result[0] if isinstance(total_result, tuple) else total_result)
