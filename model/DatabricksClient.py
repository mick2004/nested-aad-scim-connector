import json
import requests

class DatabricksClient:
    dbbaseUrl: str
    dbscimToken: str
    def __init__(self, config):
        self.settings = config
        self.dbbaseUrl = self.settings['dbbaseUrl']
        self.dbscimToken = self.settings['dbscimToken']

    def get_DBUsers(self):

        api_url = self.dbbaseUrl+"/Users"

        my_headers = {'Authorization': 'Bearer '+self.dbscimToken}
        response = requests.get(api_url,  headers=my_headers).text
        return json.loads(response)



    def createdbuser(self,user):
        api_url = self.dbbaseUrl+"/Users"
        u={
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:User",
                "urn:ietf:params:scim:schemas:core:2.0:User"
            ],
            "userName": user[1],
            "displayName": user[0]
        }

        my_headers = {'Authorization': 'Bearer '+self.dbscimToken}
        response = requests.post(api_url, data=json.dumps(u), headers=my_headers)
        return response

    def createdbgroup(self, group, members ,dbus):
        api_url = self.dbbaseUrl+"/Groups"
        u={
              "displayName": group,
              "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:Group"
              ]
            }

        mem =[]
        for member in members:
            for dbu in dbus["Resources"]:
                if dbu["displayName"] == member[0]:
                    obj = dict()
                    obj["value"] = dbu["id"]
                    mem.append(obj)

        gdata=json.loads(json.dumps(u))
        # for member in members:
        #     gdata["members"].append(dict("value",member[0]))
        gdata["members"]=mem
        ujson=json.dumps(gdata)
        my_headers = {'Authorization': 'Bearer '+self.dbscimToken}
        response = requests.post(api_url, data=ujson, headers=my_headers)
        print(ujson)

    def patchdbgroup(self, gid, members, dbg, dbus):
        api_url = self.dbbaseUrl + "/Groups/"+gid
        u = {
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:Group"
            ]
        }

        toadd = []
        toremove = []

        for member in members:
            exists = False
            #if dbg["members"] exists:
            if "members" in dbg :
                for dbmember in dbg["members"]:
                    if member[0].casefold() == dbmember["display"].casefold():
                        exists = True;
            if not exists :
                toadd.append(member)

        if "members" in dbg:
            for dbmember in dbg["members"]:
                exists = False
                for member in members:
                    if member[0].casefold() == dbmember["display"].casefold():
                        exists = True;
                if not exists :
                    toremove.append(member)

        ops = []

        if len(toadd) ==0 and len(toremove)==0:
            return

        if len(toadd) > 0:
            mem = []
            for member in toadd:
                for dbu in dbus["Resources"]:
                    if dbu["displayName"] == member[0]:
                        obj = dict()
                        obj["value"] = dbu["id"]
                        mem.append(obj)

            #add
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
        # for member in members:
        #     gdata["members"].append(dict("value",member[0]))
        gdata["Operations"] = ops
        ujson = json.dumps(gdata)
        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
        response = requests.patch(api_url, data=ujson, headers=my_headers)
        print(ujson)

    def get_DBGroups(self):
        api_url = self.dbbaseUrl + "/Groups"

        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
        response = requests.get(api_url, headers=my_headers).text
        return json.loads(response)

    def deleteUser(self, uid):
        api_url = self.dbbaseUrl + "/Users/"+uid

        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
        response = requests.delete(api_url, headers=my_headers).text
        return response

    def deleteGroup(self, uid):
        api_url = self.dbbaseUrl + "/Groups/"+uid

        my_headers = {'Authorization': 'Bearer ' + self.dbscimToken}
        response = requests.delete(api_url, headers=my_headers).text
        return response



