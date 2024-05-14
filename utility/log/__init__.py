import inspect
import logging

from .log_setup import setup_logging

frame = inspect.currentframe().f_back
file_path = frame.f_globals["__file__"]
file_name = file_path.split("/")[-1].split(".")[0]

logger = logging.getLogger(file_name)

setup_logging()

__all__ = ['setup_logging', 'logger']