import pymongo
import subprocess

def create_consistent_mongodb_snapshot(mongo_uri):

        # Connect to MongoDB and lock the database for consistency
        client = pymongo.MongoClient(mongo_uri)
        admin_db = client.admin
        admin_db.command("fsyncLock")
    
        # list of secondary nodes in the replica set
        secondary_nodes = client.admin.command("replSetGetStatus")["members"]
        secondary_node = None
    
        # Select the first secondary node 
        for node in secondary_nodes:
            if node["stateStr"] == "SECONDARY":
                secondary_node = node["name"]
                break
    try: 
        if secondary_node:
            # Create a snapshot of the VM disk for the selected secondary node
            snapshot_command = f"make-vm-snapshot {secondary_node}"
            subprocess.run(snapshot_command, shell=True)
            print(f"Snapshot created for secondary node: {secondary_node}")
        else:
            print("No secondary nodes found in the replica set.")
    except Exception as e:
        print(f"exception: {str(e)}")
    finally:
        try:
            admin_db.command("fsyncUnlock")
        except Exception as e:
             print(f"Exception while unlocking the db: {str(e)}")

if __name__ == "__main__":
    mongo_connection_string = "mongodb://admin:password@vm-hostname1,vm-hostname2,vm-hostname3/admin?otherParams"
    create_consistent_mongodb_snapshot(mongo_connection_string)
