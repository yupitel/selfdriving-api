from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
import json


class SensorBase(BaseModel):
    """Base schema for Sensor settings bound to a vehicle.

    - `settings` is a JSON string representing sensor configuration and is
      validated as JSON. The DB stores it directly as JSON/text.
    """

    vehicle_id: UUID = Field(..., description="Associated vehicle ID")
    type: int = Field(..., ge=0, le=32767, description="Sensor type (0-32767)")
    name: Optional[str] = Field(None, max_length=255, description="Logical sensor name (e.g., front-camera)")
    settings: str = Field(..., description="Sensor settings as JSON string")

    @field_validator("settings")
    @classmethod
    def validate_settings_json(cls, v: str) -> str:
        """Ensure `settings` contains valid JSON when provided as string."""
        # Accept dict input by converting to string
        if isinstance(v, (dict, list)):
            return json.dumps(v)
        if isinstance(v, str):
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("settings must be valid JSON string")
            return v
        raise ValueError("settings must be a JSON string or JSON-serializable object")


class SensorCreate(SensorBase):
    """Schema for creating a Sensor settings record"""
    pass


class SensorUpdate(BaseModel):
    """Schema for updating a Sensor settings record"""
    vehicle_id: Optional[UUID] = Field(None, description="Associated vehicle ID")
    type: Optional[int] = Field(None, ge=0, le=32767, description="Sensor type")
    name: Optional[str] = Field(None, max_length=255, description="Logical sensor name")
    settings: Optional[str] = Field(None, description="Sensor settings as JSON string")

    @field_validator("settings")
    @classmethod
    def validate_settings_json(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Accept dict input by converting to string
        if isinstance(v, (dict, list)):
            return json.dumps(v)
        if isinstance(v, str):
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("settings must be valid JSON string")
            return v
        raise ValueError("settings must be a JSON string or JSON-serializable object")


class SensorResponse(SensorBase):
    """Schema for Sensor response"""
    id: UUID
    created_at: int
    updated_at: int
    settings_parsed: Optional[Dict[str, Any]] = Field(None, description="Parsed sensor settings")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj: Any) -> "SensorResponse":
        """Parse JSON fields for convenience on responses."""
        if hasattr(obj, "__dict__"):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)

        raw = data.get("settings")
        if isinstance(raw, (dict, list)):
            data["settings_parsed"] = raw
            data["settings"] = json.dumps(raw)
        elif isinstance(raw, str):
            try:
                data["settings_parsed"] = json.loads(raw)
            except Exception:
                data["settings_parsed"] = None

        return super().model_validate(data)


class SensorFilter(BaseModel):
    """Schema for filtering Sensor settings records"""
    vehicle_id: Optional[UUID] = Field(None, description="Filter by vehicle ID")
    type: Optional[int] = Field(None, ge=0, le=32767, description="Filter by sensor type")
    name: Optional[str] = Field(None, description="Filter by name (partial match)")
    start_time: Optional[datetime] = Field(None, description="Filter by creation time (after)")
    end_time: Optional[datetime] = Field(None, description="Filter by creation time (before)")
    limit: int = Field(100, gt=0, le=1000, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class SensorBulkCreate(BaseModel):
    """Schema for bulk creating Sensor settings"""
    sensors: List[SensorCreate] = Field(
        ..., min_length=1, max_length=1000, description="List of sensor settings to create"
    )


class SensorBulkResponse(BaseModel):
    """Response for bulk operations"""
    created: int = Field(..., description="Number of successfully created items")
    failed: int = Field(..., description="Number of failed items")
    ids: List[UUID] = Field(..., description="IDs of created items")
    errors: List[dict] = Field(default_factory=list, description="Error details for failed items")


class SensorTypeEnum:
    """Enumeration of Sensor types (aligned with datastream types)"""
    CAMERA = 0
    LIDAR = 1
    RADAR = 2
    IMU = 3
    GPS = 4
    CAN = 5
    ULTRASONIC = 6
    THERMAL = 7
    MICROPHONE = 8
    OTHER = 99

    @classmethod
    def get_name(cls, type_value: int) -> str:
        type_map = {
            0: "CAMERA",
            1: "LIDAR",
            2: "RADAR",
            3: "IMU",
            4: "GPS",
            5: "CAN",
            6: "ULTRASONIC",
            7: "THERMAL",
            8: "MICROPHONE",
            99: "OTHER",
        }
        return type_map.get(type_value, "UNKNOWN")

    @classmethod
    def is_valid(cls, type_value: int) -> bool:
        return 0 <= type_value <= 32767

