"""Converters for timeoutd."""

from __future__ import annotations

from datetime import datetime, timedelta


def time_to_seconds(
    limit: float | datetime | timedelta | None = None,
    *,
    seconds: float | None = None,
    minutes: float | None = None,
    hours: float | None = None,
) -> float:
    """Convert time to seconds."""
    if limit is not None:
        if isinstance(limit, datetime):
            return (limit - datetime.now()).total_seconds()
        if isinstance(limit, timedelta):
            return limit.total_seconds()
        return limit
    if seconds is None:
        seconds = 0
    if minutes is None:
        minutes = 0
    if hours is None:
        hours = 0
    return seconds + (minutes * 60) + (hours * 3600)
