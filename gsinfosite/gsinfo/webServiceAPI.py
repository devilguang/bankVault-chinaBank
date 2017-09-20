# encoding=UTF-8
from suds.client import Client
from gsinfosite.settings import WEBSERVERAPI


# 二维码生成箱、包、件号接口
def getNumberAPI(code):
    client = Client(WEBSERVERAPI, cache=None)
    number = client.service.getStringReturnCode(code)
    return number

# 金银实物清点件接口
def postThingDataAPI(code):
    client = Client(WEBSERVERAPI, cache=None)
    status_code = client.service.getEntityMessage(code)
    return status_code

# 金银实物封盒接口
def postCaseAPI(code):
    client = Client(WEBSERVERAPI, cache=None)
    status_code = client.service.getBoxMessage(code)
    return status_code

# 金银实物封箱接口
def postBoxAPI(code):
    client = Client(WEBSERVERAPI, cache=None)
    status_code = client.service.getPackMessage(code)
    return status_code

# 金银实物图片接口
def postPicAPI(filename,filecontent):  # String filename,byte[] filecontent
    client = Client(WEBSERVERAPI, cache=None)
    status_code = client.service.getEntityPicture(filename,filecontent)
    return status_code