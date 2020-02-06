_remaining issues:_ 

_- Issues with Spark cluster: new workers don't always want to connect to the master_ I have the idea that this only happens after you try to add to start an ansible playbook on an individual slave node. 

_- Check to see if in the hosts file you can also use another name than ansible-node to point to the main machine_

_- Protect the ClusterInfo.json file from user interference_

_- Modify upscaling Flask function so that user can give an argument to make multiple slaves. Do the same for downscaling_

_- Integrate everything with ansible: --> when using ansible-playbook, ssh will ask to add fingerprint. Anser this by default with yes --> when logging in to a new machien with the saem local ip, ssh will complain, since the ip is known, but the fingerprints do not match. Use_ `ssh-keygen -f "/home/erik/.ssh/known_hosts" -R 10.0.0.5` _to remove previous fingerprint. Try to do this automatically: when deleting a machine, also remove the fingerprint._


# Introduction
The . It functions using Ubuntu 16.04 images  

You can have a look at the original cluster here....

Make a file _<my_file.sh>_  runnable using the command `chmod +x <my_file.sh>`

# Setup

Working from a Swedish setup, I had some issues with the locale settings during installations. Although it shouldn't affect functionality, the errors are a bit annoying. To avoid these error prompts during installations, use the following commands: `export LC_ALL="en_US.UTF-8"`, `export LC_CTYPE="en_US.UTF-8"` and `sudo dpkg-reconfigure locales`

The next step sets the personal information of the user in the _cloud_var_ file. In this file you can enter your personal information and settings. By default, we're using the image: Canonical:UbuntuServer:16.04-LTS:16.04.201910310. If you want to find a different Ubuntu 16.04 image, use the following command: `az vm image list --all -p Canonical -f UbuntuServer -s 16.04 --query [].urn -o tsv` and enter your choose within the cloud_var.sh file. Use source to create variables `source ./cloud_var.sh`

Install the necessary programs with the _initialization.sh_ script using the command `./initialization.sh`

# Optional - create custom image
Create a customized image with the command `create_custom_image.sh`. This will take several minutes and will create an image from which new VMs can be started. This will greatly decrease the time needed for initializing new VMs when adding them to the spark cluster. The script will output the name of the custom image. This name should be inserted in the cloud_var.sh file, in the place of VMIMAGE. Afterwards, set the environmental variables again with the command `source ./cloud_var.sh`.

After you're finished with everything this custom image can be removed from the Azure portal or with the command: `az image delete --name <YourImageName> --resource-group <YourResourceGroupName>`.


Beware: "We recommend that you limit the number of concurrent deployments to 20 VMs from a single image."
See for more information on the webpage: https://docs.microsoft.com/en-us/azure/virtual-machines/linux/tutorial-custom-images
Another option might also be to remove the last part of the create_custom_image.sh script, so that the ImageVM is not automatically removed after creating an image. This way you can create a new image when this is needed.


# Flask options

`curl http://127.0.0.1:5000/SparkCluster/setup` : Set up a new cluster (one node which functions as Spark master and also includes one Spark slave)

`curl http://127.0.0.1:5000/SparkCluster/upscaling` : Add one node to an existing Spark cluster

`curl http://127.0.0.1:5000/SparkCluster/downscaling` : Remove one node from the Spark cluster

`curl http://127.0.0.1:5000/SparkCluster/destroycluster` : Destroy the entire cluster

`curl http://127.0.0.1:5000/SparkCluster/clusterinfo` : Retrieve information about the cluster


# Sources
__An interesting article I used was this:__ https://adamtheautomator.com/remove-azure-virtual-machine-powershell/ 
Also: https://docs.microsoft.com/en-us/azure/virtual-machines/windows/capture-image-resource
Link to the two other git repos.




# ACC group 6
## QTL as a service (QTLaaS), a cloud service for genetic analysis

### Setup and run REST API 
In order to run the service one first need to create a instance and using super user privalage do the following: 
1. Clone the repository with `git clone https://github.com/MrHed/ACC-grp6.git` to the home directory of the instance.
2. Start the script `programs.sh` as sudo user, so first `sudo bash` to become sudo user, then run `bash programs.sh`. This will install the necessary programs and update them and also clone the repository `https://github.com/QTLaaS/QTLaaS.git` to the home directory on the instance.
3. From the home directory, run the command: `cd QTLaaS && source ansible_install.sh && cd ..`
4. From the home directory, run the command: `cd ACC-grp6 && source SNIC.sh && python3 run.py`, this will start the Flask server.


The Flask server needs to be opened in one terminal and run. Whenever we build new instanes it will ask to add new fingerprints, enter `yes` in the terminal to continue.


From another terminal it is now possible to run different commands. To start a stack do
* `curl -i http://0.0.0.0:5000/QTL/setup?workers=NUM`  

where `NUM` is the number of workers to start the instance with. This will run the Heat template and put in the number of workers in this file.   

Other possible commands are  
* `curl -i http://0.0.0.0:5000/QTL/upscaling?workers=NUM`
* `curl -i http://0.0.0.0:5000/QTL/downscaling?workers=NUM`
* `curl -i http://0.0.0.0:5000/QTL/stack`
* `curl -i http://0.0.0.0:5000/QTL/delete`

The upscaling command lets the user specify how many users to add to the stack, and the downscaling removes workers from the stack. The stack command show how many workers there currently are on the stack, and the delete stack command terminates the cluster. 
