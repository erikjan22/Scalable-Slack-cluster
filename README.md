_Next time:_ 

_- there might be something wrong with the installation of pip3. Make sure the installation for simplejson is working_

_- Protect the ClusterInfo.json file from user interference_

_- Modify upscaling Flask function so that user can give an argument to make multiple slaves. Do the same for downscaling_

_- Integrating everything with ansilbe. How about the idea of creating an image from the master node_


# Introduction
The . It functions using Ubuntu 16.04 images  

You can have a look at the original cluster here....

# Setup

Working from a Swedish setup, I had some issues with the locale settings during installations. Although it shouldn't affect functionality, the errors are a bit annoying. To avoid these error prompts during installations, use the following commands: `export LC_ALL="en_US.UTF-8"`, `export LC_CTYPE="en_US.UTF-8"` and `sudo dpkg-reconfigure locales`

Install the necessary programs witht the _initialization_ script. First make the file exacutable with `chmod +x initialization.sh` and then run it with `./initialization.sh`

The next step sets the personal information of the user in the _cloud_var_ file. In this file you can enter your personal information and settings. If you want to find a different Ubuntu 16.04 image, use the following command: `az vm image list --all -p Canonical -f UbuntuServer -s 16.04 --query [].urn -o tsv`. Make the _cloud_var_ file runnable using the command `chmod +x cloud_var.sh` and then use source to create variables `source ./cloud_var.sh`




__An interesting article I used was this:__ https://adamtheautomator.com/remove-azure-virtual-machine-powershell/ 


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
