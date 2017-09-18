# encoding=UTF-8
from django.shortcuts import render
from django.http.response import HttpResponse
import json
from report_process import *
from gsinfosite import settings
from django.contrib.auth.decorators import login_required
import datetime
import base64
from . import log

@login_required  # 图像采集岗位
def photographing(request):
    userName = gsUser.objects.get(user=request.user)
    return render(request, 'p.html', context={'operator': userName, })

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

    img_dir = settings.IMGS_DATA_PATH
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    box_path = os.path.join(img_dir,boxOrSubBox)
    if not os.path.exists(box_path):
        os.makedirs(box_path)

    serialNumber_path = os.path.join(box_path,serialNumber)
    if not os.path.exists(serialNumber_path):
        os.makedirs(serialNumber_path)

    log.log(user=request.user, operationType=u'业务操作', content=u'图像采集信息更新')
    if pic_path:
        img_path = json.loads(pic_path)

        for file_name,img in img_path.items():
            save_path = os.path.join(serialNumber_path,file_name)
            img = base64.b64decode(img)
            with open(save_path,'wb') as f:
                f.write(img)

        user = request.user
        operator = gsUser.objects.get(user=user).userName

        try:
            # 检测作业是否可用
            thing = gsThing.objects.get(serialNumber=serialNumber)
            if thing.work.status == 0:
                # 作业不可用
                raise ValueError, u'作业不可用！请联系实物分发岗位进行分发，并刷新页面！'

            # now = datetime.datetime.utcnow()  # 这里使用utcnow生成时间,存入mariaDB后被数据库当做非UTC时间,自动减去了8个小时,所以这里改用now
            now = datetime.datetime.now()
            gsStatus.objects.filter(thing=thing).update(photographingStatus=True,photographingOperator=operator,photographingUpdateDateTime=now)
            thing_status = gsStatus.objects.filter(thing=thing)
            thing_obj = thing_status[0]
            status = thing_obj.numberingStatus and thing_obj.analyzingStatus and thing_obj.measuringStatus and \
                     thing_obj.photographingStatus and thing_obj.checkingStatus
            if status:
                thing_status.update(status=status,completeTime=now)
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