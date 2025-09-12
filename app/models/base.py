import time
import uuid
from uuid import UUID

from app.cores.config import SCHEMA
from sqlmodel import Field, SQLModel


class BaseSQLModel(SQLModel):
    __table_args__ = {"schema": SCHEMA}
    
    # Generate UUID in application layer to avoid NULL identity issues on insert
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    created_at: int = Field(..., nullable=False)
    updated_at: int = Field(..., nullable=False)

    def __init__(self, **data):
        super().__init__(**data)
        self.created_at = int(time.time())
        self.updated_at = int(time.time())

    def save(self):
        self.updated_at = int(time.time())
        # Save the instance to the database
