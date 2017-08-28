#!/bin/sh

if [ "$1" == "stop" ]; then
	/opt/bin/lsof -i:9090 | awk '{if (1 != NR){ print "kill -9 " $2 }}' | sh
	nginx -s stop >/dev/null 2>&1
elif [ "$1" == "start" ]; then
	/opt/bin/lsof -i:9090 | awk '{if (1 != NR){ print "kill -9 " $2 }}' | sh
	nginx -s stop >/dev/null 2>&1
	nohup uwsgi --ini /volume1/storage/mh/gsinfosite/gsinfosite_uwsgi.ini & nginx 2>&1
else
	echo 'site.sh [start|stop]'
fi