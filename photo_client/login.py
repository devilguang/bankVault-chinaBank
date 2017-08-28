# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 280)
        Form.setMinimumSize(QtCore.QSize(400, 270))
        Form.setMaximumSize(QtCore.QSize(400, 280))
        font = QtGui.QFont()
        font.setFamily("宋体")
        Form.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/logo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        Form.setToolTipDuration(-3)
        self.okButton = QtWidgets.QPushButton(Form)
        self.okButton.setGeometry(QtCore.QRect(100, 210, 80, 30))
        self.okButton.setObjectName("okButton")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(150, 90, 171, 27))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(150, 140, 171, 27))
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(80, 100, 54, 12))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(80, 150, 54, 12))
        self.label_2.setObjectName("label_2")
        self.cancelButton = QtWidgets.QPushButton(Form)
        self.cancelButton.setGeometry(QtCore.QRect(230, 210, 80, 30))
        self.cancelButton.setObjectName("cancelButton")
        self.graphicsView = QtWidgets.QGraphicsView(Form)
        self.graphicsView.setGeometry(QtCore.QRect(0, 0, 401, 51))
        self.graphicsView.setStyleSheet("border-image: url(:/images/logo.jpg);")
        self.graphicsView.setObjectName("graphicsView")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(190, 30, 141, 20))
        font = QtGui.QFont()
        font.setFamily("SimSun-ExtB")
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.settingButton = QtWidgets.QPushButton(Form)
        self.settingButton.setGeometry(QtCore.QRect(360, 20, 26, 26))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settingButton.sizePolicy().hasHeightForWidth())
        self.settingButton.setSizePolicy(sizePolicy)
        self.settingButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.settingButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/settings.jpeg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settingButton.setIcon(icon1)
        self.settingButton.setIconSize(QtCore.QSize(26, 26))
        self.settingButton.setObjectName("settingButton")
        self.tiplabel = QtWidgets.QLabel(Form)
        self.tiplabel.setGeometry(QtCore.QRect(150, 180, 241, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.tiplabel.setFont(font)
        self.tiplabel.setObjectName("tiplabel")

        self.retranslateUi(Form)
        self.cancelButton.clicked.connect(Form.close)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "登录-图像采集岗"))
        self.okButton.setText(_translate("Form", "确定"))
        self.label.setText(_translate("Form", "用 户 名："))
        self.label_2.setText(_translate("Form", "密    码："))
        self.cancelButton.setText(_translate("Form", "取消"))
        self.label_3.setText(_translate("Form", "<html><head/><body><p><span style=\" font-weight:600; color:#ffff99;\">金银清点查验业务系统</span></p></body></html>"))
        self.tiplabel.setText(_translate("Form", "<html><head/><body><p><br/></p></body></html>"))

import image_path_rc
