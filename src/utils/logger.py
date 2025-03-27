import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logger(name: str = "lia_logger", level: int = logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create a stream handler (to STDOUT)
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    
    return logger

# Initialize the logger
logger = setup_logger()
