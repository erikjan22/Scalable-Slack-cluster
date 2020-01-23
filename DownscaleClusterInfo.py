#!/usr/bin/python

import simplejson as json
import sys

def downscale_cluster_info():
  """ Function which updates the ClusterInfo.json file after a node has been removed from the cluster.
      Can only remove the master from the ClusterInfo. For this, use another function: EmptyClusterInfo.py
      Only removes the information of one machine from ClusterInfo.json
  """
  with open('ClusterInfo.json', mode='r') as jsonfile:
    if len(jsonfile.readline()) == 0:
      sys.exit('Error: ClusterInfo.json file appears to be empty.')
    else:
      jsonfile.seek(0,0)   # Return the pointer to the beginning of the file
      ClusterInfo = json.load(jsonfile)
      nrSlaves = ClusterInfo[0].get("NumberSlaves")
      if nrSlaves == 0:
      	sys.exit("Error: According to the 'NumberSlaves' counter in ClusterInfo there are already no more slave nodes.")
      elif not ClusterInfo[0]["ExistMaster"]:
        sys.exit('Error: Trying to remove a slave while according to ClusterInfo there is no master.')
    jsonfile.close()

  with open('ClusterInfoUpdated.json', mode='w') as jsonfile:
  	VMname = ClusterInfo[-1].get("VMname")
  	del ClusterInfo[-1]   # Remove the info of the final machine
  	ClusterInfo[0]["NumberSlaves"] = nrSlaves-1 # Subtract one from the number of slaves after removal
  	json.dump(ClusterInfo, jsonfile)
  	jsonfile.close()
  	print(VMname)
  	return



if __name__ == '__main__':
  if len(sys.argv) != 1:
    sys.exit("Error: Function doesn't take arguments")
  downscale_cluster_info()
