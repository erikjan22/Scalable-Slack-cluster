#!/bin/bash

echo -e "\n\nStep 1 out of 3: Get updates.\n"
sudo apt-get --assume-yes update
sudo apt-get --assume-yes upgrade

echo -e "\n\nStep 2 out of 3: Install the necessary programs.\n"
sudo apt-get install --assume-yes python
sudo apt-get install --assume-yes python3
sudo apt-get install --assume-yes python3-pip
# pip install --upgrade pip

pip3 install simplejson  # Installation for handling json files

sudo apt-get install -y libssl-dev libffi-dev python-dev build-essential
curl -L https://aka.ms/InstallAzureCli | bash

echo -e "\n\n Installing Flask. \n"
pip3 install flask
#pip install ruamel.yaml
#apt update && apt dist-upgrade

echo -e "\n\n Installing ansible. \n"
sudo apt-add-repository -y ppa:ansible/ansible
sudo apt-get install -y ansible

# Install the jq tool to analyze JSON in bash
sudo apt install jq

echo -e "\n\nStep 3 out of 3: Perform necessary azure operations.\n"
ssh-keygen -t rsa -N ''   # Generate a ssh key, there should not be one present
# Log-in to az, very important
az login

# Set defualt resource group:
az configure --defaults group=$RESOURCEGROUP
