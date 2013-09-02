# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/DL.ui'
#
# Created: Thu Mar 21 22:26:20 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DL(object):
    def setupUi(self, DL):
        DL.setObjectName(_fromUtf8("DL"))
        DL.resize(692, 65)
        self.widget = QtGui.QWidget(DL)
        self.widget.setGeometry(QtCore.QRect(23, 20, 329, 25))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btn_JointSet = QtGui.QPushButton(self.widget)
        self.btn_JointSet.setObjectName(_fromUtf8("btn_JointSet"))
        self.horizontalLayout.addWidget(self.btn_JointSet)
        self.btn_Tunnel = QtGui.QPushButton(self.widget)
        self.btn_Tunnel.setObjectName(_fromUtf8("btn_Tunnel"))
        self.horizontalLayout.addWidget(self.btn_Tunnel)
        self.line = QtGui.QFrame(self.widget)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.btn_Preview = QtGui.QPushButton(self.widget)
        self.btn_Preview.setObjectName(_fromUtf8("btn_Preview"))
        self.horizontalLayout.addWidget(self.btn_Preview)
        self.btn_Calculate = QtGui.QPushButton(self.widget)
        self.btn_Calculate.setObjectName(_fromUtf8("btn_Calculate"))
        self.horizontalLayout.addWidget(self.btn_Calculate)

        self.retranslateUi(DL)
        QtCore.QMetaObject.connectSlotsByName(DL)

    def retranslateUi(self, DL):
        DL.setWindowTitle(_translate("DL", "Form", None))
        self.btn_JointSet.setText(_translate("DL", "JointSets", None))
        self.btn_Tunnel.setText(_translate("DL", "Tunnels", None))
        self.btn_Preview.setText(_translate("DL", "Preview", None))
        self.btn_Calculate.setText(_translate("DL", "Calculate", None))

