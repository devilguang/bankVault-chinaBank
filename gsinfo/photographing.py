# encoding=UTF-8
import sys
from django.shortcuts import render
from django.http.response import HttpResponse
import json, os
from report_process import *
from gsinfosite import settings
from django.contrib.auth.decorators import login_required
from datetime import datetime
import datetime
import base64


@login_required  # 图像采集岗位
def photographing(request):
    nickName = gsUser.objects.get(user=request.user)
    return render(request, 'p.html', context={'operator': nickName, })

def getPictures(request):
    boxOrSubBox = request.GET.get('boxNumber', '')
    serialNumber = request.GET.get('serialNumber', '')

    ret = {}

    boxDir = os.path.join(settings.STATIC_PATH,'img', boxOrSubBox)
    if not os.path.exists(boxDir):
        os.mkdir(boxDir)

    thingsDir = os.path.join(boxDir, serialNumber)
    if not os.path.exists(thingsDir):
        os.mkdir(thingsDir)

    picPath = thingsDir
    sendDir = os.path.join('static', 'img',boxOrSubBox, serialNumber)

    fileList = os.listdir(picPath)
    if fileList:
        ret['havePic'] = True
        filePathList = []
        for fileName in fileList:
            filePath = os.path.join(sendDir,fileName)
            filePathList.append(filePath)
        ret['filePathList'] = filePathList
    else:
        ret['havePic'] = False

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)

def updatePhotographingInfo(request):
    serialNumber = request.POST.get('serialNumber', '')
    boxOrSubBox = request.POST.get('boxNumber', '')
    pic_path = request.POST.get('pic_path', '')
    ret = {}
    if pic_path:
        img_path = json.loads(pic_path)

        for k,v in img_path.items():
            file_name = serialNumber + '-' + k + '.jpg'
            save_path = os.path.join(settings.STATIC_PATH,'img',boxOrSubBox,serialNumber,file_name)
            img = base64.b64decode(v)
            with open(save_path,'wb') as f:
                f.write(img)

        if '-' in boxOrSubBox:
            boxNumber = int(boxOrSubBox.split('-')[0])
            subBoxNumber = int(boxOrSubBox.split('-')[1])
        else:
            boxNumber = int(boxOrSubBox)
            subBoxNumber = ''


        user = request.user
        operator = gsUser.objects.get(user=user).nickName

        box = gsBox.objects.get(boxNumber=boxNumber)

        try:
            # 检测作业是否可用
            t = gsThing.objects.get(serialNumber=serialNumber)
            wt = gsWorkThing.objects.get(thing=t)
            if wt.work.status != 1:
                # 作业不可用
                raise ValueError, u'作业不可用！请联系现场负责人进行分发，并刷新页面！'

            # now = datetime.datetime.utcnow()  # 这里使用utcnow生成时间,存入mariaDB后被数据库当做非UTC时间,自动减去了8个小时,所以这里改用now
            now = datetime.datetime.now()
            gsStatus.objects.filter(box=box, serialNumber=serialNumber).update(photographingStatus=True,
                                                                               photographingOperator=operator,
                                                                               photographingUpdateDateTime=now)

            s = gsStatus.objects.get(box=box, serialNumber=serialNumber)
            status = s.numberingStatus and s.analyzingStatus and s.measuringStatus and s.photographingStatus
            gsStatus.objects.filter(box=box, serialNumber=serialNumber).update(status=status)
        except Exception as e:
            ret['success'] = False
            ret['message'] = '图片上传失败！'
        else:
            ret['success'] = True
            ret['message'] = '图片上传成功！'
    else:
        ret['success'] = False
        ret['message'] = '图片上传失败！'

    ret_json = json.dumps(ret, separators=(',', ':'))
    # return HttpResponse('success_jsonpCallback(' + ret_json +')')
    return HttpResponse(ret_json)

def delectPic(request):
    boxOrSubBox = request.POST.get('boxNumber', '')
    serialNumber = request.POST.get('serialNumber', '')
    fileName = request.POST.get('fileName', '')
    ret={}
    delect_path = os.path.join(settings.STATIC_PATH,'img',boxOrSubBox,serialNumber,fileName)
    if os.path.exists(delect_path):
        os.remove(delect_path)
        ret['success'] = True
        ret['message'] = '图片删除成功！'
    else:
        ret['success'] = False
        ret['message'] = '服务器上无该图片！'
    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)