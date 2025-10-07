import logging
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, and_, or_
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.vehicle import VehicleModel
from app.schemas.vehicle import (
    VehicleUpdate,
    VehicleFilter,
    VehicleBulkCreate
)
from app.utils.datetime import ensure_utc
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
    InternalServerException
)
from app.cores.config import BULK_INSERT_MAX_NUM

logger = logging.getLogger(__name__)


class VehicleService:
    """Service class for Vehicle operations"""
    
    def __init__(self, db_session: Session):
        self.session = db_session
    
    # Note: Single create is removed in favor of bulk-at-root API usage.
    
    async def get_vehicle(self, vehicle_id: UUID) -> VehicleModel:
        """Get a vehicle by ID"""
        try:
            statement = select(VehicleModel).where(VehicleModel.id == vehicle_id)
            vehicle = self.session.exec(statement).first()
            
            if not vehicle:
                raise NotFoundException(f"Vehicle with ID {vehicle_id} not found")
            
            return vehicle
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching vehicle {vehicle_id}: {str(e)}")
            raise InternalServerException(f"Failed to fetch vehicle: {str(e)}")

    async def get_vehicles_by_id(self, vehicle_id: UUID) -> List[VehicleModel]:
        """Get vehicle(s) by ID as a list (0 or 1 items)."""
        try:
            statement = select(VehicleModel).where(VehicleModel.id == vehicle_id)
            vehicles = self.session.exec(statement).all()
            return list(vehicles)
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching vehicles list {vehicle_id}: {str(e)}")
            raise InternalServerException(f"Failed to fetch vehicles: {str(e)}")
    
    async def list_vehicles(self, filters: VehicleFilter) -> List[VehicleModel]:
        """List vehicles with optional filters"""
        try:
            statement = select(VehicleModel)
            
            # Build filter conditions
            conditions = []
            
            if filters.country:
                conditions.append(VehicleModel.country == filters.country)
            
            if filters.name:
                conditions.append(VehicleModel.name.contains(filters.name))
            
            if filters.data_path:
                conditions.append(VehicleModel.data_path.contains(filters.data_path))
            
            if filters.type is not None:
                conditions.append(VehicleModel.type == filters.type)
            
            if filters.status is not None:
                conditions.append(VehicleModel.status == filters.status)
            
            if filters.start_time:
                conditions.append(VehicleModel.created_at >= filters.start_time)
            
            if filters.end_time:
                conditions.append(VehicleModel.created_at <= filters.end_time)
            
            # Apply filters
            if conditions:
                statement = statement.where(and_(*conditions))
            
            # Apply ordering and pagination
            statement = statement.order_by(VehicleModel.created_at.desc())
            statement = statement.limit(filters.limit).offset(filters.offset)
            
            # Execute query
            vehicles = self.session.exec(statement).all()
            
            logger.info(f"Listed {len(vehicles)} vehicles with filters")
            return list(vehicles)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error listing vehicles: {str(e)}")
            raise InternalServerException(f"Failed to list vehicles: {str(e)}")

    async def count_vehicles(self, filters: VehicleFilter) -> int:
        """Count vehicles matching filters using SELECT COUNT(*)"""
        try:
            statement = select(func.count()).select_from(VehicleModel)

            conditions = []
            if filters.country:
                conditions.append(VehicleModel.country == filters.country)
            if filters.name:
                conditions.append(VehicleModel.name.contains(filters.name))
            if filters.data_path:
                conditions.append(VehicleModel.data_path.contains(filters.data_path))
            if filters.type is not None:
                conditions.append(VehicleModel.type == filters.type)
            if filters.status is not None:
                conditions.append(VehicleModel.status == filters.status)
            if filters.start_time:
                conditions.append(VehicleModel.created_at >= ensure_utc(filters.start_time))
            if filters.end_time:
                conditions.append(VehicleModel.created_at <= ensure_utc(filters.end_time))

            if conditions:
                statement = statement.where(and_(*conditions))

            result = self.session.exec(statement).one()
            # SQLAlchemy/SQLModel may return scalar or tuple depending on driver
            return int(result[0] if isinstance(result, tuple) else result)
        except SQLAlchemyError as e:
            logger.error(f"Database error counting vehicles: {str(e)}")
            raise InternalServerException(f"Failed to count vehicles: {str(e)}")
    
    async def update_vehicle(
        self, 
        vehicle_id: UUID, 
        update_data: VehicleUpdate
    ) -> VehicleModel:
        """Update a vehicle"""
        try:
            # Get existing vehicle
            vehicle = await self.get_vehicle(vehicle_id)
            
            # Update fields
            update_dict = update_data.model_dump(exclude_unset=True)
            
            for field, value in update_dict.items():
                setattr(vehicle, field, value)
            
            vehicle.save()
            
            # Commit changes
            self.session.add(vehicle)
            self.session.commit()
            self.session.refresh(vehicle)
            
            logger.info(f"Updated vehicle {vehicle_id}")
            return vehicle
            
        except IntegrityError as e:
            self.session.rollback()
            if "unique" in str(e).lower():
                raise ConflictException(f"Vehicle with this name already exists")
            raise ConflictException(f"Update conflict: {str(e)}")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error updating vehicle {vehicle_id}: {str(e)}")
            raise InternalServerException(f"Failed to update vehicle: {str(e)}")
    
    async def delete_vehicle(self, vehicle_id: UUID) -> None:
        """Delete a vehicle"""
        try:
            # Get existing vehicle
            vehicle = await self.get_vehicle(vehicle_id)
            
            # Delete from database
            self.session.delete(vehicle)
            self.session.commit()
            
            logger.info(f"Deleted vehicle {vehicle_id}")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error deleting vehicle {vehicle_id}: {str(e)}")
            raise InternalServerException(f"Failed to delete vehicle: {str(e)}")
    
    async def create_vehicles(
        self, 
        bulk_data: VehicleBulkCreate
    ) -> dict:
        """Bulk create vehicles"""
        if len(bulk_data.vehicles) > BULK_INSERT_MAX_NUM:
            raise BadRequestException(
                f"Too many vehicles. Maximum allowed: {BULK_INSERT_MAX_NUM}"
            )
        
        created_ids = []
        errors = []
        
        try:
            for idx, vehicle_data in enumerate(bulk_data.vehicles):
                try:
                    # Create vehicle
                    vehicle = VehicleModel(**vehicle_data.model_dump())
                    self.session.add(vehicle)
                    self.session.flush()  # Flush to get ID without committing
                    created_ids.append(vehicle.id)
                    
                except IntegrityError as e:
                    errors.append({
                        "index": idx,
                        "error": str(e),
                        "data": vehicle_data.model_dump()
                    })
                except Exception as e:
                    errors.append({
                        "index": idx,
                        "error": str(e),
                        "data": vehicle_data.model_dump()
                    })
            
            # Commit all successful creations
            if created_ids:
                self.session.commit()
                logger.info(f"Bulk created {len(created_ids)} vehicles")
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
            raise InternalServerException(f"Failed to bulk create vehicles: {str(e)}")
    
    async def get_vehicle_by_name(self, name: str) -> Optional[VehicleModel]:
        """Get a vehicle by name"""
        try:
            statement = select(VehicleModel).where(VehicleModel.name == name)
            vehicle = self.session.exec(statement).first()
            return vehicle
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching vehicle by name {name}: {str(e)}")
            raise InternalServerException(f"Failed to fetch vehicle: {str(e)}")
    
    async def get_vehicles_by_country(
        self, 
        country: str,
        limit: int = 100
    ) -> List[VehicleModel]:
        """Get all vehicles for a specific country"""
        try:
            statement = select(VehicleModel).where(
                VehicleModel.country == country
            ).limit(limit)
            
            vehicles = self.session.exec(statement).all()
            
            logger.info(f"Found {len(vehicles)} vehicles for country {country}")
            return list(vehicles)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching vehicles for country {country}: {str(e)}")
            raise InternalServerException(f"Failed to fetch vehicles: {str(e)}")
    
    async def get_vehicle_statistics(self) -> dict:
        """Get statistics about vehicles"""
        try:
            # Get all vehicles for statistics
            all_vehicles = self.session.exec(select(VehicleModel)).all()
            
            # Count by country
            country_counts = {}
            for vehicle in all_vehicles:
                if vehicle.country:
                    country_counts[vehicle.country] = country_counts.get(vehicle.country, 0) + 1
            
            # Count by type
            type_counts = {}
            for vehicle in all_vehicles:
                type_counts[vehicle.type] = type_counts.get(vehicle.type, 0) + 1
            
            # Count by status
            status_counts = {}
            for vehicle in all_vehicles:
                status_counts[vehicle.status] = status_counts.get(vehicle.status, 0) + 1
            
            # Count vehicles with data_path
            with_data_path = len([v for v in all_vehicles if v.data_path is not None])
            
            return {
                "total": len(all_vehicles),
                "by_country": country_counts,
                "by_type": type_counts,
                "by_status": status_counts,
                "with_data_path": with_data_path
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting statistics: {str(e)}")
            raise InternalServerException(f"Failed to get statistics: {str(e)}")
