"""Datetime utilities for ensuring timezone-aware comparisons."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Return a UTC-aware datetime.

    Database columns use `TIMESTAMPTZ`, so we normalize filter inputs that might
    arrive without timezone information. Naive datetimes are assumed to be UTC.
    """
    if dt is None:
        return None
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
