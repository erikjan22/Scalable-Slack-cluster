## This script is used to create a master node, thereby starting a new cluster

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
