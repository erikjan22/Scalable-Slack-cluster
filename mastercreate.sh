az vm create -n $MASTERNAME --image $VMIMAGE > TemporaryInfo.json

if python3 UpscaleClusterInfo.py $MASTERNAME yes; then
    echo "Finished creating a vm"
    rm TemporaryInfo.json && rm ClusterInfo.json && mv ClusterInfoUpdated.json ClusterInfo.json
else
    echo 'No overwrite of ClusterInfo.json, something went wrong. See ClusterInfoUpdated.json for output.'
fi

sudo python3 UpdateHostFiles.py $ANSIBLEIP $USERNAME

echo "Finished registering the vm"
