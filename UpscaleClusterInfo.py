#!/usr/bin/python

import simplejson as json
import sys

def update_cluster_info(args):
  """ Function which updates the ClusterInfo.json file after new nodes are created.
  Calling this function with the argument consisting of multiple elements will result in a master node being added to the info.
  Else a slave node will be added to the info.
  """
  with open('TemporaryInfo.json', mode='r') as jsonfile:
    TemporaryInfo = json.load(jsonfile)
    VMname = args[0]
    privateIP = TemporaryInfo.get("privateIpAddress")
    publicIP = TemporaryInfo.get("publicIpAddress")
    if len(args) > 1:
      master = True
    else:
      master = False
    jsonfile.close()

  with open('ClusterInfo.json', mode='r') as jsonfile:
    if len(jsonfile.readline()) == 0:
      sys.exit('Error: ClusterInfo.json file appears to be empty.')
    else:
      jsonfile.seek(0,0)   # Return the pointer to the beginning of the file
      ClusterInfo = json.load(jsonfile)
      nrSlaves = ClusterInfo[0].get("NumberSlaves")
    jsonfile.close()

  with open('ClusterInfoUpdated.json', mode='w') as jsonfile:
    newmachine = {}
    newmachine['privateIP'] = privateIP
    newmachine['publicIP'] = publicIP
    newmachine['VMname'] = VMname
    if master:
        if ClusterInfo[0]["ExistMaster"]:
          sys.exit('Error: Trying to add a master while according to ClusterInfo there already is one.')
        else:
          ClusterInfo[0]["ExistMaster"] = True
          newmachine['role'] = 'Master'
    else:
        if not ClusterInfo[0]["ExistMaster"]:
          sys.exit('Error: Trying to add a slave while according to ClusterInfo there is no master.')
        else:
          nrSlaves += 1   # Adding a new slave to the count
          ClusterInfo[0]["NumberSlaves"] = nrSlaves
          newmachine['SlaveID'] = str(nrSlaves)
          newmachine['role'] = 'Slave'
    ClusterInfo.append(newmachine)
    json.dump(ClusterInfo, jsonfile)
    jsonfile.close()



if __name__ == '__main__':
  if len(sys.argv) == 1 or len(sys.argv) > 3:
    sys.exit('Wrong arguments given.')
  update_cluster_info(sys.argv[1:])
