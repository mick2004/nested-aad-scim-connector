import sys

import configparser

from databricks.model.DatabricksClient import DatabricksClient
from databricks.model.Graph import Graph
from collections import defaultdict


class SyncNestedGroups:
    '''
    Dictionaries used for extracting and reusing user and group mappings(Including nestedAAD groups) in AAD
    '''

    groupgp = defaultdict(set)
    distinct_users = set()
    distinct_groups = set()

    '''
    Entry point of the application
    Can provide --dryrun to do a dryrun
    Can provide a top level group as program argument as top level group
    Ex:
    python PythonEndpoint/SyncNestedGroups.py parent
    python PythonEndpoint/SyncNestedGroups.py parent --dryrun
    '''

    def main(self, group):
        dryrun = False;

        print('Number of arguments:', len(sys.argv[1:]), 'arguments.')
        print('Argument List:', str(sys.argv[1:]))

        '''
        Validation for program arguments
        '''
        if len(sys.argv[1:]) > 2:
            print("only 2 arguments supported")
            return

        toplevelgroup = ""

        for arg in sys.argv[1:]:
            if arg.casefold() == "--dryrun":
                dryrun = True;
            else:
                if toplevelgroup == "":
                    toplevelgroup = arg;
                else:
                    print("Only one group supported")
                    return

        '''
        set top level group
        Priority is for program argument and if not provided then checks method argument
        '''
        if toplevelgroup == "":
            toplevelgroup = group

        '''
        Initialise clients
        '''
        config = configparser.ConfigParser()
        config.read(['../config/config.cfg', 'config.dev.cfg'])
        azure_settings = config['azure']
        db_settings = config['databricks']

        graph: Graph = Graph(azure_settings)
        dbclient: DatabricksClient = DatabricksClient(db_settings)

        '''
        Read All Databricks users and groups
        '''
        dbusers = dbclient.get_dbusers()
        dbgroups = dbclient.get_dbgroups()

        print("1.All Databricks Users Read")

        '''
        Read all groups from AAD
        '''
        groups_page = graph.get_groups()

        print("2.All AAD groups Read done")

        print("3.Top level group requested is " + toplevelgroup)

        '''
        Indicates whether user and group collection are loaded successfully
        '''
        for top in toplevelgroup.split(","):

            self.distinct_groups.clear()
            self.distinct_users.clear()
            self.groupgp.clear()

            colInitialised = False

            '''
            Iterate through each group in AAD and map members corresponding to it including nested child group members
            '''
            for group in groups_page['value']:
                print("Group is " + group["displayName"])

                '''
                If this is invoked via cli with program arguments
                '''
                if len(sys.argv[1:]) > 0:
                    for arg in sys.argv[1:]:
                        if not arg.startswith("--") and top.casefold() == group["displayName"].casefold():
                            distinct_groupsU, distinct_usersU, groupgpU = graph.extract_children_from_group(graph,
                                                                                                            group["id"],
                                                                                                            group[
                                                                                                                "displayName"],
                                                                                                            self.distinct_groups,
                                                                                                            self.distinct_users,
                                                                                                            self.groupgp);
                            colInitialised = True
                elif top != "" and top.casefold() == group["displayName"].casefold():
                    distinct_groupsU, distinct_usersU, groupgpU = graph.extract_children_from_group(graph,
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
                        dbclient.create_dbuser(u, dryrun)

                for u in distinct_groupsU:
                    exists = False
                    for dbg in dbgroups["Resources"]:
                        if u.casefold() == dbg["displayName"].casefold():
                            exists = True

                    if not exists:
                        dbclient.create_blank_dbgroup(u, dryrun)

                '''
                Reloading users from Databricks as we need id of new users as well added in last step
                '''
                dbusers = dbclient.get_dbusers()
                dbgroups = dbclient.get_dbgroups()

                '''
                Create groups or update membership of groups i.e. add/remove users from groups
                '''
                for u in distinct_groupsU:
                    exists = False
                    for dbg in dbgroups["Resources"]:
                        if u.casefold() == dbg["displayName"].casefold():
                            exists = True
                            # compare and add remove the members as needed
                            dbclient.patch_dbgroup(dbg["id"], groupgpU.get(u), dbg, dbusers, dbgroups, dryrun)

        print("All Operation completed !")


if __name__ == '__main__':
    SyncNestedGroups().main("")
