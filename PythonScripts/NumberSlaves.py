#!/usr/bin/env python3

import simplejson as json
import sys

def number_slaves():
  """ Function which retrieves the current number of workers from the ClusterInfo.json.
  """

  with open('ClusterInfo.json', mode='r') as jsonfile:
    if len(jsonfile.readline()) == 0:
      sys.exit('Error: ClusterInfo.json file appears to be empty.')
    else:
      jsonfile.seek(0,0)   # Return the pointer to the beginning of the file
      ClusterInfo = json.load(jsonfile)
      nrSlaves = ClusterInfo[0].get("NumberSlaves")
    jsonfile.close()
  print(nrSlaves)
  return "Finished printing the number of slaves"



if __name__ == '__main__':
  if len(sys.argv) != 1:
    sys.exit('Error in function call. This function requires no arguments.')
  else:
    output = number_slaves()
    sys.exit(str(output))
