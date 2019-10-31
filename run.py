import subprocess
from ruamel import yaml
from flask import Flask, request, render_template, g, jsonify, Response
import json
import shelve # For temporary storage
from random import randrange

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
#cmd = ["source", "SNIC.sh"]
#process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
#output, error = process.communicate()

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

worker_name = "sparkworker"
master_name = "sparkmaster"
ansible = {"name": "ansible-node", "ip": "192.168.1.9"}
ansible_host = " ansible_ssh_host="
prefix = "team6_"

PATH = os.path.abspath("/etc/")

app = Flask(__name__)

NumberWorkers = 0   # Global counter for keeping track of number of workers


# Return the index from our webpage
@app.route('/QTL/index')
def index():
    return render_template('index.html')


# Return the 'about' section from our webpage
@app.route('/QTL/about')
def about():
    return render_template('about.html')


# Building a new clustter from scratch
@app.route('/QTL/setup', methods=['GET', 'POST'])
def start_instance():
    """ 
    Set up how many workers to use
    """

    global ansible
    workers_list = []
    master = {}

    # Modifies the Heat templates with number of workers and start the stack
    heat_template = 'Heat.yml'
    workers = request.args.get('workers')
    with open(heat_template) as f:
        list_doc = yaml.safe_load(f)
        parameters = list_doc['parameters']
        node_count = parameters['node_count']
        list_doc['parameters']['node_count']['default'] = int(workers)

        with open(heat_template, 'w') as f:
            yaml.dump(list_doc, f, default_flow_style=False)

        # Create stack
        cmd = ["openstack", "stack", "create",
               "team6_api", "-f", "yaml", "-t", "Heat.yml"]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output, error = process.communicate()

    # Remove all IP addresses in  ~/.ssh/known_hosts
    cmd = ["truncate", "-s", "0", "../.ssh/known_hosts"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, error = process.communicate()

    # Find instances for NOVA
    time.sleep(180)
    relevant_instances = nova.servers.list(search_opts={"name": prefix})

    global NumberWorkers
    workerid = 1

    # Finds the relevant instances, aka workers
    for instance in relevant_instances:
        if (instance.status != "ACTIVE"):
            # if the instance not active, wait 5 seconds
            time.sleep(5)
        try:
            ip = instance.networks[private_net][0]
            name = instance.name
            status = instance.status
            print("Name: ", name)
            print("IP: ", ip)

            if worker_name in name:
                print("Worker " + str(name) + " has IP " + str(ip))
                workername = "sparkworker" + str(workerid)
                print("workername is: " + str(workername))
                workers_list.append({"name": workername, "ip": ip})
                print(workers_list)
                workerid =  workerid + 1
                global NumberWorkers
                NumberWorkers = NumberWorkers + 1
                #id_nr = int(name.strip(worker_name))
                #if id_nr > 0:
                #    workers_list.append({"name": name.strip(prefix), "ip": ip})
            else:
                master = {"name": name.strip(prefix), "ip": ip}
                print("Master " + str(name) + " has IP " + str(ip))
            print("\n")
        except:
            pass

    print(workers_list)
    print(master)
    print("")
    print("Got Instances")
    print("")

    print("Total number of workers = " + str(NumberWorkers))

    # Write to host files
    time.sleep(60)
    write_to_ansible_host(ansible, master, workers_list)
    print("Finished setting up the hosts files for Ansible\n")

    print("Next step is to use Ansible on our new nodes")
    time.sleep(60)
    run_ansible()
    print("=================")
    print("Finished running Ansible on the nodes")

    return "Finished setup process\n"


# Adding workers to the stack
@app.route('/QTL/upscaling', methods=['GET', 'POST'])
def upscaling_workers():
    """ 
    Modify workers, adding new ones to the stack
    """

    global ansible
    workers_list = []
    master = {}
    print("Starting more clusters")

    # Modifies the Heat templates with number
    heat_template = 'Heat_worker.yml'  # Different heat file, only starts workers
    #if request.method == 'POST':
        #workers = request.form['numWorkers']
    workers = request.args.get('workers')
    with open(heat_template) as f:
        list_doc = yaml.safe_load(f)
        parameters = list_doc['parameters']
        node_count = parameters['node_count']
        list_doc['parameters']['node_count']['default'] = int(workers)

        with open(heat_template, 'w') as f:
            yaml.dump(list_doc, f, default_flow_style=False)

        stackname = "team6_addWorkers_ID_" + str(randrange(1000))
        print("The name of the new stack is: " + stackname)

        cmd = ["openstack", "stack", "create",
               stackname, "-f", "yaml", "-t", "Heat_worker.yml"]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output, error = process.communicate()


    # Find instances for NOVA
    time.sleep(60)
    relevant_instances = nova.servers.list(search_opts={"name": prefix})
    print("We now have these instances:" + str(relevant_instances))

    id_worker = 0
    global NumberWorkers
    NumberWorkers = 0  # Restart counting, going through all workers again

    # Finds the relevant instances, aka workers
    for instance in relevant_instances:
        if (instance.status != "ACTIVE"):
            # if the instance not active, wait 5 seconds
            time.sleep(5)

        try:
            ip = instance.networks[private_net][0]
            name = instance.name
            status = instance.status
            print("Instance name: ", name)
            print("Instance IP: ", ip)

            if worker_name in name:
                print("The worker " + str(name) + " has IP " + str(ip))
                id_worker = id_worker + 1
                print("The id_worker = " + str(id_worker))
                workername = "sparkworker" + str(id_worker)
                print("Printing id_worker and workername:")
                workers_list.append({"name": workername, "ip": ip})
                NumberWorkers += 1
                print("Number of workers = " + str(NumberWorkers))

            else:
                master = {"name": name.strip(prefix), "ip": ip}
                print("The master " + str(name) + " has IP " + str(ip))

            print("\n=============================================\n")

        except:
            pass

    print(workers_list)
    print(master)
    print("")
    print("Got Instances")
    print("")

    print("Total number of workers = " + str(NumberWorkers))

    # Write to host files
    time.sleep(30)
    write_to_ansible_host(ansible, master, workers_list)
    print("Wrote to both /etc/hosts and /etc/ansible/hosts files \n")

    time.sleep(15)
    print("Next step is using Ansible on all the nodes.")
    run_ansible()
    print("=================")
    print("Ansible launch has been completed")

    return "Finished upscaling process\n"


    #return render_template('modify.html')  # For web interface



# Removing workers from the stack
@app.route('/QTL/downscaling', methods=['GET', 'POST'])
def downscaling_workers():
    """ 
    Removing workers, downscaling the stack
    """

    # Temporary storage
    StorageStrings = []

    # User input for how many workers to remove
    NrOfRemovals = int(request.args.get('workers'))
    global NumberWorkers
    NrOfWorkers = NumberWorkers

    # Adjusting /etc/ansible/hosts file
    # Read File
    with open(PATH+"/ansible/hosts", "r") as f:
        lines = f.readlines()

        NewNrOfWorkers = 0 # This represents how many workers there are supposed to be

        # Check to see that user is not trying to remove more workers than are available.
        if NrOfWorkers - NrOfRemovals < 1:
            print('User is trying to remove more workers than possible. Atleast one worker should be present.')
            return "STOP. Trying to remove too many workers. Atleast one worker should remain in the cluster\n"

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
    with open(PATH + "/ansible/hosts", "w") as f1:
        for line in StorageStrings:
            f1.write(line)

    # Adjusting /etc/hosts file
    StorageStrings = [] # Make it empty again.
    RemovedMachines = {} # Add the details of the machines which have been removed.

    # Read File
    with open(PATH+"/hosts", "r") as f:
        lines = f.readlines()

        NewNrOfWorkers = 0 # This represents how many workers there are supposed to be

        for line in lines:
            print(line)
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
    with open(PATH + "/hosts", "w") as f1:
        for line in StorageStrings:
            f1.write(line)

    # Removing the actual machines from OpenStack
    print("These are the machines we want to remove from OpenStack: " + str(RemovedMachines))

    # Find the instances from OpenStack which are relevant to us
    relevant_instances = nova.servers.list(search_opts={"name": prefix})
    print("These are the machines we currently have on openstack: " + str(relevant_instances))

    IPadresses = RemovedMachines.values()

    for CurrentIP in IPadresses:
        print("\nThe IP of the instance which we want to delete from OpenStack: " + str(CurrentIP))
        for instance in relevant_instances:
            name = instance.name
            IPfound = False   # A check to see if we've found the IP we're looking for.
            ip = instance.networks[private_net][0]

            if CurrentIP in ip:
                print("Instance " + str(name) + " has IP: ", CurrentIP)
                IPfound = True
                print('Lets delete instance ' + str(name) + ' from Openstack')
                nova.servers.delete(instance)
                print('Deletion complete')
        if IPfound != True:
            print("Instance " + str(name) + " does not have IP: ", CurrentIP)

    print("Removal process succesfull")

    # Finds the relevant instances, aka workers, and returns them to the user
    time.sleep(10)
    relevant_instances = nova.servers.list(search_opts={"name": prefix})
    print("We still have these nodes left:")
    for instance in relevant_instances:
        try:
            ip = instance.networks[private_net][0]
            name = instance.name
            print("Name: " + str(name) + ", IP: " + str(ip))
        except:
            pass

    global NumberWorkers
    NumberWorkers = NumberWorkers - NrOfRemovals
    print("Total number of workers = " + str(NumberWorkers))

    return('Done with removal process')


# Delete the entire cluster
@app.route('/QTL/delete')
def delete_stack():
    """ 
    Delete entire stack
    """
    stack_name = "team6_api"
    cmd = "openstack stack delete team6_api -y"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return "Deleting Stack\n"



# Show all the workers in the cluster
@app.route('/QTL/stack')
def show_stack():
    """ 
    Shows workers in stack
    """
    #return Response(json.dumps(workers_list), mimetype='application/json')
    global NumberWorkers
    print("\nThere are " + str(NumberWorkers) + " workers in the cluster.\n")
    return "Number of workers " + str(NumberWorkers) + "\n"


# Writes to hosts files the information of ansible, master, worker nodes
def write_to_ansible_host(a, m, w):
    proceed = True
    if (len(a) * len(m) * len(w) ) == 0:
        proceed = False
    if proceed:
        # Open /etc/hosts
        with open(PATH+"/hosts", "w") as f:
            f.writelines(a["ip"] + " " + a["name"] + "\n")
            f.writelines(m["ip"] + " " + m["name"] + "\n")
            for i in range(len(w)):
                # Get number of spark workers
                tmp_num = int(w[i]["name"].split("sparkworker", 1)[1])
                if (tmp_num > 0):
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
                tmp_num = int(w[i]["name"].split("sparkworker", 1)[1])
                if (tmp_num > 0):
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



# Running ansible. Called in setup.
def run_ansible():
    # Change user privilage and run ansible
    cmd = "sudo -u ubuntu ansible-playbook -b ../QTLaaS/spark_deployment.yml"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output, error



# Old function: running ansible seperately from the rest of the setup.
@app.route('/QTL/ansible')
def ansible_r():
    # Change user privilage and run ansible installation
    cmd = "sudo -u ubuntu ansible-playbook -b ../QTLaaS/spark_deployment.yml"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print()
    return "Done with Ansible"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
