import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date, timedelta

from sqlmodel import Session, select, and_, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.driver import DriverModel
from app.schemas.driver import (
    DriverCreate,
    DriverUpdate,
    DriverFilter,
    DriverBulkCreate,
    DriverStatistics
)
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
    InternalServerException
)
from app.cores.config import BULK_INSERT_MAX_NUM

logger = logging.getLogger(__name__)


class DriverService:
    """Service class for Driver operations"""
    
    def __init__(self, db_session: Session):
        self.session = db_session
    
    async def create_driver(self, driver_data: DriverCreate) -> DriverModel:
        """Create a new driver"""
        try:
            # Check if email already exists (if provided)
            if driver_data.email:
                existing_email = await self.get_driver_by_email(driver_data.email)
                if existing_email:
                    raise ConflictException(f"Driver with email '{driver_data.email}' already exists")
            
            # Create driver instance
            payload = driver_data.model_dump()
            driver = DriverModel(**payload)
            
            # Add to session and commit
            self.session.add(driver)
            self.session.commit()
            self.session.refresh(driver)
            
            logger.info(f"Created driver with ID: {driver.id}")
            return driver
            
        except IntegrityError as e:
            self.session.rollback()
            if "unique" in str(e).lower():
                raise ConflictException(f"Driver with this code or email already exists")
            raise ConflictException(f"Driver creation failed: {str(e)}")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error creating driver: {str(e)}")
            raise InternalServerException(f"Failed to create driver: {str(e)}")
    
    async def get_driver(self, driver_id: UUID) -> DriverModel:
        """Get a driver by ID"""
        try:
            statement = select(DriverModel).where(DriverModel.id == driver_id)
            driver = self.session.exec(statement).first()
            
            if not driver:
                raise NotFoundException(f"Driver with ID {driver_id} not found")
            
            return driver
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching driver {driver_id}: {str(e)}")
            raise InternalServerException(f"Failed to fetch driver: {str(e)}")
    
    
    
    async def list_drivers(self, filters: DriverFilter) -> tuple[List[DriverModel], int]:
        """List drivers with optional filters"""
        try:
            statement = select(DriverModel)
            
            # Build filter conditions
            conditions = []
            
            
            if filters.email:
                conditions.append(DriverModel.email == filters.email)
            
            if filters.name:
                conditions.append(DriverModel.name.contains(filters.name))
            
            if filters.certification_level is not None:
                conditions.append(DriverModel.certification_level == filters.certification_level)
            
            if filters.status is not None:
                conditions.append(DriverModel.status == filters.status)
            
            if filters.employment_type is not None:
                conditions.append(DriverModel.employment_type == filters.employment_type)
            
            if filters.department:
                conditions.append(DriverModel.department == filters.department)
            
            if filters.team:
                conditions.append(DriverModel.team == filters.team)
            
            if filters.supervisor_id:
                conditions.append(DriverModel.supervisor_id == filters.supervisor_id)
            
            if filters.license_expiring_before:
                conditions.append(DriverModel.license_expiry_date <= filters.license_expiring_before)
            
            if filters.last_drive_after:
                conditions.append(DriverModel.last_drive_date >= filters.last_drive_after)
            
            if filters.last_drive_before:
                conditions.append(DriverModel.last_drive_date <= filters.last_drive_before)
            
            if filters.min_safety_score is not None:
                conditions.append(DriverModel.safety_score >= filters.min_safety_score)
            
            if filters.min_efficiency_score is not None:
                conditions.append(DriverModel.efficiency_score >= filters.min_efficiency_score)
            
            if filters.min_data_quality_score is not None:
                conditions.append(DriverModel.data_quality_score >= filters.min_data_quality_score)
            
            # Apply filters
            if conditions:
                statement = statement.where(and_(*conditions))
            
            # Get total count
            count_statement = select(DriverModel)
            if conditions:
                count_statement = count_statement.where(and_(*conditions))
            total = len(self.session.exec(count_statement).all())
            
            # Apply ordering and pagination
            statement = statement.order_by(DriverModel.name)
            statement = statement.limit(filters.limit).offset(filters.offset)
            
            # Execute query
            drivers = self.session.exec(statement).all()
            
            logger.info(f"Listed {len(drivers)} drivers with filters")
            return list(drivers), total
            
        except SQLAlchemyError as e:
            logger.error(f"Database error listing drivers: {str(e)}")
            raise InternalServerException(f"Failed to list drivers: {str(e)}")
    
    async def update_driver(
        self, 
        driver_id: UUID, 
        update_data: DriverUpdate
    ) -> DriverModel:
        """Update a driver"""
        try:
            # Get existing driver
            driver = await self.get_driver(driver_id)
            
            # Check email uniqueness if email is being updated
            if update_data.email and update_data.email != driver.email:
                existing_email = await self.get_driver_by_email(update_data.email)
                if existing_email:
                    raise ConflictException(f"Driver with email '{update_data.email}' already exists")
            
            # Update fields
            update_dict = update_data.model_dump(exclude_unset=True)
            
            for field, value in update_dict.items():
                setattr(driver, field, value)
            
            # Update timestamp
            driver.updated_at = int(datetime.utcnow().timestamp())
            
            # Commit changes
            self.session.add(driver)
            self.session.commit()
            self.session.refresh(driver)
            
            logger.info(f"Updated driver {driver_id}")
            return driver
            
        except IntegrityError as e:
            self.session.rollback()
            if "unique" in str(e).lower():
                raise ConflictException(f"Driver with this email already exists")
            raise ConflictException(f"Update conflict: {str(e)}")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error updating driver {driver_id}: {str(e)}")
            raise InternalServerException(f"Failed to update driver: {str(e)}")
    
    async def delete_driver(self, driver_id: UUID) -> None:
        """Delete a driver"""
        try:
            # Get existing driver
            driver = await self.get_driver(driver_id)
            
            # Delete from database
            self.session.delete(driver)
            self.session.commit()
            
            logger.info(f"Deleted driver {driver_id}")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error deleting driver {driver_id}: {str(e)}")
            raise InternalServerException(f"Failed to delete driver: {str(e)}")
    
    async def bulk_create_drivers(
        self, 
        bulk_data: DriverBulkCreate
    ) -> dict:
        """Bulk create drivers"""
        if len(bulk_data.drivers) > BULK_INSERT_MAX_NUM:
            raise BadRequestException(
                f"Too many drivers. Maximum allowed: {BULK_INSERT_MAX_NUM}"
            )
        
        created_ids = []
        errors = []
        
        try:
            for idx, driver_data in enumerate(bulk_data.drivers):
                try:
                    if driver_data.email:
                        existing_email = await self.get_driver_by_email(driver_data.email)
                        if existing_email:
                            errors.append({
                                "index": idx,
                                "error": f"Email '{driver_data.email}' already exists",
                                "data": driver_data.model_dump()
                            })
                            continue
                    
                    # Create driver
                    payload = driver_data.model_dump()
                    driver = DriverModel(**payload)
                    self.session.add(driver)
                    self.session.flush()  # Flush to get ID without committing
                    created_ids.append(driver.id)
                    
                except IntegrityError as e:
                    errors.append({
                        "index": idx,
                        "error": str(e),
                        "data": driver_data.model_dump()
                    })
                except Exception as e:
                    errors.append({
                        "index": idx,
                        "error": str(e),
                        "data": driver_data.model_dump()
                    })
            
            # Commit all successful creations
            if created_ids:
                self.session.commit()
                logger.info(f"Bulk created {len(created_ids)} drivers")
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
            raise InternalServerException(f"Failed to bulk create drivers: {str(e)}")
    
    async def get_driver_statistics(self) -> DriverStatistics:
        """Get statistics about drivers"""
        try:
            # Get all drivers for statistics
            all_drivers = self.session.exec(select(DriverModel)).all()
            
            # Count by status
            status_counts = {}
            for driver in all_drivers:
                status_counts[driver.status] = status_counts.get(driver.status, 0) + 1
            
            # Count by certification level
            cert_level_counts = {}
            for driver in all_drivers:
                cert_level_counts[driver.certification_level] = cert_level_counts.get(driver.certification_level, 0) + 1
            
            # Count by employment type
            emp_type_counts = {}
            for driver in all_drivers:
                emp_type_counts[driver.employment_type] = emp_type_counts.get(driver.employment_type, 0) + 1
            
            # Count by department
            dept_counts = {}
            for driver in all_drivers:
                if driver.department:
                    dept_counts[driver.department] = dept_counts.get(driver.department, 0) + 1
            
            # Count active drivers
            active_drivers = len([d for d in all_drivers if d.status == 1])
            
            # Count drivers with licenses expiring soon (within 30 days)
            expiring_soon = 0
            cutoff_date = date.today() + timedelta(days=30)
            for driver in all_drivers:
                if driver.license_expiry_date and driver.license_expiry_date <= cutoff_date:
                    expiring_soon += 1
            
            return DriverStatistics(
                total=len(all_drivers),
                by_status=status_counts,
                by_certification_level=cert_level_counts,
                by_employment_type=emp_type_counts,
                by_department=dept_counts,
                active_drivers=active_drivers,
                license_expiring_soon=expiring_soon
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting statistics: {str(e)}")
            raise InternalServerException(f"Failed to get statistics: {str(e)}")
    
    async def get_drivers_by_supervisor(self, supervisor_id: UUID) -> List[DriverModel]:
        """Get all drivers under a specific supervisor"""
        try:
            statement = select(DriverModel).where(DriverModel.supervisor_id == supervisor_id)
            drivers = self.session.exec(statement).all()
            
            logger.info(f"Found {len(drivers)} drivers under supervisor {supervisor_id}")
            return list(drivers)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching drivers by supervisor {supervisor_id}: {str(e)}")
            raise InternalServerException(f"Failed to fetch drivers: {str(e)}")
    
    async def update_driver_statistics(self, driver_id: UUID) -> DriverModel:
        """Update driver statistics from measurement data"""
        try:
            # This would typically calculate statistics from the measurement table
            # For now, we'll just return the driver as-is
            # In a real implementation, you would:
            # 1. Query measurement table for this driver
            # 2. Calculate total_drives, total_distance, total_duration
            # 3. Update last_drive_date
            # 4. Calculate scores based on performance metrics
            
            driver = await self.get_driver(driver_id)
            
            # TODO: Implement statistics calculation from measurement data
            # Example:
            # from app.models.measurement import MeasurementModel
            # measurements = self.session.exec(
            #     select(MeasurementModel).where(MeasurementModel.driver_id == driver_id)
            # ).all()
            # 
            # driver.total_drives = len(measurements)
            # driver.total_distance = sum(m.distance for m in measurements if m.distance)
            # driver.total_duration = sum(m.duration for m in measurements if m.duration)
            # if measurements:
            #     driver.last_drive_date = max(m.local_time.date() for m in measurements)
            
            logger.info(f"Updated statistics for driver {driver_id}")
            return driver
            
        except SQLAlchemyError as e:
            logger.error(f"Database error updating driver statistics {driver_id}: {str(e)}")
            raise InternalServerException(f"Failed to update driver statistics: {str(e)}")
