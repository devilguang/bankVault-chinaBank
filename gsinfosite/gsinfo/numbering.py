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

    ret = []
    field_list = {'level':'等级',
                  'detailedName':'名称',
                  'peroid': '年代',
                  'year': '年份',
                  'country': '国别',
                  'faceAmount': '面值',
                  'dingSecification': '规格',
                  'zhangType': '性质',
                  'shape': '名称',
                  'appearance': '品相',
                  'mark': '铭文',
                  'originalQuantity': '成色',
                  }

    prop_list =  ['level','detailedName','peroid','country','faceAmount','dingSecification','zhangType','shape',
                  'appearance']
    shape = models.CharField(verbose_name='工艺品类器型（型制）', max_length=512, blank=True)

    for field in field_list:
        detail={}
        thing = gsThing.objects.filter(serialNumber=serialNumber)
        code = thing.values(field)
        if field in prop_list:
            gsProperty.objects.get(project=jj)

    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)

def getReadyInfo(request):
    field = request.Get.get('field', '')
    ret = []
    type_list = list(gsProperty.objects.filter(project=field).values_list('type',flat=True))
    code_list = list(gsProperty.objects.filter(project=field).values_list('code', flat=True))
    for type,code in zip(type_list,code_list):
        detail = {}
        detail['text'] = type
        detail['id'] = code
        ret.append(detail)
    ret_json = json.dumps(ret, separators=(',', ':'))
    return HttpResponse(ret_json)

def updateNumberingInfo(request):
    serialNumber = request.POST.get('serialNumber', '')
    workName = request.POST.get('workName', '')
    # -----------------------------------------------
    level = request.POST.get('level', '')
    detailedName = request.POST.get('detailedName', '')
    peroid = request.POST.get('peroid', '')
    year = request.POST.get('year', '')
    country = request.POST.get('country', '')
    faceAmount = request.POST.get('faceAmount', '')
    dingSecification = request.POST.get('dingSecification', '')
    zhangType = request.POST.get('zhangType', '')
    shape = request.POST.get('shape', '')
    appearance = request.POST.get('appearance', '')
    mark = request.POST.get('mark', '')
    originalQuantity = float(request.POST.get('originalQuantity'))
    remark = request.POST.get('remark', '')
    # -----------------------------------------------
    operator = request.POST.get('operator', '')
    workSeq = request.POST.get('workSeq', '')  # 更新单件实物信息是workSeq不传值，设置缺省信息是传值

    if serialNumber == '' and workSeq != '':
        work = gsWork.objects.get(workName=workName)
        thing_set = gsThing.objects.filter(work=work)
    elif serialNumber != '' and workSeq == '':
        thing_set = gsThing.objects.filter(serialNumber=serialNumber)

    ret = {}
    try:
        log.log(user=request.user, operationType=u'业务操作', content=u'实物外观信息更新')
        thing_set.update(level=level,
                         detailedName=detailedName,
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
        ret['message'] = serialNumber + u'实物信息更新失败！'
    else:
        ret['success'] = True
        ret['message'] = serialNumber + u'实物信息更新成功！'

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