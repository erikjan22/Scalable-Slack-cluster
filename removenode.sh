#!/bin/bash

## This script is used to remove nodes from the cluster

# Start by checking if all the necessary variables are still set
if [[ -z ${USERNAME+x} ]]  ||  [[ -z ${ANSIBLEIP+x} ]]; then
    echo "User variables need to be set again!";
    source cloud_var.sh;
fi


## Update ClusterInfo, which returns the name of the VM to be removed
vm_to_be_deleted=$(python3 PythonScripts/DownscaleClusterInfo.py)

echo "The vm to be deleted:" $vm_to_be_deleted

if [ ! -z $vm_to_be_deleted ]; then
     echo "Virtual machine" $vm_to_be_deleted "has been removed from the cluster info."
     rm ClusterInfo.json && mv ClusterInfoUpdated.json ClusterInfo.json
else
     echo 'No overwrite of ClusterInfo.json, something went wrong. See ClusterInfoUpdated.json for output.'
     exit 1
fi

## Next update the ssh files according to the current info in ClusterInfo.json

sudo python3 PythonScripts/UpdateHostFiles.py $ANSIBLEIP $USERNAME

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
echo "Removing the vm together with its nic, public-ip, disk and nsg"
az vm delete --name $vm_to_be_deleted --yes
az network nic delete --name $nic_name
az network public-ip delete --name $publicip_name
az disk delete --name $disk_name --yes
az network nsg delete --name $nsg_name

echo "Finished with removal of node"
