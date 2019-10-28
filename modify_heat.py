import subprocess
from ruamel import yaml
from flask import Flask, request, render_template


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
    TODO: Start the cluster from here
    """
    heat_template = 'Heat_test.yml'
    #if request.method == 'POST':
        #workers = request.form['numWorkers']
    workers = 2
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
        
        return "Starting instance", output, error
    #return render_template('setup.html')
    return 'Starting' #output, error


@app.route('/QTL/modify', methods=['GET', 'POST'])
def modify_workers():
    """
    Modify workers, adding or removing from the stack
    """
    return render_template('modify.html')


@app.route('/QTL/terminate', methods=['GET', 'POST'])
def terminate_instance():
    """
    Remove the stack
    """
    return render_template('terminate.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
