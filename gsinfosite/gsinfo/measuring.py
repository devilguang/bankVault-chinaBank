# encoding=UTF-8
from django.shortcuts import render
from django.http.response import HttpResponse
import json
from report_process import *
from django.contrib.auth.decorators import login_required
from datetime import datetime
import datetime
from . import log


@login_required  # 测量称重岗位
def measuring(request):
    userName = gsUser.objects.get(user=request.user)
    return render(request, 'me.html', context={'operator': userName, })


def getMeasuringInfo(request):
    serialNumber = request.GET.get('serialNumber', '')
    boxNumber = int(request.GET.get('boxNumber', ''))
    productType = request.GET.get('productType', '')

    box = gsBox.objects.get(boxNumber=boxNumber)
    thing = gsThing.objects.get(serialNumber=serialNumber,box=box)

    ret = {}
    if (0 == cmp(productType, u'金银锭类')):
        thing = gsDing.objects.get(thing=thing)
        ret['grossWeight'] = thing.grossWeight
        ret['length'] = thing.length
        ret['width'] = thing.width
        ret['height'] = thing.height
    elif (0 == cmp(productType, u'金银币章类')):
        thing = gsBiZhang.objects.get(thing=thing)
        ret['grossWeight'] = thing.grossWeight
        ret['diameter'] = thing.diameter
        ret['thick'] = thing.thick
    elif (0 == cmp(productType, u'银元类')):
        thing = gsYinYuan.objects.get(thing=thing)
        ret['grossWeight'] = thing.grossWeight
        ret['diameter'] = thing.diameter
        ret['thick'] = thing.thick
    elif (0 == cmp(productType, u'金银工艺品类')):
        thing = gsGongYiPin.objects.get(thing=thing)
        ret['grossWeight'] = thing.grossWeight
        ret['length'] = thing.length
        ret['width'] = thing.width
        ret['height'] = thing.height

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def updateMeasuringInfo(request):
    serialNumber = request.POST.get('serialNumber', '')
    boxOrSubBox = request.POST.get('boxNumber', '')
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

    if '-' in boxOrSubBox:
        boxNumber = int(boxOrSubBox.split('-')[0])
        subBoxNumber = boxOrSubBox.split('-')[1]
    else:
        boxNumber = int(boxOrSubBox)
        subBoxNumber = ''

    box = gsBox.objects.get(boxNumber=boxNumber)

    try:
        log.log(user=request.user, operationType=u'业务操作', content=u'测量称重信息更新')
        # 检测作业是否可用
        thing = gsThing.objects.get(serialNumber=serialNumber)
        if thing.work.status == 0:  # 0:未启用 1:已启用 2:已完成
            # 作业不可用
            raise ValueError, u'作业不可用！请联系实物分发岗位进行分发，并刷新页面！'

        if productType == u'金银锭类':
            gsDing.objects.filter(thing=thing).update(length=length, width=width, height=height,grossWeight=grossWeight)
        elif productType == u'金银币章类':
            gsBiZhang.objects.filter(thing=thing).update(diameter=diameter, thick=thick,grossWeight=grossWeight)
        elif productType == u'银元类':
            gsYinYuan.objects.filter(thing=thing).update(diameter=diameter, thick=thick,grossWeight=grossWeight)
        elif productType == u'金银工艺品类':
            gsGongYiPin.objects.filter(thing=thing).update(length=length, width=width,height=height,grossWeight=grossWeight)

        # now = datetime.datetime.utcnow()  # 这里使用utcnow生成时间,存入mariaDB后被数据库当做非UTC时间,自动减去了8个小时,所以这里改用now
        now = datetime.datetime.now()
        gsStatus.objects.filter(thing=thing).update(measuringStatus=True,measuringOperator=operator,measuringUpdateDateTime=now)
        thing_set = gsStatus.objects.filter(thing=thing)
        thing_status = thing_set[0]
        status = thing_status.numberingStatus and thing_status.analyzingStatus and thing_status.measuringStatus and \
                 thing_status.photographingStatus and thing_status.checkingStatus
        if status:
            thing_set.update(status=status, completeTime=now)
    except Exception as e:
        ret = {}
        ret['success'] = False
        ret['message'] = boxOrSubBox + u'号箱作业更新失败！' if (0 == cmp(serialNumber, '')) else boxOrSubBox + u'号箱，编号为' + serialNumber + u'实物信息更新失败！'
        ret['message'] = ret['message'] + u'\r\n原因:' + e.message
    else:
        ret = {}
        ret['success'] = True
        ret['message'] = boxOrSubBox + u'号箱作业更新成功！' if (0 == cmp(serialNumber, '')) else boxOrSubBox + u'号箱，编号为' + serialNumber + u'实物信息更新成功！'

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


