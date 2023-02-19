from nestedaaddb.nested_groups import SyncNestedGroups
sn = SyncNestedGroups()
sn.loadConfig("/Users/abhishekpratap.singh/Desktop/nestedAADSynBakUp16Nov/config/config.cfg")
sn.sync("Parent",True)