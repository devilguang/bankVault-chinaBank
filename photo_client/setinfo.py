# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'setinfo.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_setdialog(object):
    def setupUi(self, setdialog):
        setdialog.setObjectName("setdialog")
        setdialog.resize(431, 251)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/logo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        setdialog.setWindowIcon(icon)
        self.ip_label = QtWidgets.QLabel(setdialog)
        self.ip_label.setGeometry(QtCore.QRect(40, 40, 81, 20))
        font = QtGui.QFont()
        font.setKerning(True)
        self.ip_label.setFont(font)
        self.ip_label.setObjectName("ip_label")
        self.port_label = QtWidgets.QLabel(setdialog)
        self.port_label.setGeometry(QtCore.QRect(40, 90, 91, 21))
        self.port_label.setObjectName("port_label")
        self.photodir_label = QtWidgets.QLabel(setdialog)
        self.photodir_label.setGeometry(QtCore.QRect(40, 140, 81, 21))
        self.photodir_label.setObjectName("photodir_label")
        self.ip_lineEdit = QtWidgets.QLineEdit(setdialog)
        self.ip_lineEdit.setGeometry(QtCore.QRect(130, 30, 260, 27))
        self.ip_lineEdit.setObjectName("ip_lineEdit")
        self.port_lineEdit = QtWidgets.QLineEdit(setdialog)
        self.port_lineEdit.setGeometry(QtCore.QRect(130, 80, 260, 27))
        self.port_lineEdit.setObjectName("port_lineEdit")
        self.photodir_lineEdit = QtWidgets.QLineEdit(setdialog)
        self.photodir_lineEdit.setGeometry(QtCore.QRect(130, 130, 260, 27))
        self.photodir_lineEdit.setObjectName("photodir_lineEdit")
        self.setcancelButton = QtWidgets.QPushButton(setdialog)
        self.setcancelButton.setGeometry(QtCore.QRect(260, 190, 80, 30))
        self.setcancelButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setcancelButton.setAutoDefault(False)
        self.setcancelButton.setObjectName("setcancelButton")
        self.setokButton = QtWidgets.QPushButton(setdialog)
        self.setokButton.setGeometry(QtCore.QRect(90, 190, 80, 30))
        self.setokButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setokButton.setStyleSheet("background-color: rgb(170, 170, 255);")
        self.setokButton.setObjectName("setokButton")

        self.retranslateUi(setdialog)
        self.setcancelButton.clicked.connect(setdialog.close)
        QtCore.QMetaObject.connectSlotsByName(setdialog)

    def retranslateUi(self, setdialog):
        _translate = QtCore.QCoreApplication.translate
        setdialog.setWindowTitle(_translate("setdialog", "设置"))
        self.ip_label.setText(_translate("setdialog", "服务器IP地址："))
        self.port_label.setText(_translate("setdialog", "服务器端口号："))
        self.photodir_label.setText(_translate("setdialog", "相机输出路径："))
        self.setcancelButton.setText(_translate("setdialog", "取 消"))
        self.setokButton.setText(_translate("setdialog", "确 定"))

import image_path_rc
