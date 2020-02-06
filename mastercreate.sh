#!/bin/bash

## This script is used to create a master node, thereby starting a new cluster

# Start by checking if all the necessary variables are still set
if [[ -z ${USERNAME+x} ]]  ||  [[ -z ${ANSIBLEIP+x} ]]; then
    echo "User variables need to be set again!";
    source cloud_var.sh;
fi


az vm create -n $MASTERNAME --image $VMIMAGE > TemporaryInfo.json

echo "Finished creating a vm"

echo '[{"NumberSlaves": 0, "ExistMaster": false}]' > ClusterInfo.json

if python3 PythonScripts/UpscaleClusterInfo.py $MASTERNAME yes; then
    rm TemporaryInfo.json && rm ClusterInfo.json && mv ClusterInfoUpdated.json ClusterInfo.json
else
    echo 'No overwrite of ClusterInfo.json, something went wrong. See ClusterInfoUpdated.json for output.'
    exit;

fi

sudo python3 PythonScripts/UpdateHostFiles.py $ANSIBLEIP $USERNAME

# Retrieve the name of the network security group
nsg_name=$(az network nsg list | jq '.[] | .name' | grep $MASTERNAME | cut -d '"' -f 2)
# Add security rules to make Spark webbrowser possible
az network nsg rule create --nsg-name $nsg_name -n "AllowSparkWebBrowserInbound" --priority 1010 --destination-port-ranges 8080 --direction Inbound
az network nsg rule create --nsg-name $nsg_name -n "AllowSparkWebBrowserOutbound" --priority 1010 --destination-port-ranges 8080 --direction Outbound

echo "Finished registering the vm"


