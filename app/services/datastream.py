import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import Session, select, and_, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.datastream import DataStreamModel
from app.schemas.datastream import (
    DataStreamUpdate,
    DataStreamFilter,
    DataStreamBulkCreate,
    DataStreamTypeEnum
)
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
    InternalServerException
)
from app.cores.config import BULK_INSERT_MAX_NUM

logger = logging.getLogger(__name__)


class DataStreamService:
    """Service class for DataStream operations"""
    
    def __init__(self, db_session: Session):
        self.session = db_session
    
    # Note: Single create is removed in favor of bulk-at-root API usage.
    
    async def get_datastream(self, datastream_id: UUID) -> DataStreamModel:
        """Get a datastream by ID"""
        try:
            statement = select(DataStreamModel).where(DataStreamModel.id == datastream_id)
            datastream = self.session.exec(statement).first()
            
            if not datastream:
                raise NotFoundException(f"DataStream with ID {datastream_id} not found")
            
            return datastream
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching datastream {datastream_id}: {str(e)}")
            raise InternalServerException(f"Failed to fetch datastream: {str(e)}")

    async def get_datastreams_by_id(self, datastream_id: UUID) -> List[DataStreamModel]:
        """Get datastream(s) by ID as a list (0 or 1 items).
        Returns 200 with an empty list when not found, matching list semantics.
        """
        try:
            statement = select(DataStreamModel).where(DataStreamModel.id == datastream_id)
            datastreams = self.session.exec(statement).all()
            return list(datastreams)
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching datastream list {datastream_id}: {str(e)}")
            raise InternalServerException(f"Failed to fetch datastreams: {str(e)}")
    
    async def list_datastreams(self, filters: DataStreamFilter) -> List[DataStreamModel]:
        """List datastreams with optional filters"""
        try:
            statement = select(DataStreamModel)
            
            # Build filter conditions
            conditions = []
            
            if filters.type is not None:
                conditions.append(DataStreamModel.type == filters.type)
            
            if filters.measurement_id:
                conditions.append(DataStreamModel.measurement_id == filters.measurement_id)
            
            if filters.name:
                conditions.append(DataStreamModel.name.contains(filters.name))
            
            if filters.data_path:
                conditions.append(DataStreamModel.data_path.contains(filters.data_path))
            
            if filters.src_path:
                conditions.append(DataStreamModel.src_path.contains(filters.src_path))
            
            if filters.sequence_number is not None:
                conditions.append(DataStreamModel.sequence_number == filters.sequence_number)
            
            if filters.processing_status is not None:
                conditions.append(DataStreamModel.processing_status == filters.processing_status)
            
            if filters.has_data_loss is not None:
                conditions.append(DataStreamModel.has_data_loss == filters.has_data_loss)
            
            if filters.segment_start_time:
                conditions.append(DataStreamModel.start_time >= filters.segment_start_time)
            
            if filters.segment_end_time:
                conditions.append(DataStreamModel.end_time <= filters.segment_end_time)
            
            if filters.start_time:
                conditions.append(DataStreamModel.created_at >= filters.start_time)
            
            if filters.end_time:
                conditions.append(DataStreamModel.created_at <= filters.end_time)
            
            # Apply filters
            if conditions:
                statement = statement.where(and_(*conditions))
            
            # Apply ordering and pagination
            statement = statement.order_by(DataStreamModel.created_at.desc())
            statement = statement.limit(filters.limit).offset(filters.offset)
            
            # Execute query
            datastreams = self.session.exec(statement).all()
            
            logger.info(f"Listed {len(datastreams)} datastreams with filters")
            return list(datastreams)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error listing datastreams: {str(e)}")
            raise InternalServerException(f"Failed to list datastreams: {str(e)}")
    
    async def update_datastream(
        self, 
        datastream_id: UUID, 
        update_data: DataStreamUpdate
    ) -> DataStreamModel:
        """Update a datastream"""
        try:
            # Get existing datastream
            datastream = await self.get_datastream(datastream_id)
            
            # Update fields
            update_dict = update_data.model_dump(exclude_unset=True)
            
            # Validate type if being updated
            if 'type' in update_dict and not DataStreamTypeEnum.is_valid(update_dict['type']):
                raise BadRequestException(f"Invalid datastream type: {update_dict['type']}")
            
            for field, value in update_dict.items():
                setattr(datastream, field, value)
            
            # Update timestamp
            datastream.updated_at = datetime.utcnow()
            
            # Commit changes
            self.session.add(datastream)
            self.session.commit()
            self.session.refresh(datastream)
            
            logger.info(f"Updated datastream {datastream_id}")
            return datastream
            
        except IntegrityError as e:
            self.session.rollback()
            if "foreign key" in str(e).lower():
                raise BadRequestException(f"Measurement ID does not exist")
            raise ConflictException(f"Update conflict: {str(e)}")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error updating datastream {datastream_id}: {str(e)}")
            raise InternalServerException(f"Failed to update datastream: {str(e)}")
    
    async def delete_datastream(self, datastream_id: UUID) -> None:
        """Delete a datastream"""
        try:
            # Get existing datastream
            datastream = await self.get_datastream(datastream_id)
            
            # Delete from database
            self.session.delete(datastream)
            self.session.commit()
            
            logger.info(f"Deleted datastream {datastream_id}")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error deleting datastream {datastream_id}: {str(e)}")
            raise InternalServerException(f"Failed to delete datastream: {str(e)}")
    
    async def create_datastreams(
        self, 
        bulk_data: DataStreamBulkCreate
    ) -> dict:
        """Bulk create datastreams"""
        if len(bulk_data.datastreams) > BULK_INSERT_MAX_NUM:
            raise BadRequestException(
                f"Too many datastreams. Maximum allowed: {BULK_INSERT_MAX_NUM}"
            )
        
        created_ids = []
        errors = []
        
        try:
            for idx, datastream_data in enumerate(bulk_data.datastreams):
                try:
                    # Validate type
                    if not DataStreamTypeEnum.is_valid(datastream_data.type):
                        errors.append({
                            "index": idx,
                            "error": f"Invalid datastream type: {datastream_data.type}",
                            "data": datastream_data.model_dump()
                        })
                        continue
                    
                    # Create datastream
                    datastream = DataStreamModel(**datastream_data.model_dump())
                    self.session.add(datastream)
                    self.session.flush()  # Flush to get ID without committing
                    created_ids.append(datastream.id)
                    
                except IntegrityError as e:
                    errors.append({
                        "index": idx,
                        "error": str(e),
                        "data": datastream_data.model_dump()
                    })
                except Exception as e:
                    errors.append({
                        "index": idx,
                        "error": str(e),
                        "data": datastream_data.model_dump()
                    })
            
            # Commit all successful creations
            if created_ids:
                self.session.commit()
                logger.info(f"Bulk created {len(created_ids)} datastreams")
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
            raise InternalServerException(f"Failed to bulk create datastreams: {str(e)}")
    
    async def get_datastreams_by_measurement(
        self, 
        measurement_id: UUID,
        limit: int = 100
    ) -> List[DataStreamModel]:
        """Get all datastreams for a specific measurement"""
        try:
            statement = select(DataStreamModel).where(
                DataStreamModel.measurement_id == measurement_id
            ).limit(limit)
            
            datastreams = self.session.exec(statement).all()
            
            logger.info(f"Found {len(datastreams)} datastreams for measurement {measurement_id}")
            return list(datastreams)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching datastreams for measurement {measurement_id}: {str(e)}")
            raise InternalServerException(f"Failed to fetch datastreams: {str(e)}")
    
    async def get_datastream_statistics(self) -> dict:
        """Get statistics about datastreams"""
        try:
            # Total count
            total_count = self.session.exec(
                select(DataStreamModel)
            ).all()
            
            # Count by type
            type_counts = {}
            for type_val in [0, 1, 2, 3, 4, 5, 6, 7, 8, 99]:
                count = len([d for d in total_count if d.type == type_val])
                if count > 0:
                    type_counts[DataStreamTypeEnum.get_name(type_val)] = count
            
            # Count datastreams with paths
            with_data_path = len([d for d in total_count if d.data_path is not None])
            with_src_path = len([d for d in total_count if d.src_path is not None])
            
            return {
                "total": len(total_count),
                "by_type": type_counts,
                "with_data_path": with_data_path,
                "with_src_path": with_src_path
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting statistics: {str(e)}")
            raise InternalServerException(f"Failed to get statistics: {str(e)}")
