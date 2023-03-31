#!/bin/bash

if [ ! $1 ]; then
    echo "please pass conf"
    exit
fi
if [ ! -f $1 ]; then
    echo 'file not found'
    exit
fi
sudo apt install openvpn -y
sudo cp $1 /etc/openvpn/client.conf
sudo systemctl enable openvpn@client.service
sudo systemctl start openvpn@client
