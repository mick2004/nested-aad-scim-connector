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
        print("1.1 Number of groups in databricks is :" + str(len(dbgroups)))


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

                #print("----0m----users identified to be present in groups selected")

                #print(u)

                for udb in dbusers:
                    if u[1].casefold() == udb["userName"].casefold():
                        exists = True;

                if not exists:
                    self.dbclient.create_dbuser(u, dryrun)

            for u in distinct_groupsU:
                exists = False
                for dbg in dbgroups:
                    if u.casefold() == dbg.get("displayName", "").casefold():
                        exists = True

                if not exists:
                    self.dbclient.create_blank_dbgroup(u, dryrun)

            '''
            Reloading users from Databricks as we need id of new users as well added in last step
            '''
            dbusers = self.dbclient.get_dbusers()
            dbgroups = self.dbclient.get_dbgroups()

            # UserName lookup by id databricks
            userName_lookup_by_id_db = {user['id']: user['userName'] for user in dbusers}

            '''
            Create groups or update membership of groups i.e. add/remove users from groups
            distinct_groupsU : distinct groups to be added as part of this operation
            we are comparing it with  databricks all groups to retrive gid
            which will be used to make databricks rest api calls
            '''
            for u in distinct_groupsU:
                exists = False
                for dbg in dbgroups:
                    if u.casefold() == dbg.get("displayName", "").casefold():
                        exists = True
                        # compare and add remove the members as needed
                        # groupgpU : dsitinct users per group.This is retrieved from Azure AAD
                        # we are getting all the users that should be in the final state of the group
                        # dbg : databricks group with id
                        # dbusers : all databricks users
                        # dbgroups : all databricks groups
                        self.dbclient.patch_dbgroup(dbg["id"], groupgpU.get(u), dbg, dbusers, dbgroups,userName_lookup_by_id_db, dryrun)
        print("All Operation completed !")

    '''
       Analyse AAD structure and DB groups
       '''

    def analyse(self, toplevelgroup, dryrun=False):
        '''
        Read All Databricks users and groups
        '''
        dbusers = self.dbclient.get_dbusers()
        dbgroups = self.dbclient.get_dbgroups()

        print("1. All Databricks Users and Groups Read")
        print("1.1 Number of Users in Databricks: " + str(len(dbusers)))
        print("1.2 Number of Groups in Databricks: " + str(len(dbgroups)))

        print("2. Top-level group requested is: " + toplevelgroup)

        group = self.graph.getGroupByName(toplevelgroup)

        if len(group["value"]) == 0:
            print("Top-level group not found, exiting...")
            return

        print("3. Top-level group retrieved from AAD")

        '''
        Indicates whether user and group collection are loaded successfully
        '''
        colInitialised = False

        '''
        Iterate through each group in AAD and map members corresponding to it, including nested child group members
        '''
        group = group['value'][0]
        if toplevelgroup != "" and toplevelgroup.casefold() == group.get("displayName", "").casefold():
            # Extracting child groups and users from the provided top-level group
            distinct_groupsU, distinct_usersU, groupgpU = self.graph.extract_children_from_group(
                self.graph,
                group["id"],
                group["displayName"],
                self.distinct_groups,
                self.distinct_users,
                self.groupgp
            )
            colInitialised = True

        print("4. Hierarchy analysed")

        if colInitialised:
            # Full Count of the collections
            print("\n=== Full Analysis Summary for children partent groups ===>" + toplevelgroup)

            # Distinct Groups Summary
            print(f"5. Total Number of Distinct Groups: {len(distinct_groupsU)}")
            print("5.1 Top 5 Distinct Groups:")
            for group_name in list(distinct_groupsU)[:5]:
                print(f"   - {group_name}")

            # Distinct Users Summary
            print(f"\n6. Total Number of Distinct Users: {len(distinct_usersU)}")
            print("6.1 Top 5 Distinct Users:")
            for user in list(distinct_usersU)[:5]:
                print(f"   - Display Name: {user[0]}, User Principal Name: {user[1]}")

            # Group Members Mapping Summary
            print(f"\n7. Total Number of Groups in Group-User Map: {len(groupgpU)}")
            print("7.1 Top 5 Group-User Mappings:")
            for group_name, members in list(groupgpU.items())[:5]:
                print(f"   - Group: {group_name}, Members: {list(members)[:5]}")

        print("\nAnalysis completed!")


