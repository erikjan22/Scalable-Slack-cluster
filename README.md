# Introduction
This git repo provides an automated way of setting up, upscaling, downscaling and completely removing a Spark cluster using the Azure cloud provider. This project was inspired by a group project I created with fellow students at Uppsala University (see sources below) using the SNIC Science Cloud. However, due to the unrealibility of the code in performing as desired, I decided to start a new projects from scratch.

I cannot guarentee the code will function using virutal machines started from something else than __Ubuntu 16.04__ images  

# Setup

Working from a Swedish location, I had some issues with the locale settings during installations. Although it shouldn't affect functionality, the errors are a bit annoying. To avoid these error prompts during installations, use the following commands: `export LC_ALL="en_US.UTF-8"`, `export LC_CTYPE="en_US.UTF-8"` and `sudo dpkg-reconfigure locales`

The first step is to set the user information in the _cloud_var_ file, where you can enter your personal information and settings. By default, I'm using the image: __Canonical:UbuntuServer:16.04-LTS:16.04.201910310__. If you want to find a different Ubuntu 16.04 image, use the following command: `az vm image list --all -p Canonical -f UbuntuServer -s 16.04 --query [].urn -o tsv` and enter your choice within the cloud_var.sh file. Use source to create variables `source ./cloud_var.sh`

Install the necessary programs with the _initialization.sh_ script using the command `./initialization.sh`


# Optional - create custom image
Create a customized image with the command `create_custom_image.sh`. This will take several minutes and will create an image from which new virtual machines can be started. This will greatly decrease the time needed for initializing new VMs when adding them to the Spark cluster. The script will output the name of the custom image when it is finished. This name should be inserted in the _cloud_var.sh_ file, in the place where the VMIMAGE variable is defined. Be sure to set the environmental variables again with the command `source ./cloud_var.sh` when the new image has been added.

After you're finished with everything this custom image can be removed from the Azure portal or with the command: `az image delete --name <YourImageName> --resource-group <YourResourceGroupName>`.

Beware, as is stated by the Azure [article](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/tutorial-custom-images) dealing with creating custom image, "We recommend that you limit the number of concurrent deployments to 20 VMs from a single image." One solution to this issue might be to remove the last part of the create_custom_image.sh script, so that the virtual machine which is used to create the custom image is not automatically removed. This way you can create more images from the same source when this is needed.


# Flask options

When the setup is completed, there are several actions which can be performed through a Flask application. This application should be started in one terminal window with the command _python3 flask_app.py_. The options below can than be executed by running the respective command from another terminal window. Be aware that most of the relevant information to the user, as well as some prompts, is presented in the first (Flask) window.

`curl http://127.0.0.1:5000/SparkCluster/setup` : Set up a new cluster (one node which functions as Spark master and also includes one Spark slave)

`curl http://127.0.0.1:5000/SparkCluster/upscaling?number=1` : Add one (or more) node(s) to an existing Spark cluster

`curl http://127.0.0.1:5000/SparkCluster/downscaling?number=1` : Remove one (or more) node(s) from the Spark cluster

`curl http://127.0.0.1:5000/SparkCluster/destroycluster` : Destroy the entire cluster

`curl http://127.0.0.1:5000/SparkCluster/clusterinfo` : Retrieve information about the cluster

The script automatically adds the necessary security rules, which means it's possible to view the Spark cluster using the Web UI by filling the following address in your browser: _http://<publip ip of master node>:8080/_.


# Improvements

Below you can find a list of improvements which can still be made:

- Although the ansible playbook also orders a Spark worker to start on the same node as the master is located, this doesn't always seem to happen.

- Currently the cluster expansion works by building new machines and then starting the complete ansible-playbook. This causes a number of redundant actions to happen, since the playbook has already been ran on the existing nodes in the cluster. This 'sledgehammer' approach to cluster expasnion is also rather unsubtle. However, starting the ansible playbook from a certain task, or only running the playbook on the new nodes, starts new worker processes, but doesn't seem to connect them properly to the master node.

- When connecting to a new machine through ssh (which is how ansible functions), causes a prompt which asks if the user trusts this machine and if it's fingerprint should be added to 

- Currently multiple virtual machines are created and destroyed with the Azure CLI sequentially (through a for loop). It is worth checking out whether these actions can be executed in one go, as would happen when performing these actions through the Azure portal. 

- Since the _ClusterInfo.json_ file is essential to the functioning of the program, it's a nice idea to see if it can in some way be protected from user interference.

- In the original git repo (see link below) there is html and css code available which creates a web UI, as an alternative for using the flask command directly in the terminal. Perhaps this can be adapted, into something similar for this application.


# Sources

As mentioned above, the inspiration from this topic can be found in two other git repo's: [QTL-as-a-service](https://github.com/QTLaaS/QTLaaS) and the [ACC group 6] (https://github.com/MrHed/ACC-grp6) project. No code from these sources is included in my, apart from the ansible playbook _spark_deployment.yml_, created by __sztoor__ and heavily edited by me.

I would also like to point to an interesting article which helped me a lot: https://adamtheautomator.com/remove-azure-virtual-machine-powershell/
