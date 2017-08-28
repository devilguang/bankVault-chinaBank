# encoding=UTF-8
import os
from gsinfosite import settings
import time
import shutil
import zipfile

#LOGBIN = r'C:\ProgramData\MySQL\MySQL Server 5.7\incrementalBackup'
BACKUPDIR = os.path.join(settings.BASE_DIR, time.strftime("%Y%m%d"))
hardDir = settings.HARDDIR
#daily = os.path.join(settings.BASE_DIR, time.strftime("%Y%m%d"))
def backupDatabase(type):
    database = settings.DATABASES['default']
    NAME = database['NAME']
    HOST = database['HOST']
    USER = database['USER']
    PASSWORD = database['PASSWORD']
    if type == '0':  # 做全量备份
        fileName = time.strftime("%Y%m%d") + ".sql"
        backupPath = os.path.join(BACKUPDIR, fileName)
        cmd_dump = r'mysqldump -h%s -u%s -p%s %s > %s' % (HOST, USER, PASSWORD, NAME, backupPath)
        if os.system(cmd_dump) == 0:
            print 'database backup'
        else:
            print 'database backup failed!'
    elif type == '1':  # 做增量备份
        listDir = os.listdir(LOGBIN)
        fileSuffix = []
        for d in listDir:
            dList = d.split('.')
            if 'index' not in dList:
                fileSuffix.append(dList[1])
        sortedSuffix = sorted(fileSuffix)
        print sortedSuffix
        tarFile = sortedSuffix[0]
        Incremental = 'mysqladmin -u{0} -p{1} flush-logs'.format(USER, PASSWORD)
        os.system(Incremental)

    else:
        print '参数有误！'


def getAllPath(rootPath):
    path = os.walk(rootPath)
    pathList = []

    for root, dirs, files in path:
        if dirs:
            for dir in dirs:
                pathList.append(os.path.join(root,dir))
        if files:
            for file in files:
                pathList.append(os.path.join(root,file))
    return pathList


def backupBinFile(type):
    file_src = os.path.join(settings.BASE_DIR, 'data')
    file_dst = os.path.join(BACKUPDIR, 'data')
    if type == '0':  # 二进制文件全量备份
        shutil.copytree(file_src, file_dst)
    elif type == '1':  # 做增量备份
        fullBackup = getAllPath(file_dst)
        nextBackup = getAllPath(file_src)
        addFile = []
        for path in set(nextBackup):
            if path not in fullBackup:
                addFile.append(path)
        for p in addFile:
            ind = p.find('data')
            newPath = os.path.join(BACKUPDIR,p[ind:])
            if os.path.isfile(p):
                shutil.copyfile(p, newPath)
            else:
                shutil.copytree(p, newPath)

        deleteFile = []
        for p in set(fullBackup):
            if p not in nextBackup:
                deleteFile.append(p)
        if deleteFile:
            with open('deleteFile.txt','w') as f:
                f.write(deleteFile)
    else:
        print '参数有误！'

def main():
    if not os.path.exists(BACKUPDIR):
        os.mkdir(BACKUPDIR)
    database = settings.DATABASES['default']
    NAME = database['NAME']
    HOST = database['HOST']
    USER = database['USER']
    PASSWORD = database['PASSWORD']
    fileName = NAME + ".sql"
    backupPath = os.path.join(BACKUPDIR, fileName)
    cmd_dump = r'mysqldump -h%s -u%s -p%s %s > %s' % (HOST, USER, PASSWORD, NAME, backupPath)
    os.system(cmd_dump)

    # 二进制文件备份
    file_src = os.path.join(settings.BASE_DIR, 'data')
    file_dst = os.path.join(BACKUPDIR, 'data')
    shutil.copytree(file_src, file_dst)

    # 对备份后的文件进行压缩
    zip_file = BACKUPDIR + '.zip'  # 只要修改BACKUPDIR就可以将文件压缩到指定的目录下
    f_zip = zipfile.ZipFile(zip_file, 'w')

    for root, dirs, files in os.walk(BACKUPDIR):
        for f in files:
            # 获取文件相对路径，在压缩包内建立相同的目录结构
            abs_path = os.path.join(os.path.join(root, f))
            rel_path = os.path.relpath(abs_path, os.path.dirname(BACKUPDIR))
            f_zip.write(abs_path, rel_path, zipfile.ZIP_STORED)
    f_zip.setpassword('nimei')
    f_zip.close()

    if os.path.exists(BACKUPDIR):
        shutil.rmtree(BACKUPDIR)

    # 将压缩后的文件拷贝到制定的硬盘
    #shutil.copytree(zip_file, '')

if __name__ == '__main__':
    main()

