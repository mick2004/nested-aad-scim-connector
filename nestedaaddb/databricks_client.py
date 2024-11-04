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

    '''
    Get all the users on Databricks
    '''

    def get_dbusers(self):


        all_users = []

        api_url = self.dbbaseUrl + "/Users"
        start_index=1
        count=10000

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

    def patch_dbgroup(self, gid, members, dbg, dbus, dbgroups,userName_lookup_by_id_db, dryrun):
        api_url = self.dbbaseUrl + "/Groups/" + gid
        u = {
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ]
        }

        toadd = []
        toremove = []

        if members is not None:
            for member in members:
                #logger.info("-----1m-----")
                #logger.info(member)
                exists = False
                if "members" in dbg:
                    for dbmember in dbg["members"]:
                        '''call to retrived user SPN'''


                        '''
                        If it is user we are storing both name and email
                        If group we only store name
                        check if user or group exists
                        '''


                        if(member["type"] == "user"):
                            username = userName_lookup_by_id_db.get(dbmember["value"], "NONE").casefold()
                            if member["data"][1].casefold() == username:
                                exists = True
                                break
                        if member["type"] == "group" and member["data"].casefold() == dbmember["display"].casefold():
                            exists = True
                            break
                if not exists:
                    logger.info("-----3m")
                    logger.info(member)
                    toadd.append(member)

        if "members" in dbg:
            for dbmember in dbg["members"]:
                exists = False

                if members is not None:
                    for member in members:
                        if (member["type"] == "user"):
                            username = userName_lookup_by_id_db.get(dbmember["value"], "NONE").casefold()
                            if member["data"][1].casefold() == username:
                                exists = True
                                break
                        if member["type"] == "group" and member["data"].casefold() == dbmember["display"].casefold():
                            exists = True
                            break
                if not exists:
                    toremove.append(dbmember)

        ops = []


        if len(toadd) == 0 and len(toremove) == 0:
            logger.info(f"----No change in membership detected for group id {gid} -----")
            return

        logger.info(f"----Change in membership detected for group id {gid}.Doing Sync for it -----")
        if len(toadd) > 0:
            mem = []
            for member in toadd:

                logger.info("----15m-----Going to add user in group-----")
                logger.info(member)

                # check if it's a user
                if member["type"] == "user":
                    for dbu in dbus:
                        if dbu["userName"].casefold() == member["data"][1].casefold():
                            obj = dict()
                            obj["value"] = dbu["id"]
                            mem.append(obj)
                            break
                # or if it is a group
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
                dictsub = {'op': "remove", 'path': "members[value eq \"" + member["value"] + "\""}
                ops.append(dictsub)

        gdata = json.loads(json.dumps(u))
        gdata["Operations"] = ops
        ujson = json.dumps(gdata)
        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
        if not dryrun:
            response = requests.patch(api_url, data=ujson, headers=my_headers)
            logger.info("Group Existed but membership updated. Request was :" + ujson)
            logger.info("Response was :" + response.text)

        else:
            logger.info("Group Exists but membership need to be updated for :"
                  + dbg.get("displayName", "NoNameExist") + ". Request details-> data " + ujson + ",EndPoint :" + api_url)

    '''
    Get all Databricks groups
    '''

    def get_dbgroups(self):
        all_groups = []

        api_url = self.dbbaseUrl + "/Groups"
        start_index = 1
        count = 10000

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

    '''Get User '''
    def get_useremail_by_id(self,uid):
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
