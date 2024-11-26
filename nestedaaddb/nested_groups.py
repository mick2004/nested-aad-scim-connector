import configparser
from json import JSONDecodeError

from nestedaaddb.graph_client import Graph
from logger_config import logger
from nestedaaddb.databricks_client import DatabricksClient
from collections import defaultdict
import csv


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
        # logger.info(self)
        # logger.info(path)
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

        logger.info("1.All Databricks Users and group Read")

        logger.info("1.1 Number of Users in databricks is :"+str(len(dbusers)))
        logger.info("1.1 Number of groups in databricks is :" + str(len(dbgroups)))


        logger.info("2.Top level group requested is " + toplevelgroup)

        #group = self.graph.getGroupByName(toplevelgroup)
        response = self.graph.getGroupByName(toplevelgroup)
        if not response:
            print("Error: Received empty response for group lookup.")
            print("Response for group was:", response)  # This helps verify if the data is valid JSON or not.

            return

        try:
            # Assuming response should be parsed as JSON
            group = response.json() if isinstance(response, str) else response
            if 'value' not in group or not group['value']:
                print("Warning: 'value' key missing or empty in response:", group)
                print("Response for group was:", response)  # This helps verify if the data is valid JSON or not.
                return
        except JSONDecodeError as e:
            print(f"JSON Decode Error: {e}. Response content: {response}")
            raise SystemExit("Terminating due to JSON Decode Error")

        if len(group["value"]) == 0:
            logger.info("Top level group not found,exiting...")
            return

        logger.info("3.Top level group retrieved from AAD")

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

        logger.info("4.Hierarchy analysed,going to create users and groups")

        if dryrun:
            logger.info("THIS IS DRY RUN.NO CHANGES WILL TAKE PLACE ON DATABRICKS")

        if colInitialised:

            '''
            Create Users and groups in Databricks as required
            This is retrieved from AAD
            
            '''
            for u in distinct_usersU:

                exists = False

                #logger.info("----0m----users identified to be present in groups selected")

                #logger.info(u)

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
                        # dbg : databricks group with id with members
                        # dbusers : all databricks users
                        # dbgroups : all databricks groups


                        self.dbclient.patch_dbgroup(dbg["id"], groupgpU.get(u), dbg, dbusers, dbgroups,userName_lookup_by_id_db, dryrun)
        logger.info("All Operation completed !")

    '''
       Analyse AAD structure and DB groups
       '''

    def analyse(self, toplevelgroup, dryrun=False):
        '''
        Read All Databricks users and groups
        '''
        #dbusers = self.dbclient.get_dbusers()
        #dbgroups = self.dbclient.get_dbgroups()

        #logger.info("1. All Databricks Users and Groups Read")
        #logger.info("1.1 Number of Users in Databricks: " + str(len(dbusers)))
        #logger.info("1.2 Number of Groups in Databricks: " + str(len(dbgroups)))

        logger.info("2. Top-level group requested is: " + toplevelgroup)

        #group = self.graph.getGroupByName(toplevelgroup)

        response = self.graph.getGroupByName(toplevelgroup)
        if not response:
            print("Error: Received empty response for group lookup.")
            print("Response for group was:", response)  # This helps verify if the data is valid JSON or not.
            return

        try:
            # Assuming response should be parsed as JSON
            group = response.json() if isinstance(response, str) else response
            if 'value' not in group or not group['value']:
                print("Warning: 'value' key missing or empty in response:", group)
                print("Response for group was:", response)  # This helps verify if the data is valid JSON or not.
                return
        except JSONDecodeError as e:
            print(f"JSON Decode Error: {e}. Response content: {response}")
            return

        if len(group["value"]) == 0:
            logger.info("Top-level group not found, exiting...")
            return

        logger.info("3. Top-level group retrieved from AAD")

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

        logger.info("4. Hierarchy analysed")

        if colInitialised:
            # Save distinct groups to CSV
            with open('distinct_groups.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Group Name"])
                for group_name in distinct_groupsU:
                    writer.writerow([group_name])
            logger.info("Distinct groups saved to distinct_groups.csv")

            # Save distinct users to CSV
            with open('distinct_users.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Display Name", "User Principal Name"])
                for user in distinct_usersU:
                    writer.writerow([user[0], user[1]])
            logger.info("Distinct users saved to distinct_users.csv")

            # Save group-user mappings to CSV
            # Save group-user mappings to CSV
            # Save group-user mappings to CSV
            with open('group_user_mappings.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Group Name", "Members"])
                for group_name, members in groupgpU.items():
                    # Converting each member to a string
                    members_str = "; ".join([str(member) for member in list(members)])
                    writer.writerow([group_name, members_str])
            logger.info("Group-user mappings saved to group_user_mappings.csv")

            # Distinct Groups Summary
            logger.info(f"5. Total Number of Distinct Groups: {len(distinct_groupsU)}")
            logger.info("5.1 Distinct Groups for parent group ===>" + toplevelgroup)
            for group_name in list(distinct_groupsU):
                logger.info(f"   - {group_name}")

            # Distinct Users Summary
            logger.info(f"\n6. Total Number of Distinct Users: {len(distinct_usersU)}")
            logger.info("6.1 Distinct Users for parent group ===>" + toplevelgroup)
            for user in list(distinct_usersU):
                logger.info(f"   - Display Name: {user[0]}, User Principal Name: {user[1]}")

            # Group Members Mapping Summary
            logger.info(f"\n7. Total Number of Groups in Group-User Map: {len(groupgpU)}")
            logger.info("7.1 Group-User Mappings for parent group ===>" + toplevelgroup)
            for group_name, members in list(groupgpU.items()):
                logger.info(f"   - Group: {group_name}, Members: {list(members)}")
