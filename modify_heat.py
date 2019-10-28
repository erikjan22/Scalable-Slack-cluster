import subprocess
from ruamel import yaml
from flask import Flask, request, render_template

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
    heat_template = 'Heat_v6_test.yml'
    if request.method == 'POST':
        workers = request.form['numWorkers']
        with open(heat_template) as f:
            list_doc = yaml.load(f)
            parameters = list_doc['parameters']
            node_count = parameters['node_count']
            list_doc['parameters']['node_count']['default'] = int(workers)

            with open(heat_template, 'w') as f:
                yaml.dump(list_doc, f, default_flow_style=False)

        cmd = "ls -l"
        #cmd = "openstack stack create team6_v2 -f 'yaml' -t 'Heat_v6_test.yml'"
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        return "Starting instance", output, error
    return render_template('setup.html')



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
