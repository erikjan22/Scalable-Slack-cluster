import os
import sys
import time
import logging
from os import system
from novaclient import client
from os import environ as env
from keystoneauth1 import loading
from keystoneauth1 import session
import glanceclient.v2.client as glclient

# Setting up logging parameters
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setting up cloud configuration parameters
flavor_name = "ssc.small"
private_net = "SNIC 2019/10-32 Internal IPv4 Network"  #"team6_private_network" 
floating_ip_pool_name = None
floating_ip = None
image_name = "Ubuntu 16.04 LTS (Xenial Xerus) - latest"
keyname = "team6key"
loader = loading.get_plugin_loader('password')


# Authorizing user from global variables
auth = loader.load_from_options(auth_url=env['OS_AUTH_URL'],
                                username=env['OS_USERNAME'],
                                password=env['OS_PASSWORD'],
                                project_name=env['OS_PROJECT_NAME'],
                                project_domain_name=env['OS_USER_DOMAIN_NAME'],
                                project_id=env['OS_PROJECT_ID'],
                                user_domain_name=env['OS_USER_DOMAIN_NAME'])
sess = session.Session(auth=auth)
nova = client.Client('2.1', session=sess)
glance = glclient.Client('2.1', session=sess)
logger.info("__ACC__: Successfully completed User Authorization.")

worker_name = "team6_sparkworker"
master_name = "team6_sparkmaster"
ansible = {"name": "ansible-node", "ip": "192.168.1.9"}
ansible_host = " ansible_ssh_host="
prefix = "team6_"

PATH = os.path.abspath("/etc/")


# Simple function to print all Group12 relevant instances
def find_all_instances():

	workers = []
	ansible = ""
	master = ""
	
	

	relevant_instances = nova.servers.list(search_opts={"name": prefix})
	for instance in relevant_instances:
		if (instance.status != "ACTIVE"):
			# if the instance not active, wait 5 seconds
			time.sleep(5)
		try:
			ip = instance.networks[private_net][0]
			name = instance.name
			status = instance.status
			print(status)
			if worker_name in name:
				print("Worker ", name, "Has IP ", ip)
				id_nr = int(name.strip(worker_name))
				if id_nr > 0:
					workers.append({"name": name.strip(prefix), "ip": ip})
			else:
				master = {"name": name.strip(prefix), "ip": ip}
				print("Master ", name, "HAS ip ", ip)
		except:
			pass
	print("Got Instances")
	return master, workers




# Takes in ansible, master, worker
def write_to_ansible_host(a, m, w):
	proceed = True
	if (len(a) * len(m) * len(w) ) == 0:
		proceed = False
	if proceed:
		# Open /etc/hosts
		
		with open(PATH+"/hosts", "w") as f:
			f.writelines(a["ip"] + " " + a["name"] + "\n")
			f.writelines(m["ip"] + " " + m["name"] + "\n")
			for i in range(len(workers)):
				f.writelines(w[i]["ip"] + " " + w[i]["name"] + "\n")

			# The following lines are desirable for IPv6 capable 
			f.writelines("\n::1 ip6-localhost ip6-loopback\n")
			f.writelines("fe00::0 ip6-localnet\n")
			f.writelines("ff00::0 ip6-mcastprefix\n")
			f.writelines("ff02::1 ip6-allnodes\n")
			f.writelines("ff02::2 ip6-allrouters\n")
			f.writelines("ff02::3 ip6-allhosts\n")
			f.writelines("192.168.1.9 ansible-node\n")

		print("Wrote to etc/hosts")
		f.close()


		# Open /etc/ansible/hosts
		ansible_conn = " ansible_connection=local ansible_user=ubuntu"
		master_conn  = " ansible_connection=ssh ansible_user=ubuntu"
		worker_conn  = " ansible_connection=ssh ansible_user=ubuntu"
		ansible_host = " ansible_ssh_host="
		with open(PATH+"/ansible/hosts", "w") as f:
			f.writelines(a["name"] + ansible_host + a["ip"] + "\n")
			f.writelines(m["name"] + ansible_host + m["ip"] + "\n")
    			for i in range(len(w)):
        			f.writelines(w[i]["name"] + ansible_host + w[i]["ip"] + "\n")

			# Write ansible config
			f.writelines("\n" + "[configNode]" + "\n")
			f.writelines(a["name"] + ansible_conn + "\n")

			# Write sparkMaster
			f.writelines("\n" + "[sparkmaster]" + "\n")
			f.writelines(m["name"] + master_conn + "\n")

			# Write sparkWorker
			f.writelines("\n" + "[sparkworker]" + "\n")
			for i in range(len(w)):
				f.writelines(w[i]["name"] + worker_conn + "\n")

		print("Wrote to /etc/ansible/hosts")
		f.close()

	else:
		print("Failed to write to files...")
		print("Not enough workers or masters were found!")


master, workers = find_all_instances()
write_to_ansible_host(ansible, master, workers)
