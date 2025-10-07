import uuid
from datetime import datetime, timezone
from uuid import UUID

from app.cores.config import SCHEMA
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    """Return the current UTC time with timezone information."""
    return datetime.now(timezone.utc)


class BaseSQLModel(SQLModel):
    __table_args__ = {"schema": SCHEMA}
    
    # Generate UUID in application layer to avoid NULL identity issues on insert
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)

    def save(self) -> None:
        """Update the `updated_at` timestamp before persisting the instance."""
        self.updated_at = utcnow()
        # Save the instance to the database
