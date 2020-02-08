#!/bin/bash

ansible-playbook -b spark_deployment.yml

# Instead of running the entire playbook, you can also start running the playbook at a certain task
#ansible-playbook -b spark_deployment.yml --start-at-task="wait for one seconds"
