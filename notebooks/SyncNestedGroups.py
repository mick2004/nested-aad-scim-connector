# Databricks notebook source
dbutils.widgets.text("txtTopGroup", "","Enter Top Level Group to Sync")
dbutils.widgets.dropdown("txtIsDryRun", "True",['True','False'])

# COMMAND ----------

# MAGIC %md
# MAGIC Before running code,go to repo and create a new file config.cfg with relevant attributes https://github.com/mick2004/AzureAADDatabricksConnector/blob/main/README.md
# MAGIC For prod use recommended to store these in Databricks Vault https://learn.microsoft.com/en-us/azure/databricks/security/secrets/secret-scopes

# COMMAND ----------

# MAGIC %md
# MAGIC Install necessary dependencies

# COMMAND ----------

# MAGIC %pip install azure-identity

# COMMAND ----------

# MAGIC %pip install msgraph-core

# COMMAND ----------

# MAGIC %md
# MAGIC Import dependencies

# COMMAND ----------

import sys

import configparser

from model.DatabricksClient import DatabricksClient
from model.Graph import Graph
from collections import defaultdict

groupgp = defaultdict(set)
distinct_users = set()
distinct_groups = set()

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC The Input source top level group is printed here.This is the group which will be synced including all the nested child groups

# COMMAND ----------

toplevelgroup = dbutils.widgets.get("txtTopGroup")

print("top level group input is :"+toplevelgroup)

dryrun = eval(dbutils.widgets.get("txtIsDryRun"))

print("Is This Dry Run :"+str(dryrun))

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC Load the config and initialize the client

# COMMAND ----------

config = configparser.ConfigParser()
config.read(['../config/config.cfg', 'config.dev.cfg'])
azure_settings = config['azure']
db_settings = config['databricks']

graph: Graph = Graph(azure_settings)
dbclient: DatabricksClient = DatabricksClient(db_settings)

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC Read all Databricks Users and groups.

# COMMAND ----------

dbusers = dbclient.get_dbusers()
dbgroups = dbclient.get_dbgroups()
print("1.All Databricks Users and Groups Read")

# COMMAND ----------

# MAGIC %md
# MAGIC Read All groups from AAD.This is required to identify needed groups and extract their AAD id for further API calls

# COMMAND ----------

groups_page = graph.get_groups()

print("2.All AAD groups Read")

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC The input group along with AAD groups analysed recursively to extract all relevant groups and users.All nested groups and their users will be recorded in:
# MAGIC 
# MAGIC groupgpU

# COMMAND ----------

colInitialised = False;
for group in groups_page['value']:
    
    if toplevelgroup.casefold() == group["displayName"].casefold():
          distinct_groupsU, distinct_usersU, groupgpU = graph.extract_children_from_group(graph,
                                                                                group["id"],
                                                                                group["displayName"],
                                                                                distinct_groups,
                                                                                distinct_users,
                                                                                groupgp);
          colInitialised = True

print("4.Hierarchy analysed,going to create users and groups")

# COMMAND ----------

# MAGIC %md
# MAGIC Lets see content of the analysis i.e. user and group maps

# COMMAND ----------

print("Is there some groups and users retrieved :"+str(colInitialised))

# COMMAND ----------

if colInitialised:
    print(distinct_groupsU)

# COMMAND ----------

# MAGIC %md
# MAGIC Compare users and groups in Databricks with AAD and add if dont exist.
# MAGIC 
# MAGIC Note:
# MAGIC 
# MAGIC 1. Only users/groups under top level group or their derived groups are considered
# MAGIC 
# MAGIC 2. Users and groups are not deleted from databricks (however we will remove group user assosciation if user dont exist in AAD)

# COMMAND ----------

if colInitialised:
    for u in distinct_usersU:

        exists = False

        for udb in dbusers["Resources"]:
            if u[0].casefold() == udb["displayName"].casefold():
                exists = True;

        if not exists:
            dbclient.create_dbuser(u, dryrun)

    for u in distinct_groupsU:
        exists = False
        for dbg in dbgroups["Resources"]:
            if u.casefold() == dbg["displayName"].casefold():
                exists = True

        if not exists:
            dbclient.create_blank_dbgroup(u, dryrun)

# COMMAND ----------

# MAGIC %md
# MAGIC Patch Groups in Databricks with groupMap derived from AAD.
# MAGIC 
# MAGIC 1.Update group membership (add/remove) as per AAD

# COMMAND ----------

if colInitialised:
  dbusers = dbclient.get_dbusers()
  dbgroups = dbclient.get_dbgroups()
  print(dbgroups["Resources"])


  for u in distinct_groupsU:
      exists = False
      for dbg in dbgroups["Resources"]:
          if u.casefold() == dbg["displayName"].casefold():
              exists = True
              # compare and add remove the members as needed
              dbclient.patch_dbgroup(dbg["id"], groupgpU.get(u), dbg, dbusers, dbgroups, dryrun)
else:
  print("No action required as did not found any users/groups under AAD.Please check top level group exists an AAD and have some users or groups.")
              

