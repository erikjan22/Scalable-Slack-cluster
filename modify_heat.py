import subprocess
from ruamel import yaml
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/form', methods=['POST', 'GET'])
def form_post():
    if request.method == 'POST':
        num_workers = request.form['numWorkers']
        return num_workers
    return render_template('form_qtl.html')


@app.route('/QTL/index')
def index():
    return render_template('index.html')


@app.route('/QTL/about')
def about():
    return render_template('about.html')


@app.route('/QTL/set_workers', methods=['GET', 'POST'])
def set_workers():
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
    return render_template('form_qtl.html')


@app.route('/QTL/run', methods=['GET', 'POST'])
def start_workers():
    """                                                                               
    Start the stack of workers
    # TODO: test with openstack on ansible host
    """
    #cmd = "openstack stack create team6_v2 -f 'yaml' -t 'Heat_v6_test.yml'"
    cmd = "ls -al" # placeholder
    if request.method == 'POST':
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        return output, error
    print('Cluster starting')
    return render_template('run_qtl.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
