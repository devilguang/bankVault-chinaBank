# encoding=UTF-8
import sys
from django.shortcuts import render
from django.http.response import HttpResponse, StreamingHttpResponse, HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist
from models import *
import json, os
from utils import readFile, dateTimeHandler, deleteDir
from tag_process import *
from report_process import *
from gsinfosite import settings
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone
import datetime



@login_required  # 测量称重岗位
def measuring(request):
    nickName = gsUser.objects.get(user=request.user)
    return render(request, 'me.html', context={'operator': nickName, })


def getMeasuringInfo(request):
    serialNumber = request.GET.get('serialNumber', '')
    boxNumber = int(request.GET.get('boxNumber', ''))
    productType = request.GET.get('productType', '')

    box = gsBox.objects.get(boxNumber=boxNumber)

    ret = {}
    if (0 == cmp(productType, u'金银锭类')):
        thing = gsDing.objects.get(box=box, serialNumber=serialNumber)
        ret['grossWeight'] = thing.grossWeight
        ret['length'] = thing.length
        ret['width'] = thing.width
        ret['height'] = thing.height
    elif (0 == cmp(productType, u'金银币章类')):
        thing = gsBiZhang.objects.get(box=box, serialNumber=serialNumber)
        ret['grossWeight'] = thing.grossWeight
        ret['diameter'] = thing.diameter
        ret['thick'] = thing.thick
    elif (0 == cmp(productType, u'银元类')):
        thing = gsYinYuan.objects.get(box=box, serialNumber=serialNumber)
        ret['grossWeight'] = thing.grossWeight
        ret['diameter'] = thing.diameter
        ret['thick'] = thing.thick
    elif (0 == cmp(productType, u'金银工艺品类')):
        thing = gsGongYiPin.objects.get(box=box, serialNumber=serialNumber)
        ret['grossWeight'] = thing.grossWeight
        ret['length'] = thing.length
        ret['width'] = thing.width
        ret['height'] = thing.height

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def updateMeasuringInfo(request):
    serialNumber = request.POST.get('serialNumber', '')
    boxNumber = int(request.POST.get('boxNumber', ''))
    productType = request.POST.get('productType', '')
    className = request.POST.get('className', '')
    subClassName = request.POST.get('subClassName', '')
    wareHouse = request.POST.get('wareHouse', '')
    grossWeight = float(request.POST.get('grossWeight', ''))
    diameter = request.POST.get('diameter', '')
    thick = request.POST.get('thick', '')
    length = request.POST.get('length', '')
    width = request.POST.get('width', '')
    height = request.POST.get('height', '')
    operator = request.POST.get('operator', '')

    if diameter != '':
        diameter = float(diameter)
    if thick != '':
        thick = float(thick)
    if length != '':
        length = float(length)
    if width != '':
        width = float(width)
    if height != '':
        height = float(height)

    box = gsBox.objects.get(boxNumber=boxNumber)

    try:
        # 检测作业是否可用
        t = gsThing.objects.get(serialNumber=serialNumber)
        wt = gsWorkThing.objects.get(thing=t)
        if wt.work.status != 1:  # 0:未启用 1:已启用 2:已完成
            # 作业不可用
            raise ValueError, u'作业不可用！请联系现场负责人进行分发，并刷新页面！'

        if productType == u'金银锭类':
            gsDing.objects.filter(box=box, serialNumber=serialNumber).update(length=length, width=width, height=height,
                                                                             grossWeight=grossWeight)
        elif productType == u'金银币章类':
            gsBiZhang.objects.filter(box=box, serialNumber=serialNumber).update(diameter=diameter, thick=thick,
                                                                                grossWeight=grossWeight)
        elif productType == u'银元类':
            gsYinYuan.objects.filter(box=box, serialNumber=serialNumber).update(diameter=diameter, thick=thick,
                                                                                grossWeight=grossWeight)
        elif productType == u'金银工艺品类':
            gsGongYiPin.objects.filter(box=box, serialNumber=serialNumber).update(length=length, width=width,
                                                                                  height=height,
                                                                                  grossWeight=grossWeight)

        # now = datetime.datetime.utcnow()  # 这里使用utcnow生成时间,存入mariaDB后被数据库当做非UTC时间,自动减去了8个小时,所以这里改用now
        now = datetime.datetime.now()
        gsStatus.objects.filter(box=box, serialNumber=serialNumber).update(measuringStatus=True,
                                                                           measuringOperator=operator,
                                                                           measuringUpdateDateTime=now)

        s = gsStatus.objects.get(box=box, serialNumber=serialNumber)
        status = s.numberingStatus and s.analyzingStatus and s.measuringStatus and s.photographingStatus
        gsStatus.objects.filter(box=box, serialNumber=serialNumber).update(status=status)
    except Exception as e:
        ret = {}
        ret['success'] = False
        ret['message'] = str(boxNumber) + u'号箱作业更新失败！' if (0 == cmp(serialNumber, '')) else str(
            boxNumber) + u'号箱，编号为' + serialNumber + u'实物信息更新失败！'
        ret['message'] = ret['message'] + u'\r\n原因:' + e.message
    else:
        ret = {}
        ret['success'] = True
        ret['message'] = str(boxNumber) + u'号箱作业更新成功！' if (0 == cmp(serialNumber, '')) else str(
            boxNumber) + u'号箱，编号为' + serialNumber + u'实物信息更新成功！'

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


