# encoding=UTF-8
from django.shortcuts import render
from django.http.response import HttpResponse
import json
from .report_process import *
from django.contrib.auth.decorators import login_required
import datetime
from django.utils import timezone
from . import log
from middleWare import postThing,getserialNumber2

@login_required
def checking(request):
    userName = gsUser.objects.get(user=request.user)
    return render(request, 'c.html', context={'operator': userName, })


# ----------------------------------------------------
def boxIsExist(request):
    boxNumber = request.GET.get('boxNumber', '')

    try:
        box = gsBox.objects.filter(boxNumber=boxNumber)
    except ObjectDoesNotExist:
        ret = {
            "isExist": False,
            "message": u'',
        }
    else:
        ret = {
            "isExist": True,
            "message": u'{0}号箱已存在! 请返回修改箱号！'.format(boxNumber),
        }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def getWorkStatus(request):
    boxNumber = request.POST.get('boxNumber', '')
    ss = gsStatus.objects.filter(box=boxNumber)
    if (ss):
        workStatus = 1
        for s in ss:
            if (s.status1st != 1):
                workStatus = 0
            if (s.status2nd != 1):
                workStatus = 0
            if (s.status3rd != 1):
                workStatus = 0

            if (workStatus == 0):
                break
    else:
        workStatus = 0

    ret = {}
    ret['workStatus'] = workStatus

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def getDurationCompleteThingAmount(request):
    boxNumber = request.GET.get('boxNumber', '')
    fromDate = request.GET.get('fromDate', '')
    toDate = request.GET.get('toDate', '')

    fromDate = timezone.make_aware(datetime.strptime(fromDate + ' 00:00:00', '%m/%d/%Y %H:%M:%S'),
                                   timezone.get_default_timezone())
    toDate = timezone.make_aware(datetime.strptime(toDate + ' 23:59:59', '%m/%d/%Y %H:%M:%S'),
                                 timezone.get_default_timezone())
    ss = gsStatus.objects.filter(box=boxNumber)
    amount = 0
    for s in ss:
        lastUpdateDate = (
            s.updateDate1st if (s.updateDate1st is not None and s.updateDate2nd is None) else s.updateDate2nd) if (
            s.updateDate1st is None or s.updateDate2nd is None) else (
            s.updateDate1st if s.updateDate1st > s.updateDate2nd else s.updateDate2nd)
        lastUpdateDate = (
            lastUpdateDate if (lastUpdateDate is not None and s.updateDate3rd is None) else s.updateDate3rd) if (
            lastUpdateDate is None or s.updateDate3rd is None) else (
            lastUpdateDate if lastUpdateDate > s.updateDate3rd else s.updateDate3rd)

        if (s.status1st and s.status2nd and s.status3rd):  # 各环节均完成
            if (fromDate <= lastUpdateDate and toDate >= lastUpdateDate):
                amount = amount + 1

    ret = {}
    ret['amount'] = amount

    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)

def updateCheckingInfo(request):
    serialNumber = request.POST.get('serialNumber', '')
    productType = request.POST.get('productType', '')
    subClassName = request.POST.get('subClassName', '')
    className = request.POST.get('className', '')
    # -----------------------------------------------
    level = request.POST.get('level', None)
    detailedName = request.POST.get('detailedName', None)
    peroid = request.POST.get('peroid', None)
    year = request.POST.get('year', None)
    country = request.POST.get('country', None)
    faceAmount = request.POST.get('faceAmount', None)
    dingSecification = request.POST.get('dingSecification', None)
    zhangType = request.POST.get('zhangType', None)
    shape = request.POST.get('shape', None)
    appearance = request.POST.get('appearance', None)
    mark = request.POST.get('mark', None)
    originalQuantity = float(request.POST.get('originalQuantity'))
    remark = request.POST.get('remark', None)
    # -----------------------------------------------
    operator = request.POST.get('operator', '')

    thing_set = gsThing.objects.filter(serialNumber=serialNumber)

    ret = {}
    try:
        log.log(user=request.user, operationType=u'业务操作', content=u'实物认定信息更新')
        if subClassName == '国内银元' and level and detailedName:
            prop = gsProperty.objects.filter(type=detailedName)
            if prop.exists():
                code = gsProperty.objects.get(type=detailedName).code
            else:
                raise ValueError, u'名称填写错误！'
        else:
            code = detailedName
        thing_set.update(level=level,
                         detailedName=code,
                         peroid=peroid,
                         year=year,
                         country=country,
                         faceAmount=faceAmount,
                         dingSecification=dingSecification,
                         zhangType=zhangType,
                         shape=shape,
                         appearance=appearance,
                         mark=mark,
                         originalQuantity=originalQuantity,
                         remark=remark,)
        now = datetime.datetime.now()
        gsStatus.objects.filter(thing=thing_set[0]).update(checkingStatus=True, checkingOperator=operator,checkingUpdateDateTime=now)
        status_set = gsStatus.objects.filter(thing=thing_set[0])
        thing_status = status_set[0]
        status = thing_status.numberingStatus and thing_status.analyzingStatus and thing_status.measuringStatus and \
                 thing_status.photographingStatus and thing_status.checkingStatus
        if status:
            status_set.update(status=status, completeTime=now)

    except Exception as e:
        ret['success'] = False
        ret['message'] =  u'实物信息更新失败！'
    else:
        ret['success'] = True
        ret['message'] = u'实物信息更新成功！'

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def getThingData(request):
    boxNumber = request.GET.get('boxNumber', '')
    serialNumber = request.GET.get('serialNumber', '')

    box = gsBox.objects.get(boxNumber=boxNumber)

    ret = {}
    ret['serialNumber'] = serialNumber
    ret['boxNumber'] = boxNumber

    prop = box.boxType
    type = prop.type
    parentType = prop.parentType
    grandpaType = prop.grandpaType
    if grandpaType:
        ret['productType'] =grandpaType
        ret['className'] = parentType
        ret['subClassName'] =type
    else:
        ret['productType'] = parentType
        ret['className'] = type
        ret['subClassName'] = '-'
    wareHouseCode = box.wareHouse
    wareHouse = gsProperty.objects.get(project='发行库', code=wareHouseCode)
    ret['wareHouse'] = wareHouse.type

    thing = gsThing.objects.get(serialNumber=serialNumber)

    ret['detailedName'] = thing.detailedName
    ret['typeName'] = thing.typeName
    ret['peroid'] = thing.peroid
    ret['producer'] = thing.producer
    ret['producePlace'] = thing.producePlace
    ret['carveName'] = thing.carveName
    ret['remark'] = thing.remark
    ret['quality'] = thing.quality
    ret['level'] = thing.level
    ret['originalQuantity'] = thing.originalQuantity if (thing.originalQuantity is not None) else ''
    ret['detectedQuantity'] = thing.detectedQuantity if (thing.detectedQuantity is not None) else ''
    ret['length'] = thing.length if (thing.length is not None) else ''
    ret['width'] = thing.width if (thing.width is not None) else ''
    ret['height'] = thing.height if (thing.height is not None) else ''
    ret['grossWeight'] = thing.grossWeight if (thing.grossWeight is not None) else ''
    ret['pureWeight'] = thing.pureWeight if (thing.pureWeight is not None) else ''
    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def updateThingData(request):
    serialNumber = request.POST.get('serialNumber', '')
    boxNumber = int(request.POST.get('boxNumber', ''))
    className = request.POST.get('className', '')
    subClassName = request.POST.get('subClassName', '')
    wareHouse = request.POST.get('wareHouse', '')
    detailedName = request.POST.get('detailedName', '')
    typeName = request.POST.get('typeName', '')
    peroid = request.POST.get('peroid', '')
    producer = request.POST.get('producer', '')
    producePlace = request.POST.get('producePlace', '')
    carveName = request.POST.get('carveName', '')
    originalQuantity = request.POST.get('originalQuantity', '')
    detectedQuantity = request.POST.get('detectedQuantity', '')
    grossWeight = request.POST.get('grossWeight', '')
    versionName = request.POST.get('versionName', '')
    value = request.POST.get('value', '')
    marginShape = request.POST.get('marginShape', '')
    quality = request.POST.get('quality', '')
    level = request.POST.get('level', '')
    remark = request.POST.get('remark', '')
    operator = request.POST.get('operator', '')
    length = request.POST.get('length', '')
    width = request.POST.get('width', '')
    height = request.POST.get('height', '')
    diameter = request.POST.get('diameter', '')
    thick = request.POST.get('thick', '')

    if (0 != cmp(originalQuantity, '')):
        originalQuantity = float(originalQuantity)
    if (0 != cmp(detectedQuantity, '')):
        detectedQuantity = float(detectedQuantity)
    if (0 != cmp(grossWeight, '')):
        grossWeight = float(grossWeight)
    if (0 != cmp(length, '')):
        length = float(length)
    if (0 != cmp(width, '')):
        width = float(width)
    if (0 != cmp(height, '')):
        height = float(height)
    if (0 != cmp(diameter, '')):
        diameter = float(diameter)
    if (0 != cmp(thick, '')):
        thick = float(thick)

    box = gsBox.objects.get(boxNumber=boxNumber)
    productTypeCode = box.productType
    type = gsProperty.objects.get(project='实物类型', code=productTypeCode)
    productType = type.type

    try:
        # 检测作业是否可用
        thing = gsThing.objects.get(serialNumber=serialNumber)
        if thing.work.status == 0:
            # 作业不可用
            raise ValueError(u'作业不可用！请联系实物分发岗位进行分发！')

        if productType == u'金银锭类':
            gsDing.objects.filter(thing=thing).update(detailedName=detailedName,
                                                      typeName=typeName, peroid=peroid,
                                                      producer=producer,
                                                      producePlace=producePlace,
                                                     carveName=carveName,
                                                     originalQuantity=originalQuantity,
                                                     quality=quality, level=level,
                                                     remark=remark,
                                                     detectedQuantity=detectedQuantity,
                                                     grossWeight=grossWeight, length=length,
                                                     width=width, height=height)
        elif productType == u'金银币章类':
            gsBiZhang.objects.filter(thing=thing).update(detailedName=detailedName,
                                                         peroid=peroid,
                                                         producer=producer,
                                                         producePlace=producePlace,
                                                        originalQuantity=originalQuantity,
                                                        quality=quality, level=level,
                                                        versionName=versionName, remark=remark,
                                                        detectedQuantity=detectedQuantity,
                                                        diameter=diameter, thick=thick,
                                                        grossWeight=grossWeight, value=value)
        elif productType == u'银元类':
            gsYinYuan.objects.filter(thing=thing).update(marginShape=marginShape,
                                                         peroid=peroid,
                                                         producer=producer,
                                                         producePlace=producePlace,
                                                        quality=quality, level=level,
                                                        versionName=versionName, value=value,
                                                        remark=remark,
                                                        detectedQuantity=detectedQuantity,
                                                        diameter=diameter, thick=thick,
                                                        grossWeight=grossWeight)
        elif productType == u'金银工艺品类':
            gsGongYiPin.objects.filter(thing=thing).update(detailedName=detailedName,
                                                           peroid=peroid,
                                                          originalQuantity=originalQuantity,
                                                          quality=quality, level=level,
                                                          remark=remark,
                                                          detectedQuantity=detectedQuantity,
                                                          grossWeight=grossWeight,
                                                          length=length, width=width,
                                                          height=height)
    except Exception as e:
        ret = {
            'success': False,
            'message': u'实物{0}信息修改失败！\n原因:{1}'.format(serialNumber, e.message)
        }
    else:
        ret = {
            'success': True,
            'message': u'实物{0}信息修改成功！'.format(serialNumber),
        }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)
