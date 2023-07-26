import sys

import configparser
from nestedaaddb.graph_client import Graph
from nestedaaddb.databricks_client import DatabricksClient
from collections import defaultdict


class SyncNestedGroups:
    '''
    Dictionaries used for extracting and reusing user and group mappings(Including nestedAAD groups) in AAD
    '''

    groupgp = defaultdict(set)
    distinct_users = set()
    distinct_groups = set()

    config = configparser.ConfigParser()
    graph: Graph
    dbclient: DatabricksClient

    def loadConfig(self, path):
        # print(self)
        # print(path)
        self.config.read(path)
        azure_settings = self.config['azure']
        db_settings = self.config['databricks']

        self.graph: Graph = Graph(azure_settings)
        self.dbclient: DatabricksClient = DatabricksClient(db_settings)

    '''
    Peforms sync of Users and Groups
    '''
    def sync(self, toplevelgroup, dryrun=False):

        '''
        Read All Databricks users and groups
        '''
        dbusers = self.dbclient.get_dbusers()
        dbgroups = self.dbclient.get_dbgroups()

        print("1.All Databricks Users Read")

        '''
        Read all groups from AAD
        '''
        groups_page = self.graph.get_groups()

        print("2.All AAD groups Read done")

        print("3.Top level group requested is " + toplevelgroup)


        '''
        Indicates whether user and group collection are loaded successfully
        '''
        colInitialised = False

        '''
        Iterate through each group in AAD and map members corresponding to it including nested child group members
        '''
        for group in groups_page['value']:
            print("Group is " + group["displayName"])

            if toplevelgroup != "" and toplevelgroup.casefold() == group["displayName"].casefold():
                distinct_groupsU, distinct_usersU, groupgpU = self.graph.extract_children_from_group(self.graph,
                                                                                                     group["id"],
                                                                                                     group[
                                                                                                         "displayName"],
                                                                                                     self.distinct_groups,
                                                                                                     self.distinct_users,
                                                                                                     self.groupgp);
                colInitialised = True

        print("4.Hierarchy analysed,going to create users and groups")

        if dryrun:
            print("THIS IS DRY RUN.NO CHANGES WILL TAKE PLACE ON DATABRICKS")

        if colInitialised:

            '''
            Create Users and groups in Databricks as required
            '''
            for u in distinct_usersU:

                exists = False

                for udb in dbusers["Resources"]:
                    if u[0].casefold() == udb["displayName"].casefold():
                        exists = True;

                if not exists:
                    self.dbclient.create_dbuser(u, dryrun)

            for u in distinct_groupsU:
                exists = False
                for dbg in dbgroups["Resources"]:
                    if u.casefold() == dbg["displayName"].casefold():
                        exists = True

                if not exists:
                    self.dbclient.create_blank_dbgroup(u, dryrun)

            '''
            Reloading users from Databricks as we need id of new users as well added in last step
            '''
            dbusers = self.dbclient.get_dbusers()
            dbgroups = self.dbclient.get_dbgroups()

            '''
            Create groups or update membership of groups i.e. add/remove users from groups
            '''
            for u in distinct_groupsU:
                exists = False
                for dbg in dbgroups["Resources"]:
                    if u.casefold() == dbg["displayName"].casefold():
                        exists = True
                        # compare and add remove the members as needed
                        self.dbclient.patch_dbgroup(dbg["id"], groupgpU.get(u), dbg, dbusers, dbgroups, dryrun)
        print("All Operation completed !")


