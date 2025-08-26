"""
Timezone and datetime utilities.

This module provides helper functions to convert naive or UTC datetimes
returned by the database into the user's local timezone.  The project’s
requirements specify that all timestamps are stored in UTC in the database,
but responses sent to clients should be presented in the Asia/Taipei
timezone (UTC+8)【695493780409242†L24-L25】.  Use the `to_local` function to
convert a datetime object into this timezone and return an ISO formatted
string.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional

LOCAL_ZONE = ZoneInfo("Asia/Taipei")
UTC_ZONE = timezone.utc

def to_local(dt: Optional[datetime]) -> Optional[str]:
    """
    Convert a naive or timezone‑aware datetime into the Asia/Taipei timezone.
    If `dt` is `None`, returns `None`.  The input is assumed to represent a
    UTC timestamp if it has no timezone information attached.

    Args:
        dt (Optional[datetime]): The datetime to convert.

    Returns:
        Optional[str]: The ISO formatted date/time string in the local
        timezone, or `None` if the input was `None`.
    """
    if dt is None:
        return None
    # Attach UTC timezone if naive
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_ZONE)
    # Convert to local timezone
    local_dt = dt.astimezone(LOCAL_ZONE)
    # Return ISO formatted string without microseconds for readability
    return local_dt.replace(microsecond=0).isoformat()
