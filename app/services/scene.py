import logging
from typing import List
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session, select, and_

from app.models.scene import SceneDataModel
from app.schemas.scene import SceneCreate, SceneUpdate, SceneFilter
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
    InternalServerException,
)

logger = logging.getLogger(__name__)


class SceneService:
    """Service class for Scene operations"""

    def __init__(self, db_session: Session):
        self.session = db_session

    async def create_scene(self, scene_data: SceneCreate) -> SceneDataModel:
        """Create a new scene"""
        try:
            # Basic validation: indices
            if scene_data.end_idx < scene_data.start_idx:
                raise BadRequestException("end_idx must be greater than or equal to start_idx")

            scene = SceneDataModel(**scene_data.model_dump())
            self.session.add(scene)
            self.session.commit()
            self.session.refresh(scene)
            logger.info(f"Created scene with ID: {scene.id}")
            return scene
        except IntegrityError as e:
            self.session.rollback()
            if "foreign key" in str(e).lower():
                raise BadRequestException("Invalid foreign key: datastream_id does not exist")
            raise ConflictException(f"Scene constraint violation: {str(e)}")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error creating scene: {str(e)}")
            raise InternalServerException(f"Failed to create scene: {str(e)}")

    async def get_scene(self, scene_id: UUID) -> SceneDataModel:
        """Get a scene by ID"""
        try:
            statement = select(SceneDataModel).where(SceneDataModel.id == scene_id)
            scene = self.session.exec(statement).first()
            if not scene:
                raise NotFoundException(f"Scene with ID {scene_id} not found")
            return scene
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching scene {scene_id}: {str(e)}")
            raise InternalServerException(f"Failed to fetch scene: {str(e)}")

    async def list_scenes(self, filters: SceneFilter) -> List[SceneDataModel]:
        """List scenes with optional filters"""
        try:
            statement = select(SceneDataModel)

            conditions = []
            if filters.type is not None:
                conditions.append(SceneDataModel.type == filters.type)
            if filters.state is not None:
                conditions.append(SceneDataModel.state == filters.state)
            if filters.datastream_id is not None:
                conditions.append(SceneDataModel.datastream_id == filters.datastream_id)
            if filters.name:
                conditions.append(SceneDataModel.name.contains(filters.name))
            if filters.start_time:
                conditions.append(SceneDataModel.created_at >= int(filters.start_time.timestamp()))
            if filters.end_time:
                conditions.append(SceneDataModel.created_at <= int(filters.end_time.timestamp()))

            if conditions:
                statement = statement.where(and_(*conditions))

            statement = statement.order_by(SceneDataModel.created_at.desc())
            statement = statement.limit(filters.limit).offset(filters.offset)

            scenes = self.session.exec(statement).all()
            return list(scenes)
        except SQLAlchemyError as e:
            logger.error(f"Database error listing scenes: {str(e)}")
            raise InternalServerException(f"Failed to list scenes: {str(e)}")

    async def update_scene(self, scene_id: UUID, update_data: SceneUpdate) -> SceneDataModel:
        """Update an existing scene"""
        try:
            scene = await self.get_scene(scene_id)

            update_dict = update_data.model_dump(exclude_unset=True)

            if {
                k: v
                for k, v in update_dict.items()
                if k in {"start_idx", "end_idx"}
            }:
                start_idx = update_dict.get("start_idx", scene.start_idx)
                end_idx = update_dict.get("end_idx", scene.end_idx)
                if end_idx < start_idx:
                    raise BadRequestException("end_idx must be greater than or equal to start_idx")

            for field, value in update_dict.items():
                setattr(scene, field, value)

            scene.save()  # updates updated_at
            self.session.add(scene)
            self.session.commit()
            self.session.refresh(scene)
            logger.info(f"Updated scene {scene_id}")
            return scene
        except IntegrityError as e:
            self.session.rollback()
            if "foreign key" in str(e).lower():
                raise BadRequestException("Invalid foreign key: datastream_id does not exist")
            raise ConflictException(f"Scene update conflict: {str(e)}")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error updating scene {scene_id}: {str(e)}")
            raise InternalServerException(f"Failed to update scene: {str(e)}")

    async def delete_scene(self, scene_id: UUID) -> None:
        """Delete a scene by ID"""
        try:
            scene = await self.get_scene(scene_id)
            self.session.delete(scene)
            self.session.commit()
            logger.info(f"Deleted scene {scene_id}")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error deleting scene {scene_id}: {str(e)}")
            raise InternalServerException(f"Failed to delete scene: {str(e)}")

