#!/bin/bash
IP=$(curl http://169.254.169.254/latest/meta-data/public-ipv4)
echo "public IP : $IP"
sed -i.bak "s/127.0.0.1/$IP/" /usr/share/nginx/html/my-script.js 