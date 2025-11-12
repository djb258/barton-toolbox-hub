"""
Logger Core Module
Contains event logging engine with Neon/Firebase failover.
"""
from .event_logger import (
    EventLogger,
    EventLevel,
    EventType,
    get_event_logger
)

__all__ = [
    "EventLogger",
    "EventLevel",
    "EventType",
    "get_event_logger",
]
