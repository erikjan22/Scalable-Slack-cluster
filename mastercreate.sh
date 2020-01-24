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

if python3 UpscaleClusterInfo.py $MASTERNAME yes; then
    rm TemporaryInfo.json && rm ClusterInfo.json && mv ClusterInfoUpdated.json ClusterInfo.json
else
    echo 'No overwrite of ClusterInfo.json, something went wrong. See ClusterInfoUpdated.json for output.'
    exit;

fi

sudo python3 UpdateHostFiles.py $ANSIBLEIP $USERNAME

echo "Finished registering the vm"
