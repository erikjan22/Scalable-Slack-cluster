#!/usr/bin/env python

from flask import Flask, request
import simplejson as json
import subprocess


app = Flask(__name__)


@app.route('/SparkCluster/setup', methods=['GET', 'POST'])
def new_cluster():
  """ 
  Def: Function which builds a new Spark cluster from scratch. This is done by starting a new vm and placing a master and slave node on this single machine
  """
  print("\nStart of building a new cluster. \n")

  subprocess.call("./mastercreate.sh")
  subprocess.call("./AnsibleScripts/ansible-master-script.sh")

  return ("\nDone building a new cluster. \n")


@app.route('/SparkCluster/upscaling', methods=['GET', 'POST'])
def new_slave():
  """ 
  Def: Function which adds at most 3 slave nodes to the existing Spark cluster.
  """
  numberAddSlaves = request.args.get('number', '')
  numberAddSlaves = str(numberAddSlaves)

  if numberAddSlaves > 3:
    return_message = "\nUser is trying to add "+str(numberAddSlaves)+" slaves, while at most 3 is possible")
    return(return_message)
  elif numberAddSlaves > 0:
    numberAddSlaves = numberAddSlaves
  else:
    numberAddSlaves = 1

  print("\nAdding " + str(numberAddSlaves)+"  Spark slave(s) to the cluster. \n")

  for i in range(0, numberAddSlaves):
    subprocess.call("./slavecreate.sh")

  print("Starting Spark processes for new nodes")
  subprocess.call("./AnsibleScripts/ansible-slave-script.sh")

  return ("\nAdded "+str(numberAddSlaves)+" slave node(s) to the Spark cluster. \n")


@app.route('/SparkCluster/downscaling', methods=['GET', 'POST'])
def remove_slave():
  """ 
  Def: Function which removes at most 3 slave nodes from the existing Spark cluster.
  """
  numberRemSlaves = request.args.get('number', '')
  numberRemSlaves = str(numberRemSlaves)

  if numberRemSlaves > 3:
    return_message = "\nUser is trying to remove "+str(numberRemSlaves)+" slaves, while at most 3 is possible")
    return(return_message)
  elif numberRemSlaves > 0:
    numberRemSlaves = numberRemSlaves
  else:
    numberRemSlaves = 1

  print("\Removing " + str(numberRemSlaves)+"  Spark slave(s) from the cluster. \n")

  for i in range(0, numberRemSlaves):
    subprocess.call("./removenode.sh")

  return ("\nRemoved "+str(numberRemSlaves)+" slave node(s) from the Spark cluster. \n")


@app.route('/SparkCluster/destroycluster', methods=['GET', 'POST'])
def destoy_spark_cluster():
  """ 
  Def: Function which removes all the nodes from the Spark cluster.
  """

  user_input = input("Are you sure you want to destoy the Spark cluster? Answer with 'yes' if that is the case. Else, answer with something else.")

  if not str(user_input)=='yes':
    return_message = "\nYou responded with '"+str(user_input)+"', thereby choosing not to destroy the cluster\n"
    return (return_message)

  print("\nRemoving all the nodes from the Spark cluster. \n")

  subprocess.call("./destroycluster.sh")

  return ("\nFinished removing the Spark cluster. \n")


@app.route('/SparkCluster/clusterinfo', methods=['GET', 'POST'])
def retrieve_cluster_info():
  """ 
  Def: Function which collects the information from the ClusterInfo.json file and returns it to the user.
  """
  print("Start with retrieving cluster info.")

  cluster_info = "\n"

  try:
    with open('ClusterInfo.json', mode='r') as jsonfile:
      if len(jsonfile.readline()) == 0:
        sys.exit('Error: ClusterInfo.json file appears to be empty.')
      else:
        jsonfile.seek(0,0)   # Return the pointer to the beginning of the file
        ClusterInfo = json.load(jsonfile)

        if ClusterInfo[0]["ExistMaster"]:
          master_name = ClusterInfo[1].get("VMname")
          master_private_ip = ClusterInfo[1].get("privateIP")
          master_public_ip = ClusterInfo[1].get("publicIP")
          cluster_info = cluster_info + "The master node is build on a VM named "+master_name+", with privat IP "+master_private_ip+ " and public ip "+master_public_ip+"\n"
        else:
          cluster_info += "There doesn't appear to be a master node.\n"

      for index in range(0,len(ClusterInfo)):
        if ClusterInfo[index].get("role")=="Slave":
          slave_name = ClusterInfo[index].get("VMname")
          slave_private_ip = ClusterInfo[index].get("privateIP")
          slave_public_ip = ClusterInfo[index].get("publicIP")
          slave_id = ClusterInfo[index].get("SlaveID")
          cluster_info = cluster_info + "Slave "+slave_id+" is build on a VM named "+slave_name+", with privat IP "+slave_private_ip+ " and public ip "+slave_public_ip+"\n"

    jsonfile.close()
  except IOError:
    cluster_info = "\nError: There is no ClusterInfo.json file!\n\n"

  return cluster_info


if __name__ == '__main__':
	app.run(debug=True)
