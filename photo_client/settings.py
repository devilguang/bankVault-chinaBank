# encoding=UTF-8

import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 服务器IP地址
SERVERHOST = '127.0.0.1'
# 服务器端口号
SERVERPORT = '9090'
# 相机输出路径
PHOTODIR = r'C:\Users\Administrator\Desktop\photo'
UPLOADDIR = os.path.join(BASE_DIR,'upload')
