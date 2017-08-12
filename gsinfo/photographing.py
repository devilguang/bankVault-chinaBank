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
#from django.views.decorators.csrf import csrf_exempt


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

    return HttpResponse('success_jsonpCallback(' + ret_json +')')

# 将删除该箱子所属的所有图片
def deletePic(request):
    boxOrSubBox = '1-5' # request.POST.get('boxNumber', '')

    ret = {}

    if '-' in boxOrSubBox:
        boxNumber = int(boxOrSubBox.split('-')[0])
        subBoxNumber = int(boxOrSubBox.split('-')[1])
    else:
        boxNumber = int(boxOrSubBox)
        subBoxNumber = ''

# def savePics(request):
#     file_obj = request.FILES.get('your_file', None)
#     # 写入文件
#     if file_obj == None:
#         return HttpResponse('file not existing in the request')
#     file_name = 'temp_file-%d' % random.randint(0, 100000)  # 不能使用文件名称，因为存在中文，会引起内部错误
#     file_full_path = os.path.join(UPLOAD_ROOT, file_name)
#     dest = open(file_full_path, 'wb+')
#     dest.write(file_obj.read())
#     dest.close()
#     return HttpResponse(ret_json)

def updatePhotographingInfo(request):
    serialNumber = request.POST.get('serialNumber', '')
    boxOrSubBox = request.POST.get('boxNumber', '')

    file_obj = request.FILES.get('your_file', None)

    ret = {}
    # 写入文件
    if file_obj == None:
        ret['success'] = True
        ret['message'] = '图片上传失败！'
        ret_json = json.dumps(ret, separators=(',', ':'))
        return HttpResponse(ret_json)
    save_path = os.path.join(settings.STATIC_PATH,boxOrSubBox,'123.jpg')  # 不能使用文件名称，因为存在中文，会引起内部错误
    dest = open(save_path, 'wb+')
    dest.write(file_obj.read())
    dest.close()

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
        ret['message'] = '图片上传失败！'

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)




# 图片需要三个路径：相机拍摄后保存路径，备份到硬盘路径，长传到系统路径

# def getMeasuringInfo(request):
#     serialNumber = request.GET.get('serialNumber', '')
#     boxNumber = int(request.GET.get('boxNumber', ''))
#     productType = request.GET.get('productType', '')
#
#     box = gsBox.objects.get(boxNumber=boxNumber)
#
#     ret = {}
#     if (0 == cmp(productType, u'金银锭类')):
#         thing = gsDing.objects.get(box=box, serialNumber=serialNumber)
#         ret['grossWeight'] = thing.grossWeight
#         ret['length'] = thing.length
#         ret['width'] = thing.width
#         ret['height'] = thing.height
#     elif (0 == cmp(productType, u'金银币章类')):
#         thing = gsBiZhang.objects.get(box=box, serialNumber=serialNumber)
#         ret['grossWeight'] = thing.grossWeight
#         ret['diameter'] = thing.diameter
#         ret['thick'] = thing.thick
#     elif (0 == cmp(productType, u'银元类')):
#         thing = gsYinYuan.objects.get(box=box, serialNumber=serialNumber)
#         ret['grossWeight'] = thing.grossWeight
#         ret['diameter'] = thing.diameter
#         ret['thick'] = thing.thick
#     elif (0 == cmp(productType, u'金银工艺品类')):
#         thing = gsGongYiPin.objects.get(box=box, serialNumber=serialNumber)
#         ret['grossWeight'] = thing.grossWeight
#         ret['length'] = thing.length
#         ret['width'] = thing.width
#         ret['height'] = thing.height
#
#     ret_json = json.dumps(ret, separators=(',', ':'))
#
#     return HttpResponse(ret_json)