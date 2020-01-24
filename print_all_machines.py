#!/usr/bin/env python3

import simplejson as json
import sys

def list_of_all_machines():
  """ Function which retrieves a list of all unique vm names from ClusterInfo.json.
  """

  with open('ClusterInfo.json', mode='r') as jsonfile:
    if len(jsonfile.readline()) == 0:
      sys.exit('Error: ClusterInfo.json file appears to be empty.')
    else:
      jsonfile.seek(0,0)   # Return the pointer to the beginning of the file
      ClusterInfo = json.load(jsonfile)
      list_vm_names = []
      for index in range(0, len(ClusterInfo)):
        if ClusterInfo[index].get("VMname"):
          list_vm_names.append(ClusterInfo[index].get("VMname"))
      list_vm_names = list(set(list_vm_names))

  print(list_vm_names)
  return "Finished retrieving all machine names"



if __name__ == '__main__':
  if len(sys.argv) != 1:
    sys.exit('Error in function call. This function requires no arguments.')
  else:
    output = list_of_all_machines()
    sys.exit(str(output))

