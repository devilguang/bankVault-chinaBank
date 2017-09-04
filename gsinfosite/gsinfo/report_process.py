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

templateRootDir = settings.DATA_DIRS['template_dir']
boxRootDir = settings.DATA_DIRS['box_dir']
boxDir = boxRootDir
boxPhotoDir = boxDir
boxWordDir = boxDir
workRootDir = settings.DATA_DIRS['work_dir']
workDir = workRootDir


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
        t = gsThing.objects.get(box=box, serialNumber=serialNumber)
        subBoxSeq = t.subBoxSeq
        wordDir = os.path.join(boxDir, u'{0}_{1}_{2}_word'.format(createDateTime.year, subBoxSeq, wareHouse.type))

        s = gsStatus.objects.get(box=box, serialNumber=serialNumber)
        if (0 == cmp(productType.type, u'金银锭类')):
            r = gsDing.objects.get(box=box, serialNumber=serialNumber)

            (filePath, fileName) = outputDing(r, s, manager, productType.type, className.type, subClassName.type,
                                              wareHouse.type, dateTime, wordDir)
        elif (0 == cmp(productType.type, u'金银币章类')):
            r = gsBiZhang.objects.get(box=box, serialNumber=serialNumber)

            (filePath, fileName) = outputBiZhang(r, s, manager, productType.type, className.type, subClassName.type,
                                                 wareHouse.type, dateTime, wordDir)
        elif (0 == cmp(productType.type, u'银元类')):
            r = gsYinYuan.objects.get(box=box, serialNumber=serialNumber)

            (filePath, fileName) = outputYinYuan(r, s, manager, productType.type, className.type, subClassName.type,
                                                 wareHouse.type, dateTime, wordDir)
        elif (0 == cmp(productType.type, u'金银工艺品类')):
            r = gsGongYiPin.objects.get(box=box, serialNumber=serialNumber)

            (filePath, fileName) = outputGongYiPin(r, s, manager, productType.type, className.type, subClassName.type,
                                                   wareHouse.type, dateTime, wordDir)

        zip.write(filePath, fileName)

    zip.close()

    return True

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 箱体信息报表
def createBoxTable(boxList):
    global boxDir
    boxDir = os.path.join(boxRootDir, u'箱体报表')
    if not os.path.exists(boxDir):
        os.mkdir(boxDir)  # 转移至创建作业时, 生成相应的目录

    ti = time.strftime("%Y%m%d%H", time.localtime())
    boxReportName = u'{0}箱体报表.xlsx'.format(str(ti))
    boxReportPath = os.path.join(boxDir, boxReportName)

    # 实线边框样式
    border = Border(left=Side(border_style='thin', color='FF000000'),
                    right=Side(border_style='thin', color='FF000000'),
                    top=Side(border_style='thin', color='FF000000'),
                    bottom=Side(border_style='thin', color='FF000000'),
                    outline=Side(border_style='thin', color='FF000000'),
                    vertical=Side(border_style='thin', color='FF000000'),
                    horizontal=Side(border_style='thin', color='FF000000')
                    )
    totalSubBox = 0
    for boxNumber in boxList.keys():
        box = gsBox.objects.get(boxNumber=boxNumber)
        subBox_obj = gsSubBox.objects.filter(box=box)
        num = len(subBox_obj)
        # num = gsThing.objects.filter(box=box).values('subBox').distinct().count()
        totalSubBox += num
    sheetCnt = int(ceil(float(totalSubBox) / float(30)))

    wb = load_workbook(os.path.join(templateRootDir, u'箱体报表.xlsx'))
    ws = wb.worksheets[0]

    for i in range(sheetCnt):
        newSheet = wb.copy_worksheet(ws)
        value = ws.title.encode('utf-8') + unicode(1 + i)
        value = value
        newSheet.title = value

    id = 0
    rowStartIdx = 0
    font = Font(name=u'宋体', size=9)
    alignment = Alignment(horizontal='center', vertical='center')

    for boxNumber,productType in boxList.items():

        boxNumber = int(boxNumber)
        box = gsBox.objects.get(boxNumber=boxNumber)
        subBoxList = gsSubBox.objects.filter(box=box).values_list('subBoxNumber',flat=True)
        # subBoxList = list(subBoxSet)
        rowIdx = rowStartIdx
        for no in subBoxList:
            # 写装箱清单
            if 0 == id % 30:
                # 写表头
                sheetIdx = id / 30
                ws = wb.worksheets[sheetIdx]
                ws['A1'] = u'中国人民银行' + u'箱体报表'
                rowStartIdx = 3
                id = 0
                rowIdx = rowStartIdx

            if id < 30:
                if str(no) == '0':
                    ws.cell(row=rowIdx, column=2).value = str(boxNumber)  # 子箱号
                else:
                    ws.cell(row=rowIdx, column=2).value = str(boxNumber) + '-' + str(no)  # 子箱号
                ws.cell(row=rowIdx, column=2).font = font
                ws.cell(row=rowIdx, column=2).alignment = alignment
                subBox = gsSubBox.objects.get(box=box,subBoxNumber=no)
                things = gsThing.objects.filter(box=box, subBox=subBox)
                ws.cell(row=rowIdx, column=3).value = things.count()  # 件数
                ws.cell(row=rowIdx, column=3).font = font
                ws.cell(row=rowIdx, column=3).alignment = alignment

                # totalWeight = 0
                # for thing in things:
                #     serialNumber = thing.serialNumber
                #     w = ts.get(serialNumber=serialNumber).grossWeight
                #     if w:
                #         totalWeight += w
                ws.cell(row=rowIdx, column=4).value = gsSubBox.objects.get(box=box,subBoxNumber=no).grossWeight  # 子箱总毛重
                ws.cell(row=rowIdx, column=4).font = font
                ws.cell(row=rowIdx, column=4).alignment = alignment

                rowIdx += 1
                id += 1

                if id == 30:
                    ws.merge_cells('E{0}:E{1}'.format(rowStartIdx, rowIdx - 1))
                    ws.merge_cells('F{0}:F{1}'.format(rowStartIdx, rowIdx - 1))
                    ws.merge_cells('G{0}:G{1}'.format(rowStartIdx, rowIdx - 1))

                    ws.cell(row=rowStartIdx, column=5).value = boxNumber  # 原箱号
                    ws.cell(row=rowStartIdx, column=5).font = font
                    ws.cell(row=rowStartIdx, column=5).alignment = alignment

                    ws.cell(row=rowStartIdx, column=6).value = box.amount  # 件数
                    ws.cell(row=rowStartIdx, column=6).font = font
                    ws.cell(row=rowStartIdx, column=6).alignment = alignment

                    ws.cell(row=rowStartIdx, column=7).value = box.grossWeight  # 原箱总毛重
                    ws.cell(row=rowStartIdx, column=7).font = font
                    ws.cell(row=rowStartIdx, column=7).alignment = alignment

                    row = ws['E{0}:G{1}'.format(rowStartIdx, rowIdx)]
                    for cs in row:
                        for cell in cs:
                            cell.border = border

        ws.merge_cells('E{0}:E{1}'.format(rowStartIdx, rowIdx - 1))
        ws.merge_cells('F{0}:F{1}'.format(rowStartIdx, rowIdx - 1))
        ws.merge_cells('G{0}:G{1}'.format(rowStartIdx, rowIdx - 1))

        ws.cell(row=rowStartIdx, column=5).value = boxNumber  # 原箱号
        ws.cell(row=rowStartIdx, column=5).font = font
        ws.cell(row=rowStartIdx, column=5).alignment = alignment

        ws.cell(row=rowStartIdx, column=6).value = box.amount  # 件数
        ws.cell(row=rowStartIdx, column=6).font = font
        ws.cell(row=rowStartIdx, column=6).alignment = alignment

        ws.cell(row=rowStartIdx, column=7).value = box.grossWeight  # 原箱总毛重
        ws.cell(row=rowStartIdx, column=7).font = font
        ws.cell(row=rowStartIdx, column=7).alignment = alignment

        row = ws['E{0}:G{1}'.format(rowStartIdx, rowIdx)]
        for cs in row:
            for cell in cs:
                cell.border = border

        ws.row_dimensions[rowStartIdx + 1].ht = 32.25
        rowStartIdx = rowIdx

    wb.save(boxReportPath)
    return boxReportName
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def createBoxInfo(boxNumber,subBoxNumber, date):
    box = gsBox.objects.get(boxNumber=boxNumber)
    if subBoxNumber == '':
        thing_set = gsThing.objects.filter(box=box)
    else:
        subBox = gsSubBox.objects.get(box=box,subBoxNumber=int(subBoxNumber))
        thing_set = gsThing.objects.filter(box=box,subBox=subBox)

    global boxDir
    boxDir = os.path.join(boxRootDir, str(boxNumber))
    if not os.path.exists(boxDir):
        os.mkdir(boxDir)  # 转移至创建作业时, 生成相应的目录

    # 实线边框样式
    border = Border(left=Side(border_style='thin', color='FF000000'),
                    right=Side(border_style='thin', color='FF000000'),
                    top=Side(border_style='thin', color='FF000000'),
                    bottom=Side(border_style='thin', color='FF000000'),
                    outline=Side(border_style='thin', color='FF000000'),
                    vertical=Side(border_style='thin', color='FF000000'),
                    horizontal=Side(border_style='thin', color='FF000000')
                    )

    ds = date.split('/')
    t = thing_set.first()
    productTypeCode = t.box.productType
    productType = gsProperty.objects.get(project='实物类型', code=productTypeCode)
    wareHouseCode = t.box.wareHouse
    wareHouse = gsProperty.objects.get(project='发行库', code=wareHouseCode)
    if subBoxNumber == '':
        boxInfoFileName = u'{0}_{1}号箱_{2}_list.xlsx'.format(ds[2], boxNumber, wareHouse.type)
    else:
        boxInfoFileName = u'{0}_{1}-{2}号箱_{3}_list.xlsx'.format(ds[2], boxNumber,subBoxNumber, wareHouse.type)
    boxInfoFilePath = os.path.join(boxDir, boxInfoFileName)

    if productType.type == u'金银锭类':
        rs = gsDing.objects.filter(thing__in=thing_set)
        ss = gsStatus.objects.filter(thing__in=thing_set)
        wb = load_workbook(os.path.join(templateRootDir, u'非银元装箱清单.xlsx'))
        ws = wb.worksheets[0]
        sheetCnt = int(ceil(rs.count() / 30))
        for i in range(sheetCnt):
            newSheet = wb.copy_worksheet(ws)
            newSheet.title = ws.title + unicode(1 + i)

        id = 0
        rowStartIdx = 0
        font = Font(name=u'宋体', size=9)
        alignment = Alignment(horizontal='center', vertical='center')
        for r, s in zip(rs, ss):
            # 写装箱清单
            if (0 == id % 30):
                if (0 != id):
                    # 设置当前页打印参数, 并写表尾合计
                    ws.sheet_view.view = 'pageBreakPreview'
                    # 单位: 英寸 inches. 1英寸==2.53CM
                    ws.page_margins.left = 0.43 / 2.53
                    ws.page_margins.right = 0 / 2.53
                    ws.page_margins.top = 0.5 / 2.53
                    ws.page_margins.bottom = 0.3 / 2.53
                    ws.page_margins.header = 0 / 2.53
                    ws.page_margins.footer = 0 / 2.53

                    ws.insert_rows(rowStartIdx - 1, 1, above=False, copy_style=True, fill_formulae=False)
                    ws.merge_cells('A{0}:B{0}'.format(rowStartIdx, rowStartIdx))

                    ws['A{0}'.format(rowStartIdx)] = u'小计'
                    # 写毛重小计
                    ws['D{0}'.format(rowStartIdx)] = u'=SUM(D4:D{0})'.format(rowStartIdx - 1)
                    # 写纯重小计
                    ws['F{0}'.format(rowStartIdx)] = u'=SUM(F4:F{0})'.format(rowStartIdx - 1)

                    # 加边框样式
                    row = ws['A{0}:H{1}'.format(rowStartIdx, rowStartIdx)]
                    for cs in row:
                        for cell in cs:
                            cell.border = border

                    ws.row_dimensions[rowStartIdx + 1].ht = 32.25

                # 写新一页表头
                sheetIdx = id / 30
                ws = wb.worksheets[sheetIdx]
                ws['A1'] = u'中国人民银行' + wareHouse.type + productType.type + u'装箱清单'
                ws['A2'] = u'箱号:' + str(boxNumber)
                ws['D2'] = ds[2] + u'年' + ds[0] + u'月' + ds[1] + u'日'

                rowStartIdx = 4

            # 名称
            ws.cell(row=rowStartIdx, column=2).value = r.detailedName
            ws.cell(row=rowStartIdx, column=2).font = font
            ws.cell(row=rowStartIdx, column=2).alignment = alignment
            # 编号
            ws.cell(row=rowStartIdx, column=3).value = r.serialNumber
            ws.cell(row=rowStartIdx, column=3).font = font
            ws.cell(row=rowStartIdx, column=3).alignment = alignment
            # 毛重
            ws.cell(row=rowStartIdx, column=4).value = r.grossWeight
            ws.cell(row=rowStartIdx, column=4).font = font
            ws.cell(row=rowStartIdx, column=4).alignment = alignment
            # 成色(原标注成色)
            ws.cell(row=rowStartIdx, column=5).value = r.originalQuantity
            ws.cell(row=rowStartIdx, column=5).font = font
            ws.cell(row=rowStartIdx, column=5).alignment = alignment
            # 纯重
            if (r.grossWeight is not None and r.detectedQuantity is not None):
                ws.cell(row=rowStartIdx, column=6).value = float('%0.2f' % (r.grossWeight * r.detectedQuantity / 100))
            ws.cell(row=rowStartIdx, column=6).font = font
            ws.cell(row=rowStartIdx, column=6).alignment = alignment
            # 品相
            ws.cell(row=rowStartIdx, column=7).value = r.quality
            ws.cell(row=rowStartIdx, column=7).font = font
            ws.cell(row=rowStartIdx, column=7).alignment = alignment
            # 评价等级
            ws.cell(row=rowStartIdx, column=8).value = r.level
            ws.cell(row=rowStartIdx, column=8).font = font
            ws.cell(row=rowStartIdx, column=8).alignment = alignment

            # 生成单个实物信息档案
            # outputDing(r, s, productType.type, className.type, subClassName.type, wareHouse.type, date, reportWordDir)

            id = id + 1
            rowStartIdx = rowStartIdx + 1

        # 设置最后一页打印参数, 并写表尾合计
        ws.sheet_view.view = 'pageBreakPreview'
        # 单位: 英寸 inches. 1英寸==2.53CM
        ws.page_margins.left = 0.43 / 2.53
        ws.page_margins.right = 0 / 2.53
        ws.page_margins.top = 0.5 / 2.53
        ws.page_margins.bottom = 0.3 / 2.53
        ws.page_margins.header = 0 / 2.53
        ws.page_margins.footer = 0 / 2.53

        ws.insert_rows(33, 2, above=False, copy_style=True, fill_formulae=False)
        ws.merge_cells('A{0}:B{0}'.format(34, 34))
        ws['A{0}'.format(34)] = u'小计'
        # 写毛重小计
        ws['D{0}'.format(34)] = u'=SUM(D4:D{0})'.format(rowStartIdx - 1)
        # 写纯重小计
        ws['F{0}'.format(34)] = u'=SUM(F4:F{0})'.format(rowStartIdx - 1)

        # 加边框样式
        row = ws['A{0}:H{1}'.format(34, 34)]
        for cs in row:
            for cell in cs:
                cell.border = border

        ws.merge_cells('A{0}:B{0}'.format(35, 35))
        cs = ws['A{0}'.format(rowStartIdx)]
        # cs.alignment = a
        ws['A{0}'.format(35)] = u'合计'

        # 构造合计EXCEL计算公式
        grossWeightTotalFormula = u'=SUM('
        pureWeightTotalFormula = u'=SUM('
        for i in range(sheetCnt + 1):
            ws = wb.worksheets[i]
            if (i != sheetCnt):
                grossWeightTotalFormula = grossWeightTotalFormula + u'{0}!D34'.format(ws.title)
                pureWeightTotalFormula = pureWeightTotalFormula + u'{0}!F34'.format(ws.title)
            else:
                grossWeightTotalFormula = grossWeightTotalFormula + u'D34'.format(ws.title)
                pureWeightTotalFormula = pureWeightTotalFormula + u'F34'.format(ws.title)

            if (i < sheetCnt):
                grossWeightTotalFormula = grossWeightTotalFormula + ','
                pureWeightTotalFormula = pureWeightTotalFormula + ','

        grossWeightTotalFormula = grossWeightTotalFormula + ')'
        pureWeightTotalFormula = pureWeightTotalFormula + ')'

        # 写毛重合计
        ws['D{0}'.format(35)] = u'{0}'.format(grossWeightTotalFormula)
        # 写纯重合计
        ws['F{0}'.format(35)] = u'{0}'.format(pureWeightTotalFormula)

        # 加边框样式
        row = ws['A{0}:H{1}'.format(35, 35)]
        for cs in row:
            for cell in cs:
                cell.border = border

        ws.row_dimensions[36].ht = 32.25

    elif (0 == cmp(productType.type, u'金银币章类')):
        rs = gsBiZhang.objects.filter(thing__in=thing_set)
        ss = gsStatus.objects.filter(thing__in=thing_set)
        wb = load_workbook(os.path.join(templateRootDir, u'非银元装箱清单.xlsx'))
        ws = wb.worksheets[0]
        sheetCnt = int(ceil(rs.count() / 30))
        for i in range(sheetCnt):
            newSheet = wb.copy_worksheet(ws)
            newSheet.title = ws.title + unicode(1 + i)

        id = 0
        font = Font(name=u'宋体', size=9)
        alignment = Alignment(horizontal='center', vertical='center')
        for r, s in zip(rs, ss):
            # 写装箱清单
            if (0 == id % 30):
                if (0 != id):
                    # 设置当前页打印参数, 并写表尾合计
                    ws.sheet_view.view = 'pageBreakPreview'
                    # 单位: 英寸 inches. 1英寸==2.53CM
                    ws.page_margins.left = 0.43 / 2.53
                    ws.page_margins.right = 0 / 2.53
                    ws.page_margins.top = 0.5 / 2.53
                    ws.page_margins.bottom = 0.3 / 2.53
                    ws.page_margins.header = 0 / 2.53
                    ws.page_margins.footer = 0 / 2.53

                    ws.insert_rows(rowStartIdx - 1, 1, above=False, copy_style=True, fill_formulae=False)
                    ws.merge_cells('A{0}:B{0}'.format(rowStartIdx, rowStartIdx))

                    ws['A{0}'.format(rowStartIdx)] = u'小计'
                    # 写毛重小计
                    ws['D{0}'.format(rowStartIdx)] = u'=SUM(D4:D{0})'.format(rowStartIdx - 1)
                    # 写纯重小计
                    ws['F{0}'.format(rowStartIdx)] = u'=SUM(F4:F{0})'.format(rowStartIdx - 1)

                    # 加边框样式
                    row = ws['A{0}:H{1}'.format(rowStartIdx, rowStartIdx)]
                    for cs in row:
                        for cell in cs:
                            cell.border = border

                    ws.row_dimensions[rowStartIdx + 1].ht = 32.25

                # 写表头
                sheetIdx = id / 30
                ws = wb.worksheets[sheetIdx]
                ws['A1'] = u'中国人民银行' + wareHouse.type + productType.type + u'装箱清单'
                ws['A2'] = u'箱号:' + str(boxNumber)
                ws['D2'] = ds[2] + u'年' + ds[0] + u'月' + ds[1] + u'日'

                rowStartIdx = 4

            # 名称
            ws.cell(row=rowStartIdx, column=2).value = r.detailedName
            ws.cell(row=rowStartIdx, column=2).font = font
            ws.cell(row=rowStartIdx, column=2).alignment = alignment
            # 编号
            ws.cell(row=rowStartIdx, column=3).value = r.serialNumber
            ws.cell(row=rowStartIdx, column=3).font = font
            ws.cell(row=rowStartIdx, column=3).alignment = alignment
            # 毛重
            ws.cell(row=rowStartIdx, column=4).value = r.grossWeight
            ws.cell(row=rowStartIdx, column=4).font = font
            ws.cell(row=rowStartIdx, column=4).alignment = alignment
            # 成色(原标注成色)
            ws.cell(row=rowStartIdx, column=5).value = r.originalQuantity
            ws.cell(row=rowStartIdx, column=5).font = font
            ws.cell(row=rowStartIdx, column=5).alignment = alignment
            # 纯重
            if (r.grossWeight is not None and r.detectedQuantity is not None):
                ws.cell(row=rowStartIdx, column=6).value = float(
                    '%0.2f' % (r.grossWeight * r.detectedQuantity / 100))
            ws.cell(row=rowStartIdx, column=6).font = font
            ws.cell(row=rowStartIdx, column=6).alignment = alignment
            # 品相
            ws.cell(row=rowStartIdx, column=7).value = r.quality
            ws.cell(row=rowStartIdx, column=7).font = font
            ws.cell(row=rowStartIdx, column=7).alignment = alignment
            # 评价等级
            ws.cell(row=rowStartIdx, column=8).value = r.level
            ws.cell(row=rowStartIdx, column=8).font = font
            ws.cell(row=rowStartIdx, column=8).alignment = alignment

            # 生成单个实物信息档案
            # outputBiZhang(r, s, productType.type, className.type, subClassName.type, wareHouse.type, date, reportWordDir)

            id = id + 1
            rowStartIdx = rowStartIdx + 1

        # 设置最后一页打印参数, 并写表尾合计
        ws.sheet_view.view = 'pageBreakPreview'
        # 单位: 英寸 inches. 1英寸==2.53CM
        ws.page_margins.left = 0.43 / 2.53
        ws.page_margins.right = 0 / 2.53
        ws.page_margins.top = 0.5 / 2.53
        ws.page_margins.bottom = 0.3 / 2.53
        ws.page_margins.header = 0 / 2.53
        ws.page_margins.footer = 0 / 2.53

        ws.insert_rows(33, 2, above=False, copy_style=True, fill_formulae=False)
        ws.merge_cells('A{0}:B{0}'.format(34, 34))
        # cs = ws['A{0}'.format(rowStartIdx)]
        # cs.alignment = a
        ws['A{0}'.format(34)] = u'小计'
        # 写毛重小计
        ws['D{0}'.format(34)] = u'=SUM(D4:D{0})'.format(rowStartIdx - 1)
        # 写纯重小计
        ws['F{0}'.format(34)] = u'=SUM(F4:F{0})'.format(rowStartIdx - 1)

        # 加边框样式
        row = ws['A{0}:H{1}'.format(34, 34)]
        for cs in row:
            for cell in cs:
                cell.border = border

        ws.merge_cells('A{0}:B{0}'.format(35, 35))
        cs = ws['A{0}'.format(rowStartIdx)]
        # cs.alignment = a
        ws['A{0}'.format(35)] = u'合计'

        # 构造合计EXCEL计算公式
        grossWeightTotalFormula = u'=SUM('
        pureWeightTotalFormula = u'=SUM('
        for i in range(sheetCnt + 1):
            ws = wb.worksheets[i]
            if (i != sheetCnt):
                grossWeightTotalFormula = grossWeightTotalFormula + u'{0}!D34'.format(ws.title)
                pureWeightTotalFormula = pureWeightTotalFormula + u'{0}!F34'.format(ws.title)
            else:
                grossWeightTotalFormula = grossWeightTotalFormula + u'D34'.format(ws.title)
                pureWeightTotalFormula = pureWeightTotalFormula + u'F34'.format(ws.title)

            if (i < sheetCnt):
                grossWeightTotalFormula = grossWeightTotalFormula + ','
                pureWeightTotalFormula = pureWeightTotalFormula + ','

        grossWeightTotalFormula = grossWeightTotalFormula + ')'
        pureWeightTotalFormula = pureWeightTotalFormula + ')'

        # 写毛重合计
        ws['D{0}'.format(35)] = u'{0}'.format(grossWeightTotalFormula)
        # 写纯重合计
        ws['F{0}'.format(35)] = u'{0}'.format(pureWeightTotalFormula)

        # 加边框样式
        row = ws['A{0}:H{1}'.format(35, 35)]
        for cs in row:
            for cell in cs:
                cell.border = border

        ws.row_dimensions[36].ht = 32.25

    elif (0 == cmp(productType.type, u'银元类')):
        rs = gsYinYuan.objects.filter(thing__in=thing_set)
        ss = gsStatus.objects.filter(thing__in=thing_set)
        wb = load_workbook(os.path.join(templateRootDir, u'银元装箱清单.xlsx'))
        ws = wb.worksheets[0]
        sheetCnt = int(ceil(rs.count() / 30))
        for i in range(sheetCnt):
            newSheet = wb.copy_worksheet(ws)
            newSheet.title = ws.title + unicode(1 + i)

        id = 0
        font = Font(name=u'宋体', size=9)
        alignment = Alignment(horizontal='center', vertical='center')
        for r, s in zip(rs, ss):
            # 写装箱清单
            if (0 == id % 30):
                # 写表头
                sheetIdx = id / 30
                ws = wb.worksheets[sheetIdx]
                ws['A1'] = u'中国人民银行' + wareHouse.type + productType.type + u'装箱清单'
                ws['A2'] = u'箱号:' + str(boxNumber)
                ws['D2'] = ds[2] + u'年' + ds[0] + u'月' + ds[1] + u'日'

                rowStartIdx = 4

            # 明细品名
            ws.cell(row=rowStartIdx, column=2).value = r.subClassName.type
            ws.cell(row=rowStartIdx, column=2).font = font
            ws.cell(row=rowStartIdx, column=2).alignment = alignment
            # 编号
            ws.cell(row=rowStartIdx, column=3).value = r.serialNumber
            ws.cell(row=rowStartIdx, column=3).font = font
            ws.cell(row=rowStartIdx, column=3).alignment = alignment
            # 毛重
            ws.cell(row=rowStartIdx, column=4).value = r.grossWeight
            ws.cell(row=rowStartIdx, column=4).font = font
            ws.cell(row=rowStartIdx, column=4).alignment = alignment
            # 成色(原标注成色)
            ws.cell(row=rowStartIdx, column=5).value = r.originalQuantity
            ws.cell(row=rowStartIdx, column=5).font = font
            ws.cell(row=rowStartIdx, column=5).alignment = alignment
            # 枚数
            # ws.cell(row = rowStartIdx, column = 6).value = r.grossWeight*r.detectedQuantity
            ws.cell(row=rowStartIdx, column=6).font = font
            ws.cell(row=rowStartIdx, column=6).alignment = alignment
            # 品相
            ws.cell(row=rowStartIdx, column=7).value = r.quality
            ws.cell(row=rowStartIdx, column=7).font = font
            ws.cell(row=rowStartIdx, column=7).alignment = alignment
            # 评价等级
            ws.cell(row=rowStartIdx, column=8).value = r.level
            ws.cell(row=rowStartIdx, column=8).font = font
            ws.cell(row=rowStartIdx, column=8).alignment = alignment

            # 生成单个实物信息档案
            # outputYinYuan(r, s, productType.type, className.type, subClassName.type, wareHouse.type, date, reportWordDir)

            id = id + 1
            rowStartIdx = rowStartIdx + 1

    elif (0 == cmp(productType.type, u'金银工艺品类')):
        rs = gsGongYiPin.objects.filter(thing__in=thing_set)
        ss = gsStatus.objects.filter(thing__in=thing_set)
        wb = load_workbook(os.path.join(templateRootDir, u'非银元装箱清单.xlsx'))
        ws = wb.worksheets[0]
        sheetCnt = int(ceil(rs.count() / 30))
        for i in range(sheetCnt):
            newSheet = wb.copy_worksheet(ws)
            newSheet.title = ws.title + unicode(1 + i)

        id = 0
        font = Font(name=u'宋体', size=9)
        alignment = Alignment(horizontal='center', vertical='center')
        for r, s in zip(rs, ss):
            # 写装箱清单
            if (0 == id % 30):
                if (0 != id):
                    # 设置当前页打印参数, 并写表尾合计
                    ws.sheet_view.view = 'pageBreakPreview'
                    # 单位: 英寸 inches. 1英寸==2.53CM
                    ws.page_margins.left = 0.43 / 2.53
                    ws.page_margins.right = 0 / 2.53
                    ws.page_margins.top = 0.5 / 2.53
                    ws.page_margins.bottom = 0.3 / 2.53
                    ws.page_margins.header = 0 / 2.53
                    ws.page_margins.footer = 0 / 2.53

                    ws.insert_rows(rowStartIdx - 1, 1, above=False, copy_style=True, fill_formulae=False)
                    ws.merge_cells('A{0}:B{0}'.format(rowStartIdx, rowStartIdx))

                    ws['A{0}'.format(rowStartIdx)] = u'小计'
                    # 写毛重小计
                    ws['D{0}'.format(rowStartIdx)] = u'=SUM(D4:D{0})'.format(rowStartIdx - 1)
                    # 写纯重小计
                    ws['F{0}'.format(rowStartIdx)] = u'=SUM(F4:F{0})'.format(rowStartIdx - 1)

                    # 加边框样式
                    row = ws['A{0}:H{1}'.format(rowStartIdx, rowStartIdx)]
                    for cs in row:
                        for cell in cs:
                            cell.border = border

                    ws.row_dimensions[rowStartIdx + 1].ht = 32.25

                # 写表头
                sheetIdx = id / 30
                ws = wb.worksheets[sheetIdx]
                ws['A1'] = u'中国人民银行' + wareHouse.type + productType.type + u'装箱清单'
                ws['A2'] = u'箱号:' + str(boxNumber)
                ws['D2'] = ds[2] + u'年' + ds[0] + u'月' + ds[1] + u'日'

                rowStartIdx = 4

            # 名称
            ws.cell(row=rowStartIdx, column=2).value = r.detailedName
            ws.cell(row=rowStartIdx, column=2).font = font
            ws.cell(row=rowStartIdx, column=2).alignment = alignment
            # 编号
            ws.cell(row=rowStartIdx, column=3).value = r.serialNumber
            ws.cell(row=rowStartIdx, column=3).font = font
            ws.cell(row=rowStartIdx, column=3).alignment = alignment
            # 毛重
            ws.cell(row=rowStartIdx, column=4).value = r.grossWeight
            ws.cell(row=rowStartIdx, column=4).font = font
            ws.cell(row=rowStartIdx, column=4).alignment = alignment
            # 成色(原标注成色)
            ws.cell(row=rowStartIdx, column=5).value = r.originalQuantity
            ws.cell(row=rowStartIdx, column=5).font = font
            ws.cell(row=rowStartIdx, column=5).alignment = alignment
            # 纯重
            if (r.grossWeight is not None and r.detectedQuantity is not None):
                ws.cell(row=rowStartIdx, column=6).value = float(
                    '%0.2f' % (r.grossWeight * r.detectedQuantity / 100))
            ws.cell(row=rowStartIdx, column=6).font = font
            ws.cell(row=rowStartIdx, column=6).alignment = alignment
            # 品相
            ws.cell(row=rowStartIdx, column=7).value = r.quality
            ws.cell(row=rowStartIdx, column=7).font = font
            ws.cell(row=rowStartIdx, column=7).alignment = alignment
            # 评价等级
            ws.cell(row=rowStartIdx, column=8).value = r.level
            ws.cell(row=rowStartIdx, column=8).font = font
            ws.cell(row=rowStartIdx, column=8).alignment = alignment

            # 生成单个实物信息档案
            # outputGongYiPin(r, s, productType.type, className.type, subClassName.type, wareHouse.type, date, reportWordDir)

            id = id + 1
            rowStartIdx = rowStartIdx + 1

        # 设置最后一页打印参数, 并写表尾合计
        ws.sheet_view.view = 'pageBreakPreview'
        # 单位: 英寸 inches. 1英寸==2.53CM
        ws.page_margins.left = 0.43 / 2.53
        ws.page_margins.right = 0 / 2.53
        ws.page_margins.top = 0.5 / 2.53
        ws.page_margins.bottom = 0.3 / 2.53
        ws.page_margins.header = 0 / 2.53
        ws.page_margins.footer = 0 / 2.53

        ws.insert_rows(33, 2, above=False, copy_style=True, fill_formulae=False)
        ws.merge_cells('A{0}:B{0}'.format(34, 34))
        # cs = ws['A{0}'.format(rowStartIdx)]
        # cs.alignment = a
        ws['A{0}'.format(34)] = u'小计'
        # 写毛重小计
        ws['D{0}'.format(34)] = u'=SUM(D4:D{0})'.format(rowStartIdx - 1)
        # 写纯重小计
        ws['F{0}'.format(34)] = u'=SUM(F4:F{0})'.format(rowStartIdx - 1)

        # 加边框样式
        row = ws['A{0}:H{1}'.format(34, 34)]
        for cs in row:
            for cell in cs:
                cell.border = border

        ws.merge_cells('A{0}:B{0}'.format(35, 35))
        cs = ws['A{0}'.format(rowStartIdx)]
        # cs.alignment = a
        ws['A{0}'.format(35)] = u'合计'

        # 构造合计EXCEL计算公式
        grossWeightTotalFormula = u'=SUM('
        pureWeightTotalFormula = u'=SUM('
        for i in range(sheetCnt + 1):
            ws = wb.worksheets[i]
            if (i != sheetCnt):
                grossWeightTotalFormula = grossWeightTotalFormula + u'{0}!D34'.format(ws.title)
                pureWeightTotalFormula = pureWeightTotalFormula + u'{0}!F34'.format(ws.title)
            else:
                grossWeightTotalFormula = grossWeightTotalFormula + u'D34'.format(ws.title)
                pureWeightTotalFormula = pureWeightTotalFormula + u'F34'.format(ws.title)

            if (i < sheetCnt):
                grossWeightTotalFormula = grossWeightTotalFormula + ','
                pureWeightTotalFormula = pureWeightTotalFormula + ','

        grossWeightTotalFormula = grossWeightTotalFormula + ')'
        pureWeightTotalFormula = pureWeightTotalFormula + ')'

        # 写毛重合计
        ws['D{0}'.format(35)] = u'{0}'.format(grossWeightTotalFormula)
        # 写纯重合计
        ws['F{0}'.format(35)] = u'{0}'.format(pureWeightTotalFormula)

        # 加边框样式
        row = ws['A{0}:H{1}'.format(35, 35)]
        for cs in row:
            for cell in cs:
                cell.border = border

        ws.row_dimensions[36].ht = 32.25

    wb.save(boxInfoFilePath)
    return boxInfoFileName


def createBoxInfoDetailedVersion(boxNumber,subBoxNumber, date):
    box = gsBox.objects.get(boxNumber=boxNumber)
    if subBoxNumber == '':
        thing_set = gsThing.objects.filter(box=box)
    else:
        subBox = gsSubBox.objects.get(box=box, subBoxNumber=int(subBoxNumber))
        thing_set = gsThing.objects.filter(box=box, subBox=subBox)

    global boxDir
    boxDir = os.path.join(boxRootDir, str(boxNumber))
    if not os.path.exists(boxDir):
        os.mkdir(boxDir)  # 转移至创建作业时, 生成相应的目录

    # 实线边框样式
    border = Border(left=Side(border_style='thin', color='FF000000'),
                    right=Side(border_style='thin', color='FF000000'),
                    top=Side(border_style='thin', color='FF000000'),
                    bottom=Side(border_style='thin', color='FF000000'),
                    outline=Side(border_style='thin', color='FF000000'),
                    vertical=Side(border_style='thin', color='FF000000'),
                    horizontal=Side(border_style='thin', color='FF000000')
                    )

    ds = date.split('/')

    t = thing_set.first()
    productTypeCode = t.box.productType
    productType = gsProperty.objects.get(project='实物类型', code=productTypeCode)
    wareHouseCode = t.box.wareHouse
    wareHouse = gsProperty.objects.get(project='发行库', code=wareHouseCode)
    classNameCode = box.className
    className = gsProperty.objects.get(project='品名', code=classNameCode, parentProject=productType.project,
                                       parentType=productType.type)
    subClassNameCode = box.subClassName
    subClassName = gsProperty.objects.get(project='明细品名', code=subClassNameCode, parentProject=className.project,
                                          parentType=className.type, grandpaProject=productType.project,
                                          grandpaType=productType.type)
    if subBoxNumber == '':
        boxInfoFileName = u'{0}_{1}号箱_{2}_list(详细版).xlsx'.format(ds[2], boxNumber, wareHouse.type)
    else:
        boxInfoFileName = u'{0}_{1}-{2}号箱_{3}_list(详细版).xlsx'.format(ds[2], boxNumber, subBoxNumber, wareHouse.type)
    boxInfoFilePath = os.path.join(boxDir, boxInfoFileName)

    if (0 == cmp(productType.type, u'金银锭类')):
        rs = gsDing.objects.filter(thing__in=thing_set)
        ss = gsStatus.objects.filter(thing__in=thing_set)
        wb = load_workbook(os.path.join(templateRootDir, u'金银锭类装箱清单(详细版).xlsx'))
        ws = wb.worksheets[0]
        sheetCnt = int(ceil(rs.count() / 30))
        for i in range(sheetCnt):
            newSheet = wb.copy_worksheet(ws)
            newSheet.title = ws.title + unicode(1 + i)

        id = 0
        font = Font(name=u'宋体', size=9)
        alignment = Alignment(horizontal='center', vertical='center')
        for r, s in zip(rs, ss):
            # 写装箱清单
            if (0 == id % 30):
                if (0 != id):
                    # 设置当前页打印参数, 并写表尾合计
                    # 设置页横向, 缩放比例81%
                    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
                    ws.page_setup.scale = 81
                    ws.sheet_view.view = 'pageBreakPreview'
                    # 单位: 英寸 inches. 1英寸==2.53CM
                    ws.page_margins.left = 2.31 / 2.53
                    ws.page_margins.right = 2.31 / 2.53
                    ws.page_margins.top = 0 / 2.53
                    ws.page_margins.bottom = 0 / 2.53
                    ws.page_margins.header = 0 / 2.53
                    ws.page_margins.footer = 0 / 2.53

                    ws.insert_rows(rowStartIdx - 1, 1, above=False, copy_style=True, fill_formulae=False)
                    ws.merge_cells('A{0}:B{0}'.format(rowStartIdx, rowStartIdx))

                    ws['A{0}'.format(rowStartIdx)] = u'小计'
                    # 写毛重小计
                    ws['M{0}'.format(rowStartIdx)] = u'=SUM(M6:M{0})'.format(rowStartIdx - 1)
                    # 写纯重小计
                    ws['Q{0}'.format(rowStartIdx)] = u'=SUM(Q6:Q{0})'.format(rowStartIdx - 1)

                    # 给当前页加边框样式, 即整个表格
                    table = ws['A{0}:V{1}'.format(4, rowStartIdx)]
                    for cs in table:
                        for cell in cs:
                            cell.border = border

                    ws.row_dimensions[rowStartIdx + 1].ht = 32.25

                # 写新一页表头
                sheetIdx = id / 30
                ws = wb.worksheets[sheetIdx]
                ws['A2'] = u'中国人民银行' + wareHouse.type + productType.type + u'装箱清单'
                ws['A3'] = u'箱号:' + str(boxNumber)
                ws['S3'] = ds[2] + u'年' + ds[0] + u'月' + ds[1] + u'日'

                rowStartIdx = 6;

            # 品名
            ws.cell(row=rowStartIdx, column=2).value = className.type
            ws.cell(row=rowStartIdx, column=2).font = font
            ws.cell(row=rowStartIdx, column=2).alignment = alignment

            # 明细品名
            ws.cell(row=rowStartIdx, column=3).value = subClassName.type
            ws.cell(row=rowStartIdx, column=3).font = font
            ws.cell(row=rowStartIdx, column=3).alignment = alignment

            # 编号
            ws.cell(row=rowStartIdx, column=4).value = r.serialNumber
            ws.cell(row=rowStartIdx, column=4).font = font
            ws.cell(row=rowStartIdx, column=4).alignment = alignment

            # 名称
            ws.cell(row=rowStartIdx, column=5).value = r.detailedName
            ws.cell(row=rowStartIdx, column=5).font = font
            ws.cell(row=rowStartIdx, column=5).alignment = alignment

            # 型制类型
            ws.cell(row=rowStartIdx, column=6).value = r.typeName
            ws.cell(row=rowStartIdx, column=6).font = font
            ws.cell(row=rowStartIdx, column=6).alignment = alignment

            # 时代
            ws.cell(row=rowStartIdx, column=7).value = r.typeName
            ws.cell(row=rowStartIdx, column=7).font = font
            ws.cell(row=rowStartIdx, column=7).alignment = alignment

            # 制造地
            ws.cell(row=rowStartIdx, column=8).value = r.producerPlace
            ws.cell(row=rowStartIdx, column=8).font = font
            ws.cell(row=rowStartIdx, column=8).alignment = alignment

            # 制作人
            ws.cell(row=rowStartIdx, column=9).value = r.producerPlace
            ws.cell(row=rowStartIdx, column=9).font = font
            ws.cell(row=rowStartIdx, column=9).alignment = alignment

            # 性质

            # 品相
            ws.cell(row=rowStartIdx, column=11).value = r.quality
            ws.cell(row=rowStartIdx, column=11).font = font
            ws.cell(row=rowStartIdx, column=11).alignment = alignment

            # 铭文
            ws.cell(row=rowStartIdx, column=12).value = r.carveName
            ws.cell(row=rowStartIdx, column=12).font = font
            ws.cell(row=rowStartIdx, column=12).alignment = alignment

            # 毛重
            ws.cell(row=rowStartIdx, column=13).value = r.grossWeight
            ws.cell(row=rowStartIdx, column=13).font = font
            ws.cell(row=rowStartIdx, column=13).alignment = alignment

            # 成色(原标注成色)
            ws.cell(row=rowStartIdx, column=14).value = r.originalQuantity
            ws.cell(row=rowStartIdx, column=14).font = font
            ws.cell(row=rowStartIdx, column=14).alignment = alignment

            # 成色(仪器检测成色)
            ws.cell(row=rowStartIdx, column=15).value = r.detectedQuantity
            ws.cell(row=rowStartIdx, column=15).font = font
            ws.cell(row=rowStartIdx, column=15).alignment = alignment

            # 成色(目测)

            # 纯重
            if (r.grossWeight is not None and r.detectedQuantity is not None):
                ws.cell(row=rowStartIdx, column=17).value = float(
                    '%0.2f' % (r.grossWeight * r.detectedQuantity / 100))
            ws.cell(row=rowStartIdx, column=17).font = font
            ws.cell(row=rowStartIdx, column=17).alignment = alignment

            # 长度
            ws.cell(row=rowStartIdx, column=18).value = r.length
            ws.cell(row=rowStartIdx, column=18).font = font
            ws.cell(row=rowStartIdx, column=18).alignment = alignment

            # 宽度
            ws.cell(row=rowStartIdx, column=19).value = r.width
            ws.cell(row=rowStartIdx, column=19).font = font
            ws.cell(row=rowStartIdx, column=19).alignment = alignment

            # 高度
            ws.cell(row=rowStartIdx, column=20).value = r.height
            ws.cell(row=rowStartIdx, column=20).font = font
            ws.cell(row=rowStartIdx, column=20).alignment = alignment

            # 直径

            # 评价等级
            ws.cell(row=rowStartIdx, column=22).value = r.level
            ws.cell(row=rowStartIdx, column=22).font = font
            ws.cell(row=rowStartIdx, column=22).alignment = alignment

            # 生成单个实物信息档案
            # outputDing(r, s, productType.type, className.type, subClassName.type, wareHouse.type, date, reportWordDir)

            id = id + 1
            rowStartIdx = rowStartIdx + 1

        # 设置最后一页打印参数, 并写表尾合计
        # 设置页横向, 缩放比例81%
        ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
        ws.page_setup.scale = 81
        ws.sheet_view.view = 'pageBreakPreview'
        # 单位: 英寸 inches. 1英寸==2.53CM
        ws.page_margins.left = 2.31 / 2.53
        ws.page_margins.right = 2.31 / 2.53
        ws.page_margins.top = 0 / 2.53
        ws.page_margins.bottom = 0 / 2.53
        ws.page_margins.header = 0 / 2.53
        ws.page_margins.footer = 0 / 2.53

        ws.insert_rows(35, 2, above=False, copy_style=True, fill_formulae=False)
        ws.merge_cells('A{0}:B{0}'.format(36, 36))
        ws['A{0}'.format(36)] = u'小计'
        # 写毛重小计
        ws['M{0}'.format(36)] = u'=SUM(M6:M{0})'.format(rowStartIdx - 1)
        # 写纯重小计
        ws['Q{0}'.format(36)] = u'=SUM(Q6:Q{0})'.format(rowStartIdx - 1)

        ws.merge_cells('A{0}:B{0}'.format(37, 37))
        ws['A{0}'.format(37)] = u'合计'

        # 构造合计EXCEL计算公式
        grossWeightTotalFormula = u'=SUM('
        pureWeightTotalFormula = u'=SUM('
        for i in range(sheetCnt + 1):
            ws = wb.worksheets[i]
            if (i != sheetCnt):
                grossWeightTotalFormula = grossWeightTotalFormula + u'\'{0}\'!M36'.format(ws.title)
                pureWeightTotalFormula = pureWeightTotalFormula + u'\'{0}\'!Q36'.format(ws.title)
            else:
                grossWeightTotalFormula = grossWeightTotalFormula + u'M36'.format(ws.title)
                pureWeightTotalFormula = pureWeightTotalFormula + u'Q36'.format(ws.title)

            if (i < sheetCnt):
                grossWeightTotalFormula = grossWeightTotalFormula + ','
                pureWeightTotalFormula = pureWeightTotalFormula + ','

        grossWeightTotalFormula = grossWeightTotalFormula + ')'
        pureWeightTotalFormula = pureWeightTotalFormula + ')'

        # 写毛重合计
        ws['M{0}'.format(37)] = u'{0}'.format(grossWeightTotalFormula)
        # 写纯重合计
        ws['Q{0}'.format(37)] = u'{0}'.format(pureWeightTotalFormula)

        # 给最后一页加边框样式, 即整个表格
        table = ws['A{0}:V{1}'.format(4, 37)]
        for cs in table:
            for cell in cs:
                cell.border = border

        ws.row_dimensions[38].ht = 32.25

    elif (0 == cmp(productType.type, u'金银币章类')):
        rs = gsBiZhang.objects.filter(thing__in=thing_set)
        ss = gsStatus.objects.filter(thing__in=thing_set)
        wb = load_workbook(os.path.join(templateRootDir, u'金银币章类装箱清单(详细版).xlsx'))
        ws = wb.worksheets[0]
        sheetCnt = int(ceil(rs.count() / 30))
        for i in range(sheetCnt):
            newSheet = wb.copy_worksheet(ws)
            newSheet.title = ws.title + unicode(1 + i)

        id = 0
        font = Font(name=u'宋体', size=9)
        alignment = Alignment(horizontal='center', vertical='center')
        for r, s in zip(rs, ss):
            # 写装箱清单
            if (0 == id % 30):
                if (0 != id):
                    # 设置当前页打印参数, 并写表尾合计
                    ws.sheet_view.view = 'pageBreakPreview'
                    # 单位: 英寸 inches. 1英寸==2.53CM
                    ws.page_margins.left = 0.43 / 2.53
                    ws.page_margins.right = 0 / 2.53
                    ws.page_margins.top = 0.5 / 2.53
                    ws.page_margins.bottom = 0.3 / 2.53
                    ws.page_margins.header = 0 / 2.53
                    ws.page_margins.footer = 0 / 2.53

                    ws.insert_rows(rowStartIdx - 1, 1, above=False, copy_style=True, fill_formulae=False)
                    ws.merge_cells('A{0}:B{0}'.format(rowStartIdx, rowStartIdx))

                    ws['A{0}'.format(rowStartIdx)] = u'小计'
                    # 写毛重小计
                    ws['D{0}'.format(rowStartIdx)] = u'=SUM(D4:D{0})'.format(rowStartIdx - 1)
                    # 写纯重小计
                    ws['F{0}'.format(rowStartIdx)] = u'=SUM(F4:F{0})'.format(rowStartIdx - 1)

                    # 加边框样式
                    row = ws['A{0}:H{1}'.format(rowStartIdx, rowStartIdx)]
                    for cs in row:
                        for cell in cs:
                            cell.border = border

                    ws.row_dimensions[rowStartIdx + 1].ht = 32.25

                # 写表头
                sheetIdx = id / 30
                ws = wb.worksheets[sheetIdx]
                ws['A1'] = u'中国人民银行' + wareHouse.type + productType.type + u'装箱清单'
                ws['A2'] = u'箱号:' + str(boxNumber)
                ws['D2'] = ds[2] + u'年' + ds[0] + u'月' + ds[1] + u'日'

                rowStartIdx = 4;

            # 名称
            ws.cell(row=rowStartIdx, column=2).value = r.detailedName
            ws.cell(row=rowStartIdx, column=2).font = font
            ws.cell(row=rowStartIdx, column=2).alignment = alignment
            # 编号
            ws.cell(row=rowStartIdx, column=3).value = r.serialNumber
            ws.cell(row=rowStartIdx, column=3).font = font
            ws.cell(row=rowStartIdx, column=3).alignment = alignment
            # 毛重
            ws.cell(row=rowStartIdx, column=4).value = r.grossWeight
            ws.cell(row=rowStartIdx, column=4).font = font
            ws.cell(row=rowStartIdx, column=4).alignment = alignment
            # 成色(原标注成色)
            ws.cell(row=rowStartIdx, column=5).value = r.originalQuantity
            ws.cell(row=rowStartIdx, column=5).font = font
            ws.cell(row=rowStartIdx, column=5).alignment = alignment
            # 纯重
            if (r.grossWeight is not None and r.detectedQuantity is not None):
                ws.cell(row=rowStartIdx, column=6).value = float(
                    '%0.2f' % (r.grossWeight * r.detectedQuantity / 100))
            ws.cell(row=rowStartIdx, column=6).font = font
            ws.cell(row=rowStartIdx, column=6).alignment = alignment
            # 品相
            ws.cell(row=rowStartIdx, column=7).value = r.quality
            ws.cell(row=rowStartIdx, column=7).font = font
            ws.cell(row=rowStartIdx, column=7).alignment = alignment
            # 评价等级
            ws.cell(row=rowStartIdx, column=8).value = r.level
            ws.cell(row=rowStartIdx, column=8).font = font
            ws.cell(row=rowStartIdx, column=8).alignment = alignment

            # 生成单个实物信息档案
            # outputBiZhang(r, s, productType.type, className.type, subClassName.type, wareHouse.type, date, reportWordDir)

            id = id + 1
            rowStartIdx = rowStartIdx + 1

        # 设置最后一页打印参数, 并写表尾合计
        ws.sheet_view.view = 'pageBreakPreview'
        # 单位: 英寸 inches. 1英寸==2.53CM
        ws.page_margins.left = 0.43 / 2.53
        ws.page_margins.right = 0 / 2.53
        ws.page_margins.top = 0.5 / 2.53
        ws.page_margins.bottom = 0.3 / 2.53
        ws.page_margins.header = 0 / 2.53
        ws.page_margins.footer = 0 / 2.53

        ws.insert_rows(33, 2, above=False, copy_style=True, fill_formulae=False)
        ws.merge_cells('A{0}:B{0}'.format(34, 34))
        # cs = ws['A{0}'.format(rowStartIdx)]
        # cs.alignment = a
        ws['A{0}'.format(34)] = u'小计'
        # 写毛重小计
        ws['D{0}'.format(34)] = u'=SUM(D4:D{0})'.format(rowStartIdx - 1)
        # 写纯重小计
        ws['F{0}'.format(34)] = u'=SUM(F4:F{0})'.format(rowStartIdx - 1)

        # 加边框样式
        row = ws['A{0}:H{1}'.format(34, 34)]
        for cs in row:
            for cell in cs:
                cell.border = border

        ws.merge_cells('A{0}:B{0}'.format(35, 35))
        cs = ws['A{0}'.format(rowStartIdx)]
        # cs.alignment = a
        ws['A{0}'.format(35)] = u'合计'

        # 构造合计EXCEL计算公式
        grossWeightTotalFormula = u'=SUM('
        pureWeightTotalFormula = u'=SUM('
        for i in range(sheetCnt + 1):
            ws = wb.worksheets[i]
            if (i != sheetCnt):
                grossWeightTotalFormula = grossWeightTotalFormula + u'{0}!D34'.format(ws.title)
                pureWeightTotalFormula = pureWeightTotalFormula + u'{0}!F34'.format(ws.title)
            else:
                grossWeightTotalFormula = grossWeightTotalFormula + u'D34'.format(ws.title)
                pureWeightTotalFormula = pureWeightTotalFormula + u'F34'.format(ws.title)

            if (i < sheetCnt):
                grossWeightTotalFormula = grossWeightTotalFormula + ','
                pureWeightTotalFormula = pureWeightTotalFormula + ','

        grossWeightTotalFormula = grossWeightTotalFormula + ')'
        pureWeightTotalFormula = pureWeightTotalFormula + ')'

        # 写毛重合计
        ws['D{0}'.format(35)] = u'{0}'.format(grossWeightTotalFormula)
        # 写纯重合计
        ws['F{0}'.format(35)] = u'{0}'.format(pureWeightTotalFormula)

        # 加边框样式
        row = ws['A{0}:H{1}'.format(35, 35)]
        for cs in row:
            for cell in cs:
                cell.border = border

        ws.row_dimensions[36].ht = 32.25

    elif (0 == cmp(productType.type, u'银元类')):
        rs = gsYinYuan.objects.filter(thing__in=thing_set)
        ss = gsStatus.objects.filter(thing__in=thing_set)
        wb = load_workbook(os.path.join(templateRootDir, u'银元类箱清单(详细版).xlsx'))
        ws = wb.worksheets[0]
        sheetCnt = int(ceil(rs.count() / 30))
        for i in range(sheetCnt):
            newSheet = wb.copy_worksheet(ws)
            newSheet.title = ws.title + unicode(1 + i)

        id = 0
        font = Font(name=u'宋体', size=9)
        alignment = Alignment(horizontal='center', vertical='center')
        for r, s in zip(rs, ss):
            # 写装箱清单
            if (0 == id % 30):
                # 写表头
                sheetIdx = id / 30
                ws = wb.worksheets[sheetIdx]
                ws['A1'] = u'中国人民银行' + wareHouse.type + productType.type + u'装箱清单'
                ws['A2'] = u'箱号:' + str(boxNumber)
                ws['D2'] = ds[2] + u'年' + ds[0] + u'月' + ds[1] + u'日'

                rowStartIdx = 4;

            # 明细品名
            ws.cell(row=rowStartIdx, column=2).value = subClassName.type
            ws.cell(row=rowStartIdx, column=2).font = font
            ws.cell(row=rowStartIdx, column=2).alignment = alignment
            # 编号
            ws.cell(row=rowStartIdx, column=3).value = r.serialNumber
            ws.cell(row=rowStartIdx, column=3).font = font
            ws.cell(row=rowStartIdx, column=3).alignment = alignment
            # 毛重
            ws.cell(row=rowStartIdx, column=4).value = r.grossWeight
            ws.cell(row=rowStartIdx, column=4).font = font
            ws.cell(row=rowStartIdx, column=4).alignment = alignment
            # 成色(原标注成色)
            ws.cell(row=rowStartIdx, column=5).value = r.originalQuantity
            ws.cell(row=rowStartIdx, column=5).font = font
            ws.cell(row=rowStartIdx, column=5).alignment = alignment
            # 枚数
            # ws.cell(row = rowStartIdx, column = 6).value = r.grossWeight*r.detectedQuantity
            ws.cell(row=rowStartIdx, column=6).font = font
            ws.cell(row=rowStartIdx, column=6).alignment = alignment
            # 品相
            ws.cell(row=rowStartIdx, column=7).value = r.quality
            ws.cell(row=rowStartIdx, column=7).font = font
            ws.cell(row=rowStartIdx, column=7).alignment = alignment
            # 评价等级
            ws.cell(row=rowStartIdx, column=8).value = r.level
            ws.cell(row=rowStartIdx, column=8).font = font
            ws.cell(row=rowStartIdx, column=8).alignment = alignment

            # 生成单个实物信息档案
            # outputYinYuan(r, s, productType.type, className.type, subClassName.type, wareHouse.type, date, reportWordDir)

            id = id + 1
            rowStartIdx = rowStartIdx + 1

    elif (0 == cmp(productType.type, u'金银工艺品类')):
        rs = gsGongYiPin.objects.filter(thing__in=thing_set)
        ss = gsStatus.objects.filter(thing__in=thing_set)
        wb = load_workbook(os.path.join(templateRootDir, u'金银工艺品类装箱清单(详细版).xlsx'))
        ws = wb.worksheets[0]
        sheetCnt = int(ceil(rs.count() / 30))
        for i in range(sheetCnt):
            newSheet = wb.copy_worksheet(ws)
            newSheet.title = ws.title + unicode(1 + i)

        id = 0
        font = Font(name=u'宋体', size=9)
        alignment = Alignment(horizontal='center', vertical='center')
        for r, s in zip(rs, ss):
            # 写装箱清单
            if (0 == id % 30):
                if (0 != id):
                    # 设置当前页打印参数, 并写表尾合计
                    ws.sheet_view.view = 'pageBreakPreview'
                    # 单位: 英寸 inches. 1英寸==2.53CM
                    ws.page_margins.left = 0.43 / 2.53
                    ws.page_margins.right = 0 / 2.53
                    ws.page_margins.top = 0.5 / 2.53
                    ws.page_margins.bottom = 0.3 / 2.53
                    ws.page_margins.header = 0 / 2.53
                    ws.page_margins.footer = 0 / 2.53

                    ws.insert_rows(rowStartIdx - 1, 1, above=False, copy_style=True, fill_formulae=False)
                    ws.merge_cells('A{0}:B{0}'.format(rowStartIdx, rowStartIdx))

                    ws['A{0}'.format(rowStartIdx)] = u'小计'
                    # 写毛重小计
                    ws['D{0}'.format(rowStartIdx)] = u'=SUM(D4:D{0})'.format(rowStartIdx - 1)
                    # 写纯重小计
                    ws['F{0}'.format(rowStartIdx)] = u'=SUM(F4:F{0})'.format(rowStartIdx - 1)

                    # 加边框样式
                    row = ws['A{0}:H{1}'.format(rowStartIdx, rowStartIdx)]
                    for cs in row:
                        for cell in cs:
                            cell.border = border

                    ws.row_dimensions[rowStartIdx + 1].ht = 32.25

                # 写表头
                sheetIdx = id / 30
                ws = wb.worksheets[sheetIdx]
                ws['A1'] = u'中国人民银行' + wareHouse.type + productType.type + u'装箱清单'
                ws['A2'] = u'箱号:' + str(boxNumber)
                ws['D2'] = ds[2] + u'年' + ds[0] + u'月' + ds[1] + u'日'

                rowStartIdx = 4;

            # 名称
            ws.cell(row=rowStartIdx, column=2).value = r.detailedName
            ws.cell(row=rowStartIdx, column=2).font = font
            ws.cell(row=rowStartIdx, column=2).alignment = alignment
            # 编号
            ws.cell(row=rowStartIdx, column=3).value = r.serialNumber
            ws.cell(row=rowStartIdx, column=3).font = font
            ws.cell(row=rowStartIdx, column=3).alignment = alignment
            # 毛重
            ws.cell(row=rowStartIdx, column=4).value = r.grossWeight
            ws.cell(row=rowStartIdx, column=4).font = font
            ws.cell(row=rowStartIdx, column=4).alignment = alignment
            # 成色(原标注成色)
            ws.cell(row=rowStartIdx, column=5).value = r.originalQuantity
            ws.cell(row=rowStartIdx, column=5).font = font
            ws.cell(row=rowStartIdx, column=5).alignment = alignment
            # 纯重
            if (r.grossWeight is not None and r.detectedQuantity is not None):
                ws.cell(row=rowStartIdx, column=6).value = float(
                    '%0.2f' % (r.grossWeight * r.detectedQuantity / 100))
            ws.cell(row=rowStartIdx, column=6).font = font
            ws.cell(row=rowStartIdx, column=6).alignment = alignment
            # 品相
            ws.cell(row=rowStartIdx, column=7).value = r.quality
            ws.cell(row=rowStartIdx, column=7).font = font
            ws.cell(row=rowStartIdx, column=7).alignment = alignment
            # 评价等级
            ws.cell(row=rowStartIdx, column=8).value = r.level
            ws.cell(row=rowStartIdx, column=8).font = font
            ws.cell(row=rowStartIdx, column=8).alignment = alignment

            # 生成单个实物信息档案
            # outputGongYiPin(r, s, productType.type, className.type, subClassName.type, wareHouse.type, date, reportWordDir)

            id = id + 1
            rowStartIdx = rowStartIdx + 1

        # 设置最后一页打印参数, 并写表尾合计
        ws.sheet_view.view = 'pageBreakPreview'
        # 单位: 英寸 inches. 1英寸==2.53CM
        ws.page_margins.left = 0.43 / 2.53
        ws.page_margins.right = 0 / 2.53
        ws.page_margins.top = 0.5 / 2.53
        ws.page_margins.bottom = 0.3 / 2.53
        ws.page_margins.header = 0 / 2.53
        ws.page_margins.footer = 0 / 2.53

        ws.insert_rows(33, 2, above=False, copy_style=True, fill_formulae=False)
        ws.merge_cells('A{0}:B{0}'.format(34, 34))
        # cs = ws['A{0}'.format(rowStartIdx)]
        # cs.alignment = a
        ws['A{0}'.format(34)] = u'小计'
        # 写毛重小计
        ws['D{0}'.format(34)] = u'=SUM(D4:D{0})'.format(rowStartIdx - 1)
        # 写纯重小计
        ws['F{0}'.format(34)] = u'=SUM(F4:F{0})'.format(rowStartIdx - 1)

        # 加边框样式
        row = ws['A{0}:H{1}'.format(34, 34)]
        for cs in row:
            for cell in cs:
                cell.border = border

        ws.merge_cells('A{0}:B{0}'.format(35, 35))
        cs = ws['A{0}'.format(rowStartIdx)]
        # cs.alignment = a
        ws['A{0}'.format(35)] = u'合计'

        # 构造合计EXCEL计算公式
        grossWeightTotalFormula = u'=SUM('
        pureWeightTotalFormula = u'=SUM('
        for i in range(sheetCnt + 1):
            ws = wb.worksheets[i]
            if (i != sheetCnt):
                grossWeightTotalFormula = grossWeightTotalFormula + u'{0}!D34'.format(ws.title)
                pureWeightTotalFormula = pureWeightTotalFormula + u'{0}!F34'.format(ws.title)
            else:
                grossWeightTotalFormula = grossWeightTotalFormula + u'D34'.format(ws.title)
                pureWeightTotalFormula = pureWeightTotalFormula + u'F34'.format(ws.title)

            if (i < sheetCnt):
                grossWeightTotalFormula = grossWeightTotalFormula + ','
                pureWeightTotalFormula = pureWeightTotalFormula + ','

        grossWeightTotalFormula = grossWeightTotalFormula + ')'
        pureWeightTotalFormula = pureWeightTotalFormula + ')'

        # 写毛重合计
        ws['D{0}'.format(35)] = u'{0}'.format(grossWeightTotalFormula)
        # 写纯重合计
        ws['F{0}'.format(35)] = u'{0}'.format(pureWeightTotalFormula)

        # 加边框样式
        row = ws['A{0}:H{1}'.format(35, 35)]
        for cs in row:
            for cell in cs:
                cell.border = border

        ws.row_dimensions[36].ht = 32.25

    wb.save(boxInfoFilePath)
    return boxInfoFileName


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
    ws['E5'] = r.box.boxNumber
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
    ws['E8'] = r.serialNumber
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

    fileName = r.serialNumber + u'.xlsx'
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
    ws['E5'] = r.box.boxNumber
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
    ws['E8'] = r.serialNumber
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

    fileName = r.serialNumber + '.xlsx'
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
    ws['E5'] = r.box.boxNumber
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
    ws['E8'] = r.serialNumber
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

    fileName = r.serialNumber + '.xlsx'
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
    ws['E5'] = r.box.boxNumber
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
    ws['E8'] = r.serialNumber
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

    fileName = r.serialNumber + '.xlsx'
    filePath = os.path.join(reportWordDir, fileName)
    wb.save(filePath)

    return (filePath, fileName)


def DingAbstract(r):
    c_format = u'箱号:{0}  编号:{1}  名称:{2}  时代:{3}  铭文:{4}  原标注成色:{5}%  检测成色:{6}%  长:{7}mm 宽:{8}mm  高:{9}mm  毛重:{10}g  纯重:{11}g'
    c = c_format.format(r.box.boxNumber, r.serialNumber, r.detailedName, r.peroid, r.carveName, r.originalQuantity,
                        r.detectedQuantity, r.length, r.width, r.height, r.grossWeight,
                        float('%0.2f' % (r.grossWeight * r.detectedQuantity / 100)))

    return c


def YinYuanAbstract(r):
    c_format = u'箱号:{0}  编号:{1}  名称:{2}  时代:{3}  币值:{4}  原标注成色:{5}%  检测成色:{6}%  直径:{7}mm 厚度:{8}mm 毛重:{9}g'
    c = c_format.format(r.box.boxNumber, r.serialNumber, r.detailedName, r.peroid, r.value, r.originalQuantity,
                        r.detectedQuantity, r.diameter, r.thick, r.grossWeight)

    return c


def BiZhangAbstract(r):
    c_format = u'箱号:{0}  编号:{1}  名称:{2}  时代:{3}  币值:{4}  原标注成色:{5}%  检测成色:{6}%  长:{7}mm  宽:{8}mm  高:{9}mm  毛重:{10}g  纯重:{11}g'
    c = c_format.format(r.box.boxNumber, r.serialNumber, r.detailedName, r.peroid, r.value, r.originalQuantity,
                        r.detectedQuantity, r.length, r.width, r.height, r.grossWeight,
                        float('%0.2f' % (r.grossWeight * r.detectedQuantity / 100)))

    return c


def GongYiPinAbstract(r):
    c_format = u'箱号:{0}  编号:{1}  名称:{2}  时代:{3}  原标注成色:{4}%  检测成色:{5}%  长:{6}mm  宽:{7}mm  高:{8}mm  毛重:{8}g  纯重:{10}g'
    c = c_format.format(r.box.boxNumber, r.serialNumber, r.detailedName, r.peroid, r.originalQuantity,
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
    #     # c1 = r.serialNumber
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
