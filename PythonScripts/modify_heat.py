import subprocess
from ruamel import yaml
from flask import Flask, request, render_template, g, jsonify, Response
import json
import shelve # For temporary storage

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

workers_list = []
master = {}

worker_name = "team6_sparkworker"
master_name = "team6_sparkmaster"
ansible = {"name": "ansible-node", "ip": "192.168.1.9"}
ansible_host = " ansible_ssh_host="
prefix = "team6_"

PATH = os.path.abspath("/etc/")

app = Flask(__name__)


@app.route('/form', methods=['POST', 'GET'])
def form_post():
    if request.method == 'POST':
        num_workers = request.form['numWorkers']
        return num_workers
    return render_template('setup.html')


@app.route('/QTL/index')
def index():
    return render_template('index.html')


@app.route('/QTL/about')
def about():
    return render_template('about.html')


@app.route('/QTL/setup', methods=['GET', 'POST'])
def start_instance():
    """                                                    
    Set up how many workers to use
    """

    global workers_list
    global ansible
    global master 

    # Modifies the Heat templates with number of workers and start the stack
    heat_template = 'Heat.yml'
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

        
        cmd = ["openstack", "stack", "create",
               "team6_api", "-f", "yaml", "-t", "Heat_test.yml"]
        
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output, error = process.communicate()

        
    # Find instances for NOVA
    time.sleep(60)
    relevant_instances = nova.servers.list(search_opts={"name": prefix})

    # Fix this instead of time.sleep(60)
    #not_ready = True
    #num_ready = 0
    #while (num_ready != int(workers)):
    #    for instance in relevant_instances:
    #        print(num_ready)
    #        if (instance.status == "ACTIVE"):
    #            num_ready += 1
    #        else:
    #            num_ready = 0
    #            # if the instance not active, wait 5 seconds
    #            time.sleep(5)
    

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
                #print("Worker ", name)
                #print("Has IP ", ip)
                id_nr = int(name.strip(worker_name))
                if id_nr > 0:
                    workers_list.append({"name": name.strip(prefix), "ip": ip})        
            else:
                master = {"name": name.strip(prefix), "ip": ip}
                #print("Master ", name)
                #print("HAS IP ", ip)

        except:
            pass

    print(workers_list)
    print(master)
    print("")
    print("Got Instances")
    print("")

    
    # Write to host files
    time.sleep(30)
    write_to_ansible_host(ansible, master, workers_list)
    print("Wrote to Ansible\n")

    # 
    time.sleep(30)
    run_ansible()
    print("=================")
    print("Launched Ansible")
    
    return "Started\n"
        

@app.route('/QTL/modify', methods=['GET', 'POST'])
def modify_workers():
    """
    Modify workers, adding or removing from the stack
    """

    global workers_list
    global ansible
    global master 

    # Modifies the Heat templates with number
    heat_template = 'Heat.yml'
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

        
        cmd = ["openstack", "stack", "create",
               "team6_api", "-f", "yaml", "-t", "Heat_test.yml"]
        
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output, error = process.communicate()

        
    # Find instances for NOVA
    time.sleep(60)
    relevant_instances = nova.servers.list(search_opts={"name": prefix})

    # Fix this instead of time.sleep(60)
    #not_ready = True
    #num_ready = 0
    #while (num_ready != int(workers)):
    #    for instance in relevant_instances:
    #        print(num_ready)
    #        if (instance.status == "ACTIVE"):
    #            num_ready += 1
    #        else:
    #            num_ready = 0
    #            # if the instance not active, wait 5 seconds
    #            time.sleep(5)
    

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
                #print("Worker ", name)
                #print("Has IP ", ip)
                id_nr = int(name.strip(worker_name))
                if id_nr > 0:
                    workers_list.append({"name": name.strip(prefix), "ip": ip})        
            else:
                master = {"name": name.strip(prefix), "ip": ip}
                #print("Master ", name)
                #print("HAS IP ", ip)

        except:
            pass

    print(workers_list)
    print(master)
    print("")
    print("Got Instances")
    print("")

    
    # Write to host files
    time.sleep(30)
    write_to_ansible_host(ansible, master, workers_list)
    print("Wrote to Ansible\n")

    # 
    time.sleep(30)
    run_ansible()
    print("=================")
    print("Launched Ansible")
    
    return "Started\n"

    
    #return render_template('modify.html')


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
    

@app.route('/QTL/stack')
def show_stack():
    """
    Shows workers in stack
    """
    #return Response(json.dumps(workers_list), mimetype='application/json')
    return jsonify(workers_list)


@app.route('/QTL/terminate', methods=['GET', 'POST'])
def terminate_instance():
    """
    Remove the stack
    """
    return render_template('terminate.html')



#m = {"name": "hej", "ip": "1292"}
#a = m
#w = [m]

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



def run_ansible():

    PATH = os.path.abspath('/home/ubuntu/QTLaaS/')
    #PATH_home = os.path.abspath('/home/ubuntu/ACC-grp6/')
    cmd = "ansible-playbook -b ../QTLaaS/spark_deployment.yml"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output, error
    
#run_ansible()
#print("\n\n=========================================\n")
#print("Done with Ansible!")




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



