# Databricks notebook source
# MAGIC %pip install azure-identity

# COMMAND ----------

# MAGIC %pip install msgraph-core==0.2.2
# MAGIC

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import sys
import os
from nestedaaddb.nested_groups import SyncNestedGroups

# Ensure the directory containing logger_config.py is in the Python path
config_dir = os.path.abspath("nestedAADSyn")
if config_dir not in sys.path:
    sys.path.append(config_dir)

# Import and set up the logger
from nestedaaddb.logger_config import setup_logger
logger = setup_logger()

# Create an instance of SyncNestedGroups
sn = SyncNestedGroups()

# Load configuration and run the analysis with error handling
try:
    sn.loadConfig("config.cfg")  # Adjust path if necessary
    logger.info("Configuration loaded successfully.")
    
    sn.analyse("Parent")
    logger.info("Analysis completed successfully.")
except Exception as e:
    logger.error(f"An error occurred: {e}")

# Explicitly flush and close handlers to ensure output is saved
for handler in logger.handlers:
    handler.flush()
    handler.close()





# COMMAND ----------

import sys
import os
from nestedaaddb.nested_groups import SyncNestedGroups

# Ensure the directory containing logger_config.py is in the Python path
config_dir = os.path.abspath("nestedAADSyn")
if config_dir not in sys.path:
    sys.path.append(config_dir)

# Import and set up the logger
from nestedaaddb.logger_config import setup_logger

logger = setup_logger()

# Create an instance of SyncNestedGroups
sn = SyncNestedGroups()

# Load configuration and run the analysis with error handling
try:
    sn.loadConfig("config.cfg")  # Adjust path if necessary
    logger.info("Configuration loaded successfully.")

    sn.sync("Parent",False)
    logger.info("Analysis completed successfully.")
except Exception as e:
    logger.error(f"An error occurred: {e}")

# Explicitly flush and close handlers to ensure output is saved
for handler in logger.handlers:
    handler.flush()
    handler.close()
