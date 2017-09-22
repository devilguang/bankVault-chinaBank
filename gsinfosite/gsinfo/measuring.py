# encoding=UTF-8
from django.shortcuts import render
from django.http.response import HttpResponse
import json
from report_process import *
from django.contrib.auth.decorators import login_required
from datetime import datetime
import datetime
from . import log
from middleWare import postThing


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
    # -------------------------------------
    grossWeight = float(request.POST.get('grossWeight'))  # 无论什么类型什么操作，毛重总是有的
    length = request.POST.get('length', '')
    width = request.POST.get('width', '')
    height = request.POST.get('height', '')
    # -------------------------------------
    operator = request.POST.get('operator', '')

    try:
        log.log(user=request.user, operationType=u'业务操作', content=u'测量称重信息更新')
        # 检测作业是否可用
        thing = gsThing.objects.get(serialNumber=serialNumber)
        if thing.work.status == 0:  # 0:未启用 1:已启用 2:已完成
            # 作业不可用
            raise ValueError, u'作业不可用！请联系实物分发岗位进行分发，并刷新页面！'

        update_fields = []
        thing.grossWeight = float(grossWeight)
        update_fields.append('grossWeight')
        if length:
            thing.length=float(length)
            update_fields.append('length')
        if width:
            thing.width=float(width)
            update_fields.append('width')
        if height:
            thing.height=float(height)
            update_fields.append('height')

        thing.save(update_fields=update_fields)

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
        ret['message'] = u'{0}实物信息更新失败！'.format(serialNumber)
    else:
        ret = {}
        ret['success'] = True
        ret['message'] = u'{0}实物信息更新成功！'.format(serialNumber)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)

def isLinSan(request):
    boxNumber = request.POST.get('boxNumber', '')
    try:
        box = gsBox.objects.get(boxNumber=boxNumber)
        oprateType_code = box.oprateType.code
        if oprateType_code == '3':
            ret = {
                'success': True
            }
        else:
            ret = {
                'success': False
            }
    except Exception as e:
        ret={
            'success':False
        }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)