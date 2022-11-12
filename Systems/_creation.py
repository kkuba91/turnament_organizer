"""_creation.py

    System class with calculation model, players organization and ranks estimation.
    This class is strictly related with class Player, Round - must be.

"""
# Global package imports:
import logging

# Local package imports:
from Systems import SystemCircular, SystemSingleElimination, SystemSwiss
from resources import SystemType


def get_system(system_type: int):
    # Factory conversion to child-class object:
    system = None
    if system_type == SystemType.SWISS:
        system = SystemSwiss()
    elif system_type == SystemType.CIRCULAR:
        system = SystemCircular()
    elif system_type == SystemType.SINGLE_ELIMINATION:
        system = SystemSingleElimination()
    else:
        msg_error = f"Wrong system typed. Please type valid system key."
        logging.error(msg=msg_error)
        return system
    return system
