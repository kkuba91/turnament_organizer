"""logger.py

    Application logger.

"""
# Global package imports:
from colorama import init, Fore, Style
import logging

from fastapi.logger import logger as fastapi_logger

init(autoreset=True)


class FMT:
    """Format data class."""
    asctime = Fore.LIGHTBLACK_EX + "%(asctime)s " + Style.RESET_ALL
    levelname = "%(levelname)-6s" + Style.RESET_ALL
    message = "%(message)s"


FORMATS = {
    logging.WARNING: FMT.asctime
    + "[ "
    + Fore.YELLOW
    + FMT.levelname
    + "] "
    + FMT.message,
    logging.ERROR: FMT.asctime + "[ " + Fore.RED + FMT.levelname + "] " + FMT.message,
    logging.DEBUG: FMT.asctime + "[ " + Fore.BLUE + FMT.levelname + "] " + FMT.message,
    logging.INFO: FMT.asctime
    + "[ "
    + Fore.LIGHTGREEN_EX
    + FMT.levelname
    + "] "
    + FMT.message,
    logging.CRITICAL: FMT.asctime
    + "[ "
    + Fore.RED
    + FMT.levelname
    + "] "
    + FMT.message,
    logging.NOTSET: FMT.asctime + "[ " + FMT.levelname + "] " + FMT.message,
}


class CustomFormatter(logging.Formatter):
    """Custom - color formatter class."""

    def format(self, record):
        _fmt = FORMATS.get(record.levelno)
        formatter = logging.Formatter(fmt=_fmt)
        return formatter.format(record=record)


def debug(func):
    """Debug filtered action - @decorator."""

    def function_handler(*args, **kvargs):
        _ret = None
        _level = logging.getLogger().getEffectiveLevel()
        if _level == logging.DEBUG:
            _ret = func(*args, **kvargs)
        else:
            msg_debug = "Debugging is switched OFF!"
            logging.debug(msg=msg_debug)
        return _ret

    return function_handler


def set_logging(**kwargs):
    """Set logging configuration."""
    _debug = kwargs.pop("debug", None)
    if 'logger_name' in kwargs:
        logger = logging.getLogger(kwargs['logger_name'])
    else:
        logger = logging.getLogger()
    stdout_handler = logging.StreamHandler()
    if _debug:
        logger.setLevel(level=logging.DEBUG)
        stdout_handler.setLevel(level=logging.DEBUG)
    else:
        logger.setLevel(level=logging.INFO)
        stdout_handler.setLevel(level=logging.INFO)
    stdout_handler.setFormatter(CustomFormatter())
    logger.addHandler(stdout_handler)

    if _debug:
        msg_debug = "Debugging is switched ON!"
        logging.debug(msg=msg_debug)

    return logger


def set_fastapi_logging(**kwargs):
    """Set logging configuration."""
    _debug = kwargs.pop("debug", None)
    logger = fastapi_logger
    stdout_handler = logging.StreamHandler()
    if _debug:
        logger.setLevel(level=logging.DEBUG)
        stdout_handler.setLevel(level=logging.DEBUG)
    else:
        logger.setLevel(level=logging.INFO)
        stdout_handler.setLevel(level=logging.INFO)
    stdout_handler.setFormatter(CustomFormatter())
    logger.addHandler(stdout_handler)
    if _debug:
        msg_debug = "Debugging is switched ON!"
        logging.debug(msg=msg_debug)
    return logger


def log_method(obj=object, func=None):
    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
        logging.debug("Call method: {}(), from {}". format(func.__name__, obj.__class__.__name__))
