"""
Logging configuration for Smart Study Assistant
"""

import logging
import os
from config import LOG_FILE, LOG_FORMAT, LOG_LEVEL

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)


def get_logger(name):
    """Get a logger instance for a module"""
    return logging.getLogger(name)
