# encoding=UTF-8
import os
from openpyxl import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.styles import Alignment, Font, Border, Side
from .models import *
from gsinfosite import settings
import time
from math import ceil
import zipfile
from openpyxl.utils.units import (
    DEFAULT_ROW_HEIGHT,
    DEFAULT_COLUMN_WIDTH
)
from openpyxl.utils.units import points_to_pixels
import re
import math
from decimal import *


def createArchivesFromWork(boxNumber,subBoxNumber, workSeq, dateTime):
    box = gsBox.objects.get(boxNumber=boxNumber)
    if subBoxNumber:
        subBox = gsSubBox.objects.get(box=box, subBoxNumber=int(subBoxNumber))
        work = gsWork.objects.get(box=box, workSeq=workSeq, subBox=subBox)
    else:
        work = gsWork.objects.get(box=box, workSeq=workSeq)
    work_thing = gsThing.objects.filter(work=work)
    SerialNumberList = work_thing.values_list('serialNumber', flat=True)

    productTypeCode = box.productType
    productType = gsProperty.objects.get(project='实物类型', code=productTypeCode)
    wareHouseCode = box.wareHouse
    wareHouse = gsProperty.objects.get(project='发行库', code=wareHouseCode)
    classNameCode = box.className
    className = gsProperty.objects.get(project='品名', code=classNameCode, parentProject=productType.project,
                                       parentType=productType.type)
    subClassNameCode = box.subClassName
    subClassName = gsProperty.objects.get(project='明细品名', code=subClassNameCode, parentProject=className.project,
                                          parentType=className.type, grandpaProject=productType.project,
                                          grandpaType=productType.type)

    global boxDir
    global boxWordDir
    global boxPhotoDir
    boxDir = os.path.join(boxRootDir, str(boxNumber))
    if not os.path.exists(boxDir):
        os.mkdir(boxDir)  # 转移至创建作业时, 生成相应的目录

    createDateTime = work.createDateTime
    subBoxesSeq = work_thing.values_list('subBoxSeq', flat=True).distinct()

    for subBoxSeq in subBoxesSeq:
        wordDir = os.path.join(boxDir, u'{0}_{1}_{2}_word'.format(createDateTime.year, subBoxSeq, wareHouse.type))
        if (not os.path.exists(wordDir)):
            os.mkdir(wordDir)

        photoDir = os.path.join(boxDir, u'{0}_{1}_{2}_photo'.format(createDateTime.year, subBoxSeq, wareHouse.type))
        if (not os.path.exists(photoDir)):
            os.mkdir(photoDir)

    # output(boxNumber, productType, className, subClassName, wareHouse, date, reportDir, reportWordDir)
    workDir = os.path.join(workRootDir, str(boxNumber))
    if not os.path.exists(workDir):
        os.mkdir(workDir)

    manager = work.manager
    zipFileName = u'{0}_信息档案.zip'.format(work.workName)
    zipFilePath = os.path.join(workDir, zipFileName)
    zip = zipfile.ZipFile(zipFilePath, 'w', zipfile.ZIP_DEFLATED)
    for serialNumber in SerialNumberList:
        thing = gsThing.objects.get(box=box, serialNumber=serialNumber)
        subBoxSeq = thing.subBoxSeq
        wordDir = os.path.join(boxDir, u'{0}_{1}_{2}_word'.format(createDateTime.year, subBoxSeq, wareHouse.type))

        s = gsStatus.objects.get(thing=thing)
        if (0 == cmp(productType.type, u'金银锭类')):
            r = gsDing.objects.get(thing=thing)

            (filePath, fileName) = outputDing(r, s, manager, productType.type, className.type, subClassName.type,
                                              wareHouse.type, dateTime, wordDir)
        elif (0 == cmp(productType.type, u'金银币章类')):
            r = gsBiZhang.objects.get(thing=thing)

            (filePath, fileName) = outputBiZhang(r, s, manager, productType.type, className.type, subClassName.type,
                                                 wareHouse.type, dateTime, wordDir)
        elif (0 == cmp(productType.type, u'银元类')):
            r = gsYinYuan.objects.get(thing=thing)

            (filePath, fileName) = outputYinYuan(r, s, manager, productType.type, className.type, subClassName.type,
                                                 wareHouse.type, dateTime, wordDir)
        elif (0 == cmp(productType.type, u'金银工艺品类')):
            r = gsGongYiPin.objects.get(thing=thing)

            (filePath, fileName) = outputGongYiPin(r, s, manager, productType.type, className.type, subClassName.type,
                                                   wareHouse.type, dateTime, wordDir)

        zip.write(filePath, fileName)

    zip.close()

    return True
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def getRows(value_list):
    # 判断value中的每一个值是中文还是英文
    zhPattern = re.compile(u'[\u4e00-\u9fa5]')
    row_list = []
    for value in value_list:
        vs,n = value
        all_len = 0
        for v in unicode(str(vs), "utf-8"):
            match = zhPattern.search(v)
            if match:
                all_len += 2
            else:
                all_len += 1
        row_num = int(math.ceil(float(all_len)/float(n)))
        row_list.append(row_num)
    max_row = max(row_list)
    return max_row

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def createBoxInfo(**kwargs):
    boxNumber = kwargs['boxNumber']

    boxDir = os.path.join(settings.BOX_DATA_PATH, boxNumber)
    if not os.path.exists(boxDir):
        os.mkdir(boxDir)  # 转移至创建作业时, 生成相应的目录
    box = gsBox.objects.get(boxNumber=boxNumber)
    thing_set = gsThing.objects.filter(box=box)
    prop = box.boxType
    type = prop.type
    parentType = prop.parentType
    grandpaType = prop.grandpaType
    if grandpaType:
        className = parentType
        subClassName = type
    else:
        className = type
        subClassName = '-'
    template_path = os.path.join(settings.TEMPLATE_DATA_PATH, u'装箱清单.xlsx')
    table = load_workbook(template_path)
    # default_height = points_to_pixels(DEFAULT_ROW_HEIGHT)
    sheet = table.worksheets[0]
    # default_height=20,而只有高度大于默认值的单元格sheet.row_dimensions[n].height才不返回None
    unit = 14.25
    if not sheet.row_dimensions[1].height:
        sheet.row_dimensions[1].height = unit
        h1 = sheet.row_dimensions[1].height
    else:
        h1 = sheet.row_dimensions[1].height

    if not sheet.row_dimensions[2].height:
        sheet.row_dimensions[2].height = unit
        h2 = sheet.row_dimensions[2].height
    else:
        h2 = sheet.row_dimensions[2].height
    if not sheet.row_dimensions[3].height:
        sheet.row_dimensions[3].height = unit
        h3 = sheet.row_dimensions[3].height
    else:
        h3 = sheet.row_dimensions[3].height
    h = h1 + h2 + h3
    print_area = 34 * unit
    name_count=1
    row_count=1
    filePath_list = []
    row_height_list = []
    rowStartIdx = 4

    # 实线边框样式
    border = Border(left=Side(border_style='thin', color='FF000000'),
                    right=Side(border_style='thin', color='FF000000'),
                    top=Side(border_style='thin', color='FF000000'),
                    bottom=Side(border_style='thin', color='FF000000'),
                    outline=Side(border_style='thin', color='FF000000'),
                    vertical=Side(border_style='thin', color='FF000000'),
                    horizontal=Side(border_style='thin', color='FF000000')
                    )
    # font = Font(name=u'仿宋', size=10)
    # alignment = Alignment(horizontal='center', vertical='center')
    # 写合计用
    grossWeight_heji = []
    detectedQuantity_heji = []
    pureWeight_heji = []
    amount_heji =[]
    # 写小计用
    grossWeight_xiaoji = []
    detectedQuantity_xiaoji = []
    pureWeight_xiaoji = []
    amount_xiaoji = []

    page = 0 # 只有一页的话就只写合计不写小计
    for i,th in enumerate(thing_set):
        # 写表头
        value_list = []
        sheet['A{0}'.format(2)] = u'箱号:' + boxNumber
        date = datetime.datetime.now()
        year = date.year
        month = date.month
        day = date.day
        sheet['G{0}'.format(2)] = u'{0}年{1}月{2}日'.format(year, month, day)
        # 写表
        # 序号
        col1 = i + 1
        sheet.cell(row=rowStartIdx, column=1).value = col1
        value_list.append((col1,4))
        # 盒号
        col2 = th.case.caseNumber if th.case else '-'
        sheet.cell(row=rowStartIdx, column=2).value = col2
        value_list.append((col2,24))
        # 实物编号
        col3 = th.serialNumber2 if th.serialNumber2 else '-'
        sheet.cell(row=rowStartIdx, column=3).value = col3
        value_list.append((col3, 24))
        # 品种
        col4= className
        sheet.cell(row=rowStartIdx, column=4).value = col4
        value_list.append((col4,12))
        # 品名
        col5 =subClassName
        sheet.cell(row=rowStartIdx, column=5).value =col5
        value_list.append((col5,8))
        # 等级
        col6 =th.level
        sheet.cell(row=rowStartIdx, column=6).value = col6
        value_list.append((col6,6))
        # 名称
        col7 =th.detailedName
        sheet.cell(row=rowStartIdx, column=7).value = col7
        value_list.append((col7,28))
        # 毛重
        col8 = '%.2f' % th.grossWeight if th.grossWeight else '%.2f' % 0
        value_len = len(col8)
        if value_len > 9:
            sheet.cell(row=rowStartIdx, column=8).value = col8
        else:
            sheet.cell(row=rowStartIdx, column=8).value =Decimal(col8).quantize(Decimal('0.00'))
        grossWeight_xiaoji.append(float(col8))
        # 检测成色
        col9 = '%.2f' % th.detectedQuantity if th.detectedQuantity else '%.2f' % 0
        value_len = len(col9)
        if value_len >9:
            sheet.cell(row=rowStartIdx, column=9).value = col9
        else:
            sheet.cell(row=rowStartIdx, column=9).value = Decimal(col9).quantize(Decimal('0.00'))
        detectedQuantity_xiaoji.append(float(col9))
        # 纯重
        col10 = '%.2f' % th.pureWeight if th.pureWeight else '%.2f' % 0
        value_len = len(col10)
        if value_len > 9:
            sheet.cell(row=rowStartIdx, column=10).value =col10
        else:
            sheet.cell(row=rowStartIdx, column=10).value = Decimal(col10).quantize(Decimal('0.00'))
        pureWeight_xiaoji.append(float(col10))
        # 件（枚）数
        col11 = th.amount
        sheet.cell(row=rowStartIdx, column=11).value =col11
        amount_xiaoji.append(float(col11))
        # ----------------------------
        max_row = getRows(value_list)
        sheet.row_dimensions[rowStartIdx].height = unit * max_row
        h_some = unit * max_row
        row_height_list.append(h_some)
        sum_row_height = sum(row_height_list)
        real_h = h + sum_row_height
        other_area = print_area - real_h
        if other_area <= 3 * unit:
            page += 1
            # 写小计
            sheet.cell(row=rowStartIdx + 1, column=1).value = u'小计'
            sheet.cell(row=rowStartIdx + 1, column=2).value = '-'
            sheet.cell(row=rowStartIdx + 1, column=3).value = '-'
            sheet.cell(row=rowStartIdx + 1, column=4).value = '-'
            sheet.cell(row=rowStartIdx + 1, column=5).value = '-'
            sheet.cell(row=rowStartIdx + 1, column=6).value = '-'
            sheet.cell(row=rowStartIdx + 1, column=7).value = '-'
            sheet.cell(row=rowStartIdx + 1, column=8).value = Decimal(str(sum(grossWeight_xiaoji))).quantize(Decimal('0.00'))
            sheet.cell(row=rowStartIdx + 1, column=9).value = Decimal(str(sum(detectedQuantity_xiaoji))).quantize(Decimal('0.00'))
            sheet.cell(row=rowStartIdx + 1, column=10).value = Decimal(str(sum(pureWeight_xiaoji))).quantize(Decimal('0.00'))
            sheet.cell(row=rowStartIdx + 1, column=11).value = Decimal(str(sum(amount_xiaoji))).quantize(Decimal('0.00'))
            # 写签名
            sheet.merge_cells('A{0}:C{0}'.format(rowStartIdx + 2, rowStartIdx + 2))
            sheet.merge_cells('D{0}:G{0}'.format(rowStartIdx + 2, rowStartIdx + 2))
            sheet.merge_cells('H{0}:K{0}'.format(rowStartIdx + 2, rowStartIdx + 2))
            sheet['A{0}'.format(rowStartIdx + 2)] = '现场负责人：'
            sheet['A{0}'.format(rowStartIdx + 2)].alignment = Alignment(horizontal="left")
            sheet['D{0}'.format(rowStartIdx + 2)] = '复核：'
            sheet['D{0}'.format(rowStartIdx + 2)].alignment = Alignment(horizontal="left")
            sheet['H{0}'.format(rowStartIdx + 2)] = '制单：'
            sheet['H{0}'.format(rowStartIdx + 2)].alignment = Alignment(horizontal="left")
            sheet.row_dimensions[rowStartIdx + 2].height = 2 * unit
            # 写样式
            sub_area1 = sheet['A{0}:K{1}'.format(3, rowStartIdx+1)]
            for cs in sub_area1:
                for cell in cs:
                    cell.border = border
            # 保存
            fileName = u'{0}-{1}.xlsx'.format(boxNumber,str(name_count))
            filePath = os.path.join(boxDir, fileName)
            filePath_list.append(filePath)
            table.save(filePath)
            # -------------
            grossWeight_heji = grossWeight_heji + grossWeight_xiaoji
            detectedQuantity_heji = detectedQuantity_heji +detectedQuantity_xiaoji
            pureWeight_heji = pureWeight_heji + pureWeight_xiaoji
            amount_heji = amount_heji + amount_xiaoji
            # 重新初始化
            name_count += 1
            rowStartIdx = 4
            row_height_list = []
            template_path = os.path.join(settings.TEMPLATE_DATA_PATH, u'装箱清单.xlsx')
            table = load_workbook(template_path)
            sheet = table.worksheets[0]

            grossWeight_xiaoji = []
            detectedQuantity_xiaoji = []
            pureWeight_xiaoji = []
            amount_xiaoji = []

        else:
            rowStartIdx +=1
            row_count +=1
    if page > 0:
        # 写小计
        sheet.cell(row=rowStartIdx, column=1).value = u'小计'
        sheet.cell(row=rowStartIdx, column=2).value = '-'
        sheet.cell(row=rowStartIdx, column=3).value = '-'
        sheet.cell(row=rowStartIdx, column=4).value = '-'
        sheet.cell(row=rowStartIdx, column=5).value = '-'
        sheet.cell(row=rowStartIdx, column=6).value = '-'
        sheet.cell(row=rowStartIdx, column=7).value = '-'
        sheet.cell(row=rowStartIdx, column=8).value = Decimal(str(sum(grossWeight_xiaoji))).quantize(Decimal('0.00'))
        sheet.cell(row=rowStartIdx, column=9).value = Decimal(str(sum(detectedQuantity_xiaoji))).quantize(Decimal('0.00'))
        sheet.cell(row=rowStartIdx, column=10).value = Decimal(str(sum(pureWeight_xiaoji))).quantize(Decimal('0.00'))
        sheet.cell(row=rowStartIdx, column=11).value = Decimal(str(sum(amount_xiaoji))).quantize(Decimal('0.00'))

        # 以下方式(写公式)的话会导致excel save后，手动打开保存的excel在未作任何操作的情况下一开始就处于修改状态
        # sheet.cell(row=rowStartIdx, column=8).value = u'=SUM(H4:H{0})'.format(rowStartIdx-1)
        # sheet.cell(row=rowStartIdx, column=9).value = u'=SUM(I4:I{0})'.format(rowStartIdx-1)
        # sheet.cell(row=rowStartIdx, column=10).value = u'=SUM(J4:J{0})'.format(rowStartIdx-1)
        # sheet.cell(row=rowStartIdx, column=11).value = u'=SUM(K4:K{0})'.format(rowStartIdx-1)

    # 写合计
    sheet['A{0}'.format(rowStartIdx + 1)] = u'合计'
    sheet['B{0}'.format(rowStartIdx + 1)] = '-'
    sheet['C{0}'.format(rowStartIdx + 1)] = '-'
    sheet['D{0}'.format(rowStartIdx + 1)] = '-'
    sheet['E{0}'.format(rowStartIdx + 1)] = '-'
    sheet['F{0}'.format(rowStartIdx + 1)] = '-'
    sheet['G{0}'.format(rowStartIdx + 1)] = '-'

    sheet['H{0}'.format(rowStartIdx + 1)] = Decimal(str(sum(grossWeight_heji))).quantize(Decimal('0.00'))
    sheet['I{0}'.format(rowStartIdx + 1)] = Decimal(str(sum(detectedQuantity_heji))).quantize(Decimal('0.00'))
    sheet['J{0}'.format(rowStartIdx + 1)] = Decimal(str(sum(pureWeight_heji))).quantize(Decimal('0.00'))
    sheet['K{0}'.format(rowStartIdx + 1)] = Decimal(str(sum(amount_heji))).quantize(Decimal('0.00'))
    # 写签名
    sheet.merge_cells('A{0}:C{0}'.format(rowStartIdx + 2, rowStartIdx + 2))
    sheet.merge_cells('D{0}:G{0}'.format(rowStartIdx + 2, rowStartIdx + 2))
    sheet.merge_cells('H{0}:K{0}'.format(rowStartIdx + 2, rowStartIdx + 2))
    sheet['A{0}'.format(rowStartIdx + 2)] = '现场负责人：'
    sheet['A{0}'.format(rowStartIdx + 2)].alignment = Alignment(horizontal="left")
    sheet['D{0}'.format(rowStartIdx + 2)] = '复核：'
    sheet['D{0}'.format(rowStartIdx + 2)].alignment = Alignment(horizontal="left")
    sheet['H{0}'.format(rowStartIdx + 2)] = '制单：'
    sheet['H{0}'.format(rowStartIdx + 2)].alignment = Alignment(horizontal="left")
    sheet.row_dimensions[rowStartIdx + 2].height = 2 * unit
    # 写样式
    sub_area1 = sheet['A{0}:K{1}'.format(3, rowStartIdx + 1)]
    for cs in sub_area1:
        for cell in cs:
            cell.border = border
    # 保存
    fileName = u'{0}-{1}.xlsx'.format(boxNumber,str(name_count))
    filePath = os.path.join(boxDir, fileName)
    filePath_list.append(filePath)
    table.save(filePath)
    all_file_path = '|'.join(filePath_list)
    return all_file_path
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''
>>> import openpyxl
>>> wb = openpyxl.Workbook()
>>> sheet = wb.active
>>> sheet['A1'] = 'Tall row'
>>> sheet['B2'] = 'Wide column'
>>> sheet.row_dimensions[1].height = 70
>>> sheet.column_dimensions['B'].width = 20
>>> wb.save('dimensions.xlsx')
'''
# --------------------------------------装盒票--------------------------------------
def createCaseTicket(**kwargs):
    boxNumber = kwargs['boxNumber']
    caseNumber = kwargs['caseNumber']
    serialNumber2_list = kwargs['serialNumber2_list']

    boxDir = os.path.join(settings.BOX_DATA_PATH, boxNumber)
    if not os.path.exists(boxDir):
        os.mkdir(boxDir)

    box = gsBox.objects.get(boxNumber=boxNumber)
    case = gsCase.objects.get(caseNumber=caseNumber)
    thing_set = gsThing.objects.filter(serialNumber2__in=serialNumber2_list,case=case)

    prop = box.boxType
    type = prop.type
    parentType = prop.parentType
    grandpaType = prop.grandpaType
    if grandpaType:
        className = parentType
        subClassName = type
    else:
        className = type
        subClassName = '-'
    template_path = os.path.join(settings.TEMPLATE_DATA_PATH, u'装盒票.xlsx')
    table = load_workbook(template_path)
    sheet = table.worksheets[0]
    unit = 14.25
    if not sheet.row_dimensions[1].height:
        sheet.row_dimensions[1].height = unit
        h1 = sheet.row_dimensions[1].height
    else:
        h1 = sheet.row_dimensions[1].height

    if not sheet.row_dimensions[2].height:
        sheet.row_dimensions[2].height = unit
        h2 = sheet.row_dimensions[2].height
    else:
        h2 = sheet.row_dimensions[2].height
    if not sheet.row_dimensions[3].height:
        sheet.row_dimensions[3].height = unit
        h3 = sheet.row_dimensions[3].height
    else:
        h3 = sheet.row_dimensions[3].height
    h = h1 + h2 + h3
    print_area = 34 * unit  # 打印区域
    name_count = 1
    row_count = 1
    filePath_list = []
    row_height_list = []
    rowStartIdx = 4

    # 实线边框样式
    border = Border(left=Side(border_style='thin', color='FF000000'),
                    right=Side(border_style='thin', color='FF000000'),
                    top=Side(border_style='thin', color='FF000000'),
                    bottom=Side(border_style='thin', color='FF000000'),
                    outline=Side(border_style='thin', color='FF000000'),
                    vertical=Side(border_style='thin', color='FF000000'),
                    horizontal=Side(border_style='thin', color='FF000000')
                    )
    # font = Font(name=u'仿宋', size=10)
    # alignment = Alignment(horizontal='center', vertical='center')
    # 写合计用
    grossWeight_heji = []
    detectedQuantity_heji = []
    pureWeight_heji = []
    amount_heji = []
    # 写小计用
    grossWeight_xiaoji = []
    detectedQuantity_xiaoji = []
    pureWeight_xiaoji = []
    amount_xiaoji = []

    page = 0  # 只有一页的话就只写合计不写小计
    for i, th in enumerate(thing_set):
        # 写表头
        value_list = []
        sheet['A{0}'.format(2)] = u'盒号:' + caseNumber
        date = datetime.datetime.now()
        year = date.year
        month = date.month
        day = date.day
        sheet['G{0}'.format(2)] = u'{0}年{1}月{2}日'.format(year, month, day)
        # 写表
        # 序号
        col1 = i + 1
        sheet.cell(row=rowStartIdx, column=1).value = col1
        value_list.append((col1, 4))
        # 实物编号
        col2 = th.serialNumber2
        sheet.cell(row=rowStartIdx, column=2).value = col2
        value_list.append((col2, 25))
        # 品种
        col3 = className
        sheet.cell(row=rowStartIdx, column=3).value = col3
        value_list.append((col3, 14))
        # 品名
        col4 = subClassName
        sheet.cell(row=rowStartIdx, column=4).value = col4
        value_list.append((col4, 10))
        # 等级
        col5 = th.level
        sheet.cell(row=rowStartIdx, column=5).value = col5
        value_list.append((col5, 8))
        # 名称
        col6 = th.detailedName
        sheet.cell(row=rowStartIdx, column=6).value = col6
        value_list.append((col6, 32))
        # 毛重
        col7 = '%.2f' % th.grossWeight if th.grossWeight else '%.2f' % 0
        value_len = len(col7)
        if value_len > 12:
            sheet.cell(row=rowStartIdx, column=7).value = col7
        else:
            sheet.cell(row=rowStartIdx, column=7).value = Decimal(col7).quantize(Decimal('0.00'))
        grossWeight_xiaoji.append(float(col7))
        # 检测成色
        col8 = '%.2f' % th.detectedQuantity if th.detectedQuantity else '%.2f' % 0
        value_len = len(col8)
        if value_len > 12:
            sheet.cell(row=rowStartIdx, column=8).value = col8
        else:
            sheet.cell(row=rowStartIdx, column=8).value = Decimal(col8).quantize(Decimal('0.00'))
        detectedQuantity_xiaoji.append(float(col8))
        # 纯重
        col9 = '%.2f' % th.pureWeight if th.pureWeight else '%.2f' % 0
        value_len = len(col9)
        if value_len > 12:
            sheet.cell(row=rowStartIdx, column=9).value = col9
        else:
            sheet.cell(row=rowStartIdx, column=9).value = Decimal(col9).quantize(Decimal('0.00'))
        pureWeight_xiaoji.append(float(col9))
        # 件（枚）数
        col10 = th.amount
        sheet.cell(row=rowStartIdx, column=10).value = col10
        amount_xiaoji.append(float(col10))
        # ----------------------------
        max_row = getRows(value_list)
        sheet.row_dimensions[rowStartIdx].height = unit * max_row
        h_some = unit * max_row
        row_height_list.append(h_some)
        sum_row_height = sum(row_height_list)
        real_h = h + sum_row_height
        other_area = print_area - real_h
        if other_area <= 3 * unit:
            page += 1
            # 写小计
            sheet.cell(row=rowStartIdx + 1, column=1).value = u'小计'
            sheet.cell(row=rowStartIdx + 1, column=2).value = '-'
            sheet.cell(row=rowStartIdx + 1, column=3).value = '-'
            sheet.cell(row=rowStartIdx + 1, column=4).value = '-'
            sheet.cell(row=rowStartIdx + 1, column=5).value = '-'
            sheet.cell(row=rowStartIdx + 1, column=6).value = '-'
            sheet.cell(row=rowStartIdx + 1, column=7).value = Decimal(str(sum(grossWeight_xiaoji))).quantize(
                Decimal('0.00'))
            sheet.cell(row=rowStartIdx + 1, column=8).value = Decimal(str(sum(detectedQuantity_xiaoji))).quantize(
                Decimal('0.00'))
            sheet.cell(row=rowStartIdx + 1, column=9).value = Decimal(str(sum(pureWeight_xiaoji))).quantize(
                Decimal('0.00'))
            sheet.cell(row=rowStartIdx + 1, column=10).value = Decimal(str(sum(amount_xiaoji))).quantize(
                Decimal('0.00'))
            # 写签名
            sheet.merge_cells('A{0}:C{0}'.format(rowStartIdx + 2, rowStartIdx + 2))
            sheet.merge_cells('D{0}:F{0}'.format(rowStartIdx + 2, rowStartIdx + 2))
            sheet.merge_cells('G{0}:J{0}'.format(rowStartIdx + 2, rowStartIdx + 2))
            sheet['A{0}'.format(rowStartIdx + 2)] = '现场负责人：'
            sheet['A{0}'.format(rowStartIdx + 2)].alignment = Alignment(horizontal="left")
            sheet['D{0}'.format(rowStartIdx + 2)] = '复核：'
            sheet['D{0}'.format(rowStartIdx + 2)].alignment = Alignment(horizontal="left")
            sheet['G{0}'.format(rowStartIdx + 2)] = '制单：'
            sheet['G{0}'.format(rowStartIdx + 2)].alignment = Alignment(horizontal="left")
            sheet.row_dimensions[rowStartIdx + 2].height = 2 * unit
            # 写样式
            sub_area1 = sheet['A{0}:J{1}'.format(3, rowStartIdx + 1)]
            for cs in sub_area1:
                for cell in cs:
                    cell.border = border
            # 保存
            fileName = u'{0}.xlsx'.format(str(name_count))
            filePath = os.path.join(boxDir, fileName)
            filePath_list.append(filePath)
            table.save(filePath)
            # -------------
            grossWeight_heji = grossWeight_heji + grossWeight_xiaoji
            detectedQuantity_heji = detectedQuantity_heji + detectedQuantity_xiaoji
            pureWeight_heji = pureWeight_heji + pureWeight_xiaoji
            amount_heji = amount_heji + amount_xiaoji
            # 重新初始化
            name_count += 1
            rowStartIdx = 4
            row_height_list = []
            template_path = os.path.join(settings.TEMPLATE_DATA_PATH, u'装盒票.xlsx')
            table = load_workbook(template_path)
            sheet = table.worksheets[0]

            grossWeight_xiaoji = []
            detectedQuantity_xiaoji = []
            pureWeight_xiaoji = []
            amount_xiaoji = []

        else:
            rowStartIdx += 1
            row_count += 1
    if page > 0:
        # 写小计
        sheet.cell(row=rowStartIdx, column=1).value = u'小计'
        sheet.cell(row=rowStartIdx, column=2).value = '-'
        sheet.cell(row=rowStartIdx, column=3).value = '-'
        sheet.cell(row=rowStartIdx, column=4).value = '-'
        sheet.cell(row=rowStartIdx, column=5).value = '-'
        sheet.cell(row=rowStartIdx, column=6).value = '-'
        sheet.cell(row=rowStartIdx, column=7).value = Decimal(str(sum(grossWeight_xiaoji))).quantize(Decimal('0.00'))
        sheet.cell(row=rowStartIdx, column=8).value = Decimal(str(sum(detectedQuantity_xiaoji))).quantize(
            Decimal('0.00'))
        sheet.cell(row=rowStartIdx, column=9).value = Decimal(str(sum(pureWeight_xiaoji))).quantize(Decimal('0.00'))
        sheet.cell(row=rowStartIdx, column=10).value = Decimal(str(sum(amount_xiaoji))).quantize(Decimal('0.00'))
    # 写合计
    sheet['A{0}'.format(rowStartIdx + 1)] = u'合计'
    sheet['B{0}'.format(rowStartIdx + 1)] = '-'
    sheet['C{0}'.format(rowStartIdx + 1)] = '-'
    sheet['D{0}'.format(rowStartIdx + 1)] = '-'
    sheet['E{0}'.format(rowStartIdx + 1)] = '-'
    sheet['F{0}'.format(rowStartIdx + 1)] = '-'
    sheet['G{0}'.format(rowStartIdx + 1)] = Decimal(str(sum(grossWeight_heji))).quantize(Decimal('0.00'))
    sheet['H{0}'.format(rowStartIdx + 1)] = Decimal(str(sum(detectedQuantity_heji))).quantize(Decimal('0.00'))
    sheet['I{0}'.format(rowStartIdx + 1)] = Decimal(str(sum(pureWeight_heji))).quantize(Decimal('0.00'))
    sheet['J{0}'.format(rowStartIdx + 1)] = Decimal(str(sum(amount_heji))).quantize(Decimal('0.00'))
    # 写签名
    sheet.merge_cells('A{0}:C{0}'.format(rowStartIdx + 2, rowStartIdx + 2))
    sheet.merge_cells('D{0}:F{0}'.format(rowStartIdx + 2, rowStartIdx + 2))
    sheet.merge_cells('G{0}:J{0}'.format(rowStartIdx + 2, rowStartIdx + 2))
    sheet['A{0}'.format(rowStartIdx + 2)] = '现场负责人：'
    sheet['A{0}'.format(rowStartIdx + 2)].alignment = Alignment(horizontal="left")
    sheet['D{0}'.format(rowStartIdx + 2)] = '复核：'
    sheet['D{0}'.format(rowStartIdx + 2)].alignment = Alignment(horizontal="left")
    sheet['G{0}'.format(rowStartIdx + 2)] = '制单：'
    sheet['G{0}'.format(rowStartIdx + 2)].alignment = Alignment(horizontal="left")
    sheet.row_dimensions[rowStartIdx + 2].height = 2 * unit
    # 写样式
    sub_area1 = sheet['A{0}:J{1}'.format(3, rowStartIdx + 1)]
    for cs in sub_area1:
        for cell in cs:
            cell.border = border
    # 保存
    fileName = u'{0}.xlsx'.format(str(name_count))
    filePath = os.path.join(boxDir, fileName)
    filePath_list.append(filePath)
    table.save(filePath)
    all_file_path = '|'.join(filePath_list)
    return all_file_path

def outputDing(r, s, manager, productType, className, subClassName, wareHouse, date, reportWordDir):
    wb = load_workbook(os.path.join(templateRootDir, u'金银锭类信息档案.xlsx'))
    ws = wb.worksheets[0]

    a1 = Alignment(horizontal='center', vertical='center')
    a2 = Alignment(horizontal='center', vertical='center')

    ds = date.split('/')
    # 写表头
    ws['B1'] = u'中国人民银行' + wareHouse
    # 写日期
    ws['B3'] = u'填表日期:' + ds[2] + u'年' + ds[0] + u'月' + ds[1] + u'日'

    # 写箱号
    ws['E5'] = r.thing.box.boxNumber
    cs = ws['E5']
    cs.alignment = a2
    # 写品名
    ws['E6'] = className
    cs = ws['E6']
    cs.alignment = a2
    # 写明细品名
    ws['E7'] = subClassName
    cs = ws['E7']
    cs.alignment = a2
    # 写编号
    ws['E8'] = r.thing.serialNumber
    cs = ws['E8']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F5:F8')
    cs = ws['F5']
    cs.alignment = a1
    ws['F5'] = manager

    # 写名称
    ws['E9'] = r.detailedName
    cs = ws['E9']
    cs.alignment = a2
    # 写型制类型
    ws['E10'] = r.typeName
    cs = ws['E10']
    cs.alignment = a2
    # 写时代
    ws['E11'] = r.peroid
    cs = ws['E11']
    cs.alignment = a2
    # 写制作地人
    ws['E12'] = r.producerPlace
    cs = ws['E12']
    cs.alignment = a2
    # 写铭文
    ws['E13'] = r.carveName
    cs = ws['E13']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F9:F13')
    cs = ws['F9']
    cs.alignment = a1
    ws['F9'] = s.numberingOperator

    # 写毛重
    ws['E14'] = r.grossWeight
    cs = ws['E14']
    cs.alignment = a2
    # 写经办人
    cs = ws['F14']
    cs.alignment = a2
    ws['F14'] = s.measuringOperator

    # 写原标注
    ws['E15'] = r.originalQuantity
    cs = ws['E15']
    cs.alignment = a2
    # 写经办人
    cs = ws['F15']
    cs.alignment = a2
    ws['F15'] = s.numberingOperator

    # 写仪器检测
    ws['E16'] = r.detectedQuantity
    cs = ws['E16']
    cs.alignment = a2
    # 写经办人
    cs = ws['F16']
    cs.alignment = a1
    ws['F16'] = s.analyzingOperator

    # 写纯重
    if (r.grossWeight is not None and r.detectedQuantity is not None):
        ws['E17'] = float('%0.2f' % (r.grossWeight * r.detectedQuantity / 100))
    cs = ws['E17']
    cs.alignment = a2
    # 写经办人
    cs = ws['F17']
    cs.alignment = a1
    ws['F17'] = s.measuringOperator

    # 写长度
    ws['E18'] = r.length
    cs = ws['E18']
    cs.alignment = a2
    # 写宽度
    ws['E19'] = r.width
    cs = ws['E19']
    cs.alignment = a2
    # 写高度
    ws['E20'] = r.height
    cs = ws['E20']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F18:F20')
    cs = ws['F18']
    cs.alignment = a1
    ws['F18'] = s.measuringOperator

    # 写品相
    ws['E21'] = r.quality
    cs = ws['E21']
    cs.alignment = a2
    # 写评价等级
    ws['E22'] = r.level
    cs = ws['E22']
    cs.alignment = a2
    # 写备注
    ws['E23'] = r.remark
    cs = ws['E23']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F21:F24')
    cs = ws['F21']
    cs.alignment = a1
    ws['F21'] = s.numberingOperator

    # fix the bug: 样式丢失
    border = Border(left=Side(border_style='thin', color='FF000000'),
                    right=Side(border_style='thin', color='FF000000'),
                    top=Side(border_style='thin', color='FF000000'),
                    bottom=Side(border_style='thin', color='FF000000'),
                    outline=Side(border_style='thin', color='FF000000'),
                    vertical=Side(border_style='thin', color='FF000000'),
                    horizontal=Side(border_style='thin', color='FF000000')
                    )
    table = ws['B4':'F24']
    for cells in table:
        for cell in cells:
            cell.border = border

    fileName = r.thing.serialNumber + u'.xlsx'
    filePath = os.path.join(reportWordDir, fileName)
    wb.save(filePath)

    return (filePath, fileName)


def outputYinYuan(r, s, manager, productType, className, subClassName, wareHouse, date, reportWordDir):
    wb = load_workbook(os.path.join(templateRootDir, u'银元类信息档案.xlsx'))
    ws = wb.worksheets[0]

    a1 = Alignment(horizontal='center', vertical='center')
    a2 = Alignment(horizontal='center', vertical='center')

    ds = date.split('/')
    # 写表头
    ws['B1'] = u'中国人民银行' + wareHouse
    # 写日期
    ws['B3'] = u'填表日期:' + ds[2] + u'年' + ds[0] + u'月' + ds[1] + u'日'

    # 写箱号
    ws['E5'] = r.thing.box.boxNumber
    cs = ws['E5']
    cs.alignment = a2
    # 写品名
    ws['E6'] = className
    cs = ws['E6']
    cs.alignment = a2
    # 写明细品名
    ws['E7'] = subClassName
    cs = ws['E7']
    cs.alignment = a2
    # 写编号
    ws['E8'] = r.thing.serialNumber
    cs = ws['E8']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F5:F8')
    cs = ws['F5']
    cs.alignment = a1
    ws['F5'] = manager

    # 写版别
    ws['E9'] = r.versionName
    cs = ws['E9']
    cs.alignment = a2
    # 写制作地人
    ws['E10'] = r.producerPlace
    cs = ws['E10']
    cs.alignment = a2
    # 写边齿
    ws['E11'] = r.marginShape
    cs = ws['E11']
    cs.alignment = a2
    # 写时代
    ws['E12'] = r.peroid
    cs = ws['E12']
    cs.alignment = a2
    # 写币值
    ws['E13'] = r.value
    cs = ws['E13']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F9:F13')
    cs = ws['F9']
    cs.alignment = a1
    ws['F9'] = s.numberingOperator

    # 写仪器检测
    ws['E14'] = r.detectedQuantity
    cs = ws['E14']
    cs.alignment = a2
    # 写经办人
    cs = ws['F14']
    cs.alignment = a2
    ws['F14'] = s.analyzingOperator

    # 写毛重
    ws['E15'] = r.grossWeight
    cs = ws['E15']
    cs.alignment = a2
    # 写直径
    ws['E16'] = r.diameter
    cs = ws['E16']
    cs.alignment = a2
    # 写厚度
    ws['E17'] = r.thick
    cs = ws['E17']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F15:F17')
    cs = ws['F15']
    cs.alignment = a1
    ws['F15'] = s.measuringOperator

    # 写品相
    ws['E18'] = r.quality
    cs = ws['E18']
    cs.alignment = a2
    # 写评价等级
    ws['E18'] = r.level
    cs = ws['E19']
    cs.alignment = a2
    # 写备注
    ws['E20'] = r.remark
    cs = ws['E20']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F18:F21')
    cs = ws['F18']
    cs.alignment = a1
    ws['F20'] = s.numberingOperator

    # fix the bug: 样式丢失
    border = Border(left=Side(border_style='thin', color='FF000000'),
                    right=Side(border_style='thin', color='FF000000'),
                    top=Side(border_style='thin', color='FF000000'),
                    bottom=Side(border_style='thin', color='FF000000'),
                    outline=Side(border_style='thin', color='FF000000'),
                    vertical=Side(border_style='thin', color='FF000000'),
                    horizontal=Side(border_style='thin', color='FF000000')
                    )
    table = ws['B4':'F21']
    for cells in table:
        for cell in cells:
            cell.border = border

    fileName = r.thing.serialNumber + '.xlsx'
    filePath = os.path.join(reportWordDir, fileName)
    wb.save(filePath)

    return (filePath, fileName)


def outputBiZhang(r, s, manager, productType, className, subClassName, wareHouse, date, reportWordDir):
    wb = load_workbook(os.path.join(templateRootDir, u'金银币章类信息档案.xlsx'))
    ws = wb.worksheets[0]

    a1 = Alignment(horizontal='center', vertical='center')
    a2 = Alignment(horizontal='center', vertical='center')

    ds = date.split('/')
    # 写表头
    ws['B1'] = u'中国人民银行' + wareHouse
    # 写日期
    ws['B3'] = u'填表日期:' + ds[2] + u'年' + ds[0] + u'月' + ds[1] + u'日'

    # 写箱号
    ws['E5'] = r.thing.box.boxNumber
    cs = ws['E5']
    cs.alignment = a2
    # 写品名
    ws['E6'] = className
    cs = ws['E6']
    cs.alignment = a2
    # 写明细品名
    ws['E7'] = subClassName
    cs = ws['E7']
    cs.alignment = a2
    # 写编号
    ws['E8'] = r.thing.serialNumber
    cs = ws['E8']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F5:F8')
    cs = ws['F5']
    cs.alignment = a1
    ws['F5'] = manager

    # 写名称
    ws['E9'] = r.detailedName
    cs = ws['E9']
    cs.alignment = a2
    # 写版别
    ws['E10'] = r.versionName
    cs = ws['E10']
    cs.alignment = a2
    # 写时代
    ws['E11'] = r.peroid
    cs = ws['E11']
    cs.alignment = a2
    # 写制作地人
    ws['E12'] = r.producerPlace
    cs = ws['E12']
    cs.alignment = a2
    # 写币值
    ws['E13'] = r.value
    cs = ws['E13']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F9:F13')
    cs = ws['F9']
    cs.alignment = a1
    ws['F9'] = s.numberingOperator

    # 写毛重
    ws['E14'] = r.grossWeight
    cs = ws['E14']
    cs.alignment = a2
    # 写经办人
    cs = ws['F14']
    cs.alignment = a2
    ws['F14'] = s.measuringOperator

    # 写原标注
    ws['E15'] = r.originalQuantity
    cs = ws['E15']
    cs.alignment = a2
    # 写经办人
    cs = ws['F15']
    cs.alignment = a2
    ws['F15'] = s.numberingOperator

    # 写仪器检测
    ws['E16'] = r.detectedQuantity
    cs = ws['E16']
    cs.alignment = a2
    # 写经办人
    cs = ws['F16']
    cs.alignment = a1
    ws['F16'] = s.analyzingOperator

    # 写纯重
    if (r.grossWeight is not None and r.detectedQuantity is not None):
        ws['E17'] = float('%0.2f' % (r.grossWeight * r.detectedQuantity / 100))
    cs = ws['E17']
    cs.alignment = a2
    # 写经办人
    cs = ws['F17']
    cs.alignment = a1
    ws['F17'] = s.measuringOperator

    # 写直径
    ws['E18'] = r.diameter
    cs = ws['E18']
    cs.alignment = a2
    # 写厚度
    ws['E19'] = r.thick
    cs = ws['E19']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F18:F19')
    cs = ws['F18']
    cs.alignment = a1
    ws['F18'] = s.measuringOperator

    # 写品相
    ws['E20'] = r.quality
    cs = ws['E20']
    cs.alignment = a2
    # 写评价等级
    ws['E21'] = r.level
    cs = ws['E21']
    cs.alignment = a2
    # 写备注
    ws['E22'] = r.remark
    cs = ws['E22']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F20:F23')
    cs = ws['F20']
    cs.alignment = a1
    ws['F20'] = s.numberingOperator

    # fix the bug: 样式丢失
    border = Border(left=Side(border_style='thin', color='FF000000'),
                    right=Side(border_style='thin', color='FF000000'),
                    top=Side(border_style='thin', color='FF000000'),
                    bottom=Side(border_style='thin', color='FF000000'),
                    outline=Side(border_style='thin', color='FF000000'),
                    vertical=Side(border_style='thin', color='FF000000'),
                    horizontal=Side(border_style='thin', color='FF000000')
                    )
    table = ws['B4':'F23']
    for cells in table:
        for cell in cells:
            cell.border = border

    fileName = r.thing.serialNumber + '.xlsx'
    filePath = os.path.join(reportWordDir, fileName)
    wb.save(filePath)

    return (filePath, fileName)


def outputGongYiPin(r, s, manager, productType, className, subClassName, wareHouse, date, reportWordDir):
    wb = load_workbook(os.path.join(templateRootDir, u'金银工艺品类信息档案.xlsx'))
    ws = wb.worksheets[0]

    a1 = Alignment(horizontal='center', vertical='center')
    a2 = Alignment(horizontal='center', vertical='center')

    ds = date.split('/')
    # 写表头
    ws['B1'] = u'中国人民银行' + wareHouse
    # 写日期
    ws['B3'] = u'填表日期:' + ds[2] + u'年' + ds[0] + u'月' + ds[1] + u'日'

    # 写箱号
    ws['E5'] = r.thing.box.boxNumber
    cs = ws['E5']
    cs.alignment = a2
    # 写品名
    ws['E6'] = className
    cs = ws['E6']
    cs.alignment = a2
    # 写明细品名
    ws['E7'] = subClassName
    cs = ws['E7']
    cs.alignment = a2
    # 写编号
    ws['E8'] = r.thing.serialNumber
    cs = ws['E8']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F5:F8')
    cs = ws['F5']
    cs.alignment = a1
    ws['F5'] = manager

    # 写名称
    ws['E9'] = r.detailedName
    cs = ws['E9']
    cs.alignment = a2
    # 写时代
    ws['E10'] = r.peroid
    cs = ws['E10']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F9:F10')
    cs = ws['F9']
    cs.alignment = a1
    ws['F9'] = s.numberingOperator

    # 写毛重
    ws['E11'] = r.grossWeight
    cs = ws['E11']
    cs.alignment = a2
    # 写经办人
    cs = ws['F11']
    cs.alignment = a2
    ws['F11'] = s.measuringOperator

    # 写原标注
    ws['E12'] = r.originalQuantity
    cs = ws['E12']
    cs.alignment = a2
    # 写经办人
    cs = ws['F12']
    cs.alignment = a2
    ws['F12'] = s.numberingOperator

    # 写仪器检测
    ws['E13'] = r.detectedQuantity
    cs = ws['E13']
    cs.alignment = a2
    # 写经办人
    cs = ws['F13']
    cs.alignment = a1
    ws['F13'] = s.analyzingOperator

    # 写纯重
    if (r.grossWeight is not None and r.detectedQuantity is not None):
        ws['E14'] = float('%0.2f' % (r.grossWeight * r.detectedQuantity / 100))
    cs = ws['E14']
    cs.alignment = a2
    # 写经办人
    cs = ws['F14']
    cs.alignment = a1
    ws['F14'] = s.measuringOperator

    # 写长度
    ws['E15'] = r.length
    cs = ws['E15']
    cs.alignment = a2
    # 写宽度
    ws['E16'] = r.width
    cs = ws['E16']
    cs.alignment = a2
    # 写高度
    ws['E17'] = r.height
    cs = ws['E17']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F15:F17')
    cs = ws['F15']
    cs.alignment = a1
    ws['F15'] = s.measuringOperator

    # 写品相
    ws['E18'] = r.quality
    cs = ws['E18']
    cs.alignment = a2
    # 写评价等级
    ws['E19'] = r.level
    cs = ws['E19']
    cs.alignment = a2
    # 写备注
    ws['E20'] = r.remark
    cs = ws['E20']
    cs.alignment = a2
    # 写经办人
    ws.merge_cells('F18:F20')
    cs = ws['F18']
    cs.alignment = a1
    ws['F18'] = s.numberingOperator

    # fix the bug: 样式丢失
    border = Border(left=Side(border_style='thin', color='FF000000'),
                    right=Side(border_style='thin', color='FF000000'),
                    top=Side(border_style='thin', color='FF000000'),
                    bottom=Side(border_style='thin', color='FF000000'),
                    outline=Side(border_style='thin', color='FF000000'),
                    vertical=Side(border_style='thin', color='FF000000'),
                    horizontal=Side(border_style='thin', color='FF000000')
                    )
    table = ws['B4':'F21']
    for cells in table:
        for cell in cells:
            cell.border = border

    fileName = r.thing.serialNumber + '.xlsx'
    filePath = os.path.join(reportWordDir, fileName)
    wb.save(filePath)

    return (filePath, fileName)


def DingAbstract(r):
    c_format = u'箱号:{0}  编号:{1}  名称:{2}  时代:{3}  铭文:{4}  原标注成色:{5}%  检测成色:{6}%  长:{7}mm 宽:{8}mm  高:{9}mm  毛重:{10}g  纯重:{11}g'
    c = c_format.format(r.thing.box.boxNumber, r.thing.serialNumber, r.detailedName, r.peroid, r.carveName, r.originalQuantity,
                        r.detectedQuantity, r.length, r.width, r.height, r.grossWeight,
                        float('%0.2f' % (r.grossWeight * r.detectedQuantity / 100)))

    return c


def YinYuanAbstract(r):
    c_format = u'箱号:{0}  编号:{1}  名称:{2}  时代:{3}  币值:{4}  原标注成色:{5}%  检测成色:{6}%  直径:{7}mm 厚度:{8}mm 毛重:{9}g'
    c = c_format.format(r.thing.box.boxNumber, r.thing.serialNumber, r.detailedName, r.peroid, r.value, r.originalQuantity,
                        r.detectedQuantity, r.diameter, r.thick, r.grossWeight)

    return c


def BiZhangAbstract(r):
    c_format = u'箱号:{0}  编号:{1}  名称:{2}  时代:{3}  币值:{4}  原标注成色:{5}%  检测成色:{6}%  长:{7}mm  宽:{8}mm  高:{9}mm  毛重:{10}g  纯重:{11}g'
    c = c_format.format(r.thing.box.boxNumber, r.thing.serialNumber, r.detailedName, r.peroid, r.value, r.originalQuantity,
                        r.detectedQuantity, r.length, r.width, r.height, r.grossWeight,
                        float('%0.2f' % (r.grossWeight * r.detectedQuantity / 100)))

    return c


def GongYiPinAbstract(r):
    c_format = u'箱号:{0}  编号:{1}  名称:{2}  时代:{3}  原标注成色:{4}%  检测成色:{5}%  长:{6}mm  宽:{7}mm  高:{8}mm  毛重:{8}g  纯重:{10}g'
    c = c_format.format(r.thing.box.boxNumber, r.thing.serialNumber, r.detailedName, r.peroid, r.originalQuantity,
                        r.detectedQuantity, r.length, r.width, r.height, r.grossWeight,
                        float('%0.2f' % (r.grossWeight * r.detectedQuantity / 100)))

    return c


def writeDataIntoXLS(ws, c, row, col, seq):
    idx = seq % 9
    # Abstract Text
    font = Font(name=u'宋体', size=12, bold=False)
    alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
    if (idx < 3):
        if (0 == idx % 3):
            text_pos_left_row = row
            text_pos_left_col = chr(ord(col))
            text_pos_right_row = row + 2 + 3
            text_pos_right_col = chr(ord(col) + 2)
        elif (1 == idx % 3):
            text_pos_left_row = row
            text_pos_left_col = chr(ord(col) + 4)
            text_pos_right_row = row + 2 + 3
            text_pos_right_col = chr(ord(col) + 6)
        elif (2 == idx % 3):
            text_pos_left_row = row
            text_pos_left_col = chr(ord(col) + 8)
            text_pos_right_row = row + 2 + 3
            text_pos_right_col = chr(ord(col) + 10)
    elif (idx >= 3 and idx < 6):
        if (0 == idx % 3):
            text_pos_left_row = row + 8
            text_pos_left_col = chr(ord(col))
            text_pos_right_row = row + 8 + 2 + 3
            text_pos_right_col = chr(ord(col) + 2)
        elif (1 == idx % 3):
            text_pos_left_row = row + 8
            text_pos_left_col = chr(ord(col) + 4)
            text_pos_right_row = row + 8 + 2 + 3
            text_pos_right_col = chr(ord(col) + 6)
        elif (2 == idx % 3):
            text_pos_left_row = row + 8
            text_pos_left_col = chr(ord(col) + 8)
            text_pos_right_row = row + 8 + 2 + 3
            text_pos_right_col = chr(ord(col) + 10)
    elif (idx >= 6):
        if (0 == idx % 3):
            text_pos_left_row = row + 8 + 8
            text_pos_left_col = chr(ord(col))
            text_pos_right_row = row + 8 + 8 + 2 + 3
            text_pos_right_col = chr(ord(col) + 2)
        elif (1 == idx % 3):
            text_pos_left_row = row + 8 + 8
            text_pos_left_col = chr(ord(col) + 4)
            text_pos_right_row = row + 8 + 8 + 2 + 3
            text_pos_right_col = chr(ord(col) + 6)
        elif (2 == idx % 3):
            text_pos_left_row = row + 8 + 8
            text_pos_left_col = chr(ord(col) + 8)
            text_pos_right_row = row + 8 + 8 + 2 + 3
            text_pos_right_col = chr(ord(col) + 10)

    text_start_pos = text_pos_left_col + str(text_pos_left_row)
    text_end_pos = text_pos_right_col + str(text_pos_right_row)
    ws.merge_cells(text_start_pos + ':' + text_end_pos)
    cs = ws[text_start_pos]
    cs.font = font
    cs.alignment = alignment
    cs.value = c


def createThingAbstract(workName,subBoxNumber,boxNumber,workSeq):
    '''
    清点查验完毕，生成实物信息摘要
    '''
    box = gsBox.objects.get(boxNumber=boxNumber)
    productTypeCode = box.productType
    type = gsProperty.objects.get(project='实物类型', code=productTypeCode).type

    if workSeq:
        workSeq = int(workSeq)
        if subBoxNumber:
            subBox = gsSubBox.objects.get(box=box, subBoxNumber=int(subBoxNumber))
            work = gsWork.objects.get(box=box, workSeq=workSeq, subBox=subBox)
        else:
            work = gsWork.objects.get(box=box, workSeq=workSeq)

        thing_set = gsThing.objects.filter(work=work)

        ss = gsStatus.objects.filter(thing__in=thing_set)
    else:
        thing_set = gsThing.objects.filter(box=box)
        ss = gsStatus.objects.filter(thing=thing_set)

    rs = []
    for i in ss:
        if (type == u'金银锭类') and int(i.status):
            ding = gsDing.objects.get(serialNumber=i.serialNumber)
            rs.append(ding)
            outputAbstract = DingAbstract
        elif (0 == cmp(type, u'金银币章类')) and int(i.status):
            biZhang = gsBiZhang.objects.get(serialNumber=i.serialNumber)
            rs.append(biZhang)
            outputAbstract = BiZhangAbstract
        elif (0 == cmp(type, u'银元类')) and int(i.status):
            yinYuan = gsYinYuan.objects.get(serialNumber=i.serialNumber)
            rs.append(yinYuan)
            outputAbstract = YinYuanAbstract
        elif (0 == cmp(type, u'金银工艺品类')) and int(i.status):
            gongYiPin = gsGongYiPin.objects.get(serialNumber=i.serialNumber)
            rs.append(gongYiPin)
            outputAbstract = GongYiPinAbstract

    if rs:
        global boxDir
        boxDir = os.path.join(boxRootDir, str(boxNumber))
        if not os.path.exists(boxDir):
            os.mkdir(boxDir)  # 转移至创建作业时, 生成相应的目录

        xlFileName = u'{0}实物信息摘要.xlsx'.format(workName)
        xlFilePath = os.path.join(boxDir, xlFileName)
        if not os.path.exists(xlFilePath):
            wb = Workbook()
            ws = wb.active

            idx = 0
            start_col = 'C'
            start_row = 0
            for r in rs:
                if (0 == idx % 9):
                    page = int(math.floor(idx / 9))
                    row = start_row + page * 24
                c = outputAbstract(r)
                writeDataIntoXLS(ws, c, row + 1, start_col, idx)

                idx = idx + 1

            ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
            ws.sheet_view.view = 'pageBreakPreview'
            # 单位: 英寸 inches. 1英寸==2.53CM
            ws.page_margins.left = 4.40 / 2.53
            ws.page_margins.right = 0.10 / 2.53
            ws.page_margins.top = 5.40 / 2.53
            ws.page_margins.bottom = 4.55 / 2.53
            ws.page_margins.header = 1.29 / 2.53
            ws.page_margins.footer = 1.29 / 2.53
            ws.column_dimensions['B'].width = 12
            ws.column_dimensions['F'].width = 5
            ws.column_dimensions['J'].width = 5

            wb.save(xlFilePath)
        ret = {
            'success': True,
            'downloadURL': u'generateAbstract/?boxNumber={0}&workName={1}'.format(boxNumber,workName),
        }
        return ret
    else:
        ret = {
            'success': False,
        }
        return ret



    # box = gsBox.objects.get(boxNumber=boxNumber)
    # productTypeCode = box.productType
    # productType = gsProperty.objects.get(project='实物类型', code=productTypeCode)
    #
    # if (0 == cmp(productType.type, u'金银锭类')):
    #     rs = gsDing.objects.filter(box=box)
    #     outputAbstract = DingAbstract
    # elif (0 == cmp(productType.type, u'金银币章类')):
    #     rs = gsBiZhang.objects.filter(box=box)
    #     outputAbstract = BiZhangAbstract
    # elif (0 == cmp(productType.type, u'银元类')):
    #     rs = gsYinYuan.objects.filter(box=box)
    #     outputAbstract = YinYuanAbstract
    # elif (0 == cmp(productType.type, u'金银工艺品类')):
    #     rs = gsGongYiPin.objects.filter(box=box)
    #     outputAbstract = GongYiPinAbstract
    #
    # global boxDir
    # boxDir = os.path.join(boxRootDir, str(boxNumber))
    # if not os.path.exists(boxDir):
    #     os.mkdir(boxDir)  # 转移至创建作业时, 生成相应的目录
    #
    # xlFileName = u'{0}号箱_摘要.xlsx'.format(boxNumber)
    # xlFilePath = os.path.join(boxDir, xlFileName)
    # if not os.path.exists(xlFilePath):
    #     # xlTmplateFileName = 'tag_template.xlsx'
    #     # xlTmplateFilePath = os.path.join(tagDir, xlTmplateFileName)
    #     # wb = load_workbook(xlTmplateFilePath)
    #     wb = Workbook()
    #     ws = wb.active  # A workbook is always created with at least one worksheet. You can get it by using the openpyxl.workbook.Workbook.active() property
    #
    #     # r = rs[0]
    #     # c1 = r.thing.serialNumber
    #     # c2 = c1+'-'+boxNumber
    #     # idx = 0
    #     # tag_pic = createQRCode(c2)
    #     # writeDataIntoXLS(ws, tag_pic, c1, idx)
    #
    #     idx = 0
    #     start_col = 'C'
    #     start_row = 0
    #     for r in rs:
    #         # insert background picture
    #         if (0 == idx % 9):
    #             page = int(math.floor(idx / 9))
    #             row = start_row + page * 24
    #             # filePath = os.path.join(tagRootDir, 'background.png')
    #             # pic = Image(filePath)
    #             # ws.add_image(pic, start_col+str(row))
    #
    #         c = outputAbstract(r)
    #         writeDataIntoXLS(ws, c, row + 1, start_col, idx)
    #
    #         idx = idx + 1
    #
    #     ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
    #     ws.sheet_view.view = 'pageBreakPreview'
    #     # 单位: 英寸 inches. 1英寸==2.53CM
    #     ws.page_margins.left = 4.40 / 2.53
    #     ws.page_margins.right = 0.10 / 2.53
    #     ws.page_margins.top = 5.40 / 2.53
    #     ws.page_margins.bottom = 4.55 / 2.53
    #     ws.page_margins.header = 1.29 / 2.53
    #     ws.page_margins.footer = 1.29 / 2.53
    #     ws.column_dimensions['B'].width = 12
    #     ws.column_dimensions['F'].width = 5
    #     ws.column_dimensions['J'].width = 5
    #
    #     wb.save(xlFilePath)
    #
    #     '''zipFileName = u'{0}_标签.zip'.format(workName)
    #     zipFilePath = os.path.join(tagDir, zipFileName)
    #     f = zipfile.ZipFile(zipFilePath, 'w' ,zipfile.ZIP_DEFLATED)
    #     f.write(xlFilePath, xlFileName)
    #     f.close()'''
