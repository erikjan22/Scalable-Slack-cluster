#!/usr/bin/env python3

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

  # Write to /etc/hosts
  with open(PATH+"/hosts", "w") as f:
  #with open("hosts", "w") as f:
    f.writelines(ansibleip + " ansible-host\n")

    f.writelines("\n# The following lines are desirable for IPv6 capable\n")
    f.writelines("::1 ip6-localhost ip6-loopback\n")
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

  with open(PATH+"/ansible/hosts", "w") as f:
  #with open("ansiblehosts", "w") as f:
    f.writelines("ansible-host" + ansible_host + ansibleip  + "\n")

    # Write ansible config
    f.writelines("\n" + "[configNode]" + "\n")
    f.writelines("ansible-node ansible_connection=local ansible_user=" + username + "\n")

    # Write sparkMaster
    f.writelines("\n" + "[sparkmaster]" + "\n")

    # Write sparkWorker
    f.writelines("\n" + "[sparkworker]" + "\n")

    print("Wrote to /etc/ansible/hosts")
    f.close()

  return


if __name__ == '__main__':
  if len(sys.argv) != 3:
    sys.exit('Wrong arguments given.')
  write_to_host_files(sys.argv[1], sys.argv[2])
