"""
Logging utility for GitHub Actions
"""

import logging
import sys
from datetime import datetime

def setup_logger(name: str) -> logging.Logger:
    """
    Setup logger with proper formatting
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console.setFormatter(formatter)
    
    logger.addHandler(console)
    
    return logger
