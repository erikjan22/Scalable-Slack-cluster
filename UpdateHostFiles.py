#!/usr/bin/python


import simplejson as json
import os
import sys
import time
import logging
from os import system
from os import environ as env

PATH = os.path.abspath("/etc/")

# Takes in ansible, master, worker
def write_to_host_files(ansibleip, username):

  # Obtain info about Virtual Machines
  with open('ClusterInfo.json', mode='r') as jsonfile:
    ClusterInfo = json.load(jsonfile)
    slavenames = []
    slaveids = []
    slaveips = []
    for node in ClusterInfo:
      if node.get('role') == 'Master':
        masterip = node.get('privateIP')
      elif node.get('role') == 'Slave':
        slavenames.append(node.get('VMname'))
        slaveids.append(node.get('SlaveID'))
        slaveips.append(node.get('privateIP'))

  # Write to /etc/hosts
  #with open(PATH+"/hosts", "w") as f:
  with open("hosts", "w") as f:
    f.writelines(ansibleip + " ansible-host\n")
    f.writelines(masterip + " sparkmaster\n")
    for i in range(len(slaveips)):
      f.writelines(slaveips[i] + " sparkworker" + slaveids[i] + "\n")

    # The following lines are desirable for IPv6 capable
    f.writelines("\n::1 ip6-localhost ip6-loopback\n")
    f.writelines("fe00::0 ip6-localnet\n")
    f.writelines("ff00::0 ip6-mcastprefix\n")
    f.writelines("ff02::1 ip6-allnodes\n")
    f.writelines("ff02::2 ip6-allrouters\n")
    f.writelines("ff02::3 ip6-allhosts\n")

    print("Wrote to etc/hosts")
    f.close()


  # Open /etc/ansible/hosts
  ansible_host = " ansible_ssh_host="
  ansible_conn = " ansible_connection=local ansible_user=" + username
  master_conn  = " ansible_connection=ssh ansible_user=" + username
  worker_conn  = " ansible_connection=ssh ansible_user=" + username

  #with open(PATH+"/ansible/hosts", "w") as f:
  with open("ansiblehosts", "w") as f:
    f.writelines("ansible_host" + ansible_host + ansibleip  + "\n")
    f.writelines("sparkmaster" + ansible_host + masterip + "\n")
    for i in range(len(slaveips)):
      f.writelines("sparkworker" + slaveids[i] + ansible_host + slaveips[i] + "\n")

    # Write ansible config
    f.writelines("\n" + "[configNode]" + "\n")
    f.writelines("ansible-node ansible_connection=local ansible_user=" + username + "\n")

    # Write sparkMaster
    f.writelines("\n" + "[sparkmaster]" + "\n")
    f.writelines("sparkmaster ansible_connection=ssh ansible_user=" + username + "\n")

    # Write sparkWorker
    f.writelines("\n" + "[sparkworker]" + "\n")
    for i in range(len(slaveips)):
      f.writelines("sparkworker" + slaveids[i] + " ansible_connection=ssh ansible_user=" + username + "\n")

    print("Wrote to /etc/ansible/hosts")
    f.close()

if __name__ == '__main__':
  if len(sys.argv) != 3:
    sys.exit('Wrong arguments given.')
  write_to_host_files(sys.argv[1], sys.argv[2])
