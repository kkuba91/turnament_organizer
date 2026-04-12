"""__init__.py"""

from importlib.metadata import version, PackageNotFoundError

from .categories import CATEGORY  # noqa: F401
from .systems import SystemType, SystemNames  # noqa: F401

try:
    __version__ = version("turnament-organizer")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

APPLICATION_NAME = "Tournament Organizer"
