import subprocess
from ruamel import yaml
from flask import Flask, request

app = Flask(__name__)


@app.route('/QTL/set_workers', methods=['GET'])
def set_workers():
    """                                                                               
    Set up how many workers to use   
    TODO: Fix so user can add more  
    """
    heat_template = 'Heat_v6_test.yml'
    workers = 2
    #workers = request.form['Workers: ']
    with open(heat_template) as f:
        list_doc = yaml.load(f)
        parameters = list_doc['parameters']
        node_count = parameters['node_count']
        list_doc['parameters']['node_count']['default'] = workers
        
        with open(heat_template, 'w') as f:
            yaml.dump(list_doc, f, default_flow_style=False)
            
            return 0


@app.route('/QTL/run', methods=['GET'])
def start_workers():
    """                                                                               
    Start the stack of workers
    """
    cmd = "openstack stack create team6_v2 -f 'yaml' -t 'Heat_v6_test.yml'"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output, error


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
