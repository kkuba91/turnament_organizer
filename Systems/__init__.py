"""__init__.py"""
from Systems._base import System  # noqa: F401
from Systems._swiss import SystemSwiss  # noqa: F401
from Systems._single_elimination import SystemSingleElimination  # noqa: F401
from Systems._circular import SystemCircular  # noqa: F401
from Systems._creation import get_system  # noqa: F401
