# encoding=UTF-8
from django.shortcuts import render
from django.http.response import HttpResponse
import json
from report_process import *
from django.contrib.auth.decorators import login_required
from datetime import datetime

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
        # 检测作业是否可用
        t = gsThing.objects.get(serialNumber=serialNumber)
        wt = gsWorkThing.objects.get(thing=t)
        if (wt.work.status != 1):
            # 作业不可用
            raise ValueError, u'作业不可用！请联系现场负责人进行分发！'

        if (0 == cmp(productType, u'金银锭类')):
            ts = gsDing.objects.filter(box=box, serialNumber=serialNumber).update(detectedQuantity=detectedQuantity)
        elif (0 == cmp(productType, u'金银币章类')):
            ts = gsBiZhang.objects.filter(box=box, serialNumber=serialNumber).update(detectedQuantity=detectedQuantity)
        elif (0 == cmp(productType, u'银元类')):
            ts = gsYinYuan.objects.filter(box=box, serialNumber=serialNumber).update(detectedQuantity=detectedQuantity)
        elif (0 == cmp(productType, u'金银工艺品类')):
            ts = gsGongYiPin.objects.filter(box=box, serialNumber=serialNumber).update(
                detectedQuantity=detectedQuantity)

        # now = datetime.utcnow() # 这里使用utcnow生成时间,存入mariaDB后被数据库当做非UTC时间,自动减去了8个小时,所以这里改用now
        # now = datetime.datetime.now()
        gsStatus.objects.filter(box=box, serialNumber=serialNumber).update(analyzingStatus=True,
                                                                           analyzingOperator=operator,
                                                                           analyzingUpdateDateTime=dt)

        s = gsStatus.objects.get(box=box, serialNumber=serialNumber)
        status = s.numberingStatus and s.analyzingStatus and s.measuringStatus and s.photographingStatus
        gsStatus.objects.filter(box=box, serialNumber=serialNumber).update(status=status)
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
    ws = gsWork.objects.filter(status=1)

    ret = {}
    for w in ws:
        box = w.box
        wts = gsWorkThing.objects.filter(work=w)
        specialThingIDList = wts.values_list('thing', flat=True)
        specialSerialNumberList = gsThing.objects.filter(id__in=specialThingIDList).values_list('serialNumber',
                                                                                                flat=True)

        key = w.workName
        ret[key] = {}
        ret[key]['boxNumber'] = box.boxNumber
        productTypeCode = box.productType
        productType = gsProperty.objects.get(project='实物类型', code=productTypeCode)
        ret[key]['productType'] = productType.type
        classNameCode = box.className
        className = gsProperty.objects.get(project='品名', code=classNameCode, parentProject='实物类型',
                                           parentType=productType.type)
        ret[key]['className'] = className.type

        if (0 == cmp(productType.type, u'金银锭类')):
            ts = gsDing.objects.filter(box=box, serialNumber__in=specialSerialNumberList)
        elif (0 == cmp(productType.type, u'金银币章类')):
            ts = gsBiZhang.objects.filter(box=box, serialNumber__in=specialSerialNumberList)
        elif (0 == cmp(productType.type, u'银元类')):
            ts = gsYinYuan.objects.filter(box=box, serialNumber__in=specialSerialNumberList)
        elif (0 == cmp(productType.type, u'金银工艺品类')):
            ts = gsGongYiPin.objects.filter(box=box, serialNumber__in=specialSerialNumberList)

        ss = gsStatus.objects.filter(box=box, serialNumber__in=specialSerialNumberList)

        idx = 1
        ret[key]['data'] = {}
        ret[key]['NotComplete'] = {}
        for t, s in zip(ts, ss):
            ret[key]['data'][idx] = []
            ret[key]['data'][idx].append(t.serialNumber)
            ret[key]['data'][idx].append(productType.type)
            ret[key]['data'][idx].append(s.analyzingStatus)

            if not s.analyzingStatus:
                ret[key]['NotComplete'][idx] = []
                ret[key]['NotComplete'][idx].append(t.serialNumber)
                ret[key]['NotComplete'][idx].append(s.analyzingStatus)

            idx = idx + 1

    ret_json = json.dumps(ret, separators=(',', ':'))

    return HttpResponse(ret_json)
