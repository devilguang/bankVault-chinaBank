# encoding=UTF-8
import sys
from django.shortcuts import render
from django.http.response import HttpResponse
import json
from report_process import *
from django.contrib.auth.decorators import login_required
import datetime
import operator
from . import log



@login_required  # 外观信息采集岗位
def numbering(request):
    userName = gsUser.objects.get(user=request.user)
    return render(request, 'n.html', context={'operator': userName, })


def getNumberingInfo(request):
    serialNumber = request.GET.get('serialNumber', '')
    boxOrSubBox = request.GET.get('boxNumber', '')
    productType = request.GET.get('productType', '')

    if '-' in boxOrSubBox:
        boxNumber = int(boxOrSubBox.split('-')[0])
    else:
        boxNumber = int(boxOrSubBox)

    box = gsBox.objects.get(boxNumber=boxNumber)

    ret = {}
    if (0 == cmp(productType, u'金银锭类')):
        thing = gsDing.objects.get(box=box, serialNumber=serialNumber)
        ret['detailedName'] = thing.detailedName
        ret['peroid'] = thing.peroid
        ret['originalQuantity'] = thing.originalQuantity
        producer = request.POST.get('producer', '')
        producePlace = request.POST.get('producePlace', '')
        ret['typeName'] = thing.typeName
        ret['carveName'] = thing.carveName
        ret['remark'] = thing.remark
        ret['quality'] = thing.quality
        ret['level'] = thing.level
    elif (0 == cmp(productType, u'金银币章类')):
        thing = gsBiZhang.objects.get(box=box, serialNumber=serialNumber)
        ret['versionName'] = thing.versionName
        ret['detailedName'] = thing.detailedName
        ret['peroid'] = thing.peroid
        ret['originalQuantity'] = thing.originalQuantity
        producer = request.POST.get('producer', '')
        producePlace = request.POST.get('producePlace', '')
        ret['remark'] = thing.remark
        ret['quality'] = thing.quality
        ret['level'] = thing.level
    elif (0 == cmp(productType, u'银元类')):
        thing = gsYinYuan.objects.get(box=box, serialNumber=serialNumber)
        ret['versionName'] = thing.versionName
        ret['value'] = thing.value
        producer = request.POST.get('producer', '')
        producePlace = request.POST.get('producePlace', '')
        ret['remark'] = thing.remark
        ret['quality'] = thing.quality
        ret['level'] = thing.level
    elif (0 == cmp(productType, u'金银工艺品类')):
        thing = gsGongYiPin.objects.get(box=box, serialNumber=serialNumber)
        ret['detailedName'] = thing.detailedName
        ret['peroid'] = thing.peroid
        ret['originalQuantity'] = thing.originalQuantity
        ret['remark'] = thing.remark
        ret['quality'] = thing.quality
        ret['level'] = thing.level

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)

def getReadyInfo(request):
    field = request.POST.get('field', '')
    ret = {}
    info = list(gsProperty.objects.filter(project=field).values_list('type',flat=True))
    ret['count'] = len(info)
    ret['info'] = info
    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)

def updateNumberingInfo(request):
    serialNumber = request.POST.get('serialNumber', '')
    boxOrSubBox = request.POST.get('boxNumber', '')
    productType = request.POST.get('productType', '')
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
    versionName = request.POST.get('versionName', '')
    value = request.POST.get('value', '')
    marginShape = request.POST.get('marginShape', '')
    quality = request.POST.get('quality', '')
    level = request.POST.get('level', '')
    remark = request.POST.get('remark', '')
    operator = request.POST.get('operator', '')
    workSeq = request.POST.get('workSeq', '')  # 更新单件实物信息是workSeq不传值，设置缺省信息是传值
    if originalQuantity != '':
        originalQuantity = float(originalQuantity)

    if '-' in boxOrSubBox:
        boxNumber = int(boxOrSubBox.split('-')[0])
        subBoxNumber = int(boxOrSubBox.split('-')[1])
    else:
        boxNumber = int(boxOrSubBox)
        subBoxNumber = ''

    box = gsBox.objects.get(boxNumber=boxNumber)
    if subBoxNumber == '':
        if serialNumber == '' and workSeq != '':
            work = gsWork.objects.get(box=box, workSeq=workSeq)
            thing_set = gsThing.objects.filter(work=work)
        elif serialNumber != '' and workSeq == '':
            thing_set = gsThing.objects.filter(serialNumber=serialNumber)
    else:
        if serialNumber == '' and workSeq != '':
            subBox = gsSubBox.objects.get(box=box, subBoxNumber=subBoxNumber)
            work = gsWork.objects.get(box=box, workSeq=workSeq, subBox=subBox)
            thing_set = gsThing.objects.filter(work=work)
        elif serialNumber != '' and workSeq == '':
            thing_set = gsThing.objects.filter(serialNumber=serialNumber)
    ret = {}
    try:
        log.log(user=request.user, operationType=u'业务操作', content=u'实物外观信息更新')
        if productType == u'金银锭类':
            gsDing.objects.filter(thing__in=thing_set).update(detailedName=detailedName,
                                                      typeName=typeName,
                                                      peroid=peroid,
                                                      producer=producer,
                                                      producePlace=producePlace,
                                                      carveName=carveName,
                                                      originalQuantity=originalQuantity,
                                                      quality=quality,
                                                      level=level,
                                                      remark=remark)
        elif productType == u'金银币章类':
            gsBiZhang.objects.filter(thing__in=thing_set).update(detailedName=detailedName,
                                                                 peroid=peroid,
                                                                 producer=producer,
                                                                 producePlace=producePlace,
                                                                 originalQuantity=originalQuantity,
                                                                 quality=quality,
                                                                 level=level,
                                                                 value=value,
                                                                 versionName=versionName,
                                                                 remark=remark)
        elif productType == u'银元类':
            gsYinYuan.objects.filter(thing__in=thing_set).update(producer=producer,
                                                         producePlace=producePlace,
                                                         quality=quality,
                                                         level=level,
                                                         versionName=versionName,
                                                         value=value,
                                                         remark=remark)
        elif productType == u'金银工艺品类':
            gsGongYiPin.objects.filter(thing__in=thing_set).update(detailedName=detailedName,
                                                           peroid=peroid,
                                                           originalQuantity=originalQuantity,
                                                           quality=quality,
                                                           level=level,
                                                           remark=remark)
        # now是本地时间，可以认为是你电脑现在的时间 utcnow是世界时间（时区不同，所以这两个是不一样的）
        # now = datetime.datetime.utcnow()  # 这里使用utcnow生成时间,存入mariaDB后被数据库当做非UTC时间,自动减去了8个小时,所以这里改用now
        if serialNumber != '' and workSeq == '':
            now = datetime.datetime.now()
            gsStatus.objects.filter(thing__in=thing_set).update(numberingStatus=True,numberingOperator=operator,numberingUpdateDateTime=now)

            status_set = gsStatus.objects.filter(thing=thing_set[0])
            s = status_set[0]
            status = s.numberingStatus and s.analyzingStatus and s.measuringStatus and s.photographingStatus and s.checkingStatus
            if status:
                status_set.update(status=status,completeTime=now)
    except Exception as e:
        ret['success'] = False
        ret['message'] = str(boxNumber) + u'号箱作业更新失败！' if (0 == cmp(serialNumber, '')) else str(
            boxNumber) + u'号箱，编号为' + serialNumber + u'实物信息更新失败！'
        ret['message'] = ret['message'] + u'\r\n原因:{0}'.format(e.message)
    else:
        ret['success'] = True
        ret['message'] = str(boxNumber) + '号箱作业更新成功！' if (0 == cmp(serialNumber, '')) else str(
            boxNumber) + u'号箱，编号为' + serialNumber + u'实物信息更新成功！'

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


# ---------------------------------------------------------------------
# 录入信息检测
def checkInfo(request):
    productType = request.POST.get('productType', '')  # u'金银锭类'
    key = request.POST.get('key', '')
    value = request.POST.get('value', '')
    ret ={}

    if productType == u'金银锭类':
        things = gsDing.objects.values_list(key,flat=True)
    elif productType == u'金银币章类':
        things = gsBiZhang.objects.values_list(key, flat=True)
    elif productType == u'银元类':
        things = gsYinYuan.objects.values_list(key, flat=True)
    elif productType == u'金银工艺品类':
        things = gsGongYiPin.objects.values_list(key, flat=True)

    historyInfo = {}
    for thing in things:
        if thing.startswith(value):
            historyInfo[thing] = historyInfo.get(thing, 0) + 1

    sortedClassCount = sorted(historyInfo.items(), key=operator.itemgetter(1),reverse=True)
    sort_len = len(sortedClassCount)
    if sortedClassCount:
        ret['success'] = True
        message_list = []
        if sort_len == 1:
            message_list.append(sortedClassCount[0][0])
        elif sort_len == 2:
            message_list.append(sortedClassCount[0][0])
            message_list.append(sortedClassCount[1][0])
        else:
            message_list.append(sortedClassCount[0][0])
            message_list.append(sortedClassCount[1][0])
            message_list.append(sortedClassCount[2][0])
        ret['message'] = message_list

    else:
        ret['success'] = False
    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)