# ACC group 6
## QTL as a service (QTLaaS), a cloud service for genetic analysis

### Setup and run REST API 
In order to run the service one first need to create a instance and using super user privalage do the following: 
1. Clone the repository with `git clone https://github.com/MrHed/ACC-grp6.git` to the home directory of the instance.
2. Start the script `programs.sh` as sudo user, so first `sudo bash` to become sudo user, then run `bash programs.sh`. This will install the necessary programs and update them and also clone the repository `https://github.com/QTLaaS/QTLaaS.git` to the home directory on the instance.
3. From the home directory, run the command: `cd QTLaaS && source ansible_install.sh && cd ..`
4. From the home directory, run the command: `cd ACC-grp6 && source SNIC.sh && python3 run.py`
5. To run the Flask app go to the folder `ACC-grp6` and run `python3 run.py`, this will start the Flask server.


From another terminal it is now possible to run different commands. To start a stack do
* `curl -i http://0.0.0.0:5000/QTL/setup?workers=NUM`  

where `NUM` is the number of workers to start the instance with. This will run the Heat template and put in the number of workers in this file.   

Other possible commands are  
* `curl -i http://0.0.0.0:5000/QTL/modify`
* `curl -i http://0.0.0.0:5000/QTL/stack`
* `curl -i http://0.0.0.0:5000/QTL/delete`

The modify command lets the user specify how many users to add to the stack. The stack command show how many workers there currently are on the stack, and the delete stack command terminates the cluster. 
