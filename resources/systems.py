"""systems.py

    System types resources.

"""
from enum import IntEnum


class SystemType(IntEnum):

    """System Types (Enum)."""

    UNKNOWN = 0
    SWISS = 1
    CIRCULAR = 2
    SINGLE_ELIMINATION = 3


SystemNames = {
    SystemType.UNKNOWN: "Unknown",
    SystemType.SWISS: "Swiss",
    SystemType.CIRCULAR: "Circular",
    SystemType.SINGLE_ELIMINATION: "Single Elimination",
}