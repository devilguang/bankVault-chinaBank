# encoding=UTF-8
from django.shortcuts import render
from django.http.response import HttpResponse
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from .models import *
import json
from .utils import dateTimeHandler
from .report_process import *
from django.contrib import auth
from . import log
from haystack.views import SearchView
from haystack.query import SearchQuerySet
from forms import advanceSearch


def login(request):
    req_method = request.method
    if req_method == 'GET':
        return render(request, 'login.html', context={})
    elif req_method == 'POST':
        nickName = request.POST.get('nickName', '')  # 用户
        workRole = request.POST.get('workRole', '')  # 岗位
        passWord = request.POST.get('passWord', '')  # 密码
        if (nickName.isspace() or passWord.isspace()):
            ret = {
                "success": False,
                "message": u'用户名或密码不能为空！'
            }
        else:
            try:
                custom_user = gsUser.objects.get(nickName=nickName)
                username = custom_user.user.username
                '''
                authenticate()---认证给出的用户名和密码是否真实。它接受两个参数：username和password ，
                如果合法返回User 对象；如果不合法，返回None
                '''
                user = auth.authenticate(username=username, password=passWord)  # 身份验证
                if user:
                    log.log(user=user, operationType=u'登录', content=u'登录系统')
                    if workRole == 'systemadmin':
                        if (1 >= custom_user.type):  # 用户类型: 1:管理员 2:一般用户
                            auth.login(request, user)
                            ret = {
                                "success": True,
                                "url": reverse('systemAdmin')
                            }
                        else:
                            ret = {
                                "success": False,
                                "message": u'该用户无系统管理岗位权限！'
                            }
                    elif workRole == 'manage':
                        hasRole = custom_user.manage
                        if hasRole:
                            auth.login(request, user)
                            ret = {
                                "success": True,
                                "url": reverse('manage')
                            }
                        else:
                            ret = {
                                "success": False,
                                "message": u'该用户无现场负责人岗位权限！'
                            }
                    elif workRole == 'checking':
                        hasRole = custom_user.checking
                        if hasRole:
                            auth.login(request, user)
                            ret = {
                                "success": True,
                                "url": reverse('checking')
                            }
                        else:
                            ret = {
                                "success": False,
                                "message": u'该用户无监控输出岗位权限！'
                            }
                    elif workRole == 'numbering':
                        hasRole = custom_user.numbering
                        if hasRole:
                            auth.login(request, user)
                            ret = {
                                "success": True,
                                "url": reverse('numbering')
                            }
                        else:
                            ret = {
                                "success": False,
                                "message": u'该用户无实物鉴定岗位权限！'
                            }
                    elif workRole == 'measuring':
                        hasRole = custom_user.measuring
                        if hasRole:
                            auth.login(request, user)
                            ret = {
                                "success": True,
                                "url": reverse('measuring')
                            }
                        else:
                            ret = {
                                "success": False,
                                "message": u'该用户无测量称重岗位权限！'
                            }
                    elif workRole == 'photographing':
                        hasRole = custom_user.photographing
                        if hasRole:
                            auth.login(request, user)
                            ret = {
                                "success": True,
                                "url": reverse('photographing')
                            }
                        else:
                            ret = {
                                "success": False,
                                "message": u'该用户无图像采集岗位权限！'
                            }
                    elif workRole == 'analyzing':
                        hasRole = custom_user.analyzing
                        if hasRole:
                            auth.login(request, user)
                            ret = {
                                "success": True,
                                "url": reverse('analyzing')
                            }
                        else:
                            ret = {
                                "success": False,
                                "message": u'该用户无频谱分析岗位权限！'
                            }

                else:  # user that auth.authenticate returns is None
                    ret = {
                        "success": False,
                        "message": u'用户名或密码错误！'
                    }
            except Exception as e:
                ret = {
                    "success": False,
                    "message": u'用户名或密码错误！'
                }
        ret_json = json.dumps(ret, separators=(',', ':'))
        return HttpResponse(ret_json)


def logout(request):
    try:
        auth.logout(request)
    except Exception as e:
        ret = {
            "success": False,
            "message": u'用户注销失败！\n原因:'.format(e.message)
        }
    else:
        ret = {
            "success": True,
            "message": u'用户注销成功！'
        }

    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)


# 从所有用户中找出非sysadmin得用户
def getAllUser(request):
    ret = []

    users = gsUser.objects.all()
    for u in users:
        r = {}
        # if u.nickName == 'sysadmin':
        #     continue
        r['text'] = u.nickName
        r['id'] = u.user.id
        ret.append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)

# --------------------------------------------------------------------------
def getWorkData(request, workSeq):
    pageSize = int(request.POST.get('rows', ''))
    page = int(request.POST.get('page', ''))
    processId = int(request.POST.get('processId', ''))
    thingStatus = request.POST.get('thingStatus', '')
    boxNumber = int(request.POST.get('boxNumber', ''))
    subBoxNumber = request.POST.get('subBoxNumber', '')

    box = gsBox.objects.get(boxNumber=boxNumber)
    if subBoxNumber == '':
        work = gsWork.objects.get(box=box, workSeq=workSeq)
    else:
        subBox = gsSubBox.objects.get(box=box,subBoxNumber=int(subBoxNumber))
        work = gsWork.objects.get(box=box, workSeq=workSeq,subBox=subBox)

    wts = gsWorkThing.objects.filter(work=work)
    specialThingIDList = wts.values_list('thing', flat=True)
    specialSerialNumberList = gsThing.objects.filter(id__in=specialThingIDList).values_list('serialNumber', flat=True)

    if thingStatus != '' and thingStatus != 'all':
        if thingStatus == 'cancheck':
            # 检索数据复核环节，可以复核的实物
            ss = gsStatus.objects.filter(box=box, serialNumber__in=specialSerialNumberList, numberingStatus=True,
                                         measuringStatus=True, analyzingStatus=True)  # , photographingStatus=True
        else:
            if thingStatus == 'notComplete':
                status = False
            elif thingStatus == 'complete':
                status = True

            if 2 == processId:  # 实物鉴定环节
                ss = gsStatus.objects.filter(box=box, serialNumber__in=specialSerialNumberList, numberingStatus=status)
            elif 3 == processId:  # 频谱分析环节
                ss = gsStatus.objects.filter(box=box, serialNumber__in=specialSerialNumberList, analyzingStatus=status)
            elif 4 == processId:  # 测量称重环节
                ss = gsStatus.objects.filter(box=box, serialNumber__in=specialSerialNumberList, measuringStatus=status)
            elif 5 == processId:  # 数据复核环节
                ss = gsStatus.objects.filter(box=box, serialNumber__in=specialSerialNumberList, checkingStatus=status)
            elif 6 == processId:  # 图像采集环节
                ss = gsStatus.objects.filter(box=box, serialNumber__in=specialSerialNumberList, photographingStatus=status)

        specialSerialNumberList = ss.values_list('serialNumber', flat=True)

    productTypeCode = box.productType
    classNameCode = box.className
    subClassNameCode = box.subClassName
    wareHouseCode = box.wareHouse

    productType = gsProperty.objects.get(project='实物类型', code=productTypeCode)
    className = gsProperty.objects.get(project='品名', code=classNameCode, parentProject=productType.project,
                                       parentType=productType.type)
    subClassName = gsProperty.objects.get(project='明细品名', code=subClassNameCode, parentProject=className.project,
                                          parentType=className.type, grandpaProject=productType.project,
                                          grandpaType=productType.type)
    wareHouse = gsProperty.objects.get(project='发行库', code=wareHouseCode)

    if productType.type == u'金银锭类':
        ts = gsDing.objects.filter(box=box, serialNumber__in=specialSerialNumberList)
    elif productType.type == u'金银币章类':
        ts = gsBiZhang.objects.filter(box=box, serialNumber__in=specialSerialNumberList)
    elif productType.type == u'银元类':
        ts = gsYinYuan.objects.filter(box=box, serialNumber__in=specialSerialNumberList)
    elif productType.type == u'金银工艺品类':
        ts = gsGongYiPin.objects.filter(box=box, serialNumber__in=specialSerialNumberList)

    ss = gsStatus.objects.filter(box=box, serialNumber__in=specialSerialNumberList)
    n = ts.count()

    start = (page - 1) * pageSize
    end = n if (page * pageSize > n) else page * pageSize

    ret = {}
    ret['total'] = n
    ret['rows'] = []
    for t, s in zip(ts[start:end], ss[start:end]):
        r = {}
        r['serialNumber'] = t.serialNumber
        r['productType'] = productType.type
        if subBoxNumber == '':
            r['boxNumber'] = boxNumber
        else:
            r['boxNumber'] = str(boxNumber) + '-' + str(subBoxNumber)
        r['className'] = className.type
        r['subClassName'] = subClassName.type
        r['wareHouse'] = wareHouse.type
        if (2 == processId):  # 实物鉴定环节
            r['status'] = s.numberingStatus
            r['operator'] = s.numberingOperator
            r['lastUpdateTime'] = s.numberingUpdateDateTime if s.numberingStatus else ''
        elif (4 == processId):  # 测量称重环节
            r['status'] = s.measuringStatus
            r['operator'] = s.measuringOperator
            r['lastUpdateTime'] = s.measuringUpdateDateTime if s.measuringStatus else ''
        elif (6 == processId):  # 图像采集环节
            r['status'] = s.photographingStatus
            r['operator'] = s.photographingOperator
            r['lastUpdateTime'] = s.photographingUpdateDateTime if s.photographingStatus else ''
        elif (5 == processId):  # 数据复核环节
            r['operation'] = s.numberingStatus and s.measuringStatus and s.analyzingStatus
            r['status'] = s.checkingStatus
            r['operator'] = s.checkingOperator
            r['lastUpdateTime'] = s.checkingUpdateDateTime if s.checkingStatus else ''
        ret['rows'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)

# --------------------------------------------------------------------------
def getWorkSpaceContent(request):
    ws = gsWork.objects.filter(status=1)
    ret = []
    for w in ws:
        r = {}
        productTypeCode = w.box.productType
        if w.subBox:
            subBoxNumber = w.subBox.subBoxNumber
        else:
            subBoxNumber = ''
        productType = gsProperty.objects.get(project='实物类型', code=productTypeCode)
        t = None
        for t in ret:
            if t['text'] == productType.type:
                break
        else:  # 未存在对应实物类型，先初始化
            r['id'] = 0
            r['text'] = productType.type
            r['state'] = 'open'

            '''if (0 == cmp(productType.type, u'金银锭类')):
                icon = 'icon-ding'
            elif (0 == cmp(productType.type, u'金银币章类')):
                icon = 'icon-bizhang'
            elif (0 == cmp(productType.type, u'银元类')):
                icon = 'icon-yinyuan'
            elif (0 == cmp(productType.type, u'金银工艺品类')):
                icon = 'icon-gongyipin'   
            r['iconCls'] = icon'''

            r['attributes'] = {'isWork': False}
            r['children'] = []
            ret.append(r)
            t = r
        # 已存在对应实物类型，可直接操作
        r = {}
        r['id'] = w.id
        r['text'] = w.workName
        r['iconCls'] = 'icon-box'
        r['attributes'] = {'isWork': True, 'boxNumber': w.box.boxNumber, 'workSeq': w.workSeq,'subBoxNumber':subBoxNumber}
        t['children'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)
# --------------------------------------------------------------------------
def searchThingInfo(request):
    serialNumber = request.POST.get('serialNumber', '')
    processId = int(request.POST.get('processId', ''))

    try:
        t = gsThing.objects.get(serialNumber=serialNumber)
        wt = gsWorkThing.objects.get(thing=t)  # 无该元素则会抛出 ObjectDoesNotExist 异常
        work = wt.work  # 这里的work、box、status都是外键，会指向对应的表
        box = work.box
        subBox = work.subBox
        boxNumber = box.boxNumber
        if subBox:
            subBoxNumber = subBox.subBoxNumber
            boxOrSubBox = str(boxNumber) + '-' + str(subBoxNumber)
        else:
            boxOrSubBox = str(boxNumber)
        status = wt.status

        wts = gsWorkThing.objects.filter(work=work)
        specialThingIDList = wts.values_list('thing', flat=True)
        specialSerialNumberList1 = gsThing.objects.filter(id__in=specialThingIDList).values_list('serialNumber',
                                                                                                 flat=True)
        if (2 == processId):
            # 实物鉴定环节
            thingStatus = status.numberingStatus
            specialSerialNumberList2 = gsStatus.objects.filter(box=box, serialNumber__in=specialSerialNumberList1,
                                                               numberingStatus=thingStatus).values_list('serialNumber',
                                                                                                        flat=True)
        if (3 == processId):
            # 频谱分析环节
            thingStatus = status.numberingStatus
            specialSerialNumberList2 = gsStatus.objects.filter(box=box, serialNumber__in=specialSerialNumberList1,
                                                               analyzingStatus=thingStatus).values_list('serialNumber',
                                                                                                        flat=True)
        elif (4 == processId):
            # 测量称重环节
            thingStatus = status.measuringStatus
            specialSerialNumberList2 = gsStatus.objects.filter(box=box, serialNumber__in=specialSerialNumberList1,
                                                               measuringStatus=thingStatus).values_list('serialNumber',
                                                                                                        flat=True)
        elif (5 == processId):
            # 数据复核环节
            thingStatus = status.checkingStatus
            specialSerialNumberList2 = gsStatus.objects.filter(box=box, serialNumber__in=specialSerialNumberList1,
                                                               checkingStatus=thingStatus).values_list('serialNumber',
                                                                                                       flat=True)
        elif (6 == processId):
            # 图像采集环节
            thingStatus = status.photographingStatus
            specialSerialNumberList2 = gsStatus.objects.filter(box=box, serialNumber__in=specialSerialNumberList1,
                                                               photographingStatus=thingStatus).values_list('serialNumber',
                                                                                                            flat=True)
        serialNumberList = list(specialSerialNumberList2)
        n = len(serialNumberList)

        idx = serialNumberList.index(serialNumber) + 1

    except ObjectDoesNotExist:
        ret = {
            'success': False,
            'message': u'未找到编号为{0}的实物！'.format(serialNumber),
        }
    except Exception as e:
        ret = {
            'success': False,
            'message': u'查找编号为{0}的实物失败！'.format(serialNumber),
        }
    else:
        ret = {}
        ret['success'] = True
        ret['id'] = work.id
        ret['workName'] = work.workName
        ret['thingStatus'] = 'complete' if thingStatus else 'notComplete'
        ret['seq'] = idx
        ret['boxOrSubBox'] = boxOrSubBox

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)

# --------------------------------------------------------------------------
def getProductType(request):
    types = gsProperty.objects.filter(project='实物类型')
    ret = []
    for t in types:
        r = {}
        r['text'] = t.type
        r['id'] = t.code
        ret.append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)

# --------------------------------------------------------------------------
def getWareHouse(request):
    types = gsProperty.objects.filter(project='发行库')
    ret = []
    for t in types:
        r = {}
        r['text'] = t.type
        r['id'] = t.code
        ret.append(r)
    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)
# --------------------------------------------------------------------------
def exploreThing(request, boxNumber, serialNumber):
    subBoxNumber = request.GET.get('subBoxNumber','')
    if subBoxNumber == '0':
        subBoxNumber = ''
        boxOrSubBox = boxNumber
    else:
        boxOrSubBox = boxNumber + '-' + subBoxNumber
    isVerify = request.GET.get('isVerify', '')
    operator = request.GET.get('operator', '')
    # 检测是否是数据审核用, 以便显示相应的审核接口和修改接口
    if (0 != cmp(isVerify, '')):
        isVerify = True
        # 最后在context中添加isVerify环境变量

    box = gsBox.objects.get(boxNumber=boxNumber)
    t = gsThing.objects.get(serialNumber=serialNumber)
    wt = gsWorkThing.objects.get(thing=t)
    work = wt.work
    specialThingIDList = gsWorkThing.objects.filter(work=work).values_list('thing', flat=True)
    specialSerialNumberList = gsThing.objects.filter(id__in=specialThingIDList).values_list('serialNumber',
                                                                                            flat=True)

    context = {}
    context['boxNumber'] = boxOrSubBox
    context['serialNumber'] = serialNumber

    productTypeCode = box.productType
    productType = gsProperty.objects.get(project='实物类型', code=productTypeCode)
    context['productType'] = productType.type
    wareHouseCode = box.wareHouse
    wareHouse = gsProperty.objects.get(project='发行库', code=wareHouseCode)
    context['wareHouse'] = wareHouse.type
    classNameCode = box.className
    className = gsProperty.objects.get(project='品名', code=classNameCode, parentProject=productType.project,
                                       parentType=productType.type)
    context['className'] = className.type
    subClassNameCode = box.subClassName
    subClassName = gsProperty.objects.get(project='明细品名', code=subClassNameCode, parentProject=className.project,
                                          parentType=className.type, grandpaProject=productType.project,
                                          grandpaType=productType.type)
    context['subClassName'] = subClassName.type

    # 档案建立时间与档案修改时间
    s = gsStatus.objects.get(box=box, serialNumber=serialNumber)
    lastUpdateDate = (s.numberingUpdateDateTime if (
        s.numberingUpdateDateTime is not None and s.analyzingUpdateDateTime is None) else s.analyzingUpdateDateTime) if (
        s.numberingUpdateDateTime is None or s.analyzingUpdateDateTime is None) else (
        s.numberingUpdateDateTime if s.numberingUpdateDateTime > s.analyzingUpdateDateTime else s.analyzingUpdateDateTime)
    lastUpdateDate = (lastUpdateDate if (
        lastUpdateDate is not None and s.measuringUpdateDateTime is None) else s.measuringUpdateDateTime) if (
        lastUpdateDate is None or s.measuringUpdateDateTime is None) else (
        lastUpdateDate if lastUpdateDate > s.measuringUpdateDateTime else s.measuringUpdateDateTime)
    context['createDate'] = dateTimeHandler(work.createDateTime)
    context['lastUpdateDate'] = dateTimeHandler(lastUpdateDate) if (lastUpdateDate is not None) else ''

    # 图像路径
    year = s.numberingCreateDateTime.year
    seq = t.subBoxSeq
    picturePathPrefix = u'/static/img/{0}/{1}/{2}'.format(boxOrSubBox, serialNumber,serialNumber)
    context['A'] = u'{0}-A.jpg'.format(picturePathPrefix)
    context['B'] = u'{0}-B.jpg'.format(picturePathPrefix)
    context['C'] = u'{0}-C.jpg'.format(picturePathPrefix)

    if (0 == cmp(productType.type, u'金银锭类')):
        thing = gsDing.objects.get(box=box, serialNumber=serialNumber)
        context['detailedName'] = thing.detailedName
        context['typeName'] = thing.typeName
        context['peroid'] = thing.peroid
        context['producerPlace'] = thing.producerPlace
        context['carveName'] = thing.carveName
        context['remark'] = thing.remark
        context['quality'] = thing.quality
        context['level'] = thing.level
        context['originalQuantity'] = thing.originalQuantity if (thing.originalQuantity is not None) else ''
        context['detectedQuantity'] = thing.detectedQuantity if (thing.detectedQuantity is not None) else ''
        context['length'] = thing.length if (thing.length is not None) else ''
        context['width'] = thing.width if (thing.width is not None) else ''
        context['height'] = thing.height if (thing.height is not None) else ''
        context['grossWeight'] = thing.grossWeight if (thing.grossWeight is not None) else ''
        context['pureWeight'] = float('%0.2f' % ((thing.detectedQuantity * thing.grossWeight) / 100)) if (
            thing.detectedQuantity is not None and thing.grossWeight is not None) else ''

        html = 'ding.html'
    elif (0 == cmp(productType.type, u'金银币章类')):
        thing = gsBiZhang.objects.get(box=box, serialNumber=serialNumber)
        context['detailedName'] = thing.detailedName
        context['versionName'] = thing.versionName
        context['peroid'] = thing.peroid
        context['producerPlace'] = thing.producerPlace
        context['value'] = thing.value
        context['remark'] = thing.remark
        context['quality'] = thing.quality
        context['level'] = thing.level
        context['originalQuantity'] = thing.originalQuantity if (thing.originalQuantity is not None) else ''
        context['detectedQuantity'] = thing.detectedQuantity if (thing.detectedQuantity is not None) else ''
        context['diameter'] = thing.diameter if (thing.diameter is not None) else ''
        context['thick'] = thing.thick if (thing.thick is not None) else ''
        context['grossWeight'] = thing.grossWeight if (thing.grossWeight is not None) else ''
        context['pureWeight'] = float('%0.2f' % ((thing.detectedQuantity * thing.grossWeight) / 100)) if (
            thing.detectedQuantity is not None and thing.grossWeight is not None) else ''

        html = 'bizhang.html'
    elif (0 == cmp(productType.type, u'银元类')):
        thing = gsYinYuan.objects.get(box=box, serialNumber=serialNumber)
        context['detailedName'] = thing.detailedName
        context['versionName'] = thing.versionName
        context['peroid'] = thing.peroid
        context['producerPlace'] = thing.producerPlace
        context['value'] = thing.value
        context['marginShape'] = thing.marginShape
        context['remark'] = thing.remark
        context['quality'] = thing.quality
        context['level'] = thing.level
        context['originalQuantity'] = thing.originalQuantity if (thing.originalQuantity is not None) else ''
        context['detectedQuantity'] = thing.detectedQuantity if (thing.detectedQuantity is not None) else ''
        context['diameter'] = thing.diameter if (thing.diameter is not None) else ''
        context['thick'] = thing.thick if (thing.thick is not None) else ''
        context['grossWeight'] = thing.grossWeight if (thing.grossWeight is not None) else ''

        html = 'yinyuan.html'
    elif (0 == cmp(productType.type, u'金银工艺品类')):
        thing = gsGongYiPin.objects.get(box=box, serialNumber=serialNumber)
        context['detailedName'] = thing.detailedName
        context['peroid'] = thing.peroid
        context['remark'] = thing.remark
        context['quality'] = thing.quality
        context['level'] = thing.level
        context['originalQuantity'] = thing.originalQuantity if (thing.originalQuantity is not None) else ''
        context['detectedQuantity'] = thing.detectedQuantity if (thing.detectedQuantity is not None) else ''
        context['length'] = thing.length if (thing.length is not None) else ''
        context['width'] = thing.width if (thing.width is not None) else ''
        context['height'] = thing.height if (thing.height is not None) else ''
        context['grossWeight'] = thing.grossWeight if (thing.grossWeight is not None) else ''
        context['pureWeight'] = float('%0.2f' % ((thing.detectedQuantity * thing.grossWeight) / 100)) if (
            thing.detectedQuantity is not None and thing.grossWeight is not None) else ''

        html = 'gongyipin.html'

    serialNumberList = list(specialSerialNumberList)
    n = len(serialNumberList)
    first = 0
    last = n - 1
    context['first'] = serialNumberList[first]
    context['last'] = serialNumberList[last]
    currentIdx = serialNumberList.index(thing.serialNumber)

    if (currentIdx < n - 1):
        context['next'] = serialNumberList[currentIdx + 1]
    else:
        context['next'] = context['last']

    if (currentIdx > 0):
        context['prev'] = serialNumberList[currentIdx - 1]
    else:
        context['prev'] = context['first']

    # 检测是否是数据审核用, 以便显示相应的审核接口和修改接口
    if (0 != cmp(isVerify, '')):
        context['first'] = context['first'] + u'?isVerify=1&operator={0}'.format(operator)
        context['last'] = context['last'] + u'?isVerify=1&operator={0}'.format(operator)
        context['next'] = context['next'] + u'?isVerify=1&operator={0}'.format(operator)
        context['prev'] = context['prev'] + u'?isVerify=1&operator={0}'.format(operator)

    context['isVerify'] = isVerify
    context['operator'] = operator
    return render(request, html, context=context)

def getClassName(request, code):
    type = gsProperty.objects.filter(project='实物类型', code=code)[0]
    classNames = gsProperty.objects.filter(project='品名', parentProject=type.project, parentType=type.type)
    ret = []
    for c in classNames:
        r = {}
        r['text'] = c.type
        r['id'] = c.code
        ret.append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)

def getSubClassName(request, code):
    codes = code.split('&')
    typeCode = codes[0]
    classNameCode = codes[1]
    type = gsProperty.objects.filter(project='实物类型', code=typeCode)[0]
    className = \
        gsProperty.objects.filter(project='品名', code=classNameCode, parentProject=type.project,
                                  parentType=type.type)[0]
    subClassNames = gsProperty.objects.filter(project='明细品名', parentProject=className.project,
                                              parentType=className.type, grandpaProject=type.project,
                                              grandpaType=type.type)
    ret = []
    for s in subClassNames:
        r = {}
        r['text'] = s.type
        r['id'] = s.code
        ret.append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)



class GeneralSearch(SearchView):
    template_name = 'search/search.html'
    form_class = advanceSearch
    queryset = SearchQuerySet().filter()

    # def get_queryset(self):
    #     queryset = super(GeneralSearch, self).get_queryset()
    #     # further filter queryset based on some set of criteria
    #     return queryset.filter()
    #
    # def get_context_data(self, *args, **kwargs):
    #     context = super(GeneralSearch, self).get_context_data(*args, **kwargs)
    #     # do something
    #     return context

# def search(request):
#     form = advanceSearch(request.GET)
#     if form.is_valid():
#         cd = form.cleaned_data
#         results = SearchQuerySet().models(gsDing).filter().load_all()
#         # count total results
#         total_results = results.count()
#
#     return render(request, 'search/search.html',
#             {'form': form,
#             'cd': '',
#             'results': '',
#             'total_results': total_results})