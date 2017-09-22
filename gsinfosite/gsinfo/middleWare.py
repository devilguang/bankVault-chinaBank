# encoding=UTF-8

from models import *
from webServiceAPI import *
import os
from gsinfosite import settings
from PIL import Image, ImageDraw, ImageFont

def getserialNumber2(serialNumber):
    thing = gsThing.objects.get(serialNumber=serialNumber)
    box = thing.box
    prop = box.boxType
    grandpaCode = prop.grandpaCode
    parentCode = prop.parentCode
    code = prop.code
    # -----------------------------
    field_list = []
    # 请求类型
    requestType = '4'
    field_list.append(requestType)
    # 发行库编码
    wareHouse = box.wareHouse
    field_list.append(wareHouse)
    if grandpaCode:
        # 类别
        productCode = grandpaCode
        # 品种
        classCode = parentCode
        # 品名
        subClassCode = code
    else:
        productCode = parentCode
        classCode = code
        subClassCode = ''
    field_list.append(productCode)
    field_list.append(classCode)
    field_list.append(subClassCode)
     # 等级
    level = thing.level
    field_list.append(level)
    # 年代
    peroid = thing.peroid
    field_list.append(peroid)
    # 国别
    country = thing.country
    field_list.append(country)
    # 规格
    dingSecification = thing.dingSecification
    field_list.append(dingSecification)
    # 器型（型制）
    shape = thing.shape
    field_list.append(shape)
    # -----------------------------
    str_data = '|'.join(field_list)
    print str_data
    error_code = ['001','002']
    for _ in range(3):
        info = getNumberAPI(str_data)  # 正常: 返回请求号; 错误：参考错误代码表
        if info not in error_code:
            thing.serialNumber2 = info
            thing.save(update_fields=['serialNumber2'])
            break
    else:
        return False
    return True

def postThing(serialNumber):
    thing = gsThing.objects.get(serialNumber=serialNumber)
    box = thing.box
    prop = box.boxType
    grandpaCode = prop.grandpaCode
    parentCode = prop.parentCode
    code =prop.code

    oprateCode = box.oprateType
    # ---------------------------------------
    field_list = []
    # 件序号
    serialNumber = serialNumber
    field_list.append(serialNumber)
    # 件编号（明文件号）
    serialNumber2 = thing.serialNumber2
    field_list.append(serialNumber2)
    # 是否同质同类标示
    isSameClass ='1' if oprateCode == '2' else '0'
    field_list.append(isSameClass)
    if grandpaCode:
        # 类别
        productCode = grandpaCode
        # 品种
        classCode = parentCode
        # 品名
        subClassCode =code
    else:
        productCode = parentCode
        classCode = code
        subClassCode = ''
    field_list.append(productCode)
    field_list.append(classCode)
    field_list.append(subClassCode)
    # 等级
    level = thing.level
    field_list.append(level)
    # 名称
    detailedName = thing.detailedName
    field_list.append(detailedName)
    # 年代
    peroid = thing.peroid
    field_list.append(peroid)
    # 年份
    year = thing.year
    field_list.append(year)
    # 器型（型制）
    shape = thing.shape
    field_list.append(shape)
    # 面值
    faceAmount = thing.faceAmount
    field_list.append(faceAmount)
    # 国别
    country = thing.country
    field_list.append(country)
    # 规格
    dingSecification = thing.dingSecification
    field_list.append(dingSecification)
    # 性质
    zhangType = thing.zhangType
    field_list.append(zhangType)
    # 完残程度（品相）
    appearance = thing.appearance
    field_list.append(appearance)
    # 文字信息（铭文）
    mark = thing.mark
    field_list.append(mark)
    # 毛重
    grossWeight = thing.grossWeight
    field_list.append(str(grossWeight))
    # 原标注成色
    originalQuantity = thing.originalQuantity
    field_list.append(str(originalQuantity))
    # 仪器检测成色
    detectedQuantity = thing.detectedQuantity
    field_list.append(str(detectedQuantity))
    # 纯重
    pureWeight = thing.pureWeight
    field_list.append(str(pureWeight))
    # 件（枚）数
    amount = thing.amount
    field_list.append(str(amount))
    # 长度（mm）
    length = thing.length
    field_list.append(str(length))
    # 宽度（mm）
    width = thing.width
    field_list.append(str(width))
    # 高度(MM)
    height = thing.height
    field_list.append(str(height))
    # 备注
    remark = thing.remark
    field_list.append(str(remark))
    # ---------------------------------------
    str_data = '|'.join(field_list)
    print str_data
    for _ in range(3):
        status_code = postThingDataAPI(str_data)
        if status_code == '000':
            thing.thingPostStatus = status_code
            thing.save(update_fields=['thingPostStatus'])
            break
    else:
        return False
    return True



def postPhoto(serialNumber):
    thing = gsThing.objects.get(serialNumber=serialNumber)
    box = thing.box
    boxNumber = box.boxNumber

    pic_dir = os.path.join(settings.IMGS_DATA_PATH,boxNumber)
    all_fileName = os.listdir(pic_dir)
    for fileName in all_fileName:
        name = fileName.split('.')[0]
        prefixes = name.split('-')[0]
        suffix = name.split('-')[1]
        if serialNumber == prefixes:
            picPath = os.path.join(pic_dir,fileName)
            serialNumber2 = thing.serialNumber2
            newSerial = '-'.join([serialNumber2,suffix])
            newPicPath = os.path.join(newSerial,'.jpg')
            # 添加水印
            image = Image.open(picPath)
            draw = ImageDraw.Draw(image)
            # 指定要使用的字体和大小；/Library/Fonts/是macOS字体目录；Linux的字体目录是/usr/share/fonts/
            font = ImageFont.truetype('arial.ttf', 16)  # 第二个参数表示字符大小
            width, height = font.getsize(newSerial)
            x = int((256 - width) / 2)
            y = 256 - height - 12
            draw.text((x, y), newSerial, fill=(255, 255, 255), font=font)
            image.save(newPicPath)
            os.remove(picPath)  # 删除旧照片


    # status_code = postPicAPI(str_data)
    # thing.thingPostStatus = status_code
    # thing.save(update_fields=['thingPostStatus'])
    pass

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++
def postInfo(serialNumber):
    status1 = getserialNumber2(serialNumber)  # 向二系统请求明文件号
    if status1:
        status2 = postThing(serialNumber)  # 向二系统推送数据
        if status2:
            pass
        else:
            pass


        # 向二系统推送图片
    else:
        return False