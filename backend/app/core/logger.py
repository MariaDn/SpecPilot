import logging
import sys

LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"

def setup_logger(name: str):
  logger = logging.getLogger(name)
  logger.setLevel(logging.INFO)
  
  handler = logging.StreamHandler(sys.stdout)
  handler.setFormatter(logging.Formatter(LOG_FORMAT))
  
  if not logger.handlers:
      logger.addHandler(handler)
  
  return logger

logger = setup_logger("ENFORENCE")