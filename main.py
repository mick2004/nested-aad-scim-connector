

import sys

import configparser

from DatabricksClient import DatabricksClient
from Graph import Graph
from collections import defaultdict



groupUsermap = defaultdict(set)
userGroupmap = defaultdict(set)







def main():
    dryrun = False;

    print('Number of arguments:', len(sys.argv[1:]), 'arguments.')
    print('Argument List:', str(sys.argv[1:]))

    for arg in str(sys.argv[1:]):
        if arg.casefold()=="--dryRun":
            dryrun = True;

    # Load settings
    config = configparser.ConfigParser()
    config.read(['config.cfg', 'config.dev.cfg'])
    azure_settings = config['azure']
    db_settings = config['databricks']

    graph: Graph = Graph(azure_settings)
    dbclient : DatabricksClient = DatabricksClient(db_settings)

    dbusers=dbclient.get_DBUsers()

    users_page = graph.get_users()

    print("1.All Users Read")

    groups_page = graph.get_groups()

    print("2.All top level groups Read")

    for group in groups_page['value']:
        print("Group is "+group["displayName"])
        for arg in sys.argv[1:]:
            if not arg.startswith("--") and arg.casefold() == group["displayName"].casefold():
                extractFromGroup(graph, group["id"], group["displayName"]);


    for u in userGroupmap.keys():
        if not dryrun:
            exists = False

            for udb in dbusers["Resources"]:
                if u[0].casefold() == udb["displayName"].casefold() :
                    exists = True;

            if not exists:
                dbclient.createdbuser(u)

    dbusers = dbclient.get_DBUsers()

    for u in groupUsermap.keys():
        print("2")
        dbclient.createdbgroup(u,groupUsermap.get(u),dbusers)



def extractFromGroup(graph: Graph,gid, displayName):
    gms = graph.get_groupmembers(gid)
    for gm in gms['value']:
        if gm["@odata.type"] == "#microsoft.graph.user":
            for gp in str(displayName).split(":"):
                groupUsermap[gp].add((gm["displayName"] , gm["userPrincipalName"]))
                userGroupmap[(gm["displayName"],gm["userPrincipalName"])].add(gp)

        elif gm["@odata.type"] == "#microsoft.graph.group":
            extractFromGroup(graph,gm["id"], displayName + ":" +gm["displayName"])


def list_users(graph: Graph):
    users_page = graph.get_users()

    for user in users_page['value']:
        print('User:', user['displayName'])
        print('  ID:', user['id'])
        print('  Email:', user['mail'])

    # If @odata.nextLink is present
    more_available = '@odata.nextLink' in users_page

    # TODO: loop and populate additional users
    print('\nMore users available?', more_available, '\n')





def display_access_token(graph: Graph):
    token = graph.get_user_token()
    print('User token:', token, '\n')


if __name__ == '__main__':

    main()
