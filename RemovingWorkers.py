import re
import stat
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


### USER INPUT ###
NrOfRemovals = 2 # This value should be given by the user. Number of workers to be removed.


### FILES - TO BE CHANGED IN FINAL VERSION ###
Read_file_name = "example-ansiblehosts-file"
Write_file_name = "New-example-ansiblehosts-file"

Read_file_name_2 = "example-normalhosts-file"
Write_file_name_2 = "New-example-normalhosts-file"


### ADJUSTING THE ANSIBLE HOSTS FILE ###

StorageStrings = [] # Temporary storage

# Read File
with open(Read_file_name) as f:
	lines = f.readlines()
	# Count how many workers there are.
	NrOfWorkers = 0
	for line in lines:
		if line.startswith("sparkworker"):
			NrOfWorkers += 1
		elif line.startswith("[configNode]"):
			break

	NewNrOfWorkers = 0 # This represents how many workers there are supposed to be

	# Check to see that user is not trying to remove more workers than are available.
	if NrOfWorkers - NrOfRemovals < 1:
		raise ValueError('User is trying to remove more workers than possible. Atleast one worker should be present.')

	PassedMidPoint = False #check if we've passed by mid-point of document. NewWorker counting restarts

	# Adding the lines, apart from those workers which should be removed.
	for line in lines:
		if PassedMidPoint == True:
			NewNrOfWorkers = 0
			PassedMidPoint = False
		if line.startswith("sparkworker"):
			if NewNrOfWorkers != NrOfWorkers - NrOfRemovals:
				StorageStrings.append(line)
				NewNrOfWorkers += 1
		else:
			StorageStrings.append(line)
			if line.startswith("[configNode]"):
				PassedMidPoint = True

# Write the correct lines to the new file:
with open(Write_file_name, "w") as f1:
	for line in StorageStrings:
		f1.write(line)

# make file executable
st = os.stat(Write_file_name)
os.chmod(Write_file_name, st.st_mode | stat.S_IEXEC)



### ADJUSTING THE 'NORMAL' HOSTS FILE ###

StorageStrings = [] # Make it empty again.
RemovedMachines = {} # Add the details of the machines which have been removed.

# Read File
with open(Read_file_name_2) as f:
	lines = f.readlines()

	NewNrOfWorkers = 0 # This represents how many workers there are supposed to be

	for line in lines:
		CurrentLine = line.split()
		if len(CurrentLine) == 2:
			if CurrentLine[1].startswith("sparkworker"):
				if NewNrOfWorkers != NrOfWorkers - NrOfRemovals:
					StorageStrings.append(line)
					NewNrOfWorkers += 1
				elif NewNrOfWorkers == NrOfWorkers - NrOfRemovals:
					RemovedMachines[CurrentLine[1]] = CurrentLine[0]
			else:
				StorageStrings.append(line)
		else:
			StorageStrings.append(line)

# Write the correct lines to the new file:
with open(Write_file_name_2, "w") as f1:
	for line in StorageStrings:
		f1.write(line)

# make file executable
st = os.stat(Write_file_name_2)
os.chmod(Write_file_name_2, st.st_mode | stat.S_IEXEC)



### REMOVING THE MACHINES FROM OPENSTACK ###

print("These are the machines we want to remove from OpenStack: " + str(RemovedMachines))


# Setting up logging parameters
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setting up cloud configuration parameters
flavor_name = "ssc.small"
private_net = "team6_private_network" #"SNIC 2018/10-30 Internal IPv4 Network"
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


# Find the instances from OpenStack which are relevant to us
relevant_instances = nova.servers.list(search_opts={"name": "team6"})
print("These are the machines we currently have on openstack: " + str(relevant_instances))

### Watch out with what you do here!!! The program will delete whatever instance you define with IPadresses! Don't just uncomment something here!
#IPadresses = RemovedMachines.values()
#IPadresses = ['192.168.1.44', '192.168.1.20', '192.168.1.9']   # The IP addresses of the instances Erik started
IPadresses = ['192.168.1.88']  # The IP of some test instance you can delete

for CurrentIP in IPadresses:
	print("\nThe IP of the instance  which we want to delete from OpenStack: " + str(CurrentIP))

	for instance in relevant_instances:
		name = instance.name
		IPfound = False   # A check to see if we've found the IP we're looking for.
		address = instance.addresses  # Getting the IP value of the instance
		for item in address.items():
			for element in item[1]:
				if CurrentIP in element.values():
					print("Instance " + str(name) + " has IP: ", CurrentIP)
					IPfound = True
					print('Lets delete instance ' + str(name) + ' from Openstack')
					nova.servers.delete(instance)
					print('Deletion complete')
		if IPfound != True:
			print("Instance " + str(name) + " does not have IP: ", CurrentIP)