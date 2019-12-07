az vm create -n $SLAVENAME --image $VMIMAGE > TemporaryInfo.json

if python3 UpscaleClusterInfo.py $SLAVENAME; then
    echo "Finished creating a vm"
    rm TemporaryInfo.json && rm ClusterInfo.json && mv ClusterInfoUpdated.json ClusterInfo.json
else
    echo 'No overwrite of ClusterInfo.json, something went wrong. See ClusterInfoUpdated.json for output.'
fi

sudo python3 UpdateHostFiles.py $ANSIBLEIP $USERNAME

echo "Finished registering the vm"
