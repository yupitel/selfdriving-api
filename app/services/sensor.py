import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import Session, select, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.sensor import SensorModel
from app.schemas.sensor import (
    SensorUpdate,
    SensorFilter,
    SensorBulkCreate,
    SensorTypeEnum,
)
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
    InternalServerException,
)
from app.cores.config import BULK_INSERT_MAX_NUM

logger = logging.getLogger(__name__)


class SensorService:
    """Service class for Sensor settings operations"""

    def __init__(self, db_session: Session):
        self.session = db_session

    async def get_sensor(self, sensor_id: UUID) -> SensorModel:
        """Get a sensor by ID or raise NotFound"""
        try:
            statement = select(SensorModel).where(SensorModel.id == sensor_id)
            sensor = self.session.exec(statement).first()
            if not sensor:
                raise NotFoundException(f"Sensor with ID {sensor_id} not found")
            return sensor
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching sensor {sensor_id}: {str(e)}")
            raise InternalServerException(f"Failed to fetch sensor: {str(e)}")

    async def get_sensors_by_id(self, sensor_id: UUID) -> List[SensorModel]:
        """Get sensor(s) by ID as a list (0 or 1)."""
        try:
            statement = select(SensorModel).where(SensorModel.id == sensor_id)
            sensors = self.session.exec(statement).all()
            return list(sensors)
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching sensor list {sensor_id}: {str(e)}")
            raise InternalServerException(f"Failed to fetch sensors: {str(e)}")

    async def list_sensors(self, filters: SensorFilter) -> List[SensorModel]:
        """List sensors with optional filters"""
        try:
            statement = select(SensorModel)

            conditions = []
            if filters.vehicle_id:
                conditions.append(SensorModel.vehicle_id == filters.vehicle_id)
            if filters.type is not None:
                conditions.append(SensorModel.type == filters.type)
            if filters.name:
                conditions.append(SensorModel.name.contains(filters.name))
            if filters.start_time:
                conditions.append(SensorModel.created_at >= filters.start_time)
            if filters.end_time:
                conditions.append(SensorModel.created_at <= filters.end_time)

            if conditions:
                statement = statement.where(and_(*conditions))

            statement = statement.order_by(SensorModel.created_at.desc())
            statement = statement.limit(filters.limit).offset(filters.offset)

            sensors = self.session.exec(statement).all()
            logger.info(f"Listed {len(sensors)} sensors with filters")
            return list(sensors)
        except SQLAlchemyError as e:
            logger.error(f"Database error listing sensors: {str(e)}")
            raise InternalServerException(f"Failed to list sensors: {str(e)}")

    async def update_sensor(self, sensor_id: UUID, update_data: SensorUpdate) -> SensorModel:
        """Update a sensor settings record"""
        # Validate type if provided
        update_dict = update_data.model_dump(exclude_unset=True)
        if "type" in update_dict and not SensorTypeEnum.is_valid(update_dict["type"]):
            raise BadRequestException(f"Invalid sensor type: {update_dict['type']}")

        try:
            sensor = await self.get_sensor(sensor_id)

            for field, value in update_dict.items():
                setattr(sensor, field, value)

            # Update timestamp stored as epoch seconds in BaseSQLModel
            sensor.updated_at = int(datetime.utcnow().timestamp())

            self.session.add(sensor)
            self.session.commit()
            self.session.refresh(sensor)
            logger.info(f"Updated sensor {sensor_id}")
            return sensor
        except IntegrityError as e:
            self.session.rollback()
            raise ConflictException(f"Update conflict: {str(e)}")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error updating sensor {sensor_id}: {str(e)}")
            raise InternalServerException(f"Failed to update sensor: {str(e)}")

    async def delete_sensor(self, sensor_id: UUID) -> None:
        """Delete a sensor settings record"""
        try:
            sensor = await self.get_sensor(sensor_id)
            self.session.delete(sensor)
            self.session.commit()
            logger.info(f"Deleted sensor {sensor_id}")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error deleting sensor {sensor_id}: {str(e)}")
            raise InternalServerException(f"Failed to delete sensor: {str(e)}")

    async def create_sensors(self, bulk_data: SensorBulkCreate) -> dict:
        """Bulk create sensor settings records"""
        if len(bulk_data.sensors) > BULK_INSERT_MAX_NUM:
            raise BadRequestException(
                f"Too many sensors. Maximum allowed: {BULK_INSERT_MAX_NUM}"
            )

        created_ids: List[UUID] = []
        errors: List[dict] = []

        try:
            for idx, sensor_data in enumerate(bulk_data.sensors):
                try:
                    if not SensorTypeEnum.is_valid(sensor_data.type):
                        errors.append(
                            {
                                "index": idx,
                                "error": f"Invalid sensor type: {sensor_data.type}",
                                "data": sensor_data.model_dump(),
                            }
                        )
                        continue

                    sensor = SensorModel(**sensor_data.model_dump())
                    self.session.add(sensor)
                    self.session.flush()
                    created_ids.append(sensor.id)
                except IntegrityError as e:
                    errors.append(
                        {
                            "index": idx,
                            "error": str(e),
                            "data": sensor_data.model_dump(),
                        }
                    )
                except Exception as e:
                    errors.append(
                        {
                            "index": idx,
                            "error": str(e),
                            "data": sensor_data.model_dump(),
                        }
                    )

            if created_ids:
                self.session.commit()
                logger.info(f"Bulk created {len(created_ids)} sensors")
            else:
                self.session.rollback()

            return {
                "created": len(created_ids),
                "failed": len(errors),
                "ids": created_ids,
                "errors": errors,
            }
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error in bulk create sensors: {str(e)}")
            raise InternalServerException(f"Failed to bulk create sensors: {str(e)}")

