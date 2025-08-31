import logging
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Session, select, and_
from app.models.measurement import MeasurementModel
from app.schemas.measurement import (
    MeasurementCreate,
    MeasurementUpdate,
    MeasurementFilter,
    MeasurementBulkCreate
)
from app.cores.config import BULK_INSERT_MAX_NUM

logger = logging.getLogger(__name__)


class MeasurementService:
    """Service class for measurement operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_measurement(self, measurement_data: MeasurementCreate) -> MeasurementModel:
        """Create a new measurement"""
        try:
            measurement = MeasurementModel(
                id=uuid4(),
                **measurement_data.model_dump()
            )
            self.session.add(measurement)
            self.session.commit()
            self.session.refresh(measurement)
            logger.info(f"Created measurement with ID: {measurement.id}")
            return measurement
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating measurement: {str(e)}")
            raise
    
    async def get_measurement(self, measurement_id: UUID) -> Optional[MeasurementModel]:
        """Get measurement by ID"""
        statement = select(MeasurementModel).where(MeasurementModel.id == measurement_id)
        result = self.session.exec(statement)
        measurement = result.first()
        
        if not measurement:
            logger.warning(f"Measurement not found: {measurement_id}")
        
        return measurement
    
    async def get_measurements(
        self,
        filter_params: MeasurementFilter
    ) -> tuple[List[MeasurementModel], int]:
        """Get measurements with filtering and pagination"""
        # Build query
        statement = select(MeasurementModel)
        
        # Apply filters
        conditions = []
        if filter_params.vehicle_id:
            conditions.append(MeasurementModel.vehicle_id == filter_params.vehicle_id)
        if filter_params.area_id:
            conditions.append(MeasurementModel.area_id == filter_params.area_id)
        if filter_params.driver_id:
            conditions.append(MeasurementModel.driver_id == filter_params.driver_id)
        if filter_params.start_time:
            conditions.append(MeasurementModel.local_time >= filter_params.start_time)
        if filter_params.end_time:
            conditions.append(MeasurementModel.local_time <= filter_params.end_time)
        if filter_params.weather_condition:
            conditions.append(MeasurementModel.weather_condition == filter_params.weather_condition)
        if filter_params.road_condition:
            conditions.append(MeasurementModel.road_condition == filter_params.road_condition)
        if filter_params.min_distance:
            conditions.append(MeasurementModel.distance >= filter_params.min_distance)
        if filter_params.max_distance:
            conditions.append(MeasurementModel.distance <= filter_params.max_distance)
        if filter_params.min_duration:
            conditions.append(MeasurementModel.duration >= filter_params.min_duration)
        if filter_params.max_duration:
            conditions.append(MeasurementModel.duration <= filter_params.max_duration)
        
        if conditions:
            statement = statement.where(and_(*conditions))
        
        # Get total count
        count_statement = select(MeasurementModel)
        if conditions:
            count_statement = count_statement.where(and_(*conditions))
        total = len(self.session.exec(count_statement).all())
        
        # Apply pagination
        statement = statement.offset(filter_params.offset).limit(filter_params.limit)
        
        # Execute query
        result = self.session.exec(statement)
        measurements = result.all()
        
        logger.info(f"Retrieved {len(measurements)} measurements (total: {total})")
        return measurements, total
    
    async def update_measurement(
        self,
        measurement_id: UUID,
        measurement_update: MeasurementUpdate
    ) -> Optional[MeasurementModel]:
        """Update measurement"""
        measurement = await self.get_measurement(measurement_id)
        if not measurement:
            return None
        
        try:
            update_data = measurement_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(measurement, key, value)
            
            measurement.save()  # Updates updated_at
            self.session.add(measurement)
            self.session.commit()
            self.session.refresh(measurement)
            
            logger.info(f"Updated measurement: {measurement_id}")
            return measurement
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating measurement: {str(e)}")
            raise
    
    async def delete_measurement(self, measurement_id: UUID) -> bool:
        """Delete measurement"""
        measurement = await self.get_measurement(measurement_id)
        if not measurement:
            return False
        
        try:
            self.session.delete(measurement)
            self.session.commit()
            logger.info(f"Deleted measurement: {measurement_id}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting measurement: {str(e)}")
            raise
    
    async def bulk_create_measurements(
        self,
        bulk_data: MeasurementBulkCreate
    ) -> List[MeasurementModel]:
        """Bulk create measurements"""
        if len(bulk_data.measurements) > BULK_INSERT_MAX_NUM:
            raise ValueError(f"Bulk insert limit exceeded. Maximum: {BULK_INSERT_MAX_NUM}")
        
        try:
            measurements = []
            for measurement_data in bulk_data.measurements:
                measurement = MeasurementModel(
                    id=uuid4(),
                    **measurement_data.model_dump()
                )
                measurements.append(measurement)
                self.session.add(measurement)
            
            self.session.commit()
            
            # Refresh all measurements
            for measurement in measurements:
                self.session.refresh(measurement)
            
            logger.info(f"Bulk created {len(measurements)} measurements")
            return measurements
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error in bulk create: {str(e)}")
            raise