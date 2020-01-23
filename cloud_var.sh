# Define username. This is the same user name with which you started the initial VM
export USERNAME='erik'
echo 'Your user name: ' $USERNAME

# Name the azure resource group within which you want to create new VMs. This resource group already has to exist.
export RESOURCEGROUP='SparkAutomation'
echo 'Your resource group is: ' $RESOURCEGROUP
# Set default resource group for the azure cli
az configure --defaults group=SparkAutomation

# Define the ip of the main machine, ansible-node. This is the machine from which the Spark cluster is started.
# It can be another Virtual Machine or your local machine.
export ANSIBLEIP='10.0.0.4'
echo 'The ip of your ansible node is: ' $ANSIBLEIP

# Define the names of the VMs which will function as spark master and spark slaves
# The names below should work fine. An integer counter will automatically be added to the slave nodes to distinguish them
export MASTERNAME='masternode'
export SLAVENAME='slavenode'

# Define standard image
export VMIMAGE='Canonical:UbuntuServer:16.04-LTS:16.04.201910310'
echo 'The ubuntu image: ' $VMIMAGE
echo
echo 'Configuration of default azure settings complete.'

