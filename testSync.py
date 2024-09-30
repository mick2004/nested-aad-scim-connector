from nestedaaddb.nested_groups import SyncNestedGroups
sn = SyncNestedGroups()
sn.loadConfig("/Users/abhishekpratap.singh/Desktop/DesktopAsOf25Jan2024/nestedAADSynBakUp16Nov/config/config.cfg")
sn.sync("Parent",False)
#print(sn.createGroup("1111"))

# import logging
# import sys
# import os
# import coloredlogs
#
# from nestedaaddb.scim import get_account_client
#
# os.environ.setdefault('DATABRICKS_ACCOUNT_ID', '7e173b8f-96e4-4102-967e-f8950a1f5d5d')
# os.environ.setdefault('DATABRICKS_HOST', 'https://accounts.azuredatabricks.net')
# os.environ.setdefault('DATABRICKS_TOKEN', 'dsapi27a20c9cb95cacaa3abe880f1db6a28a')
#
# account_client = get_account_client()
#
# # test connectivity
# dbgroups = account_client.groups.list()
#
# for g in dbgroups:
#     print(g.display_name)
#     print("1")
#
# # pushes objects to SCIM
# sync_results = sync(
#     account_client=account_client,
#     users=[x.to_sdk_user() for x in data.users.values()],
#     groups=[x.to_sdk_group() for x in data.groups.values()],
#     service_principals=[x.to_sdk_service_principal() for x in data.service_principals.values()],
#     deep_sync_group_names=list(data.deep_sync_group_names),
#     dry_run_security_principals=False,
#     dry_run_members=False,
#     worker_threads=10)
#
# # show sync results
# # you may want to save it into delta table for analytical purposes!
# sync_results