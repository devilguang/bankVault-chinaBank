# encoding=UTF-8
from django.http.response import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json, os
from PIL import Image, ImageDraw, ImageFont
import base64
from clientserver import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
photoDir = os.path.join(BASE_DIR,'photo')  # settings.PHOTODIR
uploadDir = os.path.join(BASE_DIR, 'static', 'upload')
rephotoDir = os.path.join(BASE_DIR, 'static', 'rephoto')

rephotoFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rephotoFileName.txt')
pastSerialFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pastSerialNumber.txt')
stopSignalPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stopSignal.txt')


def getSeq(request):
    serialNumber = request.GET.get('serialNumber', '')
    ret = {}
    # 指定要使用的字体和大小；/Library/Fonts/是macOS字体目录；Linux的字体目录是/usr/share/fonts/
    font = ImageFont.truetype('arial.ttf', 16)  # 第二个参数表示字符大小

    if not os.path.exists(uploadDir):
        os.mkdir(uploadDir)
    if not os.path.exists(rephotoDir):
        os.mkdir(rephotoDir)
    # -----------------------------------------------------
    try:
        with open(rephotoFile, 'r') as f:
            rephtoFile = f.read().strip()
    except:
        with open(rephotoFile, 'w') as f:
            rephtoFile = f.read().strip()
    if rephtoFile:
        deleteFilePath = os.path.join(uploadDir, rephtoFile)  # 删除旧图
        if os.path.exists(deleteFilePath):
            os.remove(deleteFilePath)
        newSerial = rephtoFile.split('.')[0]
        # ++++++++++++
        if os.path.exists(photoDir):
            fileList = os.listdir(photoDir)
            print fileList
            if len(fileList) == 1:
                picName = fileList[0]
                picPath = os.path.join(photoDir, picName)

                image = Image.open(picPath)
                imgNew = image.resize((256, 256))
                draw = ImageDraw.Draw(imgNew)
                width, height = font.getsize(newSerial)
                x = int((256 - width) / 2)
                y = 256 - height - 12
                draw.text((x, y), newSerial, fill=(255, 255, 255), font=font)
                savePath = os.path.join('static', 'rephoto', '{0}.jpg'.format(newSerial))
                ab_rephotoPath = os.path.join(rephotoDir, '{0}.jpg'.format(newSerial))
                imgNew.save(savePath)
                os.remove(picPath)
                ret['rephotoPath'] = savePath
                ret['havePic'] = True
                ret['ab_rephotoPath'] = ab_rephotoPath
                with open(rephotoFile, 'w') as f:
                    f.truncate()
            elif len(fileList) == 0:
                ret['havePic'] = False
            else:
                ret['havePic'] = False
                for file in fileList:
                    p = os.path.join(photoDir, file)
                    os.remove(p)
        else:
            ret['havePhotoDir'] = 'False'
            ret['stop'] = 'True'
    else:
        with open(pastSerialFile, 'r') as f:
            pastSerialNumber = f.read().strip()

        if not pastSerialNumber:
            char = 'A'
        else:
            contentList = pastSerialNumber.split('/')
            if serialNumber == contentList[0]:
                char = chr(ord(contentList[-1]) + 1)
            else:
                char = 'A'

        newSerial = serialNumber + '-' + char
        # ++++++++++++
        if os.path.exists(photoDir):
            fileList = os.listdir(photoDir)
            print fileList
            if len(fileList) == 1:
                picName = fileList[0]
                picPath = os.path.join(photoDir, picName)

                image = Image.open(picPath)
                imgNew = image.resize((256, 256))
                draw = ImageDraw.Draw(imgNew)
                width, height = font.getsize(newSerial)

                x = int((256 - width) / 2)
                y = 256 - height - 12
                draw.text((x, y), newSerial, fill=(255, 255, 255), font=font)
                ab_filePath = os.path.join(uploadDir, '{0}.jpg'.format(newSerial))
                savePath = os.path.join('static', 'upload', '{0}.jpg'.format(newSerial))
                imgNew.save(savePath)
                with open(pastSerialFile, 'w') as f:
                    cont = serialNumber + '/' + char
                    f.write(cont)
                os.remove(picPath)
                ret['havePic'] = True
                ret['filePath'] = savePath
                ret['ab_filePath'] = ab_filePath
            elif len(fileList) == 0:
                ret['havePic'] = False
            else:
                ret['havePic'] = False
                for file in fileList:
                    p = os.path.join(photoDir, file)
                    os.remove(p)
        else:
            ret['havePhotoDir'] = 'False'
            ret['stop'] = 'True'
    # -----------------------------------------------------
    stopSignal = True
    if os.path.exists(stopSignalPath):
        with open(stopSignalPath, 'r') as f:
            stopSignal = f.read().strip()
        with open(stopSignalPath, 'w') as f:
            f.truncate()

    if stopSignal == 'done':
        ret['stop'] = 'True'
    # -----------------------------------------------------
    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder)
    return HttpResponse('success_jsonpCallback(' + ret_json + ')')


def rephotograph(request):
    fileName = request.GET.get('fileName', '')
    with open(rephotoFile, 'w') as f:
        f.write(fileName)
    ret = {'rephoto': True}
    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder)
    return HttpResponse('success_jsonpCallback(' + ret_json + ')')


def removePic(request):
    ret = {'remove': True}
    fileName = request.GET.get('fileName', '')
    deleteFilePath = os.path.join(uploadDir, fileName)
    os.remove(deleteFilePath)
    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder)
    return HttpResponse('success_jsonpCallback(' + ret_json + ')')


def upload(request):
    img_path = request.GET.get('img_path', '')
    path_dic = json.loads(img_path)
    ret = {}
    for k, v in path_dic.items():
        base_dir = os.path.join(BASE_DIR, v)
        if os.path.exists(base_dir):
            with open(base_dir, 'rb') as f:
                f1 = base64.b64encode(f.read())
            ret[k] = f1
        else:
            break
    with open(stopSignalPath, 'w') as f:
        result = 'done'
        f.write(result)
    # 删除本地图片
    # shutil.rmtree(uploadDir)
    # shutil.rmtree(rephotoDir)
    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder)
    return HttpResponse('success_jsonpCallback(' + ret_json + ')')


def cancel(request):
    with open(stopSignalPath, 'w') as f:
        result = 'done'
        f.write(result)
    ret = {'success': 'ok'}
    ret_json = json.dumps(ret, separators=(',', ':'), cls=DjangoJSONEncoder)
    return HttpResponse('success_jsonpCallback(' + ret_json + ')')

# -----------------------------------------------------
# 频谱检测仪功能
# 一、通过复制数据库文件解除独占
