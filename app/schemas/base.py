from typing import Optional, TypeVar, Generic, Any, Union
from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime
from uuid import UUID

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Base response model with backward-compatible fields.
    - Canonical boolean is `result`.
    - Accepts/produces `success` for compatibility and keeps it in sync with `result`.
    - Accepts `error` as dict or str; coerces str to {"message": str}.
    - Optional `message` field for human-readable info.
    """

    # Canonical success flag
    result: bool
    # Backward compatibility flag; kept in sync with `result`
    success: Optional[bool] = None

    data: Optional[T] = None
    error: Optional[Union[dict[str, Any], str]] = None
    message: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_legacy_fields(cls, values: Any):
        if isinstance(values, dict):
            # Map `success` to `result` if provided
            if "success" in values and "result" not in values:
                values["result"] = bool(values["success"])
            # Mirror `result` to `success` if only `result` provided
            if "result" in values and "success" not in values:
                values["success"] = bool(values["result"])

            # Normalize error to dict form
            err = values.get("error")
            if err is not None and not isinstance(err, dict):
                values["error"] = {"message": str(err)}

        return values


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    per_page: int = 20
    total: Optional[int] = None


class PaginatedResponse(BaseResponse[T]):
    """Paginated response model"""
    pagination: Optional[PaginationParams] = None
