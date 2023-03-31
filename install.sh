#!/bin/bash
if [[ $1 != 'install' && $1 != 'update' ]]; then
  echo 'Pass "install" of "update"'
  exit 1
fi
if [[ $1 == 'install' ]]; then
  apt-get install python3-pip nginx uwsgi python3-requests -y
  getent /etc/passwd rcontrol > /dev/null
  if [[ $? -ne 0 ]]; then
    useradd rcontrol
  fi
  mkdir /opt/rcontrol
  mkdir /opt/rcontrol/html
  mkdir /opt/rcontrol/app
  mkdir /opt/rcontol/service
  rm /etc/nginx/sites-enabled/default
  cp app/example_data_file.json /opt/rcontrol/app/data_file.json
fi

cp -r html/ /opt/rcontrol/html/
cp -r app/ /opt/rcontrol/app/
cp  install/nginx_conf /opt/rcontrol/service/
cp install/rcontrol_sched.service /opt/rcontrol/service/
cp install/rcontol_web.service /opt/rcontrol/service/

if [[ $1 == 'install' ]]; then
  ln -s /opt/rcontol/service/nginx_conf /etc/nginx/sites-enabled/
  cp install/custom.css /opt/rcontrol/html/custom.css
  systemctl link /opt/rcontrol/service/rcontrol_web.service
  systemctl link /opt/rcontrol/service/rcontrol_sched.service
  systemctl enable rcontrol_web
  systemctl enable rcontrol_sched
fi
nginx -s reload
echo "Please reboot"
