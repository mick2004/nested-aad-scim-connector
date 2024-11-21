import json
import requests
from logger_config import logger

'''
Databricks client to interact with Databricks SCIM API's
https://docs.databricks.com/dev-tools/api/latest/scim/account-scim.html
'''


class DatabricksClient:
    dbbaseUrl: str
    dbscimToken: str

    def __init__(self, config):
        self.settings = config
        self.dbbaseUrl = self.settings['dbbaseUrl']
        self.dbscimToken = self.settings['dbscimToken']

    ''' Get membership of a databricks group'''

    def get_group_members(self, group_id):
        """
        Retrieve members of a specific group by group ID.
        """
        api_url = f"{self.dbbaseUrl}/Groups/{group_id}"
        my_headers = {'Authorization': f'Bearer {self.dbscimToken}'}

        try:
            response = requests.get(api_url, headers=my_headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            group_data = response.json()

            # Extract and log members if available
            members = group_data.get("members", [])
            logger.info(f"Fetched Membership from Databricks-Group ID: {group_id}, Members: {json.dumps(members, indent=2)}")
            return members
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve members for group ID {group_id}: {e}")
            return []

    '''
    Get all the users on Databricks
    '''

    def get_dbusers(self):

        all_users = []

        api_url = self.dbbaseUrl + "/Users"
        start_index = 1
        count = 100

        while True:
            my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
            params = {
                'startIndex': start_index,
                'count': count
            }

            response = requests.get(api_url, headers=my_headers, params=params).text
            users_data = json.loads(response)

            # Extract users from the current page and add them to the list
            if 'Resources' in users_data:
                all_users.extend(users_data['Resources'])

            if 'totalResults' in users_data and len(all_users) >= users_data['totalResults']:
                # If we have retrieved all users, break out of the loop
                break

            start_index += count  # Increment the startIndex for the next request

        return all_users

    '''
    Create Databricks User
    '''

    def create_dbuser(self, user, dryrun):
        api_url = self.dbbaseUrl + "/Users"
        u = {
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:User",
                "urn:ietf:params:scim:schemas:core:2.0:User"
            ],
            "userName": user[1],
            "displayName": user[0]
        }

        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}

        if not dryrun:
            response = requests.post(api_url, data=json.dumps(u), headers=my_headers)
            logger.info("User created " + str(user[0]))
            logger.info("Response was :" + response.text)
        else:
            logger.info("User to be created " + str(user[0]))

    '''
    Add or remove users in Databricks group
    members : all the users/group that should be in the final state of the group.This is retrieved from Azure AAD
    dbg : databricks group with id and membership
    dbus: all databricks users
    dbgroups : all databricks groups
    '''

    def patch_dbgroup(self, gid, members, dbg, dbus, dbgroups, userName_lookup_by_id_db, dryrun):
        """
        Add or remove users in a Databricks group.
        """
        api_url = self.dbbaseUrl + "/Groups/" + gid
        u = {
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ]
        }

        toadd = []
        toremove = []

        # Fetch group display name
        group_display_name = dbg.get("displayName", "NoNameExist")

        # Fetch members dynamically using the SCIM API
        dbg_members = self.get_group_members(gid)

        logger.info(f"Group ID: {gid}, Group Display Name: {group_display_name}")
        logger.info(f"Group Members as per Databricks: {json.dumps(dbg_members, indent=2)}")

        # Log members as per Azure AAD
        if members is None:
            logger.info(f"Group Members as per AAD: None")
        else:
            logger.info(f"Group Members as per AAD: {json.dumps(list(members), indent=2)}")

        # Logic to identify members to add
        if members is not None:
            for member in members:
                logger.info("-----1m-----")
                logger.info(f"Checking member: {member}")
                exists = False
                for dbmember in dbg_members:
                    # Log member comparisons
                    logger.info(f"Comparing with Databricks member: {dbmember}")
                    if member["type"] == "user":
                        username = userName_lookup_by_id_db.get(dbmember["value"], "NONE").casefold()
                        if member["data"][1].casefold() == username:
                            logger.info("-----2m----- Match found, user exists")
                            exists = True
                            break
                    if member["type"] == "group" and member["data"].casefold() == dbmember.get("display",
                                                                                               "").casefold():
                        logger.info("-----2m----- Match found, group exists")
                        exists = True
                        break
                if not exists:
                    logger.info("-----3m----- Member not found, adding to 'toadd'")
                    logger.info(member)
                    toadd.append(member)

        # Logic to identify members to remove
        logger.info("Checking for members to remove in Databricks.")
        for dbmember in dbg_members:
            logger.info("-----4m-----")
            exists = False
            logger.info(f"Member in Databricks id => {dbmember['value']}")
            logger.info(f"Member in Databricks display => {dbmember.get('display', '')}")
            logger.info(f"Member in Databricks ref => {dbmember.get('$ref', '')}")

            if members is not None:
                logger.info("-----5m-----")
                for member in members:
                    logger.info(f"-----6m----- Checking AAD member: {member}")
                    if member["type"] == "user":
                        logger.info("-----7m----- Checking if user exists")
                        username = userName_lookup_by_id_db.get(dbmember["value"], "NONE").casefold()
                        logger.info(f"username is {username}")
                        if member["data"][1].casefold() == username:
                            logger.info("-----8m----- Match found, user exists")
                            exists = True
                            break
                    if member["type"] == "group" and member["data"].casefold() == dbmember.get("display",
                                                                                               "").casefold():
                        logger.info("-----9m----- Match found, group exists")
                        exists = True
                        break
            if not exists:
                logger.info("-----10m----- Member not found, adding to 'toremove'")
                toremove.append(dbmember)

        # Log results of comparison
        logger.info(f"To Add: {json.dumps(list(toadd), indent=2)}")
        logger.info(f"To Remove: {json.dumps(list(toremove), indent=2)}")

        # No changes detected
        if len(toadd) == 0 and len(toremove) == 0:
            logger.info(f"----No change in membership detected for group {group_display_name} (ID: {gid}) -----")
            return

        # Apply changes
        logger.info(
            f"----Change in membership detected for group {group_display_name} (ID: {gid}). Doing Sync for it -----")
        ops = []

        if len(toadd) > 0:
            mem = []
            for member in toadd:
                logger.info("----15m----- Going to add user/group to group -----")
                logger.info(member)

                if member["type"] == "user":
                    for dbu in dbus:
                        if dbu["userName"].casefold() == member["data"][1].casefold():
                            obj = dict()
                            obj["value"] = dbu["id"]
                            mem.append(obj)
                            break
                elif member["type"] == "group":
                    for dbgg in dbgroups:
                        if dbgg.get("displayName", "").casefold() == member["data"].casefold():
                            obj = dict()
                            obj["value"] = dbgg["id"]
                            mem.append(obj)
                            break
            dictmem = {"members": mem}
            dictsub = {'op': "add", 'value': dictmem}
            ops.append(dictsub)

        if len(toremove) > 0:
            for member in toremove:
                dictsub = {'op': "remove", 'path': f"members[value eq \"{member['value']}\"]"}
                ops.append(dictsub)

        # Prepare and send API request
        gdata = json.loads(json.dumps(u))
        gdata["Operations"] = ops
        ujson = json.dumps(gdata)
        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
        if not dryrun:
            response = requests.patch(api_url, data=ujson, headers=my_headers)
            logger.info(f"Group {group_display_name} (ID: {gid}) membership updated. Request was: {ujson}")
            logger.info(f"Response was: {response.text}")
        else:
            logger.info(
                f"Group {group_display_name} (ID: {gid}) needs membership updates. "
                f"Request details -> data {ujson}, EndPoint: {api_url}"
            )

    '''
    Get all  Databricks groups
    '''

    def get_dbgroups(self):
        all_groups = []

        api_url = self.dbbaseUrl + "/Groups?excludedAttributes=entitlements,members,roles,groups"
        # api_url = self.dbbaseUrl + "/Groups"
        start_index = 1
        count = 100

        while True:
            my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
            params = {
                'startIndex': start_index,
                'count': count
            }

            response = requests.get(api_url, headers=my_headers, params=params).text
            groups_data = json.loads(response)

            # Extract groups from the current page and add them to the list
            if 'Resources' in groups_data:
                all_groups.extend(groups_data['Resources'])

            # Check if there are more groups to fetch
            if 'totalResults' in groups_data and len(all_groups) >= groups_data['totalResults']:
                break

            start_index += count  # Increment the startIndex for the next request

        return all_groups

    '''Get  User '''

    def get_useremail_by_id(self, uid):
        api_url = self.dbbaseUrl + "/Groups"

        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
        response = requests.get(api_url, headers=my_headers).text
        return json.loads(response)

    '''
    Delete a Databricks User
    '''

    def delete_user(self, uid):
        api_url = self.dbbaseUrl + "/Users/" + uid

        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
        response = requests.delete(api_url, headers=my_headers).text
        return response

    '''
    Delete a Databricks group
    '''

    def delete_group(self, uid):
        api_url = self.dbbaseUrl + "/Groups/" + uid

        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
        response = requests.delete(api_url, headers=my_headers).text
        return response

    def create_blank_dbgroup(self, group, dryrun):
        api_url = self.dbbaseUrl + "/Groups"
        u = {
            "displayName": group,
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:Group"
            ]
        }

        gdata = json.loads(json.dumps(u))
        ujson = json.dumps(gdata)
        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
        if not dryrun:
            response = requests.post(api_url, data=ujson, headers=my_headers)
            logger.info("Blank Group Created.Request was " + ujson)
            logger.info("Response was :" + response.text)
        else:
            logger.info("Blank Group to be created :" + group)
