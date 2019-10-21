from flask import Flask

app = Flask(__name__)


@app.route('/QTL/hosts')
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
    Run the task
    """
    return "Hello World \n"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
