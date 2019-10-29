# Made by Rasmus, trying to fix Markus file QTL_automation.py

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
private_net = 'SNIC 2019/10-32 Internal IPv4 Network'
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

def find_all_instances():
    relevant_instance = nova.servers.list(search_opts={"name": "team6"})

    for instance in relevant_instance:
        ip = instance.networks[private_net]
        
        name = instance.name
        if worker_name in name:
            print(name, "has IP:", ip)
        else:
            print(name, "has IP:", ip)

find_all_instances()

