from typing import Optional, List, Tuple
from uuid import UUID

from sqlmodel import Session, select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.pipelinedependency import PipelineDependencyModel
from app.models.pipelinestate import PipelineStateModel
from app.schemas.pipelinedependency import (
    PipelineDependencyCreate,
    PipelineDependencyUpdate,
    PipelineDependencyFilter,
    PipelineDependencyDetailResponse,
    PipelineDependencyBulkCreate
)


class PipelineDependencyService:
    def __init__(self, session: Session):
        self.session = session

    async def create_pipeline_dependency(self, dependency: PipelineDependencyCreate) -> PipelineDependencyModel:
        db_dependency = PipelineDependencyModel(**dependency.model_dump())
        self.session.add(db_dependency)
        self.session.commit()
        self.session.refresh(db_dependency)
        return db_dependency

    async def get_pipeline_dependency(self, dependency_id: UUID) -> Optional[PipelineDependencyModel]:
        statement = select(PipelineDependencyModel).where(
            PipelineDependencyModel.id == dependency_id
        )
        result = self.session.exec(statement)
        return result.first()

    async def get_pipeline_dependency_detail(self, dependency_id: UUID) -> Optional[PipelineDependencyDetailResponse]:
        # Get the basic dependency first
        dependency = await self.get_pipeline_dependency(dependency_id)
        if not dependency:
            return None
        
        # Get parent and child pipeline state information
        parent_statement = select(PipelineStateModel).where(PipelineStateModel.id == dependency.parent_id)
        parent_result = self.session.exec(parent_statement)
        parent_state = parent_result.first()
        
        child_statement = select(PipelineStateModel).where(PipelineStateModel.id == dependency.child_id)
        child_result = self.session.exec(child_statement)
        child_state = child_result.first()
        
        return PipelineDependencyDetailResponse(
            id=dependency.id,
            parent_id=dependency.parent_id,
            child_id=dependency.child_id,
            created_at=dependency.created_at,
            updated_at=dependency.updated_at,
            parent_name=f"Pipeline State {parent_state.pipeline_id}" if parent_state else "Unknown Parent",
            child_name=f"Pipeline State {child_state.pipeline_id}" if child_state else "Unknown Child"
        )

    async def get_pipeline_dependencies(
        self, filter_params: PipelineDependencyFilter
    ) -> Tuple[List[PipelineDependencyModel], int]:
        statement = select(PipelineDependencyModel)
        
        # Apply filters
        conditions = []
        if filter_params.parent_id:
            conditions.append(PipelineDependencyModel.parent_id == filter_params.parent_id)
        if filter_params.child_id:
            conditions.append(PipelineDependencyModel.child_id == filter_params.child_id)
        
        if conditions:
            statement = statement.where(and_(*conditions))
        
        # Get total count
        count_statement = select(PipelineDependencyModel.id)
        if conditions:
            count_statement = count_statement.where(and_(*conditions))
        count_result = self.session.exec(count_statement)
        total = len(count_result.all())
        
        # Apply pagination
        statement = statement.offset(filter_params.offset).limit(filter_params.limit)
        
        result = self.session.exec(statement)
        dependencies = result.all()
        
        return dependencies, total

    async def update_pipeline_dependency(
        self, dependency_id: UUID, dependency_update: PipelineDependencyUpdate
    ) -> Optional[PipelineDependencyModel]:
        dependency = await self.get_pipeline_dependency(dependency_id)
        if not dependency:
            return None
        
        update_data = dependency_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(dependency, field, value)
        
        self.session.commit()
        self.session.refresh(dependency)
        return dependency

    async def delete_pipeline_dependency(self, dependency_id: UUID) -> bool:
        dependency = await self.get_pipeline_dependency(dependency_id)
        if not dependency:
            return False
        
        self.session.delete(dependency)
        self.session.commit()
        return True

    async def bulk_create_pipeline_dependencies(
        self, bulk_data: PipelineDependencyBulkCreate
    ) -> List[PipelineDependencyModel]:
        if not bulk_data.dependencies:
            raise ValueError("No dependencies provided for bulk creation")
        
        db_dependencies = []
        for dependency_create in bulk_data.dependencies:
            db_dependency = PipelineDependencyModel(**dependency_create.model_dump())
            db_dependencies.append(db_dependency)
            self.session.add(db_dependency)
        
        self.session.commit()
        
        for db_dependency in db_dependencies:
            self.session.refresh(db_dependency)
        
        return db_dependencies

    async def get_dependencies_for_parent(self, parent_id: UUID) -> List[PipelineDependencyModel]:
        statement = select(PipelineDependencyModel).where(
            PipelineDependencyModel.parent_id == parent_id
        )
        result = self.session.exec(statement)
        return result.all()

    async def get_dependencies_for_child(self, child_id: UUID) -> List[PipelineDependencyModel]:
        statement = select(PipelineDependencyModel).where(
            PipelineDependencyModel.child_id == child_id
        )
        result = self.session.exec(statement)
        return result.all()

    async def get_dependency_chain(self, pipeline_state_id: UUID) -> List[PipelineDependencyModel]:
        """Get full dependency chain for a pipeline state (both parents and children)"""
        statement = select(PipelineDependencyModel).where(
            or_(
                PipelineDependencyModel.parent_id == pipeline_state_id,
                PipelineDependencyModel.child_id == pipeline_state_id
            )
        )
        result = self.session.exec(statement)
        return result.all()
