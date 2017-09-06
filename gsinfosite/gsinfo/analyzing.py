# encoding=UTF-8
from django.shortcuts import render
from django.http.response import HttpResponse
import json
from report_process import *
from django.contrib.auth.decorators import login_required
from datetime import datetime
from . import log

@login_required  # 频谱分析岗位
def analyzing(request):
    nickName = gsUser.objects.get(user=request.user)
    return render(request, 'p.html', context={'operator': nickName, })

def updateAnalyzingInfo(request):
    boxNumber = request.POST.get('boxNumber', '')
    serialNumber = request.POST.get('serialNumber', '')
    productType = request.POST.get('productType', '')
    operator = request.POST.get('operator', '')
    detectedQuantity = request.POST.get('detectedQuantity', '')
    dtstr = request.POST.get('datetime', '')

    detectedQuantity = float(detectedQuantity[:-1])
    dt = datetime.strptime(dtstr, '%Y/%m/%d %H:%M:%S')

    box = gsBox.objects.get(boxNumber=boxNumber)

    try:
        log.log(user=request.user, operationType=u'业务操作', content=u'频谱分析信息更新')
        # 检测作业是否可用
        thing = gsThing.objects.get(serialNumber=serialNumber)
        thing_status = gsStatus.objects.filter(thing=thing)
        thing_obj = thing_status[0]
        if thing_obj.status == 0:
            # 作业不可用
            raise ValueError, u'作业不可用！请联系实物分发岗位进行分发！'

        if (0 == cmp(productType, u'金银锭类')):
            ts = gsDing.objects.filter(thing=thing).update(detectedQuantity=detectedQuantity)
        elif (0 == cmp(productType, u'金银币章类')):
            ts = gsBiZhang.objects.filter(thing=thing).update(detectedQuantity=detectedQuantity)
        elif (0 == cmp(productType, u'银元类')):
            ts = gsYinYuan.objects.filter(thing=thing).update(detectedQuantity=detectedQuantity)
        elif (0 == cmp(productType, u'金银工艺品类')):
            ts = gsGongYiPin.objects.filter(thing=thing).update(detectedQuantity=detectedQuantity)

        gsStatus.objects.filter(thing=thing).update(analyzingStatus=True,analyzingOperator=operator,analyzingUpdateDateTime=dt)
        thing_status = gsStatus.objects.filter(thing=thing)
        thing_obj = thing_status[0]
        status = thing_obj.numberingStatus and thing_obj.analyzingStatus and thing_obj.measuringStatus and \
                 thing_obj.photographingStatus and thing_obj.checkingStatus
        thing_status.update(status=status)
    except Exception as e:
        ret = {}
        ret['success'] = False
        ret['message'] = u'更新失败！箱号:{0}; 编号:{1}; 检测成色:{2}; 操作员:{3}\n原因:{4}'.format(boxNumber, serialNumber,
                                                                                  detectedQuantity, operator, e.message)
    else:
        ret = {}
        ret['success'] = True
        ret['message'] = u'更新成功！箱号:{0}; 编号:{1}; 检测成色:{2}; 操作员:{3}'.format(boxNumber, serialNumber, detectedQuantity,
                                                                          operator)

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)

def getAnalyzingWorkData(request):
    work_list = gsWork.objects.filter(status=1)

    ret = {}
    for work in work_list:
        box = work.box
        key = work.workName
        ret[key] = {}
        ret[key]['boxNumber'] = box.boxNumber
        productTypeCode = box.productType
        productType = gsProperty.objects.get(project='实物类型', code=productTypeCode)
        ret[key]['productType'] = productType.type
        classNameCode = box.className
        className = gsProperty.objects.get(project='品名', code=classNameCode, parentProject='实物类型',
                                           parentType=productType.type)
        ret[key]['className'] = className.type

        thing_set = gsThing.objects.filter(work=work)
        # if (0 == cmp(productType.type, u'金银锭类')):
        #     ts = gsDing.objects.filter(thing__in=thing_set)
        # elif (0 == cmp(productType.type, u'金银币章类')):
        #     ts = gsBiZhang.objects.filter(thing__in=thing_set)
        # elif (0 == cmp(productType.type, u'银元类')):
        #     ts = gsYinYuan.objects.filter(thing__in=thing_set)
        # elif (0 == cmp(productType.type, u'金银工艺品类')):
        #     ts = gsGongYiPin.objects.filter(thing__in=thing_set)

        status_set = gsStatus.objects.filter(thing__in=thing_set)

        idx = 1
        ret[key]['data'] = {}
        ret[key]['NotComplete'] = {}
        for thing, status in zip(thing_set, status_set):
            serialNumber = thing.serialNumber
            analyzingStatus =status.analyzingStatus
            ret[key]['data'][idx] = []
            ret[key]['data'][idx].append(serialNumber)
            ret[key]['data'][idx].append(productType.type)
            ret[key]['data'][idx].append(analyzingStatus)

            if not status.analyzingStatus:
                ret[key]['NotComplete'][idx] = []
                ret[key]['NotComplete'][idx].append(serialNumber)
                ret[key]['NotComplete'][idx].append(analyzingStatus)

            idx = idx + 1

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)
