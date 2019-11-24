# Set default resource group
# az configure --defaults group=SparkAutomation

# Define username. This is the same user name with which you started the initial VM
export USERNAME='erik'
echo 'Your user name: ' $USERNAME

# Define standard image
export VMIMAGE='Canonical:UbuntuServer:16.04-LTS:16.04.201910310'
echo 'The ubuntu image: ' $VMIMAGE
echo
echo 'Configuration of default azure settings complete.'

