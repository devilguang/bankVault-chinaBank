# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, QObject, QSize, QTimer
import login
import requests
import settings
import photo
import setinfo
import tdcode
import json, os
import base64
import time
import ctypes
from ctypes import wintypes
import upload_tip
import zlib


class LoginWidget(QDialog, login.Ui_Form):
    def __init__(self, parent=None):
        super(LoginWidget, self).__init__(parent)
        self.setupUi(self)
        self.client = requests.session()
        self.settingButton.clicked.connect(self.settingDialog)
        self.okButton.clicked.connect(self.login)
        self.show()

    def login(self):
        reload(settings)
        nickName = str(self.lineEdit.text())
        passWord = str(self.lineEdit_2.text())
        try:
            if nickName and passWord:
                if settings.SERVERHOST:
                    if settings.SERVERPORT:
                        url = r'http://{0}:{1}/gsinfo/login/'.format(settings.SERVERHOST, settings.SERVERPORT)
                        res = self.client.get(url)
                        csrftoken = res.cookies['csrftoken']
                        data = {
                            'csrfmiddlewaretoken': csrftoken,
                            'userName': nickName,
                            'passWord': passWord,
                            'workRole': 'photographing'
                        }
                        resp = self.client.post(url, data=data)
                        txt = json.loads(resp.text)
                        success = txt['success']
                        if success:
                            self.accept()
                        else:
                            message = txt['message']
                            self.tiplabel.setText("<font color=red>{0}</font>".format(message))
                    else:
                        self.tiplabel.setText("<font color=red>请设置服务器端口号！</font>")
                else:
                    self.tiplabel.setText("<font color=red>请设置服务器IP地址！</font>")
            else:
                self.tiplabel.setText("<font color=red>请输入正确的用户或密码！</font>")
        except Exception as e:
            print e
            self.tiplabel.setText("<font color=red>登录失败！</font>")

    def settingDialog(self):
        reload(settings)
        newForm = setinfoDil()
        newForm.show()
        newForm.exec_()


class exitSetForm(QObject):
    closeApp = pyqtSignal()


class setinfoDil(QDialog, setinfo.Ui_setdialog):
    def __init__(self, parent=None):
        super(setinfoDil, self).__init__(parent)
        self.setupUi(self)

        self.ip_lineEdit.setText(settings.SERVERHOST)
        self.port_lineEdit.setText(settings.SERVERPORT)
        self.photodir_lineEdit.setText(settings.PHOTODIR)

        self.exitSet = exitSetForm()
        self.setokButton.clicked.connect(self.confirmInfo)
        self.exitSet.closeApp.connect(self.close)

    def confirmInfo(self):
        new_ele = []
        with open('settings.py', 'r') as f:
            ele_list = f.readlines()
            for ele in ele_list:
                if 'SERVERHOST' in ele:
                    ip = "SERVERHOST = '{0}'".format(self.ip_lineEdit.text())
                    new_ele.append(ip)
                    new_ele.append('\n')
                elif 'SERVERPORT' in ele:
                    port = "SERVERPORT = '{0}'".format(self.port_lineEdit.text())
                    new_ele.append(port)
                    new_ele.append('\n')
                elif 'PHOTODIR' in ele:
                    photo_dir = "PHOTODIR = r'{0}'".format(self.photodir_lineEdit.text())
                    new_ele.append(photo_dir)
                    new_ele.append('\n')
                else:
                    new_ele.append(ele)
        with open('settings.py', 'w') as f:
            f.truncate()
        with open('settings.py', 'a') as f:
            for i in new_ele:
                f.write(i)
        self.exitSet.closeApp.emit()


class tdcodeDil(QDialog, tdcode.Ui_code_Dialog):
    def __init__(self, client=None):
        super(tdcodeDil, self).__init__()
        self.client = client
        self.setupUi(self)
        self.setGeometry(5, 35, 335, 80)
        self.lineEdit.returnPressed.connect(self.haveSerialNumber)
        self.SerialNumber = ''
        self.boxOrSubBox = ''
        self.isvis = False
        self.timer = QTimer()

    def haveSerialNumber(self):
        sNumber = self.lineEdit.text()
        if sNumber:
            # 检测serialNumber是否可用
            url = r'http://{0}:{1}/gsinfo/photographing/searchThingInfo/'.format(settings.SERVERHOST,
                                                                                 settings.SERVERPORT)
            cookies = self.client.cookies
            csrftoken = cookies['csrftoken']
            data = {
                'csrfmiddlewaretoken': csrftoken,
                'serialNumber': str(sNumber),
                'processId': '6',
            }
            resp = self.client.post(url, data=data, cookies=cookies)
            txt = json.loads(resp.text)
            self.success = txt['success']
            if self.success:
                self.code_label.setText("")
                self.SerialNumber = sNumber
                self.boxNumber = txt['boxNumber']
            else:
                self.code_label.setText("<font color=red>{0}</font>".format(txt['message']))
        else:
            self.code_label.setText("<font color=red>请扫描二维码！</font>")

    # 修改窗体自身的X关闭按钮，只要重载closeEvent方法即可
    def closeEvent(self, event):
        self.isvis = False
        self.timer.stop()  # close timer
        print('timer stoped!')
        self.close()


class uploadTip(QDialog, upload_tip.Ui_Dialog):
    def __init__(self, client=None):
        super(uploadTip, self).__init__()
        self.setupUi(self)
        self.show()


class Window(QMainWindow, photo.Ui_Form):
    def __init__(self, client=None):
        super(Window, self).__init__()
        self.setupUi(self)

        self.client = client
        self.codeForm = tdcodeDil(client=self.client)

        self.codeButton.clicked.connect(self.codeDil)
        self.delButton.clicked.connect(self.delPic)
        self.uploadButton.clicked.connect(self.uploadPic)

        self.photo_dir = settings.PHOTODIR
        self.upload_dir = settings.UPLOADDIR

        self.img_list = {}
        self.img_list['A'] = self.img1
        self.img_list['B'] = self.img2
        self.img_list['C'] = self.img3
        self.img_list['D'] = self.img4
        self.img_list['E'] = self.img5
        self.img_list['F'] = self.img6
        self.img_list['G'] = self.img7
        self.img_list['H'] = self.img8
        self.img_list['I'] = self.img9
        self.img_list['J'] = self.img10
        self.img_list['K'] = self.img11
        self.img_list['L'] = self.img12

        self.naem_list = {}
        self.naem_list['A'] = self.name1
        self.naem_list['B'] = self.name2
        self.naem_list['C'] = self.name3
        self.naem_list['D'] = self.name4
        self.naem_list['E'] = self.name5
        self.naem_list['F'] = self.name6
        self.naem_list['G'] = self.name7
        self.naem_list['H'] = self.name8
        self.naem_list['I'] = self.name9
        self.naem_list['J'] = self.name10
        self.naem_list['K'] = self.name11
        self.naem_list['L'] = self.name12

    def codeDil(self):
        if not self.codeForm.isvis:
            self.codeForm.show()
            self.codeForm.isvis = self.codeForm.isVisible()

            self.codeForm.timer.setInterval(1000)
            self.codeForm.timer.start()
            self.codeForm.timer.timeout.connect(self.findPoto)

            self.showMinimized()
            self.codeForm.exec_()

    def findPoto(self):
        # 首先判断相机目录是否存在
        if not os.path.exists(self.upload_dir):
            os.mkdir(self.upload_dir)
        serial_num = self.codeForm.SerialNumber
        print '--', serial_num
        if serial_num:
            photoList = os.listdir(self.photo_dir)
            photo_len = len(photoList)

            if photo_len == 1:
                picName = photoList[0]
                picPath = os.path.join(self.photo_dir, picName)

                upload_len = len(os.listdir(self.upload_dir))
                char = chr(ord('A') + upload_len)
                newSerial = serial_num + '-' + char

                ab_filePath = os.path.join(self.upload_dir, '{0}.jpg'.format(newSerial))
                # imgNew.save(ab_filePath)
                os.rename(picPath,ab_filePath)
                # os.remove(picPath)
                file_name = newSerial + '.jpg'
                pic_num = len(os.listdir(self.upload_dir))
                shang, yushu = divmod(pic_num, 3)
                if yushu > 0:
                    self.scrollAreaWidgetContents.setMinimumSize(QSize(1079, 402 * (shang + 1)))

                for k, v, in self.img_list.items():
                    if char == k:
                        self.pixmap = QPixmap(ab_filePath)
                        self.img_list[k].setPixmap(self.pixmap)
                        self.naem_list[k].setText(file_name)
                        self.showMaximized()
            elif photo_len > 1:
                for file in photoList:
                    p = os.path.join(self.photo_dir, file)
                    os.remove(p)

    def delPic(self):
        pic_name_list = os.listdir(self.upload_dir)
        pic_num = len(pic_name_list)
        char = chr(ord('A') + pic_num - 1)

        for pic_name in pic_name_list:
            if char in pic_name:
                p = os.path.join(self.upload_dir, pic_name)
                os.remove(p)

        for k, v, in self.img_list.items():
            if char == k:
                self.pixmap = QPixmap('')
                self.img_list[k].setPixmap(self.pixmap)
                self.naem_list[k].setText('')
                self.showMinimized()

        pic_num = len(os.listdir(self.upload_dir))
        shang, yushu = divmod(pic_num, 3)
        if yushu > 0:
            self.scrollAreaWidgetContents.setMinimumSize(QSize(1079, 402 * (shang + 1)))
        elif shang > 0 and yushu == 0:
            self.scrollAreaWidgetContents.setMinimumSize(QSize(1079, 402 * shang))

    def uploadPic(self):
        geom = self.geometry()
        x = geom.left()
        y = geom.top()
        w = geom.width()
        h = geom.height()

        if self.codeForm.isvis:
            serial_num = self.codeForm.SerialNumber
            box_Sub = self.codeForm.boxOrSubBox
            pic_name_list = os.listdir(self.upload_dir)
            if len(pic_name_list) > 0:
                self.tipDlg = uploadTip(self)
                self.tipDlg.label.setText("正在上传中...")
                self.tipDlg.setGeometry(x + w * 0.5, y + h * 0.5, 100, 160)
                all_img = {}
                for pic_name in pic_name_list:
                    file_path = os.path.join(self.upload_dir, pic_name)
                    zlib_result3 = zlib.crc32(file_path)
                    print zlib_result3
                    with open(file_path, 'rb') as f:
                        f1 = base64.b64encode(f.read())
                        all_img[pic_name] = f1
                imgs = json.dumps(all_img)
                url = r'http://{0}:{1}/gsinfo/photographing/updatePhotographingInfo/'.format(settings.SERVERHOST,
                                                                                             settings.SERVERPORT)
                cookies = self.client.cookies
                csrftoken = cookies['csrftoken']
                data = {
                    'csrfmiddlewaretoken': csrftoken,
                    'serialNumber': str(serial_num),
                    'boxNumber': box_Sub,
                    'pic_path': imgs
                }
                resp = self.client.post(url, data=data, cookies=cookies)
                if resp.status_code == 200:
                    txt = json.loads(resp.text)
                    suc = txt['success']
                    print suc
                    if suc:
                        for pic_name in pic_name_list:
                            file_path = os.path.join(self.upload_dir, pic_name)
                            os.remove(file_path)

                        self.codeForm.lineEdit.setText('')
                        self.codeForm.SerialNumber = self.codeForm.lineEdit.text()
                        self.tipDlg.close()

                        # print geom.left(),geom.right(),geom.width(),geom.height(),geom.top()
                        messagebox = TimerMessageBox(2)
                        messagebox.setGeometry(x + w * 0.5, y + h * 0.5, 100, 160)
                        messagebox.exec_()
                        self.showMinimized()

                        for pic_name in pic_name_list:
                            se_char = pic_name.split('.')[0]
                            char = se_char.split('-')[-1]
                            for k, v, in self.img_list.items():
                                if char == k:
                                    self.pixmap = QPixmap('')
                                    self.img_list[k].setPixmap(self.pixmap)
                                    self.naem_list[k].setText('')
                    else:
                        self.tipDlg.close()
                        QMessageBox.critical(self, "警告：", self.tr("     上传失败!       "))
            else:
                QMessageBox.critical(self, "提示：", self.tr("     暂无图片上传!       "))

    def mouseDoubleClickEvent(self, event):
        self.showMinimized()

    def closeEvent(self, event):
        self.codeForm.close()
        self.close()


class TimerMessageBox(QMessageBox):
    def __init__(self, timeout=None):
        super(TimerMessageBox, self).__init__()
        self.setWindowTitle("上传")
        self.time_to_wait = timeout
        self.setText("上传成功！（{0}）".format(timeout))
        self.setStandardButtons(QMessageBox.NoButton)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.start()
        self.timer.timeout.connect(self.changeContent)

    def changeContent(self):
        self.time_to_wait -= 1
        self.setText("上传成功！（{0}）".format(self.time_to_wait))
        if self.time_to_wait <= 0:
            self.close()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
    app = QApplication(sys.argv)
    login = LoginWidget()

    if login.exec_() == QDialog.Accepted:
        client = login.client

        window = Window(client=client)
        window.show()

        sys.exit(app.exec_())
