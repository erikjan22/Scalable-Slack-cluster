#!/bin/bash

# This script creates a new slavenode, thereby expanding an existing cluster

# Start by checking if all the necessary variables are still set
if [[ -z ${USERNAME+x} ]]  ||  [[ -z ${ANSIBLEIP+x} ]]; then
    echo "User variables need to be set again!";
    source cloud_var.sh;
fi

# First we need to count the number of current slaves
nr_slaves=$(python3 PythonScripts/NumberSlaves.py)

echo "Creating a new vm with the name "$SLAVENAME$nr_slaves

az vm create -n $SLAVENAME$nr_slaves --image $VMIMAGE > TemporaryInfo.json

if python3 PythonScripts/UpscaleClusterInfo.py $SLAVENAME$nr_slaves; then
    echo "Finished creating a vm"
    rm TemporaryInfo.json && rm ClusterInfo.json && mv ClusterInfoUpdated.json ClusterInfo.json
else
    echo 'No overwrite of ClusterInfo.json, something went wrong. See ClusterInfoUpdated.json for output.'
fi

sudo python3 PythonScripts/UpdateHostFiles.py $ANSIBLEIP $USERNAME

echo "Finished registering the vm"
