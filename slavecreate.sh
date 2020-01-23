# This script creates a new slavenode, thereby expanding an existing cluster

# First we need to count the number of current slaves

nr_slaves=$(python3 NumberWorkers.py)
nr_slaves=$(($nr_slaves +1))

echo "ID of new slave:" $nr_slaves

echo $SLAVENAME$nr_slaves

az vm create -n $SLAVENAME$nr_slaves --image $VMIMAGE > TemporaryInfo.json

if python3 UpscaleClusterInfo.py $SLAVENAME; then
    echo "Finished creating a vm"
    rm TemporaryInfo.json && rm ClusterInfo.json && mv ClusterInfoUpdated.json ClusterInfo.json
else
    echo 'No overwrite of ClusterInfo.json, something went wrong. See ClusterInfoUpdated.json for output.'
fi

sudo python3 UpdateHostFiles.py $ANSIBLEIP $USERNAME

echo "Finished registering the vm"
