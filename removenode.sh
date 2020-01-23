#!/bin/bash

## This script is used to remove nodes from the cluster

## Update ClusterInfo, which returns the name of the VM to be removed
vm_to_be_deleted=$(python3 DownscaleClusterInfo.py)

echo "The vm the be deleted:"
echo $vm_to_be_deleted

if [ ! -z $vm_to_be_deleted ]; then
     echo "Virtual machine" $vm_to_be_deleted "has been removed from the cluster info."
     rm ClusterInfo.json && mv ClusterInfoUpdated.json ClusterInfo.json
else
     echo 'No overwrite of ClusterInfo.json, something went wrong. See ClusterInfoUpdated.json for output.'
     exit 1
fi

## Next update the ssh files according to the current info in ClusterInfo.json

# Check to see if the necessary variables are still set
if [[ -z ${USERNAME+x} ]]  ||  [[ -z ${ANSIBLEIP+x} ]]; then
    echo "User variables need to be set again!";
    source cloud_var.sh;
fi

sudo python3 UpdateHostFiles.py $ANSIBLEIP $USERNAME

## Finally, remove the virtual machine with all its attachments using the az cli

# Retrieve the name of the network interface
nic_name=$(az network nic list | jq '.[] | .name' | grep $vm_to_be_deleted | cut -d '"' -f 2)

# Retrieve the name of the disk
disk_name=$(az disk list | jq '.[] | .name' | grep $vm_to_be_deleted | cut -d '"' -f 2)

# Retrieve the name of the public IP
publicip_name=$(az network public-ip list | jq '.[] | .name' | grep $vm_to_be_deleted | cut -d '"' -f 2)

# Retrieve the name of the network security group
nsg_name=$(az network nsg list | jq '.[] | .name' | grep $vm_to_be_deleted | cut -d '"' -f 2)

# Perform the actual deletions
# in case of question: are you sure? Do this: echo y | command
echo "Going to remove vm"
echo y | az vm delete --name $vm_to_be_deleted
echo "Removing nic"
az network nic delete --name $nic_name
echo "removing public ip"
az network public-ip delete --name $publicip_name
echo "removing disk"
echo y | az disk delete --name $disk_name
echo "removing nsg"
az network nsg delete --name $nsg_name

echo "Finished with removal of slave node"
