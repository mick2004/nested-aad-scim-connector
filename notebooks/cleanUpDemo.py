import sys

import configparser

from model.DatabricksClient import DatabricksClient

def main():
    # Load settings
    config = configparser.ConfigParser()
    config.read(['config.cfg', 'config.dev.cfg'])
    db_settings = config['databricks']
    dbclient: DatabricksClient = DatabricksClient(db_settings)
    dbusers = dbclient.get_DBUsers()

    for udb in dbusers["Resources"]:
        if udb["displayName"] in ["Jesika Parmar","User 1","User 2"]:
            dbclient.deleteUser(udb["id"])

    dbgroups = dbclient.get_DBGroups()
    for udb in dbgroups["Resources"]:
        if udb["displayName"] in ["Child","c1","c2"]:
            dbclient.deleteGroup(udb["id"])




    print("--ready for demo-")


if __name__ == '__main__':
    main()