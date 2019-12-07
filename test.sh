if python3 UpscaleClusterInfo.py 'sparkmaster' yes; then
     rm TemporaryInfo.json && rm ClusterInfo.json && mv ClusterInfoUpdated.json ClusterInfo.json
else
     echo 'No overwrite of ClusterInfo.json, something went wrong. See ClusterInfoUpdated.json for output.'
fi
