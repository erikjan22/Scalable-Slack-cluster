#!/usr/bin/env python3

import simplejson as json
import sys

def upscale_cluster_info(VMname, master=False):
  """ Function which updates the ClusterInfo.json file after new nodes are created.
  Calling this function with the argument consisting of multiple elements will result in a master node being added to the info.
  Else a slave node will be added to the info.
  """
  with open('TemporaryInfo.json', mode='r') as jsonfile:
    TemporaryInfo = json.load(jsonfile)
    privateIP = TemporaryInfo.get("privateIpAddress")
    publicIP = TemporaryInfo.get("publicIpAddress")
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
    if master:
      if ClusterInfo[0]["ExistMaster"]:
        sys.exit('Error: Trying to add a master while according to ClusterInfo there already is one.')
      else:
        newmaster = {}
        newmaster['privateIP'] = privateIP
        newmaster['publicIP'] = publicIP
        newmaster['role'] = 'Master'
        newmaster['VMname'] = VMname
        ClusterInfo[0]["ExistMaster"] = True
        ClusterInfo.append(newmaster)

    if not ClusterInfo[0]["ExistMaster"]:
      sys.exit('Error: Trying to add a slave while according to ClusterInfo there is no master.')
    else:
      nrSlaves += 1   # Adding a new slave to the count
      newslave = {}
      newslave['privateIP'] = privateIP
      newslave['publicIP'] = publicIP
      newslave['VMname'] = VMname
      newslave['SlaveID'] = str(nrSlaves)
      newslave['role'] = 'Slave'
      ClusterInfo[0]["NumberSlaves"] = nrSlaves
      ClusterInfo.append(newslave)
    json.dump(ClusterInfo, jsonfile)
    jsonfile.close()

    return



if __name__ == '__main__':
  if len(sys.argv) == 1 or len(sys.argv) > 3:
    sys.exit('Wrong arguments given.')
  elif len(sys.argv) == 2:
    upscale_cluster_info(sys.argv[1])
  else:
    upscale_cluster_info(sys.argv[1], True)
