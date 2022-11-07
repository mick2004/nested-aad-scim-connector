import json
import requests

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

        api_url = self.dbbaseUrl + "/Users"

        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
        response = requests.get(api_url, headers=my_headers).text
        return json.loads(response)

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
            print("User created " + str(user[0]))
            print("Response was :" + response.text)
        else:
            print("User to be created " + str(user[0]))

    '''
    Create group in Databricks
    '''
    def create_dbgroup(self, group, members, dbus, dryrun):
        api_url = self.dbbaseUrl + "/Groups"
        u = {
            "displayName": group,
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:Group"
            ]
        }

        mem = []
        for member in members:
            for dbu in dbus["Resources"]:
                if dbu["displayName"] == member[0]:
                    obj = dict()
                    obj["value"] = dbu["id"]
                    mem.append(obj)

        gdata = json.loads(json.dumps(u))
        gdata["members"] = mem
        ujson = json.dumps(gdata)
        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
        if not dryrun:
            response = requests.post(api_url, data=ujson, headers=my_headers)
            print("Group Created.Request was " + ujson)
            print("Response was :" + response.text)
        else:
            print("Group to be created.Request should be " + ujson)

    '''
    Add or remove users in Databricks group
    '''
    def patch_dbgroup(self, gid, members, dbg, dbus, dryrun):
        api_url = self.dbbaseUrl + "/Groups/" + gid
        u = {
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:Group"
            ]
        }

        toadd = []
        toremove = []

        for member in members:
            exists = False
            # if dbg["members"] exists:
            if "members" in dbg:
                for dbmember in dbg["members"]:
                    if member[0].casefold() == dbmember["display"].casefold():
                        exists = True
            if not exists:
                toadd.append(member)

        if "members" in dbg:
            for dbmember in dbg["members"]:
                exists = False
                for member in members:
                    if member[0].casefold() == dbmember["display"].casefold():
                        exists = True
                if not exists:
                    toremove.append(dbmember)

        ops = []

        if len(toadd) == 0 and len(toremove) == 0:
            return

        if len(toadd) > 0:
            mem = []
            for member in toadd:
                for dbu in dbus["Resources"]:
                    if dbu["displayName"] == member[0]:
                        obj = dict()
                        obj["value"] = dbu["id"]
                        mem.append(obj)

            dictmem = {"members": mem}
            dictsub = {'op': "add", 'path': "members", 'value': dictmem}
            ops.append(dictsub)

        if len(toremove) > 0:
            mem = []
            for member in toremove:
                for dbu in dbus["Resources"]:
                    if dbu["displayName"] == member[0]:
                        obj = dict()
                        obj["value"] = dbu["id"]
                        mem.append(obj)

            dictmem = {"members": mem}
            dictsub = {'op': "add", 'path': "members", 'value': dictmem}
            ops.append(dictsub)

        gdata = json.loads(json.dumps(u))
        gdata["Operations"] = ops
        ujson = json.dumps(gdata)
        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
        if not dryrun:
            response = requests.patch(api_url, data=ujson, headers=my_headers)
            print("Group Existed but membership updated. Request was :" + ujson)
            print("Response was :" + response.text)

        else:
            print("Group Exists but membership need to be updated for :" + dbg["displayName"])

    '''
    Get all Databricks groups
    '''
    def get_dbgroups(self):
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
