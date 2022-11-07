"""__init__.py"""
# noqa: F401
from .player import CATEGORY, Player
from .round import Round
from .system import (
    System,
    SystemCircular,
    SystemSingleElimination,
    SystemSwiss,
    set_system,
    SystemType,
)
from .table import Table
