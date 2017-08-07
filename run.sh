#!/bin/sh

# nohup uwsgi --ini /volume1/storage/mh/gsinfosite/gsinfosite_uwsgi.ini & nginx -c /opt/etc/nginx/nginx.conf 2>&1
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
cp /volume1/jycy/WebSite/gsinfosite/gsinfosite.conf /etc/nginx/nginx.conf
nginx -s reload & nohup /bin/uwsgi --ini /volume1/jycy/WebSite/gsinfosite/gsinfosite_uwsgi.ini 2>&1