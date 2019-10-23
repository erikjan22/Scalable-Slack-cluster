from flask import Flask, render_template

app = Flask(__name__)

@app.route('/QTL/test')
def test():
    return 'Hello world!'

@app.route('/QTL/count_workers')
def count_hosts():
    num = 0
    files = open('/etc/ansible/hosts', 'r')
    for i in files:
        if i.strip() != "[sparkworker]":
            num += 1
        else:
            continue
        files.close()
    return num



@app.route('/QTL/run', methods=['GET'])
def run_task():
    """
    Run the heat template
    """
    setup = render_template('setup.yml', title='Setup')
    
    return setup

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
