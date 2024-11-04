import logging
import sys

# Configure the logger
def setup_logger(log_file="sync_nested_groups.log"):
    logger = logging.getLogger("SyncNestedGroupsLogger")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler(sys.stdout)

    file_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Initialize and expose the logger globally
logger = setup_logger()
