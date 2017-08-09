# encoding=UTF-8
import sys
from django.shortcuts import render
from django.http.response import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist
from models import *
import json, os
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone
import time,datetime

from PIL import Image, ImageDraw, ImageFont
import math
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
photoDir = os.path.join(BASE_DIR,'photo')
uploadDir = os.path.join(BASE_DIR,'upload')

rephotoFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),'rephotoFileName.txt')
pastSerialFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),'pastSerialNumber.txt')
uploadFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),'uploadResult.txt')

def getSeq(request):
    serialNumber = '1-02-217-3' # request.POST.get
    ret = {}
    # 指定要使用的字体和大小；/Library/Fonts/是macOS字体目录；Linux的字体目录是/usr/share/fonts/
    font = ImageFont.truetype('msyh.ttc', 16)  # 第二个参数表示字符大小

    if not os.path.exists(uploadDir):
        os.mkdir(uploadDir)
    # -----------------------------------------------------
    with open(rephotoFile, 'r') as f:
        rephtoFile = f.read().strip()

    if rephtoFile:
        deleteFilePath = os.path.join(uploadDir, rephtoFile)  # 删除旧图

        os.remove(deleteFilePath)
        newSerial = rephtoFile.split('.')[0]
        # ++++++++++++
        if os.path.exists(photoDir):
            fileList = os.listdir(photoDir)
            print fileList
            if len(fileList) == 1:
                picName = fileList[0]
                picPath = os.path.join(photoDir, picName)

                image = Image.open(picPath)
                imgNew = image.resize((256, 256))
                draw = ImageDraw.Draw(imgNew)
                width, height = font.getsize(newSerial)

                x = int((256 - width) / 2)
                y = 256 - height - 12
                draw.text((x, y), newSerial, fill=(255, 255, 255), font=font)
                # imgNew.show()

                savePath = os.path.join(uploadDir, '{0}.jpg'.format(newSerial))
                imgNew.save(savePath)
                os.remove(picPath)
                ret['filePath'] = savePath
                with open(uploadFile, 'w') as f:
                    f.truncate()
            elif len(fileList) == 0:
                pass
            else:
                # shutil.rmtree(photoDir) 会把 photoDir也删除，而photoDir可能不具有被删除的权限
                for file in fileList:
                    p = os.path.join(photoDir, file)
                    os.remove(p)
        else:
            ret['havePhotoDir'] = 'False'
            ret['stop'] = 'True'
    else:
        with open(pastSerialFile, 'r') as f:
            pastSerialNumber = f.read().strip()

        if not pastSerialNumber:
            char = 'A'
        else:
            contentList = pastSerialNumber.split('/')
            if serialNumber == contentList[0]:
                char = chr(ord(contentList[-1]) + 1)
            else:
                char = 'A'

        newSerial = serialNumber + '-' + char
        # ++++++++++++
        if os.path.exists(photoDir):
            fileList = os.listdir(photoDir)
            print fileList
            if len(fileList) == 1:
                picName = fileList[0]
                picPath = os.path.join(photoDir, picName)

                image = Image.open(picPath)
                imgNew = image.resize((256, 256))
                draw = ImageDraw.Draw(imgNew)
                width, height = font.getsize(newSerial)

                x = int((256 - width) / 2)
                y = 256 - height - 12
                draw.text((x, y), newSerial, fill=(255, 255, 255), font=font)
                # imgNew.show()

                savePath = os.path.join(uploadDir, '{0}.jpg'.format(newSerial))
                imgNew.save(savePath)
                with open(pastSerialFile, 'w') as f:
                    cont = serialNumber + '/' + char
                    f.write(cont)
                os.remove(picPath)

                ret['filePath'] = savePath
            elif len(fileList) == 0:
                pass
            else:
                # shutil.rmtree(photoDir) 会把 photoDir也删除，而photoDir可能不具有被删除的权限
                for file in fileList:
                    p = os.path.join(photoDir, file)
                    os.remove(p)
        else:
            ret['havePhotoDir'] = 'False'
            ret['stop'] = 'True'
    # -----------------------------------------------------
    uploadResult = None
    if os.path.exists('uploadResult.txt'):
        with open('uploadResult.txt', 'r+') as f:
            uploadResult = f.read().strip()
            f.truncate()

    if uploadResult == 'True':
        ret['stop'] = 'True'
    # -----------------------------------------------------
    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder)
    return HttpResponse(ret_json)


def rephotograph(request):
    ret = {}
    fileName = '1-02-217-3-A.jpg'
    with open(rephotoFile,'w') as f:
        f.write(fileName)

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder)
    return HttpResponse(ret_json)


def deletePic(request):
    fileName = '1-02-217-2002-B.jpg'
    deleteFilePath = os.path.join(uploadDir,fileName)
    os.remove(deleteFilePath)


def upload(request):
    with open('uploadResult.txt','w') as f:
        result = 'done'
        f.write(result)

# -----------------------------------------------------
# 频谱检测仪功能
# 一、通过复制数据库文件解除独占










# if __name__ == '__main__':
#     getSeq('1-02-217-2002')
