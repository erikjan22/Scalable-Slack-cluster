#!/usr/bin/python

import simplejson as json
import sys

def empty_cluster_info():
  """ Function which empties the ClusterInfo and only keeps the basic (empty) skeleton
  """
  with open('ClusterInfo.json', mode='r') as jsonfile:
    if len(jsonfile.readline()) == 0:
      sys.exit('Error: ClusterInfo.json file appears to be empty.')
    else:
      jsonfile.seek(0,0)   # Return the pointer to the beginning of the file
      ClusterInfo = json.load(jsonfile)
      nrSlaves = ClusterInfo[0].get("NumberSlaves")
      if not ClusterInfo[0]["ExistMaster"]:
        sys.exit('Error: Trying to empty ClusterInfo, while according to the info there is already no master left.')
      RemovedMachines = []
      for vm in range(1, nrSlaves+2):
        RemovedMachines.append(ClusterInfo[-vm].get("VMname"))
    jsonfile.close()

  with open('ClusterInfoUpdated.json', mode='w') as jsonfile:
    del ClusterInfo[1:]   # Remove the info of all the machines
    ClusterInfo[0]["ExistMaster"] = False # we don't have a master anymore
    ClusterInfo[0]["NumberSlaves"] = 0 # Put the number of slaves to zero
    print("In total %s virtual machines have been removed from the cluster info.\n \
      These are: %s" % (str(len(RemovedMachines)), str(RemovedMachines)))
    json.dump(ClusterInfo, jsonfile)
    jsonfile.close()
    return    



if __name__ == '__main__':
  if len(sys.argv) != 1:
    sys.exit("Error: Function doesn't take arguments")
  empty_cluster_info()
