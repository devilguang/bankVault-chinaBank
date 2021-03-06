# encoding=UTF-8
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponse, StreamingHttpResponse
from .models import *
from utils import readFile, dateTimeHandler
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
        userName = request.POST.get('userName', '')  # 用户
        workRole = request.POST.get('workRole', '')  # 岗位
        passWord = request.POST.get('passWord', '')  # 密码
        if (userName.isspace() or passWord.isspace()):
            ret = {
                "success": False,
                "message": u'用户名或密码不能为空！'
            }
        else:
            try:
                custom_user = gsUser.objects.get(userName=userName)
                username = custom_user.user.username
                '''
                authenticate()---认证给出的用户名和密码是否真实。它接受两个参数：username和password ，
                如果合法返回User 对象；如果不合法，返回None
                '''
                user = auth.authenticate(username=username, password=passWord)  # 身份验证
                if user:
                    log.log(user=user, operationType=u'登录', content=u'登录系统')
                    if workRole == 'systemadmin':
                        if custom_user.type == 0:  # 用户类型: 1:管理员 2:一般用户
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
                                "message": u'该用户无实物分发岗位岗位权限！'
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
                                "message": u'该用户无外观信息采集岗位权限！'
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
        # if u.userName == 'sysadmin':
        #     continue
        r['text'] = u.userName
        r['id'] = u.user.id
        ret.append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


# 从所有用户中找出非sysadmin得用户
# --------------------------------------------------------------------------
def getWorkData(request, workSeq):
    pageSize = int(request.POST.get('rows', ''))
    page = int(request.POST.get('page', ''))
    processId = int(request.POST.get('processId', ''))
    thingStatus = request.POST.get('thingStatus', '')
    boxNumber = request.POST.get('boxNumber', '')

    box = gsBox.objects.get(boxNumber=boxNumber)
    work = gsWork.objects.get(box=box, workSeq=workSeq)
    thing_set = gsThing.objects.filter(work=work)

    if thingStatus != '' and thingStatus != 'all':
        if thingStatus == 'notComplete':
            status = False
        elif thingStatus == 'complete':
            status = True

        if 2 == processId:  # 外观信息采集环节
            status_set = gsStatus.objects.filter(thing__in=thing_set, numberingStatus=status)
        elif 3 == processId:  # 频谱分析环节
            status_set = gsStatus.objects.filter(thing__in=thing_set, analyzingStatus=status)
        elif 4 == processId:  # 测量称重环节
            status_set = gsStatus.objects.filter(thing__in=thing_set, measuringStatus=status)
        elif 5 == processId:  # 实物认定环节
            status_set = gsStatus.objects.filter(thing__in=thing_set, checkingStatus=status, numberingStatus=True)
        elif 6 == processId:  # 图像采集环节
            status_set = gsStatus.objects.filter(thing__in=thing_set, photographingStatus=status)
    else:
        if 2 == processId:  # 外观信息采集环节
            status_set = gsStatus.objects.filter(thing__in=thing_set)
        elif 3 == processId:  # 频谱分析环节
            status_set = gsStatus.objects.filter(thing__in=thing_set)
        elif 4 == processId:  # 测量称重环节
            status_set = gsStatus.objects.filter(thing__in=thing_set)
        elif 5 == processId:  # 实物认定环节
            status_set = gsStatus.objects.filter(thing__in=thing_set, numberingStatus=True)
        elif 6 == processId:  # 图像采集环节
            status_set = gsStatus.objects.filter(thing__in=thing_set)

    prop = box.boxType
    type = prop.type
    parentType = prop.parentType
    grandpaType = prop.grandpaType

    wareHouse = gsProperty.objects.get(project='发行库', code=box.wareHouse).type

    n = status_set.count()
    start = (page - 1) * pageSize
    end = n if (page * pageSize > n) else page * pageSize

    ret = {}
    ret['total'] = n
    ret['rows'] = []

    for status in status_set[start:end]:
        r = {}
        r['serialNumber'] = status.thing.serialNumber
        r['boxNumber'] = boxNumber
        r['wareHouse'] = wareHouse
        if grandpaType:
            r['productType'] = grandpaType
            r['className'] = parentType
            r['subClassName'] = type
        else:
            r['productType'] = parentType
            r['className'] = type
            r['subClassName'] = '-'

        if (2 == processId):  # 外观信息采集环节
            r['status'] = status.numberingStatus
            r['operator'] = status.numberingOperator
            r['lastUpdateTime'] = status.numberingUpdateDateTime if status.numberingStatus else ''
        elif (4 == processId):  # 测量称重环节
            r['status'] = status.measuringStatus
            r['operator'] = status.measuringOperator
            r['lastUpdateTime'] = status.measuringUpdateDateTime if status.measuringStatus else ''
        elif (6 == processId):  # 图像采集环节
            r['status'] = status.photographingStatus
            r['operator'] = status.photographingOperator
            r['lastUpdateTime'] = status.photographingUpdateDateTime if status.photographingStatus else ''
        elif (5 == processId):  # 实物认定环节
            r['operation'] = status.numberingStatus and status.measuringStatus and status.analyzingStatus
            r['status'] = status.checkingStatus
            r['operator'] = status.checkingOperator
            r['lastUpdateTime'] = status.checkingUpdateDateTime if status.checkingStatus else ''
        ret['rows'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)


def getThingInfo(request):
    serialNumber = request.POST.get('serialNumber', '')

    ret = {}
    try:
        thing = gsThing.objects.get(serialNumber=serialNumber)

        prop = thing.box.boxType
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

        level = thing.level
        ret['level'] = level
        if productType == '银元' and className == '标准银元' and subClassName == '国内银元':
            if level == '1':
                name = '国内珍品银元名称'
            elif level == '2':
                name = '国内稀一级银元名称'
            elif level == '3':
                name = '国内稀二级银元名称'
            elif level == '4':
                name = '国内稀三级银元名称'
            elif level == '5':
                name = '国内普制银元名称'
            else:
                name = ''
            detailedName = thing.detailedName
            if name and detailedName:
                ret['detailedName'] = gsProperty.objects.get(project=name, code=detailedName).type
        else:
            ret['detailedName'] = thing.detailedName
        ret['peroid'] = thing.peroid
        ret['year'] = thing.year
        ret['country'] = thing.country
        ret['originalQuantity'] = str(thing.originalQuantity)
        ret['mark'] = thing.mark
        ret['faceAmount'] = thing.faceAmount
        ret['dingSecification'] = thing.dingSecification
        ret['shape'] = thing.shape
        ret['shape'] = thing.shape
        ret['zhangType'] = thing.zhangType
        ret['appearance'] = thing.appearance
        ret['remark'] = thing.remark
    except Exception as e:
        pass
    ret_json = json.dumps(ret)
    return HttpResponse(ret_json)


# --------------------------------------------------------------------------
def getWorkSpaceContent(request):
    work_set = gsWork.objects.filter(status=1)
    ret = []
    for work in work_set:
        prop = work.box.boxType
        parentType = prop.parentType
        grandpaType = prop.grandpaType
        if grandpaType:
            productType = grandpaType
        else:
            productType = parentType
        r = {}
        t = None
        for t in ret:
            if t['text'] == productType:
                break
        else:  # 未存在对应实物类型，先初始化
            r['id'] = 0
            r['text'] = productType
            r['state'] = 'open'
            r['attributes'] = {'isWork': False}
            r['children'] = []
            ret.append(r)
            t = r
        # 已存在对应实物类型，可直接操作
        r = {}
        r['id'] = work.id
        r['text'] = work.workName
        r['iconCls'] = 'icon-box'
        r['attributes'] = {'isWork': True, 'boxNumber': work.box.boxNumber, 'workSeq': work.workSeq}
        t['children'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


# --------------------------------------------------------------------------
def searchThingInfo(request):
    serialNumber = request.POST.get('serialNumber', '')
    processId = int(request.POST.get('processId', ''))

    try:
        thing = gsThing.objects.get(serialNumber=serialNumber)
        work = thing.work
        box = thing.box
        boxNumber = box.boxNumber
        thing_set = gsThing.objects.filter(work=work)

        status = gsStatus.objects.get(thing=thing)
        if (2 == processId):
            # 外观信息采集环节
            thingStatus = status.numberingStatus
            thing_set2 = gsStatus.objects.filter(thing__in=thing_set, numberingStatus=thingStatus).values_list('thing',
                                                                                                               flat=True)
        if (3 == processId):
            # 频谱分析环节
            thingStatus = status.analyzingStatus
            thing_set2 = gsStatus.objects.filter(thing__in=thing_set, analyzingStatus=thingStatus).values_list('thing',
                                                                                                               flat=True)
        elif (4 == processId):
            # 测量称重环节
            thingStatus = status.measuringStatus
            thing_set2 = gsStatus.objects.filter(thing__in=thing_set, measuringStatus=thingStatus).values_list('thing',
                                                                                                               flat=True)
        elif (5 == processId):
            # 实物认定环节
            thingStatus = status.checkingStatus
            thing_set2 = gsStatus.objects.filter(thing__in=thing_set, checkingStatus=thingStatus).values_list('thing',
                                                                                                              flat=True)
        elif (6 == processId):
            # 图像采集环节
            thingStatus = status.photographingStatus
            thing_set2 = gsStatus.objects.filter(thing__in=thing_set, photographingStatus=thingStatus).values_list(
                'thing', flat=True)

        specialSerialNumberList = gsThing.objects.filter(id__in=thing_set2).values_list('serialNumber', flat=True)
        serialNumberList = list(specialSerialNumberList)
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
        ret['boxNumber'] = boxNumber

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
    isVerify = request.GET.get('isVerify', '')
    operator = request.GET.get('operator', '')
    # 检测是否是数据审核用, 以便显示相应的审核接口和修改接口
    if isVerify != '':
        isVerify = True
    box = gsBox.objects.get(boxNumber=boxNumber)
    thing = gsThing.objects.get(serialNumber=serialNumber)
    work = thing.work

    prop = box.boxType
    type = prop.type
    parentType = prop.parentType
    grandpaType = prop.grandpaType

    context = {}
    context['boxNumber'] = boxNumber
    context['serialNumber'] = serialNumber
    wareHouseCode = box.wareHouse
    wareHouse = gsProperty.objects.get(project='发行库', code=wareHouseCode)
    context['wareHouse'] = wareHouse.type
    if grandpaType:
        productType = grandpaType
        className = parentType
        subClassName = type
    else:
        productType = parentType
        className = type
        subClassName = '-'

    context['productType'] = productType
    context['className'] = className
    context['subClassName'] = subClassName
    # 档案建立时间与档案修改时间
    s = gsStatus.objects.get(thing=thing)
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
    picturePathPrefix = u'/static/photo/{0}/{1}/{2}'.format(boxNumber, serialNumber, serialNumber)
    context['A'] = u'{0}-A.jpg'.format(picturePathPrefix)
    context['B'] = u'{0}-B.jpg'.format(picturePathPrefix)
    context['C'] = u'{0}-C.jpg'.format(picturePathPrefix)

    faceAmountList = ['币', '元', '辅', '钱', '外元', '减元', '色元', '外国银元']
    dingList = ['锭']
    shapeList = ['工']
    zhangTypeList = ['章']
    yinyuanList = ['国内银元']
    dairongList = ['-', '']

    subClassName = context['subClassName']
    level = thing.level
    if level:
        context['level'] = gsProperty.objects.get(project='等级', code=level).type
    peroid = thing.peroid
    if peroid:
        context['peroid'] = gsProperty.objects.get(project='年代', code=peroid).type
    context['year'] = thing.year
    country = thing.country
    if country:
        context['country'] = gsProperty.objects.get(project='国别', code=country).type
    context['originalQuantity'] = thing.originalQuantity if thing.originalQuantity else ''
    context['detectedQuantity'] = thing.detectedQuantity if thing.detectedQuantity else ''
    context['mark'] = thing.mark if thing.mark else ''
    context['length'] = thing.length if thing.length else ''
    context['width'] = thing.width if thing.width else ''
    context['height'] = thing.height if thing.height else ''
    context['grossWeight'] = thing.grossWeight if thing.grossWeight else ''
    context['pureWeight'] = float('%0.2f' % (
    (thing.detectedQuantity * thing.grossWeight) / 100)) if thing.detectedQuantity and thing.grossWeight else ''
    context['productType'] = productType
    context['className'] = className
    context['subClassName'] = subClassName

    appearance = thing.appearance
    if appearance:
        context['appearance'] = gsProperty.objects.get(project='品相', code=appearance).type
    context['remark'] = thing.remark if thing.remark else ''

    if subClassName:
        if subClassName in faceAmountList:
            faceAmount = thing.faceAmount
            if faceAmount:
                context['faceAmount'] = gsProperty.objects.get(project='面值', code=faceAmount).type
            html = 'haveFaceAmount.html'
        elif subClassName in dingList:
            dingSecification = thing.dingSecification
            if dingSecification:
                context['dingSecification'] = gsProperty.objects.get(project='金银锭类规格', code=dingSecification).type
            if productType == '黄金' and subClassName == '锭':
                name = '金锭类形制'
            elif productType == '白银' and subClassName == '锭':
                name = '银锭类形制'
            elif subClassName == '工':
                name = '工艺品类器型'
            else:
                name = ''
            shape = thing.shape
            if name and shape:
                context['shape'] = gsProperty.objects.get(project=name, code=shape).type
            html = 'ding.html'
        elif subClassName in shapeList:
            shape = thing.shape
            if shape:
                context['shape'] = gsProperty.objects.get(project='工艺品类器型', code=shape).type
            html = 'gong.html'
        elif subClassName in zhangTypeList:
            zhangType = thing.zhangType
            if zhangType:
                context['zhangType'] = gsProperty.objects.get(project='章类性质', code=zhangType).type
            html = 'zhang.html'
        elif subClassName in yinyuanList:
            faceAmount = thing.faceAmount
            if faceAmount:
                context['faceAmount'] = gsProperty.objects.get(project='面值', code=faceAmount).type
            if productType == '银元' and className == '标准银元' and subClassName == '国内银元':
                if level == '1':
                    name = '国内珍品银元名称'
                elif level == '2':
                    name = '国内稀一级银元名称'
                elif level == '3':
                    name = '国内稀二级银元名称'
                elif level == '4':
                    name = '国内稀三级银元名称'
                elif level == '5':
                    name = '国内普制银元名称'
                else:
                    name = ''
                detailedName = thing.detailedName
                if name and detailedName:
                    context['detailedName'] = gsProperty.objects.get(project=name, code=detailedName).type
            html = 'yinyuan.html'
        elif subClassName in dairongList:
            html = 'dairong.html'
    else:
        pass

    serialNumberSet = gsThing.objects.filter(work=work).values_list('serialNumber', flat=True)
    serialNumberList = list(serialNumberSet)

    n = len(serialNumberList)
    first = 0
    last = n - 1
    context['first'] = serialNumberList[first]
    context['last'] = serialNumberList[last]
    currentIdx = serialNumberList.index(serialNumber)

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


# --------------------------------------------------------------------------
def getProductType(request):
    types = gsProperty.objects.filter(project='类别')
    ret = []
    for t in types:
        r = {}
        r['text'] = t.type
        r['id'] = t.code
        ret.append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def getClassName(request, code):
    classNames = gsProperty.objects.filter(project='品种', parentCode=code)
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
    subClassNames = gsProperty.objects.filter(project='品名', parentCode=classNameCode, grandpaCode=typeCode)
    ret = []
    if subClassNames:
        for s in subClassNames:
            r = {}
            r['text'] = s.type
            r['id'] = s.code
            ret.append(r)
    else:
        r = {}
        r['text'] = '-'
        r['id'] = ''
        ret.append(r)
    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)


def getOprateType(request):
    oprateType_qs = gsProperty.objects.filter(project='实物类型')
    ret = []
    for s in oprateType_qs:
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


def getTools(request):
    if request.method == 'POST':
        ret = {}
        file_dir = settings.TOOLS_DATA_PATH
        fileName_list = os.listdir(file_dir)
        ret['count'] = len(fileName_list)
        ret['row'] = []
        ret['success'] = True
        for fileName in fileName_list:
            r = {}
            r['fileName'] = fileName
            r['downloadURL'] = u'getTools/?fileName={0}'.format(fileName)
            ret['row'].append(r)
        ret_json = json.dumps(ret, separators=(',', ':'))

        return HttpResponse(ret_json)
    elif request.method == 'GET':
        fileName = request.GET.get('fileName', '')
        file_path = os.path.join(settings.TOOLS_DATA_PATH, fileName)
        response = StreamingHttpResponse(readFile(file_path))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={0}'.format(fileName)
        return response


# 录入铭文检测
def checkInfo(request):
    value = request.POST.get('value', '')

    ret = {}

    things = gsThing.objects.values_list('mark', flat=True)

    historyInfo = {}
    for thing in things:
        # if thing.startswith(value):
        if value in thing:
            historyInfo[thing] = historyInfo.get(thing, 0) + 1

    sortedClassCount = sorted(historyInfo.items(), key=operator.itemgetter(1), reverse=True)
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


def parse(data, name):
    detail = {}
    detail['name'] = name
    detail['val'] = []
    type_list = list(gsProperty.objects.filter(project=data).values_list('type', flat=True))
    code_list = list(gsProperty.objects.filter(project=data).values_list('code', flat=True))
    for type, code in zip(type_list, code_list):
        sub = {}
        sub['text'] = type
        sub['id'] = code
        detail['val'].append(sub)
    return detail


def getReadyInfo(request):
    productType = request.POST.get('productType', '')
    field = request.POST.get('field', '')

    field_list = field.split(';')

    ret = []

    if '等级' in field_list:
        data = name = '等级'
        detail = parse(data, name)
        ret.append(detail)
    if '年代' in field_list:
        data = name = '年代'
        detail = parse(data, name)
        ret.append(detail)
    if '国别' in field_list:
        data = name = '国别'
        detail = parse(data, name)
        ret.append(detail)
    if '面值' in field_list:
        data = name = '面值'
        detail = parse(data, name)
        ret.append(detail)
    if '规格' in field_list:
        data = '金银锭类规格'
        name = '规格'
        detail = parse(data, name)
        ret.append(detail)
    if '器型' in field_list:
        data = '工艺品类器型'
        name = '器型'
        detail = parse(data, name)
        ret.append(detail)
    if '型制' in field_list and productType == '黄金':
        data = '金锭类形制'
        name = '型制'
        detail = parse(data, name)
        ret.append(detail)
    if '型制' in field_list and productType == '白银':
        data = '银锭类形制'
        name = '型制'
        detail = parse(data, name)
        ret.append(detail)
    if '性质' in field_list:
        data = '章类性质'
        name = '性质'
        detail = parse(data, name)
        ret.append(detail)

    if '品相' in field_list:
        data = name = '品相'
        detail = parse(data, name)
        ret.append(detail)
    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)


def getDetailName(request):
    productType = request.POST.get('productType', '')
    className = request.POST.get('className', '')
    subClassName = request.POST.get('subClassName', '')
    level = request.POST.get('level', '')
    try:
        name = '名称'
        if productType == '银元' and className == '标准银元' and subClassName == '国内银元':
            if level == '1':
                data = '国内珍品银元名称'
            elif level == '2':
                data = '国内稀一级银元名称'
            elif level == '3':
                data = '国内稀二级银元名称'
            elif level == '4':
                data = '国内稀三级银元名称'
            elif level == '5':
                data = '国内普制银元名称'
            ret = parse(data, name)
        else:
            ret = {}
    except Exception as e:
        ret = {}
    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)
