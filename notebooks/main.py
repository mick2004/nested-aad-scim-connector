import sys

import configparser

from model.DatabricksClient import DatabricksClient
from model.Graph import Graph
from collections import defaultdict

groupUsermap = defaultdict(set)
userGroupmap = defaultdict(set)


def main():
    dryrun = False;

    print('Number of arguments:', len(sys.argv[1:]), 'arguments.')
    print('Argument List:', str(sys.argv[1:]))

    if len(sys.argv[1:]) > 2:
        print("only 2 arguments supported")
        return

    toplevelgroup = ""

    for arg in sys.argv[1:]:
        if arg.casefold() == "--dryRun":
            dryrun = True;
        else:
            if toplevelgroup == "":
                toplevelgroup = arg;
            else:
                print("Only one group supported")
                return


    # Load settings
    config = configparser.ConfigParser()
    config.read(['../config/config.cfg', 'config.dev.cfg'])
    azure_settings = config['azure']
    db_settings = config['databricks']

    graph: Graph = Graph(azure_settings)
    dbclient: DatabricksClient = DatabricksClient(db_settings)

    dbusers = dbclient.get_DBUsers()

    print("1.All Databricks Users Read")

    groups_page = graph.get_groups()

    print("2.All top level AAD groups Read")
    print("3.Top level group requested is " + toplevelgroup)

    for group in groups_page['value']:
        print("Group is " + group["displayName"])
        for arg in sys.argv[1:]:
            if not arg.startswith("--") and arg.casefold() == group["displayName"].casefold():
                groupUsermapU, userGroupmapU = graph.extractFromGroup(graph, group["id"], group["displayName"],
                                                                      groupUsermap, userGroupmap);

    print("4.Hierarchy analysed,going to create users and groups")

    for u in userGroupmapU.keys():
        if not dryrun:
            exists = False

            for udb in dbusers["Resources"]:
                if u[0].casefold() == udb["displayName"].casefold():
                    exists = True;

            if not exists:

                dbclient.createdbuser(u)
                print("User created in databricks : " + u)

    dbusers = dbclient.get_DBUsers()
    dbGroups = dbclient.get_DBGroups()

    for u in groupUsermapU.keys():
        exists = False
        for dbg in dbGroups["Resources"]:
            if u.casefold() == dbg["displayName"].casefold():
                exists = True;
                #compare and add remove the members as needed
                dbclient.patchdbgroup(dbg["id"], groupUsermap.get(u), dbg,dbusers)


        if not exists:
            dbclient.createdbgroup(u, groupUsermap.get(u), dbusers)
            print("Group and User assignment created in databricks : " + u)


if __name__ == '__main__':
    main()
