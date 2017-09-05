# encoding=UTF-8
from django.shortcuts import render
from django.http.response import HttpResponse
import json
from .report_process import *
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone


@login_required
def checking(request):
    nickName = gsUser.objects.get(user=request.user)
    return render(request, 'c.html', context={'operator': nickName, })


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


'''def createWork(request):
    productTypeCode = request.POST.get('productType', '')
    classNameCode = request.POST.get('className', '')
    subClassNameCode = request.POST.get('subClassName', '')
    wareHouseCode = request.POST.get('wareHouse', '')
    boxNumber = int(request.POST.get('boxNumber', ''))
    amount = int(request.POST.get('amount', ''))
    startSeq = int(request.POST.get('startSeq', ''))
    operator = request.POST.get('operator', '')

    try:
        box, created = gsBox.objects.createWork(boxNumber = boxNumber, productType = productTypeCode, className = classNameCode, subClassName = subClassNameCode, wareHouse = wareHouseCode, amount = amount, startSeq = startSeq, operator = operator)

        # 创建作业对应的以箱号命名的结果目录
        reportRootDir = settings.DATA_DIRS['report_dir']
        reportDir = os.path.join(reportRootDir, str(boxNumber))
        if (not os.path.exists(reportDir)):
            os.mkdir(reportDir)
    except Exception as e:
        ret = {
            "success": False,
            "message": str(boxNumber)+u'号箱作业创建失败！\r\n原因:'+e.message
        }
    else:
        ret = {
            'success': True,
            'message': str(boxNumber)+'号箱作业创建成功！' 
        }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)

def deleteWork(request):
    boxNumber = int(request.POST.get('boxNumber', ''))
    subBoxSeq = request.POST.get('subBoxSeq', '')

    try:
        deleted = gsBox.objects.deleteWork(boxNumber = boxNumber)

        # 删除作业对应的以箱号命名的结果目录和压缩文件
        reportRootDir = settings.DATA_DIRS['report_dir']
        reportDir = os.path.join(reportRootDir, str(boxNumber))
        if (os.path.exists(reportDir)):
            deleteDir(reportDir)

        zipFilePath = os.path.join(reportRootDir, str(boxNumber)+'.zip')
        if (os.path.exists(zipFilePath)):
            os.remove(zipFilePath)

        tagRootDir = settings.DATA_DIRS['tag_dir']
        tagFilePath = os.path.join(tagRootDir, str(boxNumber)+'.zip')
        if (os.path.exists(tagFilePath)):
            os.remove(tagFilePath)
    except Exception as e:
        ret = {
            "success": False,
            "message": str(boxNumber)+u'号箱作业归档失败！\r\n原因:'+e.message
        }
    else:
        ret = {
            "success": True,
            "message": str(boxNumber)+'号箱作业删除成功！' 
        }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)'''


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


# def updateCheckingInfo(request):
#     serialNumber = request.POST.get('serialNumber', '')
#     operator = request.POST.get('operator', '')
#
#     try:
#         # 检测作业是否可用
#         thing = gsThing.objects.get(serialNumber=serialNumber)
#         thing_status = gsStatus.objects.get(thing=thing)
#         if thing_status.status == 0:
#             # 作业不可用
#             raise ValueError(u'作业不可用！请联系现场负责人进行分发，并刷新页面！')
#
#         # now = datetime.utcnow()  # 这里使用utcnow生成时间,存入mariaDB后被数据库当做非UTC时间,自动减去了8个小时,所以这里改用now
#         now = datetime.now()
#         gsStatus.objects.filter(thing=thing).update(checkingStatus=True, checkingOperator=operator,
#                                                                   checkingUpdateDateTime=now)
#     except Exception as e:
#         ret = {
#             'success': False,
#             'message': u'复核失败！\n原因: {0}'.format(e.message)
#         }
#     else:
#         ret = {
#             'success': True,
#             'message': u'实物{0}复核通过！\n审核员: {1}'.format(serialNumber, operator)
#         }
#
#     ret_json = json.dumps(ret, separators=(',', ':'))
#
#     return HttpResponse(ret_json)
def updateCheckingInfo(request):
    serialNumber = request.POST.get('serialNumber', '')
    boxOrSubBox = request.POST.get('boxNumber', '')
    productType = request.POST.get('productType', '')
    className = request.POST.get('className', '')
    subClassName = request.POST.get('subClassName', '')
    wareHouse = request.POST.get('wareHouse', '')
    detailedName = request.POST.get('detailedName', '')
    typeName = request.POST.get('typeName', '')
    peroid = request.POST.get('peroid', '')
    producerPlace = request.POST.get('producerPlace', '')
    carveName = request.POST.get('carveName', '')
    originalQuantity = request.POST.get('originalQuantity', '')
    versionName = request.POST.get('versionName', '')
    value = request.POST.get('value', '')
    marginShape = request.POST.get('marginShape', '')
    quality = request.POST.get('quality', '')
    level = request.POST.get('level', '')
    remark = request.POST.get('remark', '')
    operator = request.POST.get('operator', '')
    if originalQuantity != '':
        originalQuantity = float(originalQuantity)

    if '-' in boxOrSubBox:
        boxNumber = int(boxOrSubBox.split('-')[0])
        subBoxNumber = int(boxOrSubBox.split('-')[1])
    else:
        boxNumber = int(boxOrSubBox)
        subBoxNumber = ''

    thing_set = gsThing.objects.filter(serialNumber=serialNumber)
    ret = {}
    try:
        if productType == u'金银锭类':
            gsDing.objects.filter(thing__in=thing_set).update(detailedName=detailedName,
                                                      typeName=typeName,
                                                      peroid=peroid,
                                                      producerPlace=producerPlace,
                                                      carveName=carveName,
                                                      originalQuantity=originalQuantity,
                                                      quality=quality,
                                                      level=level,
                                                      remark=remark)
        elif productType == u'金银币章类':
            gsBiZhang.objects.filter(thing__in=thing_set).update(detailedName=detailedName,
                                                                                peroid=peroid,
                                                                                producerPlace=producerPlace,
                                                                                originalQuantity=originalQuantity,
                                                                                quality=quality, level=level,
                                                                                versionName=versionName,
                                                                                remark=remark)
        elif productType == u'银元类':
            gsYinYuan.objects.filter(thing__in=thing_set).update(producerPlace=producerPlace,
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
        now = datetime.datetime.now()
        gsStatus.objects.filter(thing__in=thing_set).update(numberingStatus=True,numberingOperator=operator,numberingUpdateDateTime=now)

        s = gsStatus.objects.get(thing=thing_set[0])
        status = s.numberingStatus and s.analyzingStatus and s.measuringStatus and s.photographingStatus and s.checkingStatus
        gsStatus.objects.filter(thing=thing_set[0]).update(status=status)
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


def getThingData(request):
    boxNumber = request.GET.get('boxNumber', '')
    serialNumber = request.GET.get('serialNumber', '')

    box = gsBox.objects.get(boxNumber=boxNumber)

    ret = {}
    ret['serialNumber'] = serialNumber
    ret['boxNumber'] = boxNumber

    productTypeCode = box.productType
    productType = gsProperty.objects.get(project='实物类型', code=productTypeCode)
    ret['productType'] = productType.type
    wareHouseCode = box.wareHouse
    wareHouse = gsProperty.objects.get(project='发行库', code=wareHouseCode)
    ret['wareHouse'] = wareHouse.type
    classNameCode = box.className
    className = gsProperty.objects.get(project='品名', code=classNameCode, parentProject=productType.project,
                                       parentType=productType.type)
    ret['className'] = className.type
    subClassNameCode = box.subClassName
    subClassName = gsProperty.objects.get(project='明细品名', code=subClassNameCode, parentProject=className.project,
                                          parentType=className.type, grandpaProject=productType.project,
                                          grandpaType=productType.type)
    ret['subClassName'] = subClassName.type

    if (0 == cmp(productType.type, u'金银锭类')):
        thing = gsDing.objects.get(box=box, serialNumber=serialNumber)
        ret['detailedName'] = thing.detailedName
        ret['typeName'] = thing.typeName
        ret['peroid'] = thing.peroid
        ret['producerPlace'] = thing.producerPlace
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

    elif (0 == cmp(productType.type, u'金银币章类')):
        thing = gsBiZhang.objects.get(box=box, serialNumber=serialNumber)
        ret['detailedName'] = thing.detailedName
        ret['versionName'] = thing.versionName
        ret['peroid'] = thing.peroid
        ret['producerPlace'] = thing.producerPlace
        ret['value'] = thing.value
        ret['remark'] = thing.remark
        ret['quality'] = thing.quality
        ret['level'] = thing.level
        ret['originalQuantity'] = thing.originalQuantity if (thing.originalQuantity is not None) else ''
        ret['detectedQuantity'] = thing.detectedQuantity if (thing.detectedQuantity is not None) else ''
        ret['diameter'] = thing.diameter if (thing.diameter is not None) else ''
        ret['thick'] = thing.thick if (thing.thick is not None) else ''
        ret['grossWeight'] = thing.grossWeight if (thing.grossWeight is not None) else ''
        ret['pureWeight'] = thing.pureWeight if (thing.pureWeight is not None) else ''

    elif (0 == cmp(productType.type, u'银元类')):
        thing = gsYinYuan.objects.get(box=box, serialNumber=serialNumber)
        ret['detailedName'] = thing.detailedName
        ret['versionName'] = thing.versionName
        ret['peroid'] = thing.peroid
        ret['producerPlace'] = thing.producerPlace
        ret['value'] = thing.value
        ret['marginShape'] = thing.marginShape
        ret['remark'] = thing.remark
        ret['quality'] = thing.quality
        ret['level'] = thing.level
        ret['originalQuantity'] = thing.originalQuantity if (thing.originalQuantity is not None) else ''
        ret['detectedQuantity'] = thing.detectedQuantity if (thing.detectedQuantity is not None) else ''
        ret['diameter'] = thing.diameter if (thing.diameter is not None) else ''
        ret['thick'] = thing.thick if (thing.thick is not None) else ''
        ret['grossWeight'] = thing.grossWeight if (thing.grossWeight is not None) else ''
        ret['pureWeight'] = thing.pureWeight if (thing.pureWeight is not None) else ''

    elif (0 == cmp(productType.type, u'金银工艺品类')):
        thing = gsGongYiPin.objects.get(box=box, serialNumber=serialNumber)
        ret['detailedName'] = thing.detailedName
        ret['peroid'] = thing.peroid
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
    producerPlace = request.POST.get('producerPlace', '')
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
        thing_status = gsStatus.objects.get(thing=thing)
        if thing_status.status == 0:
            # 作业不可用
            raise ValueError(u'作业不可用！请联系现场负责人进行分发！')

        if productType == u'金银锭类':
            gsDing.objects.filter(thing=thing).update(detailedName=detailedName,
                                                      typeName=typeName, peroid=peroid,
                                                     producerPlace=producerPlace,
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
                                                        producerPlace=producerPlace,
                                                        originalQuantity=originalQuantity,
                                                        quality=quality, level=level,
                                                        versionName=versionName, remark=remark,
                                                        detectedQuantity=detectedQuantity,
                                                        diameter=diameter, thick=thick,
                                                        grossWeight=grossWeight, value=value)
        elif productType == u'银元类':
            gsYinYuan.objects.filter(thing=thing).update(marginShape=marginShape,
                                                         peroid=peroid,
                                                        producerPlace=producerPlace,
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
