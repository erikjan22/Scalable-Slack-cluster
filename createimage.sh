#!/bin/bash

## This script is used to create an image used for faster upscaling of spark cluster

# Set the name of the custom image and the vm from which it is created.
export ImageName="CustomSparkImage"
export VMImageName="ImageMachine"

# Start by checking if all the necessary variables are still set
if [[ -z ${RESOURCEGROUP+x} ]]  ||  [[ -z ${VMIMAGE+x} ]]; then
    echo "User variables need to be set again!";
    source cloud_var.sh;
fi

# Check if a virtual machine for an image already exists
currentVM=$(az vm list | jq '.[] | .name' | grep $VMImageName | cut -d '"' -f 2)

if [ $currentVM != "" ]
then
echo "Due to the fact that a machine called" $currentVM "exists, this script does not work"
echo "Remove this virtual machine with all its attributes and try again."
exit 1
else
# Create a new virtual machine
echo "Creating a new virtual machine:" $VMImageName
az vm create -n $VMImageName --image $VMIMAGE > ImageInfo1.json
fi

# Wait in order for the machine depolyment to finish
sleep 30s

# Process information about new machine
VMpublicip=$(cat ImageInfo1.json | jq '.publicIpAddress' | cut -d '"' -f 2)
VMprivateip=$(cat ImageInfo1.json | jq '.privateIpAddress' | cut -d '"' -f 2)
echo "IP addresses of the VM: public" $VMpublicip "and private" $VMprivateip


# Use ansible to install the necesary programs on the machine
ansible-playbook -b -i $VMpublicip"," spark_deployment.yml


echo "Decommissioning" $VMImageName "and creating image" $ImageName
# Deprovision the VM
ssh $USERNAME@$VMpublicip "sudo waagent -deprovision+user -force"

# Deallocate and mark the VM as generalized
az vm deallocate --resource-group $RESOURCEGROUP --name $VMImageName
az vm generalize --resource-group $RESOURCEGROUP --name $VMImageName

# Create an image from the machine using azure cli
az image create --resource-group $RESOURCEGROUP --name $ImageName --source $VMImageName > ImageInfo2.json

# Remove the virtual machine, since it's no longer usable
echo $"The temporary vm" $VMImageName "will be removed, together with its nic, public-ip, disk and nsg"

# Retrieve the name of the network interface
nic_name=$(az network nic list | jq '.[] | .name' | grep $VMImageName | cut -d '"' -f 2)

# Retrieve the name of the disk
disk_name=$(az disk list | jq '.[] | .name' | grep $VMImageName | cut -d '"' -f 2)

# Retrieve the name of the public IP
publicip_name=$(az network public-ip list | jq '.[] | .name' | grep $VMImageName | cut -d '"' -f 2)

# Retrieve the name of the network security group
nsg_name=$(az network nsg list | jq '.[] | .name' | grep $VMImageName | cut -d '"' -f 2)

# Perform the actual deletions
echo "Removing the vm:" $VMImageName
az vm delete --name $VMImageName --yes
echo "Removing the network nic:" $nic_name
az network nic delete --name $nic_name
echo "Removing the public ip:" $publicip_name
az network public-ip delete --name $publicip_name
echo "Removing the disk:" $disk_name
az disk delete --name $disk_name --yes
echo "Removing the nsg:" $nsg_name
az network nsg delete --name $nsg_name

# Also remove the stored information about the machine and the image
rm ImageInfo1.json
rm ImageInfo2.json

# Remove fingerprint
ssh-keygen -f "/home/"$USERNAME"/.ssh/known_hosts" -R $VMprivateip

# Output information about the image to the user
echo "The created image has the name: "$ImageName
echo "Enter this name into the cloud_var.sh file, in place behind the VMIMAGE variable"
