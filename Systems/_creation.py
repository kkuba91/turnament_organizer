"""_creation.py

    System object 'factory' function.

"""
# Global package imports:
import logging

# Local package imports:
from Systems import SystemCircular, SystemSingleElimination, SystemSwiss
from Resources import SystemType


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
