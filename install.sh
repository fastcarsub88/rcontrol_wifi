#!/bin/bash
if [[ $1 != 'install' && $1 != 'update' && $1 != 'uninstall' ]]; then
  echo 'Pass "install" of "update" or "uninstall"'
  exit 1
fi
if [[ $1 == 'uninstall' ]]; then
  rm -r /opt/rcontrol
  rm /etc/nginx/sites-enabled/nginx_conf
  systemctl disable rcontrol_web
  systemctl disable rcontrol_sched
  exit
fi
if [[ $1 == 'install' ]]; then
  apt-get install python3-pip nginx uwsgi python3-requests -y
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
fi

cp -r html/* /opt/rcontrol/html/
cp -r app/* /opt/rcontrol/app/
cp install/nginx_conf /opt/rcontrol/service/
cp install/rcontrol_sched.service /opt/rcontrol/service/
cp install/rcontrol_web.service /opt/rcontrol/service/

if [[ $1 == 'install' ]]; then
  ln -s /opt/rcontrol/service/nginx_conf /etc/nginx/sites-enabled/
  cp install/custom.css /opt/rcontrol/html/custom.css
  systemctl enable /opt/rcontrol/service/rcontrol_web.service
  systemctl enable /opt/rcontrol/service/rcontrol_sched.service
  # systemctl enable rcontrol_web
  # systemctl enable rcontrol_sched
fi
nginx -s reload
echo "Please reboot"
