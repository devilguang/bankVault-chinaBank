# encoding=UTF-8
import sys
from django.shortcuts import render
from django.http.response import HttpResponse
import json
from report_process import *
from django.contrib.auth.decorators import login_required
import datetime
import operator



@login_required  # 外观信息采集岗位
def numbering(request):
    nickName = gsUser.objects.get(user=request.user)
    return render(request, 'n.html', context={'operator': nickName, })


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
        ret['producerPlace'] = thing.producerPlace
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
        ret['producerPlace'] = thing.producerPlace
        ret['remark'] = thing.remark
        ret['quality'] = thing.quality
        ret['level'] = thing.level
    elif (0 == cmp(productType, u'银元类')):
        thing = gsYinYuan.objects.get(box=box, serialNumber=serialNumber)
        ret['versionName'] = thing.versionName
        ret['value'] = thing.value
        ret['producerPlace'] = thing.producerPlace
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


def updateNumberingInfo(request):
    serialNumber = request.POST.get('serialNumber', '')
    boxOrSubBox = request.POST.get('boxNumber', '')
    productType = request.POST.get('productType', '')
    detailedName = request.POST.get('detailedName', '')
    typeName = request.POST.get('typeName', '')
    peroid = request.POST.get('peroid', '')
    producerPlace = request.POST.get('producerPlace', '')
    carveName = request.POST.get('carveName', '')
    originalQuantity = request.POST.get('originalQuantity', '')
    versionName = request.POST.get('versionName', '')
    value = request.POST.get('value', '')
    quality = request.POST.get('quality', '')
    level = request.POST.get('level', '')
    remark = request.POST.get('remark', '')
    operator = request.POST.get('operator', '')
    workSeq = request.POST.get('workSeq', '')

    if originalQuantity != '':
        originalQuantity = float(originalQuantity)

    if '-' in boxOrSubBox:
        boxNumber = int(boxOrSubBox.split('-')[0])
        subBoxNumber = int(boxOrSubBox.split('-')[1])
    else:
        boxNumber = int(boxOrSubBox)
        subBoxNumber = ''

    box = gsBox.objects.get(boxNumber=boxNumber)
    workSeq = int(workSeq)
    if subBoxNumber == '':
        work = gsWork.objects.get(box=box, workSeq=workSeq)
    else:
        subBox = gsSubBox.objects.get(box=box,subBoxNumber=subBoxNumber)
        work = gsWork.objects.get(box=box, workSeq=workSeq,subBox=subBox)
    thing_set = gsThing.objects.filter(work=work)
    thing = gsThing.objects.get(serialNumber=serialNumber)
    ret = {}
    try:
        if productType == u'金银锭类':
            if serialNumber == '':
                gsDing.objects.filter(thing__in=thing_set).update(detailedName=detailedName,
                                                                  typeName=typeName,
                                                                  peroid=peroid,
                                                                  producerPlace=producerPlace,
                                                                  carveName=carveName,
                                                                  originalQuantity=originalQuantity,
                                                                  quality=quality,
                                                                  level=level,
                                                                  remark=remark)
            else:
                gsDing.objects.filter(thing=thing).update(detailedName=detailedName,
                                                          typeName=typeName,
                                                          peroid=peroid,
                                                          producerPlace=producerPlace,
                                                          carveName=carveName,
                                                          originalQuantity=originalQuantity,
                                                          quality=quality,
                                                          level=level,
                                                          remark=remark)
        elif productType == u'金银币章类':
            if serialNumber == '':
                gsBiZhang.objects.filter(thing__in=thing_set).update(detailedName=detailedName,
                                                                     peroid=peroid,
                                                                     producerPlace=producerPlace,
                                                                     originalQuantity=originalQuantity,
                                                                     quality=quality,
                                                                     level=level,
                                                                     versionName=versionName,
                                                                     remark=remark)
            else:
                gsBiZhang.objects.filter(thing=thing).update(detailedName=detailedName,
                                                                                    peroid=peroid,
                                                                                    producerPlace=producerPlace,
                                                                                    originalQuantity=originalQuantity,
                                                                                    quality=quality, level=level,
                                                                                    versionName=versionName,
                                                                                    remark=remark)
        elif productType == u'银元类':
            if serialNumber == '':
                gsYinYuan.objects.filter(thing__in=thing_set).update(producerPlace=producerPlace,
                                                                     quality=quality,
                                                                     level=level,
                                                                     versionName=versionName,
                                                                     value=value,
                                                                     remark=remark)
            else:
                gsYinYuan.objects.filter(thing=thing).update(producerPlace=producerPlace,
                                                             quality=quality,
                                                             level=level,
                                                             versionName=versionName,
                                                             value=value,
                                                             remark=remark)
        elif productType == u'金银工艺品类':
            if serialNumber == '':
                gsGongYiPin.objects.filter(thing__in=thing_set).update(detailedName=detailedName,
                                                                       peroid=peroid,
                                                                       originalQuantity=originalQuantity,
                                                                       quality=quality,
                                                                       level=level,
                                                                       remark=remark)
            else:
                gsGongYiPin.objects.filter(thing=thing).update(detailedName=detailedName,
                                                               peroid=peroid,
                                                               originalQuantity=originalQuantity,
                                                               quality=quality,
                                                               level=level,
                                                               remark=remark)
        # now是本地时间，可以认为是你电脑现在的时间 utcnow是世界时间（时区不同，所以这两个是不一样的）
        # now = datetime.datetime.utcnow()  # 这里使用utcnow生成时间,存入mariaDB后被数据库当做非UTC时间,自动减去了8个小时,所以这里改用now
        now = datetime.datetime.now()
        if serialNumber == '':
            gsStatus.objects.filter(thing__in=thing_set).update(numberingStatus=True,
                                                                numberingOperator=operator,
                                                                numberingUpdateDateTime=now)
        else:
            gsStatus.objects.filter(thing=thing).update(numberingStatus=True,
                                                        numberingOperator=operator,
                                                        numberingUpdateDateTime=now)

        s = gsStatus.objects.get(thing=thing)
        status = s.numberingStatus and s.analyzingStatus and s.measuringStatus and s.photographingStatus and s.checkingStatus
        gsStatus.objects.filter(thing=thing).update(status=status)
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
        things = gsDing.objects.values_list(key, flat=True)
    elif productType == u'银元类':
        things = gsDing.objects.values_list(key, flat=True)
    elif productType == u'金银工艺品类':
        things = gsDing.objects.values_list(key, flat=True)

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