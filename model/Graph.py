import json
import requests
import json
from configparser import SectionProxy
from azure.identity import DeviceCodeCredential, ClientSecretCredential
from msgraph.core import GraphClient


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
        graph_scopes = self.settings['graphUserScopes'].split(' ')

        self.device_code_credential = DeviceCodeCredential(client_id, tenant_id=tenant_id)
        self.user_client = GraphClient(credential=self.device_code_credential, scopes=graph_scopes)

    def get_user_token(self):
        graph_scopes = self.settings['graphUserScopes']
        access_token = self.device_code_credential.get_token(graph_scopes)
        return access_token.token



    def ensure_graph_for_app_only_auth(self):
        if not hasattr(self, 'client_credential'):
            client_id = self.settings['clientId']
            tenant_id = self.settings['tenantId']
            client_secret = self.settings['clientSecret']

            self.client_credential = ClientSecretCredential(tenant_id, client_id, client_secret)

        if not hasattr(self, 'app_client'):
            self.app_client = GraphClient(credential=self.client_credential,
                                          scopes=['https://graph.microsoft.com/.default'])

    def get_users(self):
        self.ensure_graph_for_app_only_auth()

        endpoint = '/users'
        # Only request specific properties
        select = 'displayName,id,mail'
        # Get at most 25 results
        top = 100
        # Sort by display name
        order_by = 'displayName'
        request_url = f'{endpoint}?$select={select}&$top={top}&$orderBy={order_by}'

        users_response = self.app_client.get(request_url)
        return users_response.json()

    def get_groups(self):
        self.ensure_graph_for_app_only_auth()

        endpoint = '/groups'
        # Only request specific properties
        select = 'displayName,id'
        # Get at most 25 results
        top = 100
        # Sort by display name
        order_by = 'displayName'
        request_url = f'{endpoint}?$select={select}&$top={top}&$orderBy={order_by}'

        users_response = self.app_client.get(request_url)
        return users_response.json()

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

    def extractFromGroup(self,graph, gid, displayName,groupUsermap,userGroupmap):
        gms = graph.get_groupmembers(gid)
        for gm in gms['value']:
            if gm["@odata.type"] == "#microsoft.graph.user":
                for gp in str(displayName).split(":"):
                    groupUsermap[gp].add((gm["displayName"], gm["userPrincipalName"]))
                    userGroupmap[(gm["displayName"], gm["userPrincipalName"])].add(gp)

            elif gm["@odata.type"] == "#microsoft.graph.group":
                graph.extractFromGroup(graph, gm["id"], displayName + ":" + gm["displayName"],groupUsermap,userGroupmap)

        return groupUsermap, userGroupmap




