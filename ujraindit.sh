#!/bin/bash
sudo systemctl stop gunicorn.socket
sudo systemctl stop gunicorn.service
sudo systemctl stop nginx
git pull origin main
source venv/bin/activate
python3 restapi/manage.py migrate --noinput
python3 restapi/manage.py collectstatic --noinput --clear
sudo nginx -t && sudo systemctl start nginx
sudo systemctl status nginx --no-pager
sudo systemctl start gunicorn.socket
sudo systemctl start gunicorn.service
sudo systemctl status gunicorn --no-pager
deactivate