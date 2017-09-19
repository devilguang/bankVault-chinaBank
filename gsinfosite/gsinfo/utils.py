#encoding=UTF-8
import os
import datetime
import zipfile

def readFile(filePath, buf_size=262144):
    f = open(filePath, "rb")
    while True:
        c = f.read(buf_size)
        if c:
            yield c 
        else:
            break
    f.close()

def dateTimeHandler(obj):
    if isinstance(obj, datetime.datetime):
        # UTC时区 转换至 Asian/ShangHai
        # converted = datetime.datetime(obj.year, obj.month, obj.day, 24-(obj.hour+8)%23 if ((obj.hour+8)>=24) else (obj.hour+8), obj.minute, obj.second)
        converted = datetime.datetime(obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second)
        return converted.strftime('%Y年%m月%d日 %H:%M')
    else:
        raise TypeError
        
def zipDir(zipFileName, targetDir):
    zip = zipfile.ZipFile(zipFileName, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(targetDir, True):
        for file in files:
            filePath = os.path.join(root, file)
            zip.write(filePath, filePath[len(targetDir):])
        for dir in dirs:
            dirPath = os.path.join(root, dir)
            zip.write(dirPath, dir)
    zip.close()