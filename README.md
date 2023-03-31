
sudo apt-get install build-essential python-pip python-dev python-smbus git nginx
cd /home/pi
git clone https://github.com/SequentMicrosystems/megaioind-rpi.git
cd megaioind-rpi/python/megaioind/
sudo python setup.py install
sudo pip install uwsgi
sudo pip install requests
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /home/pi/rcontrol/install/nginx_conf /etc/nginx/sites-enabled/
sudo systemctl link /home/pi/rcontrol/install/rcontrol_web.service
sudo systemctl link /home/pi/rcontrol/install/rcontrol_sched.service
