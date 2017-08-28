# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tdcode.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_code_Dialog(object):
    def setupUi(self, code_Dialog):
        code_Dialog.setObjectName("code_Dialog")
        code_Dialog.resize(330, 80)
        code_Dialog.setMinimumSize(QtCore.QSize(330, 80))
        code_Dialog.setMaximumSize(QtCore.QSize(330, 80))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/logo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        code_Dialog.setWindowIcon(icon)
        self.lineEdit = QtWidgets.QLineEdit(code_Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(20, 10, 290, 40))
        self.lineEdit.setObjectName("lineEdit")
        self.code_label = QtWidgets.QLabel(code_Dialog)
        self.code_label.setGeometry(QtCore.QRect(20, 60, 290, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.code_label.setFont(font)
        self.code_label.setText("")
        self.code_label.setObjectName("code_label")

        self.retranslateUi(code_Dialog)
        QtCore.QMetaObject.connectSlotsByName(code_Dialog)

    def retranslateUi(self, code_Dialog):
        _translate = QtCore.QCoreApplication.translate
        code_Dialog.setWindowTitle(_translate("code_Dialog", "二维码扫描框"))

import image_path_rc
