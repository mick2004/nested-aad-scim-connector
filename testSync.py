import logging
import sys
import os
from nestedaaddb.nested_groups import SyncNestedGroups

# Ensure the directory containing logger_config.py is in the Python path
config_dir = os.path.abspath("nestedAADSyn")
if config_dir not in sys.path:
    sys.path.append(config_dir)

# Import and set up the logger
from logger_config import setup_logger

logger = setup_logger()
logger.setLevel(logging.WARN)

# Create an instance of SyncNestedGroups
sn = SyncNestedGroups()

# Load configuration and run the analysis with error handling
try:
    sn.loadConfig("/Users/abhishekpratap.singh/Desktop/DesktopAsOf25Jan2024/nestedAADSynBakUp16Nov/config//config.cfg")  # Adjust path if necessary
    logger.info("Configuration loaded successfully.")

    sn.sync("<<Top level group>>",False)
    logger.info("Analysis completed successfully.")
except Exception as e:
    logger.error(f"An error occurred: {e}")

# Explicitly flush and close handlers to ensure output is saved
for handler in logger.handlers:
    handler.flush()
    handler.close()