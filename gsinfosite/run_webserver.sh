#!/bin/sh

source /home/strongman/websites/gsinfosite/webserver/bin/activate

cd /home/strongman/websites/gsinfosite/webserver/webserver
# 获取最新版本代码
git fetch

# 更新nginx 配置文件
echo "900519" | sudo cp /home/strongman/websites/gsinfosite/webserver/webserver/gsinfo_webserver.conf /etc/nginx/sites-available/gsinfo_webserver.conf
echo "900519" | sudo nginx -t

# 启动网站
echo "900519" | sudo nginx -s reload
uwsgi --ini gsinfosite_uwsgi.ini

