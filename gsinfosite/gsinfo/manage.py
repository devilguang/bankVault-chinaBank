# encoding=UTF-8
import shutil
from django.shortcuts import render
from django.http.response import HttpResponse, StreamingHttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from utils import readFile, dateTimeHandler
from tag_process import createQRCode
from .report_process import *
from gsinfosite import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import datetime
from . import log
import MySQLdb
import win32print
import win32api
import win32ui
from PIL import Image, ImageWin
import shortuuid
from gsinfosite import settings
from django.db.models import Q
import random
from webServiceAPI import *

@login_required
def manage(request):
    userName = gsUser.objects.get(user=request.user)
    return render(request, 'manage.html', context={'operator': userName, })

def openOrigBox(request):
    origBoxNumber = request.POST.get('origBoxNumber', '')
    amount = request.POST.get('thingAmount', '')
    grossWeight = request.POST.get('grossWeight', '')

    if amount:
        amount = int(amount)
    else:
        amount =None
    if grossWeight:
        grossWeight = float(grossWeight)
    else:
        grossWeight =None

    try:
        log.log(user=request.user, operationType=u'业务操作', content=u'对{0}号箱开箱操作'.format(origBoxNumber))
        gsOrigBox.objects.create(origBoxNumber=origBoxNumber,
                                 amount=amount,
                                 grossWeight=grossWeight)
    except Exception as e:
        ret = {
            "success": False,
            "message": '开箱失败！'
        }
    else:
        ret = {
            'success': True,
            'message': '开箱成功！'
        }
    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)

def checkAmount(request):
    amount = int(request.POST.get('amount', ''))  # 件数
    origBoxNumber = request.POST.get('origBoxNumber', '') # 原箱号
    # ---检验新建箱中数量与原始箱数量是否匹配---
    try:
        origBox = gsOrigBox.objects.get(origBoxNumber=origBoxNumber)
        all_amount = origBox.amount
        box_amount = sum(list(gsBox.objects.filter(origBox=origBox).values_list('amount', flat=True))) + int(amount)
        dif = all_amount - box_amount
        if dif >= 0:
            ret = {
                'success': True,
            }
        else:
            ret = {
                'success': False,
                'message': '件数超过原箱件数，新建箱失败成功！'
            }
    except Exception as e:
        ret = {
            'success': False,
            'message': '原箱号错误！'
        }
    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)
# ------------------------------------



def createBox(request):
    productType = request.POST.get('productType', '')  # 类型
    className = request.POST.get('className', '')  # 品类
    subClassName = request.POST.get('subClassName', '')  # 品名
    wareHouse = request.POST.get('wareHouse', '')  # 发行库
    amount = int(request.POST.get('amount', ''))  # 件数
    grossWeight = request.POST.get('grossWeight', '')  # 毛重
    oprateType = request.POST.get('oprateType', '')  # 操作类型
    origBoxNumber = request.POST.get('origBoxNumber', '') # 原箱号

    if grossWeight:
        grossWeight = float(grossWeight)
    else:
        grossWeight = None
    # 向货发二代系统请求箱号
    # code = '1|{0}|{1}|{2}'.format(wareHouse,productType,className)
    # boxNumber = getNumberAPI(code)
    # -----模拟
    seq = random.randint(1, 100)
    boxNumber = '1-{0}-{1}-{2}-{3}'.format(wareHouse, productType, className, seq)

    try:
        log.log(user=request.user, operationType=u'业务操作', content=u'新建{0}号箱实物'.format(boxNumber))
        gsBox.objects.createBox(boxNumber=boxNumber,
                                productType=productType,
                                className=className,
                                subClassName=subClassName,
                                wareHouse=wareHouse,
                                amount=amount,
                                grossWeight=grossWeight,
                                oprateType=oprateType,
                                origBoxNumber=origBoxNumber)
    except Exception as e:
        ret = {
            "success": False,
            "message": '{0}号箱新建失败！'.format(boxNumber)
        }
    else:
        ret = {
            'success': True,
            'message': '{0}号箱新建成功!'.format(boxNumber)
        }
    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


# -----------------------------------------------
# 封箱入库 和 开箱出库
def boxInOutStore(request):
    boxNumber = request.POST.get('boxNumber', '')
    status = int(request.POST.get('status', ''))  # 1: 封箱入库 0: 提取出库

    if status == 1:
        box = gsBox.objects.get(boxNumber=boxNumber)
        try:
            log.log(user=request.user, operationType=u'业务操作', content=u'封箱入库')
            if gsWork.objects.filter(box=box, status=1).exists():  # 存在作业未收回, 不能封箱入库
                raise ValueError(u'{0}号箱存在作业未收回，不能封箱入库！请前往:业务管理->作业管理，收回作业！'.format(boxNumber))
            gsBox.objects.filter(boxNumber=boxNumber).update(status=True)
        except Exception as e:
            ret = {
                "success": False,
                "message": '{0}号箱实物封箱入库失败！'.format(boxNumber)
            }
        else:
            ret = {
                'success': True,
                'message': '{0}号箱实物封箱入库成功!'.format(boxNumber)
            }
    elif status == 0:
        try:
            log.log(user=request.user, operationType=u'业务操作', content=u'开箱出库')
            gsBox.objects.filter(boxNumber=boxNumber).update(status=False)
        except Exception as e:
            ret = {
                "success": False,
                "message": '{0}号箱实物封箱入库失败！'.format(boxNumber)
            }
        else:
            ret = {
                'success': True,
                'message': '{0}号箱实物封箱入库成功!'.format(boxNumber)
            }
    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)
# -----------------------------------------------
# 原来的并箱操作
def addToExistingBox(request):
    boxOrSubBox = request.POST.get('boxNumber', '')
    amount = int(request.POST.get('amount', ''))
    startSeq = int(request.POST.get('startSeq', ''))

    if '-' in boxOrSubBox:
        boxNumber = int(boxOrSubBox.split('-')[0])
        subBoxNumber = int(boxOrSubBox.split('-')[1])
    else:
        boxNumber = int(boxOrSubBox)
        subBoxNumber = ''

    try:
        box = gsBox.objects.get(boxNumber=boxNumber)
        productType = box.productType
        className = box.className
        subClassName = box.subClassName
        wareHouse = box.wareHouse

        log.log(user=request.user, operationType=u'业务操作', content=u'对{0}号箱并箱操作'.format(boxNumber))
        (box, added) = gsBox.objects.addToExistingBox(boxNumber=boxNumber, productType=productType, className=className,
                                                      subClassName=subClassName, wareHouse=wareHouse, amount=amount,
                                                      startSeq=startSeq, subBoxNumber=subBoxNumber)

        # 构造对应的存储目录结构
        boxRootDir = settings.DATA_DIRS['box_dir']
        boxDir = os.path.join(boxRootDir, str(boxNumber))
        if (not os.path.exists(boxDir)):
            os.mkdir(boxDir)

        subBoxSeq = gsThing.objects.filter(box=box).order_by('-subBoxSeq').first().subBoxSeq
        now = datetime.datetime.now()
        wareHouseCode = box.wareHouse
        wareHouse = gsProperty.objects.get(project='发行库', code=wareHouseCode)
        wordDir = os.path.join(boxDir, u'{0}_{1}_{2}_word'.format(now.year, subBoxSeq, wareHouse.type))
        if (not os.path.exists(wordDir)):
            os.mkdir(wordDir)

        photoDir = os.path.join(boxDir, u'{0}_{1}_{2}_photo'.format(now.year, subBoxSeq, wareHouse.type))
        if (not os.path.exists(photoDir)):
            os.mkdir(photoDir)

    except Exception as e:
        ret = {
            "success": False,
            "message": '{0}号箱实物新建失败！\r\n原因：{1}'.format(boxNumber, e.message)
        }
    else:
        ret = {
            'success': True,
            'message': '{0}号箱实物新建成功!'.format(boxNumber)
        }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def deleteBox(request):
    boxNumber = request.POST.get('boxNumber', '')

    try:
        gsBox.objects.deleteBox(boxNumber=boxNumber)
        boxDir = os.path.join(settings.BOX_DATA_PATH, str(boxNumber))
        if os.path.exists(boxDir):
            shutil.rmtree(boxDir)

    except Exception as e:
        ret = {
            "success": False,
            "message": '{0}号箱实物删除失败！\r\n原因：{1}'.format(boxNumber, e.message)
        }
    else:
        ret = {
            'success': True,
            'message': '{0}号箱实物删除成功!'.format(boxNumber)
        }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def getBox(request):
    pageSize = request.POST.get('rows', '')
    page = request.POST.get('page', '')
    productType = request.POST.get('productType', '')
    className = request.POST.get('className', '')
    subClassName = request.POST.get('subClassName', '')
    status = int(request.POST.get('status', ''))  # 1: 已入库 0: 未入库

    if status == 0:
        box_qs = gsBox.objects.filter(status=0)
    else:
        box_qs = gsBox.objects.filter(status=1)
    selectBox = []
    for box in box_qs:
        prop = box.boxType
        code = prop.code
        parentCode = prop.parentCode
        grandpaCode=prop.grandpaCode
        code_match = [i for i in [grandpaCode, parentCode, code] if i]
        code_query = [i for i in [productType,className,subClassName] if i]
        str_match = '-'.join(code_match)
        str_query = '-'.join(code_query)
        if str_query in str_match:
            selectBox.append(box)

    n = len(selectBox)

    pageSize = int(pageSize)
    page = int(page)
    start = (page - 1) * pageSize
    end = n if (page * pageSize > n) else page * pageSize

    ret = {}
    ret['total'] = n
    ret['rows'] = []
    for box in selectBox[start:end]:
        r = {}
        prop = box.boxType
        r['boxNumber'] = box.boxNumber
        if prop.grandpaType:
            r['productType'] = prop.grandpaType
            r['className'] = prop.parentType
            r['subClassName'] = prop.type
        else:
            r['productType'] = prop.parentType
            r['className'] = prop.type
            r['subClassName'] = '-'
        wareHouse = gsProperty.objects.get(project='发行库', code=box.wareHouse)
        r['wareHouse'] = wareHouse.type
        r['amount'] = box.amount
        r['oprateType'] = box.oprateType.type
        ret['rows'].append(r)
    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)
    return HttpResponse(ret_json)


def getThing(request):
    boxNumber = request.POST.get('boxNumber', '')
    pageSize = request.POST.get('rows', '')
    page = request.POST.get('page', '')
    isAllocated = request.POST.get('thingIsAllocated', '')
    box = gsBox.objects.get(boxNumber=boxNumber)
    oprateType_code = box.oprateType.code
    if isAllocated == 'notAllocated':
        if oprateType_code == '2':
            ts = gsThing.objects.filter(box=box, isAllocate=False,amount=1)
        else:
            ts = gsThing.objects.filter(box=box, isAllocate=False)
    elif isAllocated == 'allocated':
        if oprateType_code == '2':
            ts = gsThing.objects.filter(box=box, isAllocate=True,amount=1)
        else:
            ts = gsThing.objects.filter(box=box, isAllocate=True)
    else:  # 这是什么情况触发！
        if oprateType_code == '2':
            ts = gsThing.objects.filter(box=box, amount=1)
        else:
            ts = gsThing.objects.filter(box=box)

    ret = {}
    n = ts.count()
    ret['total'] = n

    pageSize = int(pageSize)
    page = int(page)
    start = (page - 1) * pageSize
    end = n if (page * pageSize > n) else page * pageSize

    ret['rows'] = []
    boxType = box.boxType
    grandpaType = boxType.grandpaType
    parentType = boxType.parentType
    type = boxType.type
    if grandpaType:
        productType = boxType.grandpaType
        className = boxType.parentType
        subClassName = boxType.type
    else:
        productType = boxType.parentType
        className = boxType.type
        subClassName = '-'
    for t in ts[start:end]:
        r = {}
        r['serialNumber'] = t.serialNumber
        r['boxNumber'] = boxNumber
        r['productType'] = productType
        r['className'] = className
        r['subClassName'] = subClassName
        wareHouse = gsProperty.objects.get(project='发行库', code=box.wareHouse)
        r['wareHouse'] = wareHouse.type
        ret['rows'].append(r)
    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)
    return HttpResponse(ret_json)


def generateWorkName(request):
    boxNumber = request.GET.get('boxNumber', '')

    box = gsBox.objects.get(boxNumber=boxNumber)
    ws = gsWork.objects.filter(box=box).order_by('-workSeq').first()
    if ws:
        workSeq = ws.workSeq + 1
    else:
        workSeq = 1
    workName = u'{0}号箱作业{1}'.format(boxNumber, workSeq)
    ret = {
        'workName': workName,
    }
    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def generateContentForWork(request):
    boxNumber = request.POST.get('boxNumber', '')
    amount = request.POST.get('amount', '')

    if amount:
        amount = int(amount)
    else:
        amount = 0

    box = gsBox.objects.get(boxNumber=boxNumber)
    oprateType_code = box.oprateType.code
    if oprateType_code == '2':
        specialSerialNumberList = gsThing.objects.filter(box=box, isAllocate=False,amount=1).values_list('serialNumber', flat=True)
    else:
        specialSerialNumberList = gsThing.objects.filter(box=box, isAllocate=False).values_list('serialNumber', flat=True)

    ret = {}
    ret['data'] = []
    for serialNumber in specialSerialNumberList[:amount]:
        r = {}
        r['serialNumber'] = serialNumber
        ret['data'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)


def createWork(request):
    boxNumber = request.POST.get('boxNumber', '')
    workName = request.POST.get('workName', '')
    selectedThings = request.POST.get('selectedThings', '')
    thingSet = selectedThings.split(';')[:-1]
    try:
        user = request.user
        log.log(user=user, operationType=u'业务操作', content=u'创建{0}'.format(workName))
        user_obj = gsUser.objects.get(user=user)
        gsWork.objects.createWork(user=user_obj,
                                  workName=workName,
                                  boxNumber=boxNumber,
                                  thingSet=thingSet)
    except Exception as e:
        ret = {
            'success': False,
            'message': u'{0}创建失败！\n原因:{1}'.format(workName, e.message),
        }
    else:
        ret = {
            'success': True,
            'message': u'{0}创建成功！'.format(workName),
        }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def deleteWork(request):
    boxNumber = request.POST.get('boxNumber', '')
    workSeq = request.POST.get('workSeq', '')
    workName = request.POST.get('workName', '')

    try:
        gsWork.objects.deleteWork(boxNumber=boxNumber, workSeq=workSeq)
    except Exception as e:
        ret = {
            'success': False,
            'message': u'{0}删除失败！\n原因:{1}'.format(workName, e.message),
        }
    else:
        ret = {
            'success': True,
            'message': u'{0}删除成功！'.format(workName),
        }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def getWork(request):
    pageSize = request.POST.get('rows', '')
    page = request.POST.get('page', '')
    productType = request.POST.get('productType', '')
    className = request.POST.get('className', '')
    subClassName = request.POST.get('subClassName', '')
    status = int(request.POST.get('status', ''))  # 1: 已入库 0: 未入库

    box_qs = gsBox.objects.filter(status=status)
    # 筛选符合条件的box
    selectBox = []
    for box in box_qs:
        prop = box.boxType
        code = prop.code
        parentCode = prop.parentCode
        grandpaCode = prop.grandpaCode
        code_match = [i for i in [grandpaCode, parentCode, code] if i]
        code_query = [i for i in [productType, className, subClassName] if i]
        str_match = '-'.join(code_match)
        str_query = '-'.join(code_query)
        if str_query in str_match:
            selectBox.append(box)

    work_set = gsWork.objects.filter(box__in=selectBox)
    n = work_set.count()
    pageSize = int(pageSize)
    page = int(page)
    start = (page - 1) * pageSize
    end = n if (page * pageSize > n) else page * pageSize

    ret = {}
    ret['total'] = n
    ret['rows'] = []
    for work in work_set[start:end]:
        r = {}
        r['id'] = work.id
        r['workName'] = work.workName
        r['workSeq'] = work.workSeq
        r['boxNumber'] = work.box.boxNumber
        r['createDateTime'] = work.createDateTime
        r['completeDateTime'] = work.completeDateTime if work.completeDateTime is not None else ''
        r['status'] = work.status
        work_thing = gsThing.objects.filter(work=work)
        r['amount'] = work_thing.count()
        ss = gsStatus.objects.filter(thing__in=work_thing)
        # r['checkingCompleteAmount'] = ss.filter(checkingStatus=True).count()
        # r['numberingCompleteAmount'] = ss.filter(numberingStatus=True).count()
        # r['analyzingCompleteAmount'] = ss.filter(analyzingStatus=True).count()
        # r['measuringCompleteAmount'] = ss.filter(measuringStatus=True).count()
        # r['photographingCompleteAmount'] = ss.filter(photographingStatus=True).count()

        r['completePercent'] = float('%0.2f' % (ss.filter(status=True).count() * 100 / ss.count())) if (
            0 != ss.count()) else 0
        ret['rows'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)


def startOrStopWork(request):
    boxNumber = request.POST.get('boxNumber', '')
    workSeq = request.POST.get('workSeq', '')
    workName = request.POST.get('workName', '')
    status = int(request.POST.get('status', ''))

    try:
        # status: 1:分发操作 0:收回操作
        box = gsBox.objects.get(boxNumber=boxNumber)
        work = gsWork.objects.get(box=box, workSeq=workSeq)
        gsWork.objects.filter(workSeq=workSeq, box=box).update(status=status)
        if status == 0:
            # 收回操作时, 检查作业是否完成. 若已完成, 则更新作业完成时间
            work_things = gsThing.objects.filter(work=work)
            status_set = gsStatus.objects.filter(thing__in=work_things, status=True)

            if work_things.count() == status_set.count():
                # 作业所属实物均清点查验完毕
                status_list = list(status_set.values_list('completeTime',flat=True))
                lastest_time = max(status_list)
                work.completeDateTime = lastest_time
                work.save(update_fields=['completeDateTime'])
    except Exception as e:
        ret = {
            'success': False,
            'message': u'{0}{1}失败！\n原因:{2}'.format(workName, u'收回' if (0 == status) else u'分发', e.message),
        }
    else:
        ret = {
            'success': True,
            'message': u'{0}{1}成功！'.format(workName, u'收回' if (0 == status) else u'分发'),
        }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def generateTag(request):
    if request.method == 'POST':
        boxNumber = int(request.POST.get('boxNumber', ''))
        workSeq = int(request.POST.get('workSeq', ''))
        subBoxNumber = request.POST.get('subBoxNumber', '')

        createTag(boxNumber, subBoxNumber, workSeq)

        box = gsBox.objects.get(boxNumber=boxNumber)
        if subBoxNumber:
            subBox = gsSubBox.objects.get(box=box, subBoxNumber=int(subBoxNumber))
            work = gsWork.objects.get(box=box, workSeq=workSeq, subBox=subBox)
        else:
            work = gsWork.objects.get(box=box, workSeq=workSeq)

        workName = work.workName
        fileName = u'{0}_标签.xlsx'.format(workName)
        tag_dir = os.path.join(settings.DATA_DIRS['tag_dir'], str(boxNumber))
        file_path = os.path.join(tag_dir, fileName)

        ret = {
            'success': True,
            # 'downloadURL': u'generateTag/?boxNumber={0}&subBoxNumber={1}&workSeq={2}'.format(boxNumber,subBoxNumber,workSeq),
            'file_path': file_path
        }
        log.log(user=request.user, operationType=u'业务操作', content=u'打印实物二维码')
        ret_json = json.dumps(ret, separators=(',', ':'))

        return HttpResponse(ret_json)
    elif request.method == 'GET':
        boxNumber = int(request.GET.get('boxNumber', ''))
        workSeq = int(request.GET.get('workSeq', ''))
        subBoxNumber = request.GET.get('subBoxNumber', '')

        box = gsBox.objects.get(boxNumber=boxNumber)
        if subBoxNumber:
            subBox = gsSubBox.objects.get(box=box, subBoxNumber=int(subBoxNumber))
            work = gsWork.objects.get(box=box, workSeq=workSeq, subBox=subBox)
        else:
            work = gsWork.objects.get(box=box, workSeq=workSeq)

        workName = work.workName
        fileName = u'{0}_标签.xlsx'.format(workName)
        tag_dir = os.path.join(settings.DATA_DIRS['tag_dir'], str(boxNumber))
        filePath = os.path.join(tag_dir, fileName)

        response = StreamingHttpResponse(readFile(filePath))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={0}'.format(fileName)

        return response


def generateAbstract(request):
    if request.method == 'POST':  # 生成实物信息摘要
        workName = request.POST.get('workName', '')
        boxNumber = request.POST.get('boxNumber', '')
        workSeq = request.POST.get('workSeq', '')
        subBoxNumber = request.POST.get('subBoxNumber', '')

        ret = createThingAbstract(workName, subBoxNumber, boxNumber, workSeq)

        ret_json = json.dumps(ret, separators=(',', ':'))

        return HttpResponse(ret_json)
    elif request.method == 'GET':  # 下载实物信息摘要
        boxNumber = int(request.GET.get('boxNumber', ''))
        workName = int(request.GET.get('workName', ''))

        fileName = u'{0}实物信息摘要.xlsx'.format(workName)
        boxDir = os.path.join(settings.DATA_DIRS['box_dir'], str(boxNumber))
        filePath = os.path.join(boxDir, fileName)

        response = StreamingHttpResponse(readFile(filePath))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={0}'.format(fileName)

        return response


def generateArchives(request):
    if (0 == cmp(request.method, 'POST')):
        boxNumber = int(request.POST.get('boxNumber', ''))
        workSeq = int(request.POST.get('workSeq', ''))
        dateTime = request.POST.get('dateTime', '')
        subBoxNumber = request.POST.get('subBoxNumber', '')

        createArchivesFromWork(boxNumber, subBoxNumber, workSeq, dateTime)  # 生成文件

        box = gsBox.objects.get(boxNumber=boxNumber)
        if subBoxNumber:
            subBox = gsSubBox.objects.get(box=box, subBoxNumber=int(subBoxNumber))
            work = gsWork.objects.get(box=box, workSeq=workSeq, subBox=subBox)
        else:
            work = gsWork.objects.get(box=box, workSeq=workSeq)

        workName = work.workName
        fileName = u'{0}_信息档案.zip'.format(workName)
        work_dir = os.path.join(settings.DATA_DIRS['work_dir'], str(boxNumber))
        file_path = os.path.join(work_dir, fileName)

        ret = {
            'success': True,
            # 'downloadURL': u'generateArchives/?boxNumber={0}&subBoxNumber={1}&workSeq={2}'.format(boxNumber,subBoxNumber,workSeq),
            'file_path': file_path,
        }
        log.log(user=request.user, operationType=u'业务操作', content=u'打印信息档案')
        ret_json = json.dumps(ret, separators=(',', ':'))

        return HttpResponse(ret_json)
    elif (0 == cmp(request.method, 'GET')):
        boxNumber = int(request.GET.get('boxNumber', ''))
        workSeq = int(request.GET.get('workSeq', ''))
        subBoxNumber = request.GET.get('subBoxNumber', '')

        box = gsBox.objects.get(boxNumber=boxNumber)
        if subBoxNumber:
            subBox = gsSubBox.objects.get(box=box, subBoxNumber=int(subBoxNumber))
            work = gsWork.objects.get(box=box, workSeq=workSeq, subBox=subBox)
        else:
            work = gsWork.objects.get(box=box, workSeq=workSeq)

        workName = work.workName
        fileName = u'{0}_信息档案.zip'.format(workName)
        work_dir = os.path.join(settings.DATA_DIRS['work_dir'], str(boxNumber))
        filePath = os.path.join(work_dir, fileName)

        response = StreamingHttpResponse(readFile(filePath))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={0}'.format(fileName)

        return response


def generateBoxInfo(request):
    if request.method == 'POST':
        boxNumber = request.POST.get('boxNumber', '')

        file_str = createBoxInfo(boxNumber=boxNumber)

        # downloadURL = ''
        # downloadURL = downloadURL + u'<a href="generateBoxInfo/?boxNumber={0}&boxInfoFileName={1}" style="margin-right:20px">{2}</a>'.format(
        #     boxNumber, boxInfoFileName, boxInfoFileName)
        ret = {
            'success': True,
            # 'downloadURL': downloadURL,
            'file_path': file_str,
        }
        log.log(user=request.user, operationType=u'业务操作', content=u'打印装箱清单')
        ret_json = json.dumps(ret, separators=(',', ':'))

        return HttpResponse(ret_json)
    elif request.method == 'GET':
        boxNumber = request.GET.get('boxNumber', '')
        fileName = request.GET.get('boxInfoFileName', '')

        box_dir = os.path.join(settings.DATA_DIRS['box_dir'], boxNumber)
        filePath = os.path.join(box_dir, fileName)

        response = StreamingHttpResponse(readFile(filePath))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={0}'.format(fileName)
        return response


def generateBoxInfoDetailedVersion(request):
    if request.method == 'POST':
        boxOrSubBox = request.POST.get('boxNumber', '')
        dateTime = request.POST.get('dateTime', '')
        if '-' in boxOrSubBox:
            boxNumber = boxOrSubBox.split('-')[0]
            subBoxNumber = boxOrSubBox.split('-')[1]
        else:
            boxNumber = int(boxOrSubBox)
            subBoxNumber = ''

        boxInfoFileName = createBoxInfoDetailedVersion(boxNumber, subBoxNumber, dateTime)

        box_dir = os.path.join(settings.DATA_DIRS['box_dir'], str(boxNumber))
        file_path = os.path.join(box_dir, boxInfoFileName)

        # downloadURL = ''
        # downloadURL = downloadURL + u'<a href="generateBoxInfoDetailedVersion/?boxNumber={0}&boxInfoFileName={1}" style="margin-right:20px">{2}</a>'.format(
        #     boxNumber, boxInfoFileName, boxInfoFileName)

        ret = {
            'success': True,
            # 'downloadURL': downloadURL,
            'file_path': file_path,
        }
        log.log(user=request.user, operationType=u'业务操作', content=u'打印装箱清单（详细版）')
        ret_json = json.dumps(ret, separators=(',', ':'))

        return HttpResponse(ret_json)
    elif request.method == 'GET':
        boxNumber = request.GET.get('boxNumber', '')
        fileName = request.GET.get('boxInfoFileName', '')

        box_dir = os.path.join(settings.DATA_DIRS['box_dir'], boxNumber)
        filePath = os.path.join(box_dir, fileName)

        response = StreamingHttpResponse(readFile(filePath))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={0}'.format(fileName)

        return response


def exploreBox(request):
    boxNumber = request.POST.get('boxNumber', '')
    pageSize = int(request.POST.get('rows', ''))
    page = int(request.POST.get('page', ''))

    box = gsBox.objects.get(boxNumber=boxNumber)
    prop = box.boxType
    type = prop.type
    parentType = prop.parentType
    grandpaType = prop.grandpaType

    wareHouseCode = box.wareHouse
    wareHouse = gsProperty.objects.get(project='发行库', code=wareHouseCode).type

    work_set = gsWork.objects.filter(box=box)
    work_serialNumberList = gsThing.objects.filter(work__in=work_set).values_list('serialNumber', flat=True)
    ts = gsThing.objects.filter(box=box)
    n = ts.count()

    start = (page - 1) * pageSize
    end = n if (page * pageSize > n) else page * pageSize

    ret = {}
    ret['total'] = n
    ret['rows'] = []
    for t in ts[start:end]:
        r = {}
        serialNumber = t.serialNumber
        r['serialNumber'] = serialNumber
        r['boxNumber'] = boxNumber
        if grandpaType:
            r['productType'] = grandpaType
            r['className'] = parentType
            r['subClassName'] = type
        else:
            r['productType'] = parentType
            r['className'] = type
            r['subClassName'] = '-'
        r['wareHouse'] = wareHouse
        if serialNumber in work_serialNumberList:
            r['workName'] = t.work.workName
            r['status'] = gsStatus.objects.get(thing=t).status
        else:
            r['workName'] = ''
            r['status'] = ''
        ret['rows'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)
    return HttpResponse(ret_json)


def advanceSearchHTML(request):
    return render(request, 'advancedSearch.html')


def advanceSearch(request):
    # type = request.POST.get('type', 'count')
    items = [{'sig': '', 'key': 'seq', 'symbol': '<', 'value': '10'},
             {'sig': 'or', 'key': 'seq', 'symbol': '>', 'value': '20'},
             {'sig': 'and', 'key': 'quality', 'symbol': '=', 'value': u'中'}]  # request.POST.get('items', '')
    table = 'gsinfo_gsding'  # request.POST.get('table', '')

    # 打开数据库连接
    database = settings.DATABASES['default']
    NAME = database['NAME']
    HOST = database['HOST']
    USER = database['USER']
    PASSWORD = database['PASSWORD']
    db = MySQLdb.connect(HOST, USER, PASSWORD, NAME, charset='utf8')

    cursor = db.cursor()
    sql = "SELECT * FROM {0} where ".format(table)
    for item in items:
        if item['sig']:
            sql = sql + " {0} {1} {2} '{3}'".format(item['sig'], item['key'], item['symbol'], item['value'])
        else:
            sql = sql + "{0} {1} '{2}'".format(item['key'], item['symbol'], item['value'])
    try:
        cursor.execute(sql)
        results = cursor.fetchall()

        ret = {
            'success': True,
            'results': results
        }
    except Exception, e:
        ret = {
            'success': False,
        }

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)


# 备份还原
def restore(request):
    date = '20170801'  # request.GET.get('date','')
    hardDir = settings.BASE_DIR  # settings.HARDDIR
    allZipFile = os.listdir(hardDir)
    zipFile = date + '.zip'
    if zipFile in allZipFile:
        try:
            tarPath = os.path.join(hardDir, zipFile)
            # 先解压缩
            f_zip = zipfile.ZipFile(tarPath, 'r')
            output_dir = settings.BASE_DIR
            f_zip.extractall(output_dir)

            sqlFile = os.path.join(output_dir, date, 'gsinfo.sql')
            dataFile = os.path.join(output_dir, date, 'data')

            # 运行sql文件
            database = settings.DATABASES['default']
            NAME = database['NAME']
            HOST = database['HOST']
            USER = database['USER']
            PASSWORD = database['PASSWORD']
            cmd_dump = r'mysql   -h%s -u%s -p%s -D%s < %s' % (HOST, USER, PASSWORD, NAME, sqlFile)
            os.system(cmd_dump)

            # 将原始data目录删除，将指定日期的data目录复制过去
            dataDir = os.path.join(settings.BASE_DIR, 'data')
            if os.path.exists(dataDir):
                shutil.rmtree(dataDir)

            shutil.copytree(dataFile, dataDir)

        except Exception, e:
            ret = {
                'success': False,
                'info': '恢复失败！，失败原因{0}'.format(e)
            }
        else:
            ret = {
                'success': True,
                'info': '恢复成功！'
            }
    else:
        ret = {
            'success': False,
            'info': '无该日期备份！'
        }
    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)


# --------------------------------------------------------------------------
def getStatusData(request):
    pageSize = int(request.POST.get('rows', ''))
    page = int(request.POST.get('page', ''))
    boxNumber = request.POST.get('boxNumber', '')
    workSeq = request.POST.get('workSeq', '')

    try:
        box = gsBox.objects.get(boxNumber=boxNumber)
        prop = box.boxType
        type = prop.type
        parentType = prop.parentType
        grandpaType = prop.grandpaType
        workSeq = int(workSeq)
        work = gsWork.objects.get(box=box, workSeq=workSeq)
        things = gsThing.objects.filter(work=work)
        thing_status_list = gsStatus.objects.filter(thing__in=things)

        n = thing_status_list.count()
        start = (page - 1) * pageSize
        end = n if (page * pageSize > n) else page * pageSize
        ret = {}
        ret['total'] = n
        ret['rows'] = []
        workStatus = 1
        for thing_status in thing_status_list[start:end]:
            r = {}
            r['serialNumber'] = thing_status.thing.serialNumber
            r['boxNumber'] = boxNumber
            if grandpaType:
                r['productType'] = grandpaType
                r['className'] = parentType
                r['subClassName'] = type
            else:
                r['productType'] = parentType
                r['className'] = type
                r['subClassName'] = '-'

            r['status1st'] = thing_status.numberingStatus
            if (thing_status.numberingStatus != 1):
                workStatus = 0
            r['operator1st'] = thing_status.numberingOperator
            r['updateDate1st'] = thing_status.numberingUpdateDateTime

            r['status2nd'] = thing_status.analyzingStatus
            if (thing_status.analyzingStatus != 1):
                workStatus = 0
            r['operator2nd'] = thing_status.analyzingOperator
            r['updateDate2nd'] = thing_status.analyzingUpdateDateTime

            r['status3rd'] = thing_status.measuringStatus
            if (thing_status.measuringStatus != 1):
                workStatus = 0
            r['operator3rd'] = thing_status.measuringOperator
            r['updateDate3rd'] = thing_status.measuringUpdateDateTime

            r['status4th'] = thing_status.checkingStatus
            if (thing_status.checkingStatus != 1):
                workStatus = 0
            r['operator4th'] = thing_status.checkingOperator
            r['updateDate4th'] = thing_status.checkingUpdateDateTime

            r['status5th'] = thing_status.photographingStatus
            if (thing_status.photographingStatus != 1):
                workStatus = 0
            r['operator5th'] = thing_status.photographingOperator
            r['updateDate5th'] = thing_status.photographingUpdateDateTime

            ret['rows'].append(r)
    except Exception as e:
        pass

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)


def print_service(request):
    filePath = request.POST.get('file_path', '')

    if '|' in filePath:
        file_path_list = filePath.split('|')
    else:
        file_path_list = []
        file_path_list.append(filePath)

    try:
        for file_path in file_path_list:
            print file_path_list
            print win32print.GetDefaultPrinter()
            # win32api.ShellExecute(None,"print",file_path,'/d:"%s"' % win32print.GetDefaultPrinter(),"\\",0)
    except Exception as e:
        ret = {
            'success': False,
            'message': u'打印失败！'
        }
    else:
        ret = {
            'success': True,
            'message': u'打印成功！'
        }
    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)
def print_pic(request):
    text_str = request.POST.get('text', '')
    text_list = text_str.split(';')
    try:
        for text in text_list:
            # 生成二维码图片
            file_path = createQRCode(text)
            # 开始打印
            # print_work(file_path)
            # 删除打印成功的二维码图片
            os.remove(file_path)
    except Exception as e:
        ret = {
            'success': False,
            'message': u'打印失败！'
        }
    else:
        ret = {
            'success': True,
            'message': u'打印成功！'
        }
    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)

def print_work(file_path):
    try:
        # HORZRES / VERTRES = printable area
        HORZRES = 8
        VERTRES = 10
        # LOGPIXELS = dots per inch
        LOGPIXELSX = 88
        LOGPIXELSY = 90
        # PHYSICALWIDTH/HEIGHT = total area
        PHYSICALWIDTH = 110
        PHYSICALHEIGHT = 111
        # PHYSICALOFFSETX/Y = left / top margin
        PHYSICALOFFSETX = 112
        PHYSICALOFFSETY = 113

        printer_name = win32print.GetDefaultPrinter()
        # Create a device context from a named printer and assess the printable size of the paper.
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        printable_area = hDC.GetDeviceCaps(HORZRES), hDC.GetDeviceCaps(VERTRES)
        printer_size = hDC.GetDeviceCaps(PHYSICALWIDTH), hDC.GetDeviceCaps(PHYSICALHEIGHT)
        printer_margins = hDC.GetDeviceCaps(PHYSICALOFFSETX), hDC.GetDeviceCaps(PHYSICALOFFSETY)

        bmp = Image.open(file_path, mode="r")

        if bmp.size[0] > bmp.size[1]:
            bmp = bmp.rotate(90)

        # Start the print job, and draw the bitmap to the printer device at the scaled size.
        hDC.StartDoc(file_path)
        hDC.StartPage()

        dib = ImageWin.Dib(bmp)
        scaled_width, scaled_height = [int(4 * i) for i in bmp.size]  # 对原始图片放大n倍
        x1 = int((printer_size[0] - scaled_width) / 4)
        y1 = int((printer_size[1] - scaled_height) / 4)
        x2 = x1 + scaled_width
        y2 = y1 + scaled_height
        dib.draw(hDC.GetHandleOutput(), (x1, y1, x2, y2))

        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()
    except Exception as e:
        pass

def print_auth(request):
    userName = request.POST.get('user', '')  # 系统负责人用户名
    password = request.POST.get('password', '')  # 系统负责人密码

    custom_user = gsUser.objects.filter(userName=userName,auth=1)
    if custom_user:
        username = custom_user[0].user.username
        user = auth.authenticate(username=username, password=password)
        if user:  # 通过系统管理员授权后先打印二维码后封箱入库
            ret = {
                "success": True,
            }
        else:
            ret = {
                "success": False,
                "message": u'密码错误！'
            }
    else:
        ret = {
            'success': False,
            'message': u'该用户无此权限！'
        }
    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)


def getCloseThing(request):
    boxNumber = request.POST.get('boxNumber', '')
    productType = request.POST.get('productType', '')
    className = request.POST.get('className', '')
    wareHouse = request.POST.get('wareHouse', '')  # 发行库
    pageSize = int(request.POST.get('rows', ''))
    page = int(request.POST.get('page', ''))

    try:
        box = gsBox.objects.get(boxNumber=boxNumber)
        works = gsWork.objects.filter(box=box)
        thing_set = gsThing.objects.filter(work__in=works)
        things = gsStatus.objects.filter(thing__in=thing_set, status=1, close_status=0)
        n = things.count()
        start = (page - 1) * pageSize
        end = n if (page * pageSize > n) else page * pageSize
        ret = {}
        ret['total'] = n
        ret['rows'] = []

        box = gsBox.objects.get(boxNumber=boxNumber)
        prop = box.boxType
        type = prop.type
        parentType = prop.parentType
        grandpaType = prop.grandpaType
        if grandpaType:
            productType = grandpaType
            className = parentType
            subClassName = type
        else:
            productType = parentType
            className = type
            subClassName = '-'
        for th in things[start:end]:
            r = {}
            r['serialNumber'] = th.thing.serialNumber
            r['productType'] = productType
            r['className'] = className
            r['subClassName'] = subClassName
            r['wareHouse'] = wareHouse
            r['boxNumber'] = boxNumber
            ret['rows'].append(r)
    except Exception as e:
        pass

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)


def closeThing(request):
    serialNumber = request.POST.get('serialNumber', '')
    boxNumber = request.POST.get('boxNumber', '')

    try:
        box = gsBox.objects.get(boxNumber=boxNumber)
        if gsThing.objects.filter(serialNumber=serialNumber,serialNumber2=None).exists():
            thing = gsThing.objects.get(serialNumber=serialNumber,serialNumber2=None)
            request_type = '4'
            wareHouse = box.wareHouse

            prop = box.boxType
            code = prop.code
            parentCode = prop.parentCode
            grandpaCode = prop.grandpaCode
            if grandpaCode:
                productType = grandpaCode
                className = parentCode
                subClassName = code
            else:
                productType = parentCode
                className = code
                subClassName = ''

            level = thing.level if thing.level else ''
            peroid = thing.peroid if thing.peroid else ''
            country = thing.country if thing.country else ''
            dingSecification = thing.dingSecification if thing.dingSecification else ''
            shape = thing.shape if thing.shape else ''

            thing = gsThing.objects.get(serialNumber=serialNumber)
            gsStatus.objects.filter(thing=thing, status=1).update(close_status=True)
            # 向货发二代系统请求实物编号
            # code = '{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}|{9}'.format(request_type,
            #                                                         wareHouse,
            #                                                         productType,
            #                                                         className,
            #                                                         subClassName,
            #                                                         level,
            #                                                         peroid,
            #                                                         country,
            #                                                         dingSecification,
            #                                                         shape)
            # boxNumber = getNumberAPI(code)
            # -----模拟
            serialNumber2 = '123' + str(shortuuid.ShortUUID().random(length=5))
            gsThing.objects.filter(serialNumber=serialNumber).update(serialNumber2=serialNumber2)

            ret = {
                'success': True,
                'text': serialNumber2
            }
        else:
            ret = {
                'success': False,
                'message': u'该实物已封袋！'
            }
    except Exception as e:
        ret = {
            'success': False,
            'message': u'请求实物编号失败！'
        }
    ret_json = json.dumps(ret)
    return HttpResponse(ret_json)


# 盒管理操作
# 1、首先获取能入盒的实物
def getCloseOverThing(request):
    boxNumber = request.POST.get('boxNumber', '')
    # productType = request.POST.get('productType', '')
    # className = request.POST.get('className', '')
    # wareHouse = request.POST.get('wareHouse', '')  # 发行库
    pageSize = int(request.POST.get('rows', ''))
    page = int(request.POST.get('page', ''))
    ret = {}
    try:
        box = gsBox.objects.get(boxNumber=boxNumber)
        works = gsWork.objects.filter(box=box)
        thing_set = gsThing.objects.filter(work__in=works)
        things = gsStatus.objects.filter(thing__in=thing_set, status=1, close_status=1, incase_status=0)
        n = things.count()
        start = (page - 1) * pageSize
        end = n if (page * pageSize > n) else page * pageSize
        ret['total'] = n
        ret['rows'] = []
        for th in things[start:end]:
            r = {}
            r['serialNumber2'] = th.thing.serialNumber2
            # subClassName_code = th.thing.subClassName
            # subClassName_obj = gsProperty.objects.get(grandpaType=productType,parentType=className,code=subClassName_code)
            # subClassName_type = subClassName_obj.type
            # r['subClassName'] = subClassName_type
            # r['productType'] = productType
            # r['className'] = className
            # r['wareHouse'] = wareHouse
            ret['rows'].append(r)
    except Exception as e:
        ret['success'] = False
        ret['message'] = u'获取数据失败！'

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)


# 获取盒号及其二维码
def getCaseNumber(request):
    boxNumber = request.POST.get('boxNumber', '')

    try:
        box = gsBox.objects.get(boxNumber=boxNumber)
        wareHouse = box.wareHouse

        prop = box.boxType
        code = prop.code
        parentCode = prop.parentCode
        grandpaCode = prop.grandpaCode
        if grandpaCode:
            productType = grandpaCode
            className = parentCode
        else:
            productType = parentCode
            className = code

        request_type = '2'

        # 向货发二代系统请求盒号
        # code = '{0}|{1}|{2}|{3}'.format(request_type,
        #                                 wareHouse,
        #                                 productType,
        #                                 className,)
        # boxNumber = getNumberAPI(code)
        # -----模拟
        caseNumber = '456' + str(shortuuid.ShortUUID().random(length=5))

        # 数据库记录
        gsCase.objects.create(caseNumber=caseNumber,status=0,box=box)
        ret = {
            'caseNumber': caseNumber,  # 页面展示用
            'text': caseNumber  # 打印用
        }
    except Exception as e:
        ret={
            'success':False,
            'massage':'盒号获取失败'
        }
    ret_json = json.dumps(ret)
    return HttpResponse(ret_json)

def enterEvent(request):
    serialNumber2 = request.POST.get('serialNumber2', '')
    caseNumber = request.POST.get('caseNumber', '')
    pageSize = int(request.POST.get('rows', ''))
    page = int(request.POST.get('page', ''))
    ret = {}
    try:
        # 更新信息
        case = gsCase.objects.get(caseNumber=caseNumber)
        gsThing.objects.filter(serialNumber2=serialNumber2).update(case=case)
        thing = gsThing.objects.filter(serialNumber2=serialNumber2)
        gsStatus.objects.filter(thing__in=thing).update(incase_status=1)
        # 获取盒中实物
        thing_set = gsThing.objects.filter(case=case)

        n = thing_set.count()
        start = (page - 1) * pageSize
        end = n if (page * pageSize > n) else page * pageSize
        ret['total'] = n
        ret['rows'] = []
        for th in thing_set[start:end]:
            r = {}
            r['serialNumber2'] = th.serialNumber2
            ret['rows'].append(r)
    except Exception as e:
        ret['success'] = False
        ret['message'] = u'入盒失败！'
    ret_json = json.dumps(ret)
    return HttpResponse(ret_json)


def cancleInput(request):
    serialNumber2 = request.POST.get('serialNumber2', '')
    caseNumber = request.POST.get('caseNumber', '')
    try:
        serialNumber2_list = serialNumber2.split(';')[0:-1]
        case = gsCase.objects.get(caseNumber=caseNumber)
        thing_set = gsThing.objects.filter(serialNumber2__in=serialNumber2_list).update(case=None)
        case.delete()
        thing_set = gsThing.objects.filter(serialNumber2__in=serialNumber2_list)
        gsStatus.objects.filter(thing__in=thing_set).update(incase_status=0)
        ret = {
            'success': True,
        }
    except Exception as e:
        ret = {
            'success': False
        }
    ret_json = json.dumps(ret)
    return HttpResponse(ret_json)


def confirmInputCase(request):
    boxNumber = request.POST.get('boxNumber', '')
    caseNumber = request.POST.get('caseNumber', '')
    serialNumber2 = request.POST.get('serialNumber2', '')

    serialNumber2_list = serialNumber2.split(';')[0:-1]
    try:
        file_path = createCaseTicket(boxNumber=boxNumber,
                                     caseNumber=caseNumber,
                                     serialNumber2_list=serialNumber2_list)
    except Exception as e:
        ret = {
            'success': False
        }
    else:
        ret = {
            'success': True,
            'file_path': file_path
        }
    ret_json = json.dumps(ret)
    return HttpResponse(ret_json)

def getAllCase(request):
    boxNumber = request.POST.get('boxNumber', '')
    pageSize = int(request.POST.get('rows', ''))
    page = int(request.POST.get('page', ''))
    ret = {}
    try:
        box = gsBox.objects.get(boxNumber=boxNumber)
        case_set = gsCase.objects.filter(box=box,status=False)
        n = case_set.count()
        start = (page - 1) * pageSize
        end = n if (page * pageSize > n) else page * pageSize
        ret['total'] = n
        ret['rows'] = []
        for case in case_set[start:end]:
            r = {}
            r['caseNumber'] = case.caseNumber
            ret['rows'].append(r)
    except Exception as e:
        ret['success'] = False
        ret['message'] = u'获取盒失败！'
    else:
        ret['success'] = True
    ret_json = json.dumps(ret)
    return HttpResponse(ret_json)


def closeCase(request):

    boxNumber = request.POST.get('boxNumber', '')
    caseNumber = request.POST.get('caseNumber', '')
    serialNumber2 = request.POST.get('serialNumber2', '')

    serialNumber2_list = serialNumber2.split(';')[0:-1]
    # 盒号
    # 类别
    # 品种
    # 封装人
    # 封装复核人
    # 封装时间
    # 件序号
    try:
        case = gsCase.objects.create(caseNumber=caseNumber, status=1)
        thing_set = gsThing.objects.filter(serialNumber2__in=serialNumber2_list)
        thing_set.update(case=case)
        # gsStatus.objects.filter(thing__in=thing_set).update(incase_status=1)

        file_path = createCaseTicket(boxNumber=boxNumber,
                                     caseNumber=caseNumber,
                                     serialNumber2_list=serialNumber2_list)

    except Exception as e:
        ret = {
            'success': False
        }
    else:
        ret = {
            'success': True,
            'file_path': file_path
        }
    ret_json = json.dumps(ret)
    return HttpResponse(ret_json)


# # 日终小结
def processThing(thing_set):
    val = []
    ding = {'productType': u'金银锭类',
            'thing': []}
    bizhang = {'productType': u'金银币章类',
               'thing': []}
    yinyuan = {'productType': u'银元类',
               'thing': []}
    gongyipin = {'productType': u'金银工艺品类',
                 'thing': []}

    for th in thing_set:
        thing = th.thing
        productType_code = thing.box.productType
        productType = gsProperty.objects.get(project='实物类型', code=productType_code).type
        if productType == u'金银锭类':
            ding['thing'].append(thing)
        elif productType == u'金银币章类':
            bizhang['thing'].append(thing)
        elif productType == u'银元类':
            yinyuan['thing'].append(thing)
        elif productType == u'金银工艺品类':
            gongyipin['thing'].append(thing)

    val.append(ding)
    val.append(bizhang)
    val.append(yinyuan)
    val.append(gongyipin)
    return val


def getStatisticalReport (request):
    date = '2017-9-13'  # request.POST.get('date', '')
    t = time.strptime(date, "%Y-%m-%d")
    y, m, d = t[0:3]
    start_time = datetime.datetime(y, m, d)
    end_date = start_time + datetime.timedelta(days=1)
    current_thing = gsStatus.objects.filter(status=1, completeTime__range=(start_time, end_date))

    val = processThing(current_thing)
    type = []
    try:
        for dic in val:
            productType = dic['productType']
            thing_list = dic['thing']
            sub = {}
            sub['productType'] = productType
            sub['field'] = []
            if thing_list:
                if productType == u'金银锭类':
                    field_list = ['detectedQuantity','length','width','height','grossWeight','pureWeight']
                    for f in field_list:
                        child = {}
                        child['name'] = f
                        th = gsDing.objects.filter(thing__in=thing_list)
                        v_list = list(th.values_list(f,flat=True))
                        child['max'] = max(v_list)
                        child['min'] = min(v_list)
                        num = len(v_list)
                        sum_val = sum(v_list)
                        child['average'] = float('%.2f' % (float(sum_val)/float(num)))
                        sub['field'].append(child)

                elif productType == u'金银币章类':
                    field_list = ['detectedQuantity', 'diameter', 'thick', 'grossWeight', 'pureWeight']
                    for f in field_list:
                        child = {}
                        child['name'] = f
                        th = gsDing.objects.filter(thing__in=thing_list)
                        v_list = list(th.values_list(f, flat=True))
                        child['max'] = max(v_list)
                        child['min'] = min(v_list)
                        num = len(v_list)
                        sum_val = sum(v_list)
                        child['average'] = float('%.2f' % (float(sum_val) / float(num)))
                        sub['field'].append(child)
                elif productType == u'银元类':
                    field_list = ['detectedQuantity', 'diameter', 'thick', 'grossWeight', 'pureWeight']
                    for f in field_list:
                        child = {}
                        child['name'] = f
                        th = gsDing.objects.filter(thing__in=thing_list)
                        v_list = list(th.values_list(f, flat=True))
                        child['max'] = max(v_list)
                        child['min'] = min(v_list)
                        num = len(v_list)
                        sum_val = sum(v_list)
                        child['average'] = float('%.2f' % (float(sum_val) / float(num)))
                        sub['field'].append(child)
                elif productType == u'金银工艺品类':
                    field_list = ['detectedQuantity', 'length', 'width', 'height', 'grossWeight', 'pureWeight']
                    for f in field_list:
                        child = {}
                        child['name'] = f
                        th = gsDing.objects.filter(thing__in=thing_list)
                        v_list = list(th.values_list(f, flat=True))
                        child['max'] = max(v_list)
                        child['min'] = min(v_list)
                        num = len(v_list)
                        sum_val = sum(v_list)
                        child['average'] = float('%.2f' % (float(sum_val) / float(num)))
                        sub['field'].append(child)
            type.append(sub)
    except Exception as e:
        ret = {
            'success': False
        }
    else:
        ret = {
            'success': True,
            'type':type,
        }
    ret_json = json.dumps(ret)
    return HttpResponse(ret_json)


def getCarveNameReport (request):
    date = '2017-9-15'  # request.POST.get('date', '')
    t = time.strptime(date, "%Y-%m-%d")
    y, m, d = t[0:3]
    start_time = datetime.datetime(y, m, d)
    end_date = start_time + datetime.timedelta(days=1)
    current_thing = gsStatus.objects.filter(status=1, completeTime__range=(start_time, end_date))
    history_thing = gsStatus.objects.filter(status=1, completeTime__lt=(start_time))
    current_val = processThing(current_thing)
    history_val = processThing(history_thing)
    ret = {}
    try:
        for current_dic in current_val:
            for history_dic in history_val:

                current_productType = current_dic['productType']
                current_thing_list = current_dic['thing']

                history_productType = history_dic['productType']
                history_thing_list = history_dic['thing']

                if current_productType == u'金银锭类' and history_productType == u'金银锭类':
                    dayCarve = set(list(gsDing.objects.filter(thing__in=current_thing_list).values_list('carveName',flat=True)))
                    historyCarve = set(list(gsDing.objects.filter(thing__in=history_thing_list).values_list('carveName', flat=True)))
                    newCarve = []
                    for carve in dayCarve:
                        if carve not in historyCarve:
                            newCarve.append(carve)
                    ret['dayCarve']= list(dayCarve)
                    ret['newCarve'] = newCarve
                    # gsStatus.objects.filter(status=1, completeTime__range=(start_time, end_date))
                    # historyCarve = gsDing.objects.all().exclude(thing__in=thing_list)
                    # dayCarve = gsDing.objects.filter(thing__in=thing_list)
    except Exception as e:
        print e
        ret['success'] = False
    else:
        ret['success'] = True
    ret_json = json.dumps(ret)
    return HttpResponse(ret_json)

def getEfficiencyReport (request):
    date = '2017-9-15'  # request.POST.get('date', '')
    t = time.strptime(date, "%Y-%m-%d")
    y, m, d = t[0:3]
    start_time = datetime.datetime(y, m, d)
    end_date = start_time + datetime.timedelta(days=1)
    current_thing = gsStatus.objects.filter(status=1, completeTime__range=(start_time, end_date))

    post_dic = {'numbering':u'外观信息采集岗位',
                'analyzing':'频谱分析岗位',
                'measuring':'测量称重岗位',
                'checking':'实物认定岗位',
                'photographing':'图像采集岗位'}
    type = []
    ret = {}
    try:
        for k,v in post_dic.items():
            sub={}
            sub['post']=v
            createDate_list = list(current_thing.values_list('{0}CreateDateTime'.format(k),flat=True))
            updateDate_list = list(current_thing.values_list('{0}UpdateDateTime'.format(k), flat=True))
            timespan_list = []
            for end_start in zip(updateDate_list,createDate_list):
                end,start = end_start
                dif = end-start
                timespan_second = dif.total_seconds()
                timespan_list.append(timespan_second)
            dif_len = len(timespan_list)
            sub['all_time'] = round(sum(timespan_list)/60,2)
            sub['average_time'] = round((sum(timespan_list)/dif_len)/60,2)
            type.append(sub)
    except Exception as e:
        ret['success'] = False
    else:
        ret['success'] = True
        ret['type'] = type
    ret_json = json.dumps(ret)
    return HttpResponse(ret_json)
