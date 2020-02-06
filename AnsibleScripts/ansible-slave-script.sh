#!/bin/bash

ansible-playbook -b spark_deployment.yml --start-at-task="start spark master process"
