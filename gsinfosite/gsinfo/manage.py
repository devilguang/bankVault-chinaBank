# encoding=UTF-8
import shutil
from django.shortcuts import render
from django.http.response import HttpResponse, StreamingHttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from utils import readFile, dateTimeHandler, deleteDir
from tag_process import *
from .report_process import *
from gsinfosite import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import datetime
from . import log
import MySQLdb
import win32print
import win32api
import requests
import uuid

@login_required
def manage(request):
    nickName = gsUser.objects.get(user=request.user)
    return render(request, 'manage.html', context={'operator': nickName, })


def createBox(request):
    productType = request.POST.get('productType', '')  # 实物类型
    className = request.POST.get('className', '')  # 品名
    subClassName = request.POST.get('subClassName', '')  # 明细品名
    wareHouse = request.POST.get('wareHouse', '')  # 发行库
    amount = int(request.POST.get('amount', ''))  # 件数
    grossWeight = request.POST.get('grossWeight', '')  # 毛重
    if grossWeight:
        grossWeight = float(grossWeight)
    else:
        grossWeight = float(0)

    # 从数据库中查最大箱号
    maxBoxNumber_obj = gsBox.objects.all().order_by('-boxNumber').first()
    if maxBoxNumber_obj:
        boxNumber = maxBoxNumber_obj.boxNumber+1
    else:
        boxNumber = 1

    # 向货发二代系统请求箱号和实物随机号
    '''
    要给货发二代系统的数据
    box_number = int(request.POST.get('boxNumber', ''))  # 箱号
    productType = request.POST.get('productType', '')  # 实物类型
    className = request.POST.get('className', '')  # 品名
    subClassName = request.POST.get('subClassName', '')  # 明细品名
    wareHouse = request.POST.get('wareHouse', '')  # 发行库
    amount = int(request.POST.get('amount', ''))  # 件数
    '''
    # 箱号由发行库代码，实物类别代码，品名代码，明细品名代码和箱序号五部分组成
    # 二代系统并不保存此时生成的序号数据，那么他就不知道箱的顺序号
    boxSeq = '-'.join([wareHouse, productType, className, subClassName, str(boxNumber)])

    thing_num_list = []
    for i in range(amount):
        thing_num_list.append(str(uuid.uuid4()))

    thing_num = '|'.join(thing_num_list)

    try:
        log.log(user=request.user, operationType=u'业务操作', content=u'新建{0}号箱实物'.format(boxNumber))

        box, createdBox = gsBox.objects.createBox(boxNumber=boxNumber, productType=productType, className=className,
                                                  subClassName=subClassName, wareHouse=wareHouse, amount=amount,
                                                  grossWeight=grossWeight,boxSeq=boxSeq,thing_num=thing_num)

        # 构造对应的存储目录结构
        boxRootDir = settings.DATA_DIRS['box_dir']
        boxDir = os.path.join(boxRootDir, str(boxNumber))
        if not os.path.exists(boxDir):
            os.mkdir(boxDir)

        # subBoxSeq = gsThing.objects.filter(box=box).first().subBoxSeq
        # now = datetime.datetime.now()
        # wareHouseCode = box.wareHouse
        # wareHouse = gsProperty.objects.get(project='发行库', code=wareHouseCode)
        # wordDir = os.path.join(boxDir, u'{0}_{1}_{2}_word'.format(now.year, subBoxSeq, wareHouse.type))
        # if (not os.path.exists(wordDir)):
        #     os.mkdir(wordDir)
        #
        # photoDir = os.path.join(boxDir, u'{0}_{1}_{2}_photo'.format(now.year, subBoxSeq, wareHouse.type))
        # if (not os.path.exists(photoDir)):
        #     os.mkdir(photoDir)

    except Exception as e:
        ret = {
            "success": False,
            "message": '{0}号箱实物新建失败！'.format(boxNumber)
        }
    else:
        ret = {
            'success': True,
            'message': '{0}号箱实物新建成功!'.format(boxNumber)
        }
    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)

# -----------------------------------------------
# 拆箱操作
def allotBox(request):
    boxNumber = int(request.POST.get('boxNumber', ''))  # 箱号
    fromSubBox = request.POST.get('fromSubBox', '')
    pageSize = int(request.POST.get('rows', ''))
    page = int(request.POST.get('page', ''))

    box = gsBox.objects.get(boxNumber=boxNumber)
    subBox = gsSubBox.objects.filter(box=box,isValid=True)
    if fromSubBox == '1' and not subBox:
        thing_set = gsThing.objects.filter(box=box)
    else:
        subBox = gsSubBox.objects.get(box=box,subBoxNumber=fromSubBox)
        thing_set = gsThing.objects.filter(box=box,subBox=subBox)
    num = len(thing_set)
    ret = {}
    ret['total'] = num
    ret['rows'] = []

    start = (page - 1) * pageSize
    end = num if (page * pageSize > num) else page * pageSize
    sub_thing_set = thing_set[start:end]
    for s in sub_thing_set:
        r = {}
        r['serialNumber'] = s.serialNumber
        ret['rows'].append(r)

    # 找出一个箱子所属的所有子箱
    all_subBox = gsSubBox.objects.filter(box=box,isValid=True).values_list('subBoxNumber', flat=True)
    ret['subBoxList'] = list(all_subBox)

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)
    return HttpResponse(ret_json)

# 确认拆箱操作
def confirmAllotBox(request):
    boxNumber = request.POST.get('boxNumber', '')
    selectedThings = request.POST.get('selectedThings', '')
    fromSubBox = int(request.POST.get('fromSubBox', ''))
    toSubBox = int(request.POST.get('toSubBox', ''))

    selected_serialNumber = selectedThings.split(';')[:-1]
    box = gsBox.objects.get(boxNumber=boxNumber)

    try:
        log.log(user=request.user, operationType=u'业务操作', content=u'对{0}号箱进行拆箱'.format(boxNumber))
        if fromSubBox == 1 and toSubBox == 1 and not gsSubBox.objects.filter(box=box):
            all_serialNumber = gsThing.objects.filter(box=box).values_list('serialNumber', flat=True)
            all_serialNumber = list(all_serialNumber)
            other_serialNumber = []
            for serialNumber in all_serialNumber:
                if serialNumber not in selected_serialNumber:
                    other_serialNumber.append(serialNumber)

            subBox1 = gsSubBox.objects.create(subBoxNumber=1, box=box, isValid=True)
            subBox2 = gsSubBox.objects.create(subBoxNumber=2, box=box, isValid=True)
            gsThing.objects.filter(box=box, serialNumber__in=other_serialNumber).update(subBox=subBox1)
            gsThing.objects.filter(box=box, serialNumber__in=selected_serialNumber).update(subBox=subBox2)
        elif fromSubBox == 1 and toSubBox == 1 and gsSubBox.objects.filter(box=box):
            maxSubBoxNumber = gsSubBox.objects.filter(box=box).order_by('-subBoxNumber').first().subBoxNumber
            subBox = gsSubBox.objects.create(subBoxNumber=maxSubBoxNumber+1, box=box, isValid=True)
            gsThing.objects.filter(box=box, serialNumber__in=selected_serialNumber).update(subBox=subBox)
        else:
            subBox = gsSubBox.objects.get(subBoxNumber=toSubBox, box=box, isValid=True)
            gsThing.objects.filter(box=box, serialNumber=selected_serialNumber).update(subBox=subBox)
    except Exception as e:
        ret = {
            "success": False,
            "message": '{0}号箱拆箱失败！\r\n原因：{1}'.format(boxNumber, e.message)
        }
    else:
        ret = {
            'success': True,
            'message': '{0}号箱拆箱成功!'.format(boxNumber)
        }
    ret_json = json.dumps(ret)

    return HttpResponse(ret_json)


# -----------------------------------------------
# 并箱操作
def mergeBox(request):
    boxNumber = int(request.POST.get('boxNumber', ''))  # 箱号

    ret = {}
    box = gsBox.objects.get(boxNumber=boxNumber)

    all_subBox = gsSubBox.objects.filter(box=box,isValid=True).values_list('subBoxNumber',flat=True)
    allSubBox = list(all_subBox)
    if allSubBox:
        ret['subBoxList'] = allSubBox
    else:
        ret['subBoxList'] = []
    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)
    return HttpResponse(ret_json)

# 确认并箱操作
def confirmMergeBox(request):
    boxNumber = int(request.POST.get('boxNumber', ''))  # 箱号
    originSubBox = request.POST.get('originSubBox', '')
    boxList = originSubBox.split(';')[:-1]
    box = gsBox.objects.get(boxNumber=boxNumber)
    currentMaxNo = int(gsSubBox.objects.filter(box=box).order_by('-subBoxNumber').first().subBoxNumber)
    try:
        log.log(user=request.user, operationType=u'业务操作', content=u'对{0}号箱的{1}子箱进行并箱'.format(boxNumber,boxList))
        newSubBox = gsSubBox.objects.create(subBoxNumber=currentMaxNo + 1,box=box,isValid=True)  # 新建一个
        for no in boxList:
            oldSubBox_set = gsSubBox.objects.filter(box=box, subBoxNumber=no)
            oldSubBox_set.update(isValid=False)  # 将之前的置为无效
            oldSubBox = oldSubBox_set[0]
            gsThing.objects.filter(box=box, subBox=oldSubBox).update(subBox=newSubBox,historyNo=oldSubBox.pk)

    except Exception as e:
        print e
        ret = {
            "success": False,
            "message": '{0}号箱并箱失败！\r\n原因：{1}'.format(boxNumber, e.message)
        }
    else:
        ret = {
            'success': True,
            'message': '{0}号箱并箱成功!'.format(boxNumber)
        }
    ret_json = json.dumps(ret)

    return HttpResponse(ret_json)
# -----------------------------------------------
# 箱体信息报表打印
# 1.获取所有箱子信息
def getAllBox(request):
    box_id = gsSubBox.objects.filter().values_list('box_id')
    boxId = set(box_id)
    ret={}
    ret['rows'] = []
    for b in boxId:
        b = gsBox.objects.get(id=b[0])  # 箱子中所有实物都已完成各步骤
        r = {}
        r['boxNumber'] = b.boxNumber
        r['productType'] = gsProperty.objects.get(project=u'实物类型',code=b.productType).type
        r['className'] = gsProperty.objects.get(project=u'品名', code=b.className,parentType=r['productType']).type
        r['subClassName'] = gsProperty.objects.get(project=u'明细品名', code=b.subClassName,parentType=r['className'],grandpaType=r['productType']).type
        r['wareHouse'] = gsProperty.objects.get(project=u'发行库', code=b.wareHouse).type
        r['amount'] = b.amount
        ret['rows'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)
    return HttpResponse(ret_json)

# 2.生成报表信息
def processInfo(request):
    map0 = request.GET.get('map','')  # {'1':u'金银锭类','2':u'金银币章类'}
    boxList = json.loads(map0)

    ret = []
    for boxNumber,productType in boxList.items():
        boxNumber = int(boxNumber)
        boxLevel = {}
        boxLevel['subBox'] = []
        box = gsBox.objects.get(boxNumber=boxNumber)
        subBoxList = gsSubBox.objects.filter(box=box,isValid=True).values_list('subBoxNumber',flat=True)
        for no in subBoxList:
            subBox = {}
            subBox['subBoxNo'] = no
            subBox_set = gsSubBox.objects.filter(box=box,subBoxNumber=no)
            things_num = gsThing.objects.filter(box=box,subBox=subBox_set).count()
            subBox['amount'] = things_num
            totalWeight = gsSubBox.objects.get(box=box,subBoxNumber=no).grossWeight
            subBox['totalWeight'] = totalWeight
            boxLevel['subBox'].append(subBox)

        boxLevel['boxNumber']= boxNumber

        boxLevel['amount'] = box.amount
        boxLevel['totalWeight'] = box.grossWeight
        ret.append(boxLevel)

    fileName = createBoxTable(boxList)
    box_dir = os.path.join(settings.DATA_DIRS['box_dir'], u'箱体报表')
    file_path = os.path.join(box_dir, fileName)

    log.log(user=request.user, operationType=u'业务操作', content=u'箱体报表打印')
    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)
    return render(request, 'report.html', context={'ret': ret_json,'file_path': file_path})


def downloadBoxInfo(request):
    fileName = request.GET.get('fileName', '')
    log.log(user=request.user, operationType=u'业务操作', content=u'箱体报表下载')
    box_dir = os.path.join(settings.DATA_DIRS['box_dir'], u'箱体报表')
    filePath = os.path.join(box_dir, fileName)

    response = StreamingHttpResponse(readFile(filePath))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename={0}'.format(fileName)

    return response

# -----------------------------------------------
# 包号二维码打印
# def packageQR(request):
#     boxOrSubBox = '1-5'  # request.POST.get('boxNumber', '')
#
#     if '-' in boxOrSubBox:
#         boxNumber = int(boxOrSubBox.split('-')[0])
#         subBoxNumber = int(boxOrSubBox.split('-')[1])
#     else:
#         boxNumber = int(boxOrSubBox)
#         subBoxNumber = ''
#     log.log(user=request.user, operationType=u'业务操作', content=u'包号二维码打印')
#     box = gsBox.objects.get(boxNumber=boxNumber)
#     if subBoxNumber == '':
#         packageNo = gsThing.objects.filter(box=box).values_list('packageNo', flat=True)
#         packageList = list(set(packageNo))
#     else:
#         subBox = gsSubBox.objects.filter(box=box, subBoxNumber=subBoxNumber)
#         packageNo = gsThing.objects.filter(box=box,subBox=subBox).values_list('packageNo', flat=True)
#         packageList = list(set(packageNo))
#
#     packageTag(boxNumber,subBoxNumber,packageList)
#     ret = {
#             'success': True,
#         }
#
#     ret_json = json.dumps(ret, separators=(',', ':'))
#
#     return HttpResponse(ret_json)

# -----------------------------------------------
# # 点击开箱出库弹出二维码
# def getBoxQR(request):
#     boxNumber = 4  # int(request.POST.get('boxNumber', ''))  # 父箱号
#     subBoxNumber = 1  # request.POST.get('boxNumber', '')  # 子箱号
#     ret={}
#     if subBoxNumber == '':
#         picName = u'{0}号箱标签.png'.format(boxNumber)
#     else:
#         picName = u'{0}-{1}号箱标签.png'.format(boxNumber, subBoxNumber)
#
#     tagRootDir = settings.DATA_DIRS['tag_dir']
#     ret['picPath'] = os.path.join(tagRootDir, str(boxNumber),'boxQRpictures',picName)
#     ret_json = json.dumps(ret, separators=(',', ':'))
#     return HttpResponse(ret_json)

# 封箱入库 和 开箱出库
def boxInOutStore(request):
    boxOrSubBox = request.POST.get('boxNumber', '')
    status = int(request.POST.get('status', ''))  # 1: 封箱入库 0: 提取出库
    nickName = request.POST.get('user', '')  # 系统负责人用户名
    password = request.POST.get('password', '')  # 系统负责人密码
    txtQR = request.POST.get('txtQR', '')

    if '-' in boxOrSubBox:
        boxNumber = int(boxOrSubBox.split('-')[0])
        subBoxNumber = int(boxOrSubBox.split('-')[1])
    else:
        boxNumber = int(boxOrSubBox)
        subBoxNumber = ''

    if status == 1:
        user = request.user
        userName = gsUser.objects.get(user=user).nickName

        if '-' in boxOrSubBox:
            boxNumber = int(boxOrSubBox.split('-')[0])
            subBoxNumber = int(boxOrSubBox.split('-')[1])
        else:
            boxNumber = int(boxOrSubBox)
            subBoxNumber = ''

        def printOrNot(printtimes, boxNumber, userName, subBoxNumber):
            if int(printtimes) == 0:
                log.log(user=request.user, operationType=u'业务操作', content=u'箱体二维码打印')
                boxTag(boxNumber, userName, subBoxNumber)
                if subBoxNumber == '':  # 原箱
                    gsBox.objects.filter(boxNumber=boxNumber).update(scanTimes=0)
                else:  # 子箱
                    box = gsBox.objects.get(boxNumber=boxNumber)
                    gsSubBox.objects.filter(box=box, subBoxNumber=subBoxNumber).update(
                        scanTimes=0)
                ret = {
                    'success': True,
                    'message': u'打印成功！'
                }
            else:
                ret = {
                    "success": False,
                    "message": u'该箱体的二维码已被打印过一次！'
                }
            return ret

        custom_user = gsUser.objects.filter(nickName=nickName)
        if custom_user:
            custom_user = custom_user[0]
            if int(custom_user.type) == 0:
                username = custom_user.user.username
                user = auth.authenticate(username=username, password=password)
                if user:  # 通过系统管理员授权后先打印二维码后封箱入库
                    box = gsBox.objects.get(boxNumber=boxNumber)
                    if subBoxNumber == '':  # 原箱
                        printtimes = box.printTimes
                        ret = printOrNot(printtimes, boxNumber, userName, subBoxNumber)
                        gsBox.objects.filter(boxNumber=boxNumber).update(printTimes=printtimes + 1)

                        try:
                            if gsWork.objects.filter(box=box, status=1).exists():  # 存在作业未收回, 不能封箱入库
                                raise ValueError(u'{0}号箱存在作业未收回，不能封箱入库！请前往:业务管理->作业管理，收回作业！'.format(boxNumber))
                            gsBox.objects.filter(boxNumber=boxNumber).update(status=True)
                            log.log(user=request.user, operationType=u'业务操作', content=u'封箱入库')
                        except Exception as e:
                            ret = {
                                "success": False,
                                "message": '{0}号箱实物封箱入库失败！\r\n原因：{1}'.format(boxNumber, e.message)
                            }
                        else:
                            ret = {
                                'success': True,
                                'message': '{0}号箱实物封箱入库成功!'.format(boxNumber)
                            }
                    else:  # 子箱
                        subBox = gsSubBox.objects.get(box=box, subBoxNumber=subBoxNumber)
                        printtimes = subBox.printTimes
                        ret = printOrNot(printtimes, boxNumber, userName, subBoxNumber)
                        gsSubBox.objects.filter(box=box, subBoxNumber=subBoxNumber).update(printTimes=printtimes + 1)
                        subBox = gsSubBox.objects.get(box=box, subBoxNumber=subBoxNumber)
                        try:
                            if gsWork.objects.filter(box=box, subBox=subBox, status=1).exists():  # 存在作业未收回, 不能封箱入库
                                raise ValueError(u'{0}号箱存在作业未收回，不能封箱入库！请前往:业务管理->作业管理，收回作业！'.format(boxNumber))
                            gsSubBox.objects.filter(box=box, subBoxNumber=subBoxNumber).update(status=True)
                            if not gsSubBox.objects.filter(box=box, isValid=True, status=False).exists():
                                gsBox.objects.filter(boxNumber=boxNumber).update(status=True)
                            log.log(user=request.user, operationType=u'业务操作', content=u'封箱入库')
                        except Exception as e:
                            ret = {
                                "success": False,
                                "message": '{0}号箱实物封箱入库失败！\r\n原因：{1}'.format(boxNumber, e.message)
                            }
                        else:
                            ret = {
                                'success': True,
                                'message': '{0}号箱实物封箱入库成功!'.format(boxNumber)
                            }

                else:
                    ret = {
                        "success": False,
                        "message": u'密码错误！'
                    }
            else:
                ret = {
                    "success": False,
                    "message": u'该用户无此权限！'
                }
        else:
            ret = {
                'success': False,
                'message': u'用户名错误！'
            }
        #-----
    elif status == 0:
        box = gsBox.objects.get(boxNumber=boxNumber)
        if subBoxNumber == '':
            trueQRtxt = box.txtQR
            scanTimes = box.scanTimes
        else:
            subBox = gsSubBox.objects.get(box=box, subBoxNumber=subBoxNumber)
            trueQRtxt= subBox.txtQR
            scanTimes = subBox.scanTimes

        if txtQR == trueQRtxt:
            if scanTimes == 0:
                if subBoxNumber == '':
                    try:
                        log.log(user=request.user, operationType=u'业务操作', content=u'开箱出库')
                        gsBox.objects.filter(boxNumber=boxNumber).update(scanTimes=scanTimes + 1,printTimes=0,status=False)
                    except Exception as e:
                        ret = {
                            "success": False,
                            "message": '{0}号箱实物封箱入库失败！\r\n原因：{1}'.format(boxNumber, e.message)
                        }
                    else:
                        ret = {
                            'success': True,
                            'message': '{0}号箱实物封箱入库成功!'.format(boxNumber)
                        }
                else:
                    try:
                        log.log(user=request.user, operationType=u'业务操作', content=u'开箱出库')
                        gsSubBox.objects.filter(box=box, subBoxNumber=subBoxNumber).update(scanTimes=scanTimes+1,printTimes=0,status=False)

                        if not gsSubBox.objects.filter(box=box, isValid=True, status=True).exists():
                            gsBox.objects.filter(boxNumber=boxNumber).update(status=False)
                    except Exception as e:
                        ret = {
                            "success": False,
                            "message": '{0}号箱实物封箱入库失败！\r\n原因：{1}'.format(boxNumber, e.message)
                        }
                    else:
                        ret = {
                            'success': True,
                            'message': '{0}号箱实物封箱入库成功!'.format(boxNumber)
                        }
            else:
                if subBoxNumber == '':
                    gsBox.objects.filter(boxNumber=boxNumber).update(scanTimes=scanTimes + 1)
                else:
                    gsSubBox.objects.filter(box=box, subBoxNumber=subBoxNumber).update(scanTimes=scanTimes+1)
                ret = {
                    "success": False,
                    "message": '开箱出库失败，已报警！'
                }
        else:
            if subBoxNumber == '':
                gsBox.objects.filter(boxNumber=boxNumber).update(scanTimes=scanTimes + 1)
            else:
                gsSubBox.objects.filter(box=box, subBoxNumber=subBoxNumber).update(scanTimes=scanTimes + 1)
            ret = {
                "success": False,
                "message": '开箱出库失败，二维码信息有误！'
            }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)

# def boxInOutStore(request):
#     boxNumber = int(request.POST.get('boxNumber', ''))
#     status = int(request.POST.get('status', ''))  # 1: 封箱入库 0: 提取出库
#     try:
#         box = gsBox.objects.get(boxNumber=boxNumber)
#         if gsWork.objects.filter(box=box, status=1).exists():
#             # 存在作业未收回, 不能封箱入库
#             raise ValueError(u'{0}号箱存在作业未收回，不能封箱入库！请前往:业务管理->作业管理，收回作业！'.format(boxNumber))
#
#         gsBox.objects.filter(boxNumber=boxNumber).update(status=True if status != 0 else False)
#     except Exception as e:
#         ret = {
#             "success": False,
#             "message": '{0}号箱实物封箱入库失败！\r\n原因：{1}'.format(boxNumber,
#                                                          e.message) if status != 0 else '{0}号箱实物开箱出库失败！\r\n原因：{1}'.format(
#                 boxNumber, e.message)
#         }
#     else:
#         ret = {
#             'success': True,
#             'message': '{0}号箱实物封箱入库成功!'.format(boxNumber) if status != 0 else '{0}号箱实物开箱出库成功'.format(boxNumber)
#         }
#
#     ret_json = json.dumps(ret, separators=(',', ':'))
#
#     return HttpResponse(ret_json)
# -----------------------------------------------
# 修改毛重
def weightBox(request):
    boxOrSubBox = request.POST.get('boxNumber', '')
    grossWeight = request.POST.get('weight', '')

    if '-' in boxOrSubBox:
        boxNumber = int(boxOrSubBox.split('-')[0])
        subBoxNumber = int(boxOrSubBox.split('-')[1])
    else:
        boxNumber = int(boxOrSubBox)
        subBoxNumber = ''


    try:
        if subBoxNumber == '':
            gsBox.objects.filter(boxNumber=boxNumber).update(grossWeight=float(grossWeight))
        else:
            box = gsBox.objects.filter(boxNumber=boxNumber)
            gsSubBox.objects.filter(box=box, subBoxNumber=subBoxNumber).update(grossWeight=float(grossWeight))
    except Exception,e:
        ret = {
            "success": False,
            }
    else:
        ret = {
                'success': True,
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
                                                      startSeq=startSeq,subBoxNumber=subBoxNumber)

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
    boxNumber = int(request.POST.get('boxNumber', ''))

    try:
        deletedBox = gsBox.objects.deleteBox(boxNumber=boxNumber)

        boxRootDir = settings.DATA_DIRS['box_dir']
        boxDir = os.path.join(boxRootDir, str(boxNumber))
        if (os.path.exists(boxDir)):
            deleteDir(boxDir)

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
        bs = gsBox.objects.filter(status=0)
    else:
        bs = gsBox.objects.filter(status=1)
        subBox = gsSubBox.objects.filter(isValid=1,status=1).values('box_id')
        for sb in subBox:
            box = gsBox.objects.filter(id=sb.values()[0])
            bs = bs | box  # QuerySet用 | 或 chain求并集

    # 按查询条件进行筛选
    if productType:
        bs = bs.filter(productType=productType)
    if className:
        bs = bs.filter(className=className)
    if subClassName:
        bs = bs.filter(subClassName=subClassName)
    n = bs.count()

    pageSize = int(pageSize)
    page = int(page)
    start = (page - 1) * pageSize
    end = n if (page * pageSize > n) else page * pageSize

    ret = {}
    ret['total'] = n
    ret['rows'] = []
    for b in bs[start:end]:
        r = {}
        r['boxNumber'] = b.boxNumber
        box = gsBox.objects.get(boxNumber=b.boxNumber)
        subBoxList = gsSubBox.objects.filter(box=box,isValid=True).values_list('subBoxNumber',flat=True)
        if subBoxList:
            r['haveSubBox'] = '1'  # 有子箱
            r2 = {}
            for i in subBoxList:
                subBox = gsSubBox.objects.get(box=box, subBoxNumber=int(i))
                if status == 0 and subBox.status == 0:
                    thingCount = gsThing.objects.filter(box=box, subBox=subBox).count()
                    r2[i] = thingCount
                if status == 1 and subBox.status == 1:
                    thingCount = gsThing.objects.filter(box=box, subBox=subBox).count()
                    r2[i] = thingCount
            r['subBoxDict'] = r2
        else:
            r['haveSubBox'] = '0'  # 无子箱

        productType = gsProperty.objects.get(project='实物类型', code=b.productType)
        r['productType'] = productType.type

        className = gsProperty.objects.get(project='品名', code=b.className, parentProject=productType.project,
                                           parentType=productType.type)
        r['className'] = className.type

        subClassName = gsProperty.objects.get(project='明细品名', code=b.subClassName, parentProject=className.project,
                                              parentType=className.type, grandpaProject=productType.project,
                                              grandpaType=productType.type)
        r['subClassName'] = subClassName.type

        wareHouse = gsProperty.objects.get(project='发行库', code=b.wareHouse)
        r['wareHouse'] = wareHouse.type

        r['amount'] = b.amount
        ret['rows'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)


def getThing(request):
    boxOrSubBox = request.POST.get('boxNumber', '')
    pageSize = request.POST.get('rows', '')
    page = request.POST.get('page', '')
    isAllocated = request.POST.get('thingIsAllocated', '')

    if '-' in boxOrSubBox:
        boxNumber = int(boxOrSubBox.split('-')[0])
        subBoxNumber = int(boxOrSubBox.split('-')[1])
        returnBoxNumber = '{0}-{1}'.format(boxNumber, subBoxNumber)
    else:
        boxNumber = int(boxOrSubBox)
        subBoxNumber = ''
        returnBoxNumber = boxNumber


    box = gsBox.objects.get(boxNumber=boxNumber)
    if subBoxNumber == '':
        if isAllocated == 'notAllocated':
            ts = gsThing.objects.filter(box=box, isAllocate=False)
        elif isAllocated == 'allocated':
            ts = gsThing.objects.filter(box=box, isAllocate=True)
        else:
            ts = gsThing.objects.filter(box=box)
    else:
        subBox = gsSubBox.objects.filter(box=box, subBoxNumber=subBoxNumber)
        if isAllocated == 'notAllocated':

            ts = gsThing.objects.filter(box=box,subBox=subBox, isAllocate=False)
        elif isAllocated == 'allocated':
            ts = gsThing.objects.filter(box=box,subBox=subBox, isAllocate=True)
        else:
            ts = gsThing.objects.filter(box=box,subBox=subBox)

    ret = {}
    n = ts.count()
    ret['total'] = n

    pageSize = int(pageSize)
    page = int(page)
    start = (page - 1) * pageSize
    end = n if (page * pageSize > n) else page * pageSize

    ret['rows'] = []
    for t in ts[start:end]:
        r = {}
        r['serialNumber'] = t.serialNumber
        r['boxNumber'] = returnBoxNumber

        productType = gsProperty.objects.get(project='实物类型', code=t.box.productType)
        r['productType'] = productType.type

        className = gsProperty.objects.get(project='品名', code=t.box.className, parentProject=productType.project,
                                           parentType=productType.type)
        r['className'] = className.type

        subClassName = gsProperty.objects.get(project='明细品名', code=t.box.subClassName, parentProject=className.project,
                                              parentType=className.type, grandpaProject=productType.project,
                                              grandpaType=productType.type)
        r['subClassName'] = subClassName.type

        wareHouse = gsProperty.objects.get(project='发行库', code=t.box.wareHouse)
        r['wareHouse'] = wareHouse.type

        ret['rows'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)


def generateWorkName(request):
    boxOrSubBox = request.GET.get('boxNumber', '')
    if '-' in boxOrSubBox:
        boxNumber = int(boxOrSubBox.split('-')[0])
        subBoxNumber = int(boxOrSubBox.split('-')[1])
    else:
        boxNumber = int(boxOrSubBox)
        subBoxNumber = ''

    box = gsBox.objects.get(boxNumber=int(boxNumber))
    ws = gsWork.objects.filter(box=box).order_by('-workSeq').first()
    if ws:
        workSeq = ws.workSeq + 1
    else:
        workSeq = 1

    now = datetime.datetime.now()
    workName = u'{0}年{1}月{2}日{3}号箱作业{4}'.format(now.year, now.month, now.day, boxOrSubBox, workSeq)
    ret = {
        'workName': workName,
    }
    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def generateContentForWork(request):
    boxNumber = int(request.POST.get('boxNumber', ''))
    amount = request.POST.get('amount', '')

    if 0 == cmp(amount, ''):
        amount = 0
    else:
        amount = int(amount)

    box = gsBox.objects.get(boxNumber=boxNumber)
    ts = gsThing.objects.filter(box=box, isAllocate=False)
    specialSerialNumberList = ts.values_list('serialNumber', flat=True)

    ret = {}
    ret['data'] = []
    for serialNumber in specialSerialNumberList[:amount]:
        r = {}
        r['serialNumber'] = serialNumber
        ret['data'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def createWork(request):
    boxOrSubBox = request.POST.get('boxNumber', '')
    workName = request.POST.get('workName', '')
    selectedThings = request.POST.get('selectedThings', '')
    operator = request.POST.get('operator', '')
    thingSet = selectedThings.split(';')[:-1]

    if '-' in boxOrSubBox:
        boxNumber = int(boxOrSubBox.split('-')[0])
        subBoxNumber = int(boxOrSubBox.split('-')[1])
    else:
        boxNumber = int(boxOrSubBox)
        subBoxNumber = ''

    try:
        gsWork.objects.createWork(operator=operator, workName=workName, boxNumber=boxNumber, subBoxNumber=subBoxNumber, thingSet=thingSet)
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
    subBoxNumber = request.POST.get('subBoxNumber', '')

    try:
        gsWork.objects.deleteWork(boxNumber=boxNumber, workSeq=workSeq,subBoxNumber=subBoxNumber)
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

    bs = gsBox.objects.filter(status=status)
    ws = gsWork.objects.filter(box__in=bs)
    # 按查询条件进行筛选
    if productType != '':
        bs = gsBox.objects.filter(productType=productType)
    if className != '':
        bs = bs.filter(className=className)
    if subClassName != '':
        bs = bs.filter(subClassName=subClassName)

    if productType != '' or subClassName != '' or subClassName != '':
        specialBoxIdList = bs.values_list('id', flat=True)
        ws = ws.filter(box__in=specialBoxIdList)

    n = ws.count()

    pageSize = int(pageSize)
    page = int(page)
    start = (page - 1) * pageSize
    end = n if (page * pageSize > n) else page * pageSize

    ret = {}
    ret['total'] = n
    ret['rows'] = []
    for work in ws[start:end]:
        r = {}
        r['id'] = work.id
        r['workName'] = work.workName
        r['workSeq'] = work.workSeq
        r['boxNumber'] = work.box.boxNumber
        r['subBoxNumber'] = work.subBox.subBoxNumber if work.subBox else ''
        r['createDateTime'] = work.createDateTime
        r['completeDateTime'] = work.completeDateTime if work.completeDateTime is not None else ''
        r['status'] = work.status
        work_thing = gsThing.objects.filter(work=work)

        r['amount'] = work_thing.count()
        ss = gsStatus.objects.filter(thing__in=work_thing)
        r['checkingCompleteAmount'] = ss.filter(checkingStatus=True).count()
        r['numberingCompleteAmount'] = ss.filter(numberingStatus=True).count()
        r['analyzingCompleteAmount'] = ss.filter(analyzingStatus=True).count()
        r['measuringCompleteAmount'] = ss.filter(measuringStatus=True).count()
        r['photographingCompleteAmount'] = ss.filter(photographingStatus=True).count()

        r['completePercent'] = float('%0.2f' % (ss.filter(status=True).count() * 100 / ss.count())) if (
            0 != ss.count()) else 0
        ret['rows'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)


def startOrStopWork(request):
    boxNumber = request.POST.get('boxNumber', '')
    subBoxNumber = request.POST.get('subBoxNumber', '')
    workSeq = request.POST.get('workSeq', '')
    workName = request.POST.get('workName', '')
    status = int(request.POST.get('status', ''))

    try:
        # status: 1:分发操作 0:收回操作
        box = gsBox.objects.get(boxNumber=boxNumber)
        if subBoxNumber:
            subBox = gsSubBox.objects.get(box=box,subBoxNumber=subBoxNumber)
            work = gsWork.objects.get(box=box, workSeq=workSeq,subBox=subBox)
            gsWork.objects.filter(workSeq=workSeq, box=box,subBox=subBox).update(status=status)
        else:
            work = gsWork.objects.get(box=box, workSeq=workSeq)
            gsWork.objects.filter(workSeq=workSeq, box=box).update(status=status)

        if status == 0:
            # 收回操作时, 检查作业是否完成. 若已完成, 则更新作业完成时间
            work_things = gsThing.objects.filter(work=work)
            status_set = gsStatus.objects.filter(thing__in=work_things, status=True)
            t = []
            if work_things.count() == status_set.count():
                # 作业所属实物均清点查验完毕
                try:
                    numberingLatest = status_set.latest('numberingUpdateDateTime')  # 取最近的/最新的一个对象，注意是一个对象
                except Exception as e:
                    dateTime1 = None
                else:
                    dateTime1 = numberingLatest.numberingUpdateDateTime
                    t.append(dateTime1)

                try:
                    analyzingLatest = status_set.latest('analyzingUpdateDateTime')
                except Exception as e:
                    dateTime2 = None
                else:
                    dateTime2 = analyzingLatest.analyzingUpdateDateTime
                    t.append(dateTime2)

                try:
                    measuringLatest = status_set.latest('measuringUpdateDateTime')
                except Exception as e:
                    dateTime3 = None
                else:
                    dateTime3 = measuringLatest.measuringUpdateDateTime
                    t.append(dateTime3)

                try:
                    checkingLatest = status_set.latest('checkingUpdateDateTime')
                except Exception as e:
                    dateTime4 = None
                else:
                    dateTime4 = checkingLatest.checkingUpdateDateTime
                    t.append(dateTime4)

                try:
                    photographingLatest = status_set.latest('photographingUpdateDateTime')
                except Exception as e:
                    dateTime5 = None
                else:
                    dateTime5 = photographingLatest.photographingUpdateDateTime
                    t.append(dateTime5)

                def getTimeStemp(t):
                    return t.microsecond

                if t:
                    t_list = map(getTimeStemp, t)
                    max_index = t_list.index(max(t_list))
                    workCompleteDateTime = t[max_index]
                else:
                    workCompleteDateTime = None
                    work.update(completeDateTime=workCompleteDateTime)
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
            'file_path':file_path
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

        ret = createThingAbstract(workName,subBoxNumber, boxNumber, workSeq)

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
        boxNumber =int(request.POST.get('boxNumber', ''))
        workSeq = int(request.POST.get('workSeq', ''))
        dateTime = request.POST.get('dateTime', '')
        subBoxNumber = request.POST.get('subBoxNumber', '')

        createArchivesFromWork(boxNumber,subBoxNumber, workSeq, dateTime)  # 生成文件

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
        boxOrSubBox = request.POST.get('boxNumber', '')
        dateTime = request.POST.get('dateTime', '')

        if '-' in boxOrSubBox:
            boxNumber = boxOrSubBox.split('-')[0]
            subBoxNumber = boxOrSubBox.split('-')[1]
        else:
            boxNumber = int(boxOrSubBox)
            subBoxNumber = ''

        boxInfoFileName = createBoxInfo(boxNumber,subBoxNumber, dateTime)
        box_dir = os.path.join(settings.DATA_DIRS['box_dir'], str(boxNumber))
        file_path = os.path.join(box_dir, boxInfoFileName)


        # downloadURL = ''
        # downloadURL = downloadURL + u'<a href="generateBoxInfo/?boxNumber={0}&boxInfoFileName={1}" style="margin-right:20px">{2}</a>'.format(
        #     boxNumber, boxInfoFileName, boxInfoFileName)

        ret = {
            'success': True,
            # 'downloadURL': downloadURL,
            'file_path':file_path,
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
        boxOrSubBox = '1-1'  # request.POST.get('boxNumber', '')
        dateTime = '07/08/2017'  # request.POST.get('dateTime', '')
        if '-' in boxOrSubBox:
            boxNumber = boxOrSubBox.split('-')[0]
            subBoxNumber = boxOrSubBox.split('-')[1]
        else:
            boxNumber = int(boxOrSubBox)
            subBoxNumber = ''

        boxInfoFileName = createBoxInfoDetailedVersion(boxNumber,subBoxNumber, dateTime)

        box_dir = os.path.join(settings.DATA_DIRS['box_dir'], boxNumber)
        file_path = os.path.join(box_dir, boxInfoFileName)

        # downloadURL = ''
        # downloadURL = downloadURL + u'<a href="generateBoxInfoDetailedVersion/?boxNumber={0}&boxInfoFileName={1}" style="margin-right:20px">{2}</a>'.format(
        #     boxNumber, boxInfoFileName, boxInfoFileName)

        ret = {
            'success': True,
            # 'downloadURL': downloadURL,
            'file_path':file_path,
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
    boxOrSubBox = request.POST.get('boxNumber', '')
    pageSize = int(request.POST.get('rows', ''))
    page = int(request.POST.get('page', ''))

    if '-' in boxOrSubBox:
        boxNumber = int(boxOrSubBox.split('-')[0])
        subBoxNumber = int(boxOrSubBox.split('-')[1])
    else:
        boxNumber = int(boxOrSubBox)
        subBoxNumber = ''

    box = gsBox.objects.get(boxNumber=boxNumber)

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

    subBox = gsSubBox.objects.filter(box=box,subBoxNumber=subBoxNumber)
    work_set = gsWork.objects.filter(box=box,subBox=subBox)
    work_serialNumberList = gsThing.objects.filter(work__in=work_set).values_list('serialNumber', flat=True)

    if subBoxNumber == '':
        ts = gsThing.objects.filter(box=box)
    else:
        ts = gsThing.objects.filter(box=box,subBox=subBox)
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
        if subBoxNumber != '':
            r['subBoxNumber'] = subBoxNumber
        else:
            r['subBoxNumber'] = '0'
        r['productType'] = productType.type
        r['className'] = className.type
        r['subClassName'] = subClassName.type
        r['wareHouse'] = wareHouse.type
        if (serialNumber in work_serialNumberList):
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
    items = [{'sig':'','key':'seq','symbol':'<','value':'10'},{'sig':'or','key':'seq','symbol':'>','value':'20'},{'sig':'and','key':'quality','symbol':'=','value':u'中'}] # request.POST.get('items', '')
    table = 'gsinfo_gsding' #request.POST.get('table', '')

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
            sql = sql + " {0} {1} {2} '{3}'".format(item['sig'],item['key'],item['symbol'],item['value'])
        else:
            sql = sql + "{0} {1} '{2}'".format(item['key'],item['symbol'],item['value'])
    try:
        cursor.execute(sql)
        results = cursor.fetchall()

        ret = {
            'success': True,
            'results': results
        }
    except Exception,e:
        ret = {
            'success': False,
        }

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)


# 备份还原
def restore(request):
    date ='20170801' # request.GET.get('date','')
    hardDir = settings.BASE_DIR # settings.HARDDIR
    allZipFile = os.listdir(hardDir)
    zipFile = date + '.zip'
    if zipFile in allZipFile:
        try:
            tarPath = os.path.join(hardDir,zipFile)
            # 先解压缩
            f_zip = zipfile.ZipFile(tarPath, 'r')
            output_dir = settings.BASE_DIR
            f_zip.extractall(output_dir)

            sqlFile = os.path.join(output_dir,date,'gsinfo.sql')
            dataFile  = os.path.join(output_dir,date,'data')

            # 运行sql文件
            database = settings.DATABASES['default']
            NAME = database['NAME']
            HOST = database['HOST']
            USER = database['USER']
            PASSWORD = database['PASSWORD']
            cmd_dump = r'mysql   -h%s -u%s -p%s -D%s < %s' % (HOST, USER, PASSWORD, NAME, sqlFile)
            os.system(cmd_dump)

            # 将原始data目录删除，将指定日期的data目录复制过去
            dataDir = os.path.join(settings.BASE_DIR,'data')
            if os.path.exists(dataDir):
                shutil.rmtree(dataDir)

            shutil.copytree(dataFile, dataDir)

        except Exception,e:
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
            'info':'无该日期备份！'
        }
    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)

# --------------------------------------------------------------------------
def getStatusData(request):
    pageSize = int(request.POST.get('rows', ''))
    page = int(request.POST.get('page', ''))
    boxNumber = int(request.POST.get('boxNumber', ''))
    workSeq = request.POST.get('workSeq', '')
    subBoxNumber = request.POST.get('subBoxNumber', '')

    box = gsBox.objects.get(boxNumber=boxNumber)

    productTypeCode = box.productType
    classNameCode = box.className
    subClassNameCode = box.subClassName

    productType = gsProperty.objects.get(project='实物类型', code=productTypeCode)
    className = gsProperty.objects.get(project='品名', code=classNameCode, parentProject=productType.project,
                                       parentType=productType.type)
    subClassName = gsProperty.objects.get(project='明细品名', code=subClassNameCode, parentProject=className.project,
                                          parentType=className.type, grandpaProject=productType.project,
                                          grandpaType=productType.type)

    workSeq = int(workSeq)

    if subBoxNumber:
        subBox = gsSubBox.objects.get(box=box, subBoxNumber=int(subBoxNumber))
        work = gsWork.objects.get(box=box, workSeq=workSeq, subBox=subBox)
    else:
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
        if subBoxNumber != '':
            r['subBoxNumber'] =subBoxNumber
        else:
            r['subBoxNumber'] = '0'
        r['productType'] = productType.type
        r['className'] = className.type
        r['subClassName'] = subClassName.type

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

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)


# ------------------------------------------------------------------------------------
# def getStartSequence(request):
#     codes = request.GET.get('codes','')
#     codes = codes.split('&')
#     ret = {}
#     if len(codes) == 4:
#         typeCode = codes[0]
#         wareHouse = codes[1]
#         classNameCode = codes[2]
#         subClassNameCode = codes[3]
#         lastedBox = gsBox.objects.filter(wareHouse=wareHouse, className=classNameCode,
#                                          subClassName=subClassNameCode).order_by('-id').first()
#         if lastedBox:
#             ret['maxSeq'] = gsThing.objects.filter(box=lastedBox).order_by('-seq').first().seq+1
#         else:
#             ret['maxSeq'] = '1'
#
#     ret_json = json.dumps(ret, separators=(',', ':'))
#     return HttpResponse(ret_json)

# # 日终小结
def summarizeDailyWork(request):
    pass
#     date = request.POST.get('date', '')
#     start = date + ' 00:00:00.000000'
#     date_time = datetime.datetime.strptime(start, '%Y-%m-%d')
#     date2 = date + datetime.timedelta(days=1)
#     end_date = date2 + ' 00:00:00.000000'
#     ts = gsStatus.objects.filter(analyzingUpdateDateTime__range=())
#
# # 2017-08-04 09:30:52.720000
#     # '金银锭类':
#
#     #Entry.objects.filter(pub_date__range=(start_date, end_date))
#     # '金银币章类':
#     ts = gsBiZhang.objects
#     # '银元类':
#     ts = gsYinYuan.objects
#     # '金银工艺品类':
#     ts = gsGongYiPin.objects

def print_service(request):
    file_path = request.POST.get('file_path', '')
    try:
        print win32print.GetDefaultPrinter()
        # win32api.ShellExecute(0,"print",file_path,'/d:"%s"' % win32print.GetDefaultPrinter (),".",0)
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


def print_auth(request):
    nickName = request.POST.get('user', '')  # 系统负责人用户名
    password = request.POST.get('password', '')  # 系统负责人密码

    custom_user = gsUser.objects.filter(nickName=nickName)
    if custom_user:
        custom_user = custom_user[0]
        if int(custom_user.type) == 0:
            username = custom_user.user.username
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
                "success": False,
                "message": u'该用户无此权限！'
            }
    else:
        ret = {
            'success': False,
            'message': u'用户名错误！'
        }
    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)