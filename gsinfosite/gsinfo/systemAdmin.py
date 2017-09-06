# encoding=UTF-8
from django.shortcuts import render
from django.http.response import HttpResponse, StreamingHttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from models import *
import json
from utils import readFile, dateTimeHandler
from tag_process import *
from report_process import *
from gsinfosite import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import log



@login_required
def systemAdmin(request):
    custom_user = gsUser.objects.get(user=request.user)
    nickName = custom_user.nickName
    type = custom_user.type
    return render(request, 'admin.html', context={'operator': nickName, 'type': type})


# 对用户有两种操作：新建、删除
def userProcess(request):
    type = request.POST.get('type', '')  # 管理员还是一般用户：1--管理员，2--一般用户
    password = request.POST.get('password', '')
    opType = request.POST.get('opType', '')
    nickName = request.POST.get('nickName', '')
    organization = request.POST.get('organization', '')  # 用户所在组织
    department = request.POST.get('department', '')

    ret = {}

    if opType == 'add':
        if nickName and type and password:
            type = int(type)
            try:
                log.log(user=request.user, operationType=u'系统管理', content=u'添加用户{0}'.format(nickName))
                gsUser.objects.createUser(nickName=nickName, type=type, password=password,organization=organization,department=department)
            except Exception as e:
                ret = {
                    "success": False,
                    "message": u'用户{0}添加失败！\r\n原因：{1}'.format(nickName, e.message)
                }
            else:
                ret = {
                    'success': True,
                    'message': u'用户{0}添加成功！'.format(nickName)
                }
        elif nickName == '':
            ret = {
                'success': False,
                "message": u'用户名不能为空！'
            }
        elif type == '':
            ret = {
                'success': False,
                "message": u'请选择用户类型！'
            }
        elif password == '':
            ret = {
                'success': False,
                "message": u'请输入密码！'
            }

        else:
            ret = {
                'success': False,
                "message": u'信息填写有误！！'
            }
    elif opType == 'remove':
        nickNameList = request.POST.getlist('nickName[]')  # 可以一次删除多个用户
        try:
            for nickName in nickNameList:
                if nickName == 'sysadmin':
                    ret = {
                        "success": False,
                        "message": u'系统管理员不能被删除！'
                    }
                else:
                    log.log(user=request.user, operationType=u'系统管理', content=u'删除用户{0}'.format(nickName))
                    gsUser.objects.deleteUser(nickName=nickName)
                    ret = {
                        "success": True,
                        "message": u'用户删除成功！'
                    }
        except Exception as e:
            ret = {
                "success": False,
                "message": u'用户删除失败！\r\n原因：{0}'.format(e.message)
            }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def updatePassword(request):
    if request.method == 'GET':
        return render(request, 'updatePassword.html', context={})
    elif request.method == 'POST':
        nickName = request.POST.get('nickName', '')
        password = request.POST.get('passWord', '')
        oldPassword = request.POST.get('oldPassWord', '')
        fromLoc = request.POST.get('fromLoc', '')

        try:
            custom_user = gsUser.objects.get(nickName=nickName)

            if fromLoc == 'login':
                username = custom_user.user.username
                user = auth.authenticate(username=username, password=oldPassword)
                if user is None:
                    ret = {
                        'success': False,
                        'message': u'用户{0},旧密码错误，更改密码失败！'.format(nickName)
                    }
                else:
                    if password.isspace():
                        ret = {
                            "success": False,
                            "message": u'新设密码不能为空格！'
                        }
                    # elif len(password) < 6:
                    #     ret = {
                    #         "success": False,
                    #         "message": u'新设密码至少六位！'
                    #     }
                    # elif password.isalpha() or password.isdigit():
                    #     ret = {
                    #         "success": False,
                    #         "message": u'新设密码由字母和数字组合！'
                    #     }
                    else:
                        log.log(user=request.user, operationType=u'系统管理', content=u'修改用户{0}密码'.format(nickName))
                        user.set_password(password)
                        user.save()
            elif fromLoc == 'admin':
                if not password:
                    ret = {
                        "success": False,
                        "message": u'新设密码不能为空格！'
                    }
                # elif len(password) < 6:
                #     ret = {
                #         "success": False,
                #         "message": u'新设密码至少六位！'
                #     }
                # elif password.isalpha() or password.isdigit():
                #     ret = {
                #         "success": False,
                #         "message": u'新设密码由字母和数字组合！'
                #     }
                else:
                    log.log(user=request.user, operationType=u'系统管理', content=u'修改用户{0}密码'.format(nickName))
                    # 从系统管理界面修改用户密码, 不需要对用户身份进行认证
                    custom_user.user.set_password(password)
                    custom_user.user.save()
        except Exception as e:
            ret = {
                'success': False,
                'message': u'用户{0}更改密码失败！\r\n原因：{1}'.format(nickName, e.message)
            }
        else:
            ret = {
                'success': True,
                'message': u'用户{0}更改密码成功！'.format(nickName)
            }

        ret_json = json.dumps(ret, separators=(',', ':'))

        return HttpResponse(ret_json)


def getUser(request):
    ret = {}

    users = gsUser.objects.all()
    ret['total'] = users.count()
    ret['rows'] = []
    for u in users:
        r = {}
        r['nickName'] = u.nickName
        r['type'] = u.type
        r['id'] = u.user.id
        r['text'] = u.nickName
        ret['rows'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def getAuthority(request):
    ret = {}

    users = gsUser.objects.all()
    isExistManager = gsUser.objects.filter(type__lte=1, manage=True).exists()

    ret['total'] = users.count()
    ret['rows'] = []
    for u in users:
        r = {}
        if int(u.type) == 0:  # 0表示系统管理员
            continue
        r['nickName'] = u.nickName
        r['type'] = u.type

        r['canBeManage'] = True if not isExistManager else False
        r['manage'] = u.manage

        r['checking'] = u.checking
        r['numbering'] = u.numbering
        r['measuring'] = u.measuring
        r['analyzing'] = u.analyzing
        r['photographing'] = u.photographing

        ret['rows'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def authorityProcess(request):
    nickName = request.POST.get('nickName', '')
    authority = request.POST.get('authority', '')
    opType = request.POST.get('opType', '')

    jobName = ''
    ret = {}
    if opType == 'grant':
        try:
            if authority == 'auth':
                jobName = u'现场负责人'
                log.log(user=request.user, operationType=u'系统管理', content=u'授予用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName, type=1).update(auth=True)
            elif authority == 'manage':
                jobName = u'实物分发岗位'
                log.log(user=request.user, operationType=u'系统管理', content=u'授予用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName, type=1).update(manage=True)
            elif authority == 'checking':
                jobName = u'实物认定'
                log.log(user=request.user, operationType=u'系统管理', content=u'授予用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName).update(checking=True)
            elif authority == 'numbering':
                jobName = u'外观信息采集'
                log.log(user=request.user, operationType=u'系统管理', content=u'授予用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName).update(numbering=True)
            elif authority == 'measuring':
                jobName = u'测量称重'
                log.log(user=request.user, operationType=u'系统管理', content=u'授予用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName).update(measuring=True)
            elif authority == 'analyzing':
                jobName = u'频谱分析'
                log.log(user=request.user, operationType=u'系统管理', content=u'授予用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName).update(analyzing=True)
            elif authority == 'photographing':
                jobName = u'图像采集'
                log.log(user=request.user, operationType=u'系统管理', content=u'授予用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName).update(photographing=True)
        except Exception as e:
            ret = {
                "success": False,
                "message": u'向用户{0}授予{1}岗位权限失败！\r\n原因：{2}'.format(nickName, jobName, e.message)
            }
        else:
            ret = {
                'success': True,
                'message': u'向用户{0}授予{1}岗位权限成功！'.format(nickName, jobName)
            }
    elif opType == 'revoke':
        try:
            if authority == 'auth':
                jobName = u'现场负责人'
                log.log(user=request.user, operationType=u'系统管理', content=u'授予用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName).update(auth=True)
            elif authority == 'manage':
                jobName = u'实物分发岗位'
                log.log(user=request.user, operationType=u'系统管理', content=u'收回用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName).update(manage=False)
            elif (0 == cmp(authority, 'checking')):
                jobName = u'实物认定'
                log.log(user=request.user, operationType=u'系统管理', content=u'收回用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName).update(checking=False)
            elif (0 == cmp(authority, 'numbering')):
                jobName = u'外观信息采集'
                log.log(user=request.user, operationType=u'系统管理', content=u'收回用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName).update(numbering=False)
            elif (0 == cmp(authority, 'measuring')):
                jobName = u'测量称重'
                log.log(user=request.user, operationType=u'系统管理', content=u'收回用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName).update(measuring=False)
            elif (0 == cmp(authority, 'analyzing')):
                jobName = u'频谱分析'
                log.log(user=request.user, operationType=u'系统管理', content=u'收回用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName).update(analyzing=False)
            elif (0 == cmp(authority, 'photographing')):
                jobName = u'图像采集'
                log.log(user=request.user, operationType=u'系统管理', content=u'收回用户{0}:{1}权限'.format(nickName, jobName))
                gsUser.objects.filter(nickName=nickName).update(photographing=False)
        except Exception as e:
            ret = {
                "success": False,
                "message": u'收回用户{0}, {1}岗位权限失败！\r\n原因：{2}'.format(nickName, jobName, e.message)
            }
        else:
            ret = {
                'success': True,
                'message': u'收回用户{0}, {1}岗位权限成功！'.format(nickName, jobName)
            }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def getArchive(request):
    ret = {}

    archives = gsArchive.objects.all()
    ret['total'] = archives.count()
    ret['rows'] = []
    for a in archives:
        r = {}
        r['boxNumber'] = a.box.boxNumber
        productType = gsProperty.objects.get(project='实物类型', code=a.box.productType)
        r['productType'] = productType.type
        r['amount'] = a.box.amount
        ret['rows'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def getWorkContent(request):
    ret = {}

    works = getWorkContent.objects.all()
    ret['total'] = works.count()
    ret['rows'] = []
    for a in works:
        r = {}
        r['boxNumber'] = a.box.boxNumber
        productType = gsProperty.objects.get(project='实物类型', code=a.box.productType)
        r['productType'] = productType.type
        r['amount'] = a.box.amount
        ret['rows'].append(r)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def workProcess(request, boxNumber):
    fileName = boxNumber + '.zip'
    filePath = os.path.join(settings.DATA_DIRS['report_dir'], fileName)

    if not os.path.exists(filePath):
        date = '07/15/2016'
        seq = '1'
        log.log(user=request.user, operationType=u'业务操作', content=u'生成{0}号箱装箱清单'.format(boxNumber))
        createReport(boxNumber, date, seq)

    response = StreamingHttpResponse(readFile(filePath))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename={0}'.format(fileName)

    return response


def tagProcess(request, boxNumber):
    fileName = boxNumber + '_tag.zip'
    filePath = os.path.join(settings.DATA_DIRS['tag_dir'], fileName)

    if not os.path.exists(filePath):
        log.log(user=request.user, operationType=u'业务操作', content=u'生成{0}号箱标签'.format(boxNumber))
        createTag(boxNumber, True)

    response = StreamingHttpResponse(readFile(filePath))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename={0}'.format(fileName)

    return response


def backToWork(request):
    boxNumber = request.POST.get('boxNumber', '')

    try:
        # 先插入工作空间, 后从档案检索表中删除
        box = gsBox.objects.get(boxNumber=boxNumber)
        gsWorkSpace.objects.get_or_create(box=box)
        w = gsArchive.objects.get(box=boxNumber)
        w.delete()
    except Exception as e:
        ret = {
            "success": False,
            "message": str(boxNumber) + u'号箱作业退回作业失败！\r\n原因:' + e.message
        }
    else:
        ret = {
            "success": True,
            "message": str(boxNumber) + '号箱作业退回作业成功！请以正常流程继续予以完善！'
        }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def thingProcess(request, boxNumber, serialNumber):
    fileName = serialNumber + '.xlsx'
    reportDir = os.path.join(settings.DATA_DIRS['report_dir'], boxNumber)
    isExist = False
    for root, dirs, files in os.walk(reportDir,
                                     False):  # True: 表示首先返回目录树下的文件，然后在遍历目录树的子目录. False: 表示先遍历目录树的子目录，返回子目录下的文件，最后返回根目录下的文件
        for file in files:
            if (0 == cmp(file, fileName)):
                isExist = True
                filePath = os.path.join(root, file)

    if not isExist:
        date = '07/15/2016'
        seq = '1'
        createReport(boxNumber, date, seq)

        for root, dirs, files in os.walk(reportDir,
                                         False):  # True: 表示首先返回目录树下的文件，然后在遍历目录树的子目录. False: 表示先遍历目录树的子目录，返回子目录下的文件，最后返回根目录下的文件
            for file in files:
                if (0 == cmp(file, fileName)):
                    filePath = os.path.join(root, file)

    response = StreamingHttpResponse(readFile(filePath))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename={0}'.format(fileName)

    return response

def getProperty(request):
    ret = []
    rps = {}
    rps['id'] = -1
    rps['type'] = '实物类型'
    rps['code'] = ''
    rps['remark'] = ''
    rps['children'] = []
    ret.append(rps)
    # 获取实物类型
    productTypes = gsProperty.objects.filter(project='实物类型')
    tp = None
    tc = None
    for p in productTypes:
        rp = {}
        rp['id'] = p.id
        # rp['project'] = p.project
        rp['type'] = p.type
        rp['code'] = p.code
        rp['remark'] = ''
        rp['children'] = []
        rps['children'].append(rp)

        # 获取品名
        classNames = gsProperty.objects.filter(project='品名', parentProject=p.project, parentType=p.type)
        for c in classNames:
            rc = {}
            rc['id'] = c.id
            # rc['project'] = c.project
            rc['type'] = c.type
            rc['code'] = c.code
            rc['remark'] = '品名'
            rc['children'] = []
            rp['children'].append(rc)

            # 获取明细品名
            subClassNames = gsProperty.objects.filter(project='明细品名', parentProject=c.project, parentType=c.type,
                                                      grandpaProject=p.project, grandpaType=p.type)
            for s in subClassNames:
                rs = {}
                rs['id'] = s.id
                # rs['project'] = s.project
                rs['type'] = s.type
                rs['code'] = s.code
                rs['remark'] = '明细品名'
                rc['children'].append(rs)

    # 获取发行库名称
    rws = {}
    rws['id'] = -2
    rws['type'] = '发行库'
    rws['code'] = ''
    rws['remark'] = ''
    rws['children'] = []
    ret.append(rws)
    wareHouses = gsProperty.objects.filter(project='发行库')
    for w in wareHouses:
        rw = {}
        rw['id'] = w.id
        # rw['project'] = rw.project
        rw['type'] = w.type
        rw['code'] = w.code
        rw['remark'] = '发行库'
        rws['children'].append(rw)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def propertyProcess(request):
    project = request.POST.get('project', '')
    productType_productType = request.POST.get('productType-productType', '')
    productTypeCode = request.POST.get('productTypeCode', '')
    className_productType = request.POST.get('className-productType', '')
    className_className = request.POST.get('className-className', '')
    classNameCode = request.POST.get('classNameCode', '')
    subClassName_productType = request.POST.get('subClassName-productType', '')
    subClassName_className = request.POST.get('subClassName-className', '')
    subClassName_subClassName = request.POST.get('subClassName-subClassName', '')
    subClassNameCode = request.POST.get('subClassNameCode', '')
    wareHouseType = request.POST.get('wareHouseType', '')
    wareHouseCode = request.POST.get('wareHouseCode', '')
    opType = request.POST.get('opType', '')
    recordID = request.POST.get('id', '')
    if (0 != cmp(recordID, '')):
        recordID = int(recordID)

    if (0 == cmp(opType, 'add')):
        try:
            if (0 == cmp(project, u'实物类型')):
                p = gsProperty(project=project, type=productType_productType, code=productTypeCode)
                p.save()
            elif (0 == cmp(project, u'品名')):
                productType = gsProperty.objects.get(project='实物类型', code=className_productType)
                p = gsProperty(project=project, type=className_className, code=classNameCode,
                               parentProject=productType.project, parentType=productType.type)
                p.save()
            elif (0 == cmp(project, u'明细品名')):
                productType = gsProperty.objects.get(project='实物类型', code=subClassName_productType)
                className = gsProperty.objects.get(project='品名', code=subClassName_className,
                                                   parentProject=productType.project, parentType=productType.type)
                p = gsProperty(project=project, type=subClassName_subClassName, code=subClassNameCode,
                               parentProject=className.project, parentType=className.type,
                               grandpaProject=productType.project, grandpaType=productType.type)
                p.save()
            elif (0 == cmp(project, u'发行库')):
                p = gsProperty(project=project, type=wareHouseType, code=wareHouseCode)
                p.save()
        except Exception as e:
            ret = {
                "success": False,
                "message": '属性信息添加失败！\r\n原因：' + e.message
            }
        else:
            ret = {
                'success': True,
                'message': '属性信息更新成功!'
            }
    elif (0 == cmp(opType, 'remove')):
        try:
            p = gsProperty.objects.get(id=recordID)
            if (0 == cmp(p.project, u'实物类型')):
                pchildren = gsProperty.objects.filter(project='品名', parentProject=p.project, parentType=p.type)
                for pchild in pchildren:
                    pgrandsons = gsProperty.objects.filter(project='明细品名', parentProject=pchild.project,
                                                           parentType=pchild.type, grandpaProject=p.project,
                                                           grandpaType=p.type)
                    for pgrandson in pgrandsons:
                        pgrandson.delete()

                    pchild.delete()

                p.delete()
            elif (0 == cmp(p.project, u'品名')):
                pchildren = gsProperty.objects.filter(parentProject=p.project, parentType=p.type)
                for pchild in pchildren:
                    pchild.delete()

                p.delete()
            elif (0 == cmp(p.project, u'明细品名')):
                p.delete()
            elif (0 == cmp(p.project, u'发行库')):
                p.delete()
        except Exception as e:
            ret = {
                "success": False,
                "message": '属性信息删除失败！\r\n原因：' + e.message
            }
        else:
            ret = {
                'success': True,
                'message': '属性信息删除成功!'
            }

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def getLogContent(request):
    userName = request.GET.get('userName', u'全部')
    operationType = request.GET.get('operationType', u'全部')

    if 0 == cmp(userName, u'全部'):
        userName = None
    if 0 == cmp(operationType, u'全部'):
        operationType = None
    ret = log.retriveLog(userName=userName, operationType=operationType)

    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder, default=dateTimeHandler)

    return HttpResponse(ret_json)


def getOperationType(request):
    ret = log.getOperationType()

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def getUserName(request):
    ret = log.getUserName()

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)


def setSysAdmin(request):
    nickName = request.POST.get('nickName', '')
    oldNickName = gsUser.objects.get(user=request.user).nickName
    manage = gsUser.objects.get(nickName=nickName).manage
    if manage == 1:
        ret = {
            "success": False,
            "message": u'系统管理权限不能转移给实物分发岗位 ！'
        }
    else:
        try:
            log.log(user=request.user, operationType=u'系统管理', content=u'将{0}的系统管理权限转移给{1}'.format(oldNickName,nickName))
            gsUser.objects.filter(nickName=nickName).update(type=0)
            gsUser.objects.filter(nickName=oldNickName).update(type=1)
            #gsUser.objects.deleteUser(nickName=oldNickName)
            auth.logout(request)
        except Exception as e:
            ret = {
                "success": False,
                "message": u'权限转移失败！'
            }
        else:
            ret = {
                'success': True,
                'message': u'权限转移成功！'
            }

    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)