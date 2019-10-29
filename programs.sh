#! /bin/sh

apt-get update
apt-get -y upgrade
apt-get install -y git

apt-get install -y python
apt-get install -y python3
apt-get install -y python-pip
pip install --upgrade pip
pip install flask

apt install software-properties-common
add-apt-repository cloud-archive:queens

apt install python-openstackclient

if [ ! -d "../QTLaaS" ]; then
    cd ../ && git clone https://github.com/QTLaaS/QTLaaS.git
    echo "Cloned QTLaaS"
else
    echo "QTLaaS already exists"
fi

echo "SUCCESS"
