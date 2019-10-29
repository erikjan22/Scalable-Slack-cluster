#!/bin/bash

echo "Starting"
source SNIC.sh &&
echo "Exported Keys"

# TODO!  swich python codes later
# python QTL_automation.py
sudo python QTL_test.py
echo "Wrote to ansible" &&
cd QTLaaS &&
#ansible-playbook -b spark_deployment.yml &&
cd ..


