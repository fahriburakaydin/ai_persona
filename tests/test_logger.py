# tests/test_logger.py
import logging
from src.utils.logger import setup_logger

def test_logger_setup():
    logger = setup_logger("test_logger")
    # Ensure the logger is an instance of logging.Logger
    assert isinstance(logger, logging.Logger)
    # Ensure that at least one handler is attached
    assert len(logger.handlers) > 0
