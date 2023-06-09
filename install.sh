#!/bin/bash
if [[ $1 != 'install' && $1 != 'update' && $1 != 'uninstall' ]]; then
  echo 'Pass "install" or "update" or "uninstall"'
  exit 1
fi
if [[ $1 == 'update' ]]; then
  git pull
fi
if [[ $1 == 'uninstall' ]]; then
  rm -r /opt/rcontrol
  rm /etc/nginx/sites-enabled/nginx_conf
  systemctl disable rcontrol_web
  systemctl disable rcontrol_sched
  echo "Remove all packages? Type 'yes' to remove all apt packages - python3-pip nginx uwsgi uwsgi-plugin-python3 python3-requests libffi-dev wireguard"
  read remove_apt
  if [[ $remove_apt == 'yes' ]]; then
    apt remove python3-pip nginx uwsgi uwsgi-plugin-python3 python3-requests libffi-dev wireguard -y
  fi
  exit
fi
if [[ $1 == 'install' ]]; then
  apt-get install python3-pip nginx uwsgi uwsgi-plugin-python3 python3-requests wireguard libffi-dev -y
  pip3 install ipcqueue
  getent passwd rcontrol > /dev/null
  if [[ $? -ne 0 ]]; then
    useradd rcontrol
  fi
  mkdir /opt/rcontrol
  mkdir /opt/rcontrol/html
  mkdir /opt/rcontrol/app
  mkdir /opt/rcontrol/service
  rm /etc/nginx/sites-enabled/default
  cp install/params.json /opt/rcontrol/app/params.json

  echo 'Enter wireguard IP / skip'
  read ip

  if [[ $ip != 'skip'  ]]; then
    wg genkey > /etc/wireguard/privkey
    privatekey=$(cat /etc/wireguard/privkey)
    wg pubkey < /etc/wireguard/privkey > /etc/wireguard/publickey
    echo "[Interface]
    Address = $ip
    PrivateKey = $privatekey

    [Peer]
    PublicKey = f2Y7fbMEceSH2O5hqDFuX2XvpMbOa9wFk6gnYt4wg0E=
    AllowedIPs = 10.8.1.0/24, 192.168.2.0/24
    Endpoint = vpn.hawcreektech.com:51820

    PersistentKeepalive = 60" > /etc/wireguard/wg0.conf

    systemctl enable wg-quick@wg0
    echo "wg set wg0 peer $(cat /etc/wireguard/publickey) allowed-ips $ip"
  fi

fi

cp -r html/* /opt/rcontrol/html/
cp -r app/* /opt/rcontrol/app/
cp install/nginx_conf /opt/rcontrol/service/
cp install/rcontrol_sched.service /opt/rcontrol/service/
cp install/rcontrol_web.service /opt/rcontrol/service/

if [[ $1 == 'install' ]]; then
  ln -s /opt/rcontrol/service/nginx_conf /etc/nginx/sites-enabled/
  systemctl enable /opt/rcontrol/service/rcontrol_web.service
  systemctl enable /opt/rcontrol/service/rcontrol_sched.service
fi
chown -R rcontrol:rcontrol /opt/rcontrol
nginx -s reload
systemctl daemon-reload
systemctl restart rcontrol_web
systemctl restart rcontrol_sched
echo "Done"
