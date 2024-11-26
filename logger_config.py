import logging
import sys
import os
from logging.handlers import RotatingFileHandler

# Configure the logger
def setup_logger():
    # Set log file to a relative path or Databricks-friendly path
    log_file = os.path.join(os.getcwd(), "sync_nested_groups.log")  # Use current directory
    logger = logging.getLogger("SyncNestedGroupsLogger")
    logger.setLevel(logging.INFO)  # Set overall logging level to INFO

    # Avoid re-adding handlers if already added
    if not logger.handlers:
        # Replace FileHandler with RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=100  # 5 MB max file size, 100 backup files
        )
        console_handler = logging.StreamHandler(sys.stdout)

        # Set logging levels for handlers
        file_handler.setLevel(logging.INFO)
        console_handler.setLevel(logging.INFO)

        # Set log format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# Initialize and expose the logger globally
logger = setup_logger()
