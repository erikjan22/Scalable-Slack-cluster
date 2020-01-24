#!/bin/bash

## This script is used to remove all the nodes from the cluster

echo "\n Preparing to remove all the nodes from the SparkCluster\n"

# Start by checking if all the necessary variables are still set
if [[ -z ${USERNAME+x} ]]  ||  [[ -z ${ANSIBLEIP+x} ]]; then
    echo "User variables need to be set again!";
    source cloud_var.sh;
fi


## Retrieve the names of the leftover machines
vms_to_be_deleted=($(python3 print_all_machines.py | tr -d '[],'))

rm ClusterInfo.json
#echo "\nRemoved the ClusterInfo.json file\n"

## Setting the host files back to the default setting
sudo python3 reset_host_lists.py $ANSIBLEIP $USERNAME

## Finally, remove the virtual machines with all their attachments using the az cli
for machine in "${vms_to_be_deleted[@]}"
do
    machine=$(echo "$machine" | tr -d "'")

    echo $machine "will be removed, together with its nic, public-ip, disk and nsg"

    # Retrieve the name of the network interface
    nic_name=$(az network nic list | jq '.[] | .name' | grep $machine | cut -d '"' -f 2)

    # Retrieve the name of the disk
    disk_name=$(az disk list | jq '.[] | .name' | grep $machine | cut -d '"' -f 2)

    # Retrieve the name of the public IP
    publicip_name=$(az network public-ip list | jq '.[] | .name' | grep $machine | cut -d '"' -f 2)

    # Retrieve the name of the network security group
    nsg_name=$(az network nsg list | jq '.[] | .name' | grep $machine | cut -d '"' -f 2)

    # Perform the actual deletions
    echo "Removing the vm together with its nic, public-ip, disk and nsg"
    az vm delete --name $machine --yes
    az network nic delete --name $nic_name
    az network public-ip delete --name $publicip_name
    az disk delete --name $disk_name --yes
    az network nsg delete --name $nsg_name

    echo "Finished with removal of node" $machine

done

echo "Finished removing the complete Spark cluster"

