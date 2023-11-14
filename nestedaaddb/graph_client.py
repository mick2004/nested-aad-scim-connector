import json
from collections import defaultdict
from configparser import SectionProxy
from azure.identity import DeviceCodeCredential, ClientSecretCredential
from msgraph.core import GraphClient

'''
A wrapper for Graph to interact with Graph API's
https://learn.microsoft.com/en-us/graph/overview
'''


class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


class Graph:
    settings: SectionProxy
    device_code_credential: DeviceCodeCredential
    user_client: GraphClient
    client_credential: ClientSecretCredential
    app_client: GraphClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['authTenant']

        self.device_code_credential = DeviceCodeCredential(client_id, tenant_id=tenant_id)
        self.user_client = GraphClient(credential=self.device_code_credential)

    '''
    Initialises the client
    '''

    def ensure_graph_for_app_only_auth(self):
        if not hasattr(self, 'client_credential'):
            client_id = self.settings['clientId']
            tenant_id = self.settings['tenantId']
            client_secret = self.settings['clientSecret']

            self.client_credential = ClientSecretCredential(tenant_id, client_id, client_secret)

        if not hasattr(self, 'app_client'):
            self.app_client = GraphClient(credential=self.client_credential,
                                          scopes=['https://graph.microsoft.com/.default'])

    def getGroupByName(self, group_name):
        self.ensure_graph_for_app_only_auth()

        endpoint = '/groups'
        filter_query = f"displayName eq '{group_name}'"
        select = 'displayName,id'

        request_url = f'{endpoint}?$filter={filter_query}&$select={select}'

        group_response = self.app_client.get(request_url)
        return group_response.json()

    '''
    Create groups in AAD
    '''

    def create_group(self, name):
        self.ensure_graph_for_app_only_auth()

        request_body = {
            "description": "Self help community for lib23",
            "displayName": name,
            "groupTypes": [
                "Unified"
            ],
            "mailEnabled": False,
            "mailNickname": "lib23",
            "securityEnabled": False
        }

        request_url = '/groups'

        group_response = self.app_client.post(request_url,
                                              data=json.dumps(request_body),
                                              headers={'Content-Type': 'application/json'})
        return group_response.json()

    '''
       Get all the groups from AAD
       '''

    def get_groups(self):
        self.ensure_graph_for_app_only_auth()

        endpoint = '/groups'
        # Only request specific properties
        select = 'displayName,id'

        # Sort by display name
        order_by = 'displayName'
        request_url = f'{endpoint}?$select={select}&$orderBy={order_by}'

        users_response = self.app_client.get(request_url)
        return users_response.json()

    '''
    Get all the group members from the group
    '''

    def get_groupmembers(self, gid):
        self.ensure_graph_for_app_only_auth()

        endpoint = '/groups'
        # Only request specific properties
        select = 'displayName,id,userPrincipalName'

        # Sort by display name
        order_by = 'displayName'
        request_url = f'{endpoint}/{gid}/members?$select={select}'

        users_response = self.app_client.get(request_url)
        return users_response.json()

    '''
    Extract the user and group mapping .
    This method makes recursive call to get all the group and member relationships even within nested group
    '''

    @staticmethod
    def extract_from_group(graph, gid, displayname, groupusermap, usergroupmap):
        gms = graph.get_groupmembers(gid)
        for gm in gms['value']:
            if gm["@odata.type"] == "#microsoft.graph.user":
                for gp in str(displayname).split(":"):
                    groupusermap[gp].add((gm["displayName"], gm["userPrincipalName"]))
                    usergroupmap[(gm["displayName"], gm["userPrincipalName"])].add(gp)

            elif gm["@odata.type"] == "#microsoft.graph.group":
                graph.extract_from_group(graph, gm["id"], displayname + ":" + gm["displayName"], groupusermap,
                                         usergroupmap)

        return groupusermap, usergroupmap

    @staticmethod
    def extract_children_from_group(graph, gid, displayname, distinct_groups,
                                    distinct_users, groupgp):

        gms = graph.get_groupmembers(gid)
        distinct_groups.add(displayname)
        for gm in gms['value']:
            if gm["@odata.type"] == "#microsoft.graph.user":

                groupgp[displayname].add(
                    HashableDict({'type': 'user', 'data': (gm["displayName"], gm["userPrincipalName"])}))
                distinct_users.add((gm["displayName"], gm["userPrincipalName"]))
            elif gm["@odata.type"] == "#microsoft.graph.group":

                groupgp[displayname].add(HashableDict({'type': 'group', 'data': (gm["displayName"])}))
                distinct_groups.add(gm["displayName"])
                graph.extract_children_from_group(graph, gm["id"], gm["displayName"], distinct_groups,
                                                  distinct_users, groupgp)

        return distinct_groups, distinct_users, groupgp
