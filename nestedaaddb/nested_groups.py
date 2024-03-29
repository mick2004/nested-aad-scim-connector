import sys

import configparser
from nestedaaddb.graph_client import Graph
from nestedaaddb.databricks_client import DatabricksClient
from collections import defaultdict


class SyncNestedGroups:
    '''
    Dictionaries used for extracting and reusing user and group mappings(Including nestedAAD groups) in AAD
    This utility requires the display name of databricks user exactly same as AAD name
    This is becuase Databricks Groups API gives display name and that is compared with AAD displayname in case of users
    If you have different display names in AAD vs Databricks,you can delete the user from databricks
    this program will recreate them
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

    def createGroup(self, name):
        return self.graph.create_group(name)

    '''
    Peforms sync of Users and Groups
    '''

    def sync(self, toplevelgroup, dryrun=False):

        '''
        Read All Databricks users and groups
        '''
        dbusers = self.dbclient.get_dbusers()
        dbgroups = self.dbclient.get_dbgroups()

        print("1.All Databricks Users and group Read")

        print("1.1 Number of Users in databricks is :"+str(len(dbusers)))
        print("1.1 Number of groups in databricks is :" + str(len(dbgroups["Resources"])))

        print("2.Top level group requested is " + toplevelgroup)

        group = self.graph.getGroupByName(toplevelgroup)

        if len(group["value"]) == 0:
            print("Top level group not found,exiting...")
            return

        print("3.Top level group retrieved from AAD")

        '''
        Indicates whether user and group collection are loaded successfully
        '''
        colInitialised = False

        '''
        Iterate through each group in AAD and map members corresponding to it including nested child group members
        '''
        group = group['value'][0]
        if toplevelgroup != "" and toplevelgroup.casefold() == group.get("displayName", "").casefold():
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
            This is retrieved from AAD
            
            '''
            for u in distinct_usersU:

                exists = False

                print("----0m----users identified to be present in groups selected")

                print(u)

                for udb in dbusers:
                    if u[1].casefold() == udb["userName"].casefold():
                        exists = True;

                if not exists:
                    self.dbclient.create_dbuser(u, dryrun)

            for u in distinct_groupsU:
                exists = False
                for dbg in dbgroups["Resources"]:
                    if u.casefold() == dbg.get("displayName", "").casefold():
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
            distinct_groupsU : distinct groups to be added as part of this operation
            we are comparing it with  databricks all groups to retrive gid
            which will be used to make databricks rest api calls
            '''
            for u in distinct_groupsU:
                exists = False
                for dbg in dbgroups["Resources"]:
                    if u.casefold() == dbg.get("displayName", "").casefold():
                        exists = True
                        # compare and add remove the members as needed
                        # groupgpU : dsitinct users per group.This is retrieved from Azure AAD
                        # we are getting all the users that should be in the final state of the group
                        # dbg : databricks group with id
                        # dbusers : all databricks users
                        # dbgroups : all databricks groups
                        self.dbclient.patch_dbgroup(dbg["id"], groupgpU.get(u), dbg, dbusers, dbgroups, dryrun)
        print("All Operation completed !")
