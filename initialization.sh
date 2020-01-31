#!/bin/bash

echo -e "\n\nStep 1 out of 3: Get updates.\n"
sudo apt-get --assume-yes update
sudo apt-get --assume-yes upgrade

echo -e "\n\nStep 2 out of 3: Install the necessary programs.\n"
sudo apt-get install --assume-yes python
sudo apt-get install --assume-yes python3
sudo apt-get install --assume-yes python3-pip
pip3 install --upgrade pip

pip3 install simplejson  # Installation for handling json files

sudo apt-get install -y libssl-dev libffi-dev python-dev build-essential
curl -L https://aka.ms/InstallAzureCli | bash

echo -e "\n\n Installing Flask. \n"
pip3 install flask
#pip install ruamel.yaml

echo -e "\n\n Installing ansible. \n"
sudo apt-add-repository -y ppa:ansible/ansible
sudo apt-get install -y ansible

# Install the jq tool to analyze JSON in bash
sudo apt install -y jq

echo -e "\n\nStep 3 out of 3: Perform necessary operations for setting up Azure and Ansible.\n"
ssh-keygen -f $HOME/.ssh/id_rsa -t rsa -N ''   # Generate a ssh key, there should not be one present
# Log-in to az, very important
az login

# Set default resource group for the azure cli
az configure --defaults group=$RESOURCEGROUP

# Creating the setup_var.yml file, which stored the install locations which will be used by the ansible playbook
echo "rc_file: /home/$USERNAME/.bashrc
username: $USERNAME
spark_home: /usr/local/spark-2.3.4-bin-hadoop2.7
scala_home: /usr/local/scala-2.11.8
java_home: /usr/lib/jvm/java-1.8.0-openjdk-amd64
spark_urls:
 - http://apache.mirrors.spacedump.net/spark/spark-2.3.4/spark-2.3.4-bin-hadoop2.7.tgz
 - http://downloads.lightbend.com/scala/2.11.8/scala-2.11.8.tgz
r_repo: "deb http://ftp.acc.umu.se/mirror/CRAN/bin/linux/ubuntu xenial/"
jupyter_path: /usr/local/share/jupyter
jupyter_runtime_dir: /usr/local/share/jupyter-runtime
jupyter_config_dir: /usr/local/etc/jupyter" > setup_var.yml
