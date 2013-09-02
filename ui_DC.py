# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/DC.ui'
#
# Created: Thu Mar 21 22:26:29 2013
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

class Ui_DC(object):
    def setupUi(self, DC):
        DC.setObjectName(_fromUtf8("DC"))
        DC.resize(716, 111)
        self.widget = QtGui.QWidget(DC)
        self.widget.setGeometry(QtCore.QRect(11, 10, 594, 25))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btn_BoltElement = QtGui.QPushButton(self.widget)
        self.btn_BoltElement.setObjectName(_fromUtf8("btn_BoltElement"))
        self.horizontalLayout.addWidget(self.btn_BoltElement)
        self.btn_FixPoint = QtGui.QPushButton(self.widget)
        self.btn_FixPoint.setObjectName(_fromUtf8("btn_FixPoint"))
        self.horizontalLayout.addWidget(self.btn_FixPoint)
        self.btn_LoadingPoint = QtGui.QPushButton(self.widget)
        self.btn_LoadingPoint.setObjectName(_fromUtf8("btn_LoadingPoint"))
        self.horizontalLayout.addWidget(self.btn_LoadingPoint)
        self.btn_MeasuredPoint = QtGui.QPushButton(self.widget)
        self.btn_MeasuredPoint.setObjectName(_fromUtf8("btn_MeasuredPoint"))
        self.horizontalLayout.addWidget(self.btn_MeasuredPoint)
        self.btn_HolePoint = QtGui.QPushButton(self.widget)
        self.btn_HolePoint.setObjectName(_fromUtf8("btn_HolePoint"))
        self.horizontalLayout.addWidget(self.btn_HolePoint)
        self.line = QtGui.QFrame(self.widget)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.btn_Preivew = QtGui.QPushButton(self.widget)
        self.btn_Preivew.setObjectName(_fromUtf8("btn_Preivew"))
        self.horizontalLayout.addWidget(self.btn_Preivew)
        self.btn_Calculate = QtGui.QPushButton(self.widget)
        self.btn_Calculate.setObjectName(_fromUtf8("btn_Calculate"))
        self.horizontalLayout.addWidget(self.btn_Calculate)

        self.retranslateUi(DC)
        QtCore.QMetaObject.connectSlotsByName(DC)

    def retranslateUi(self, DC):
        DC.setWindowTitle(_translate("DC", "Form", None))
        self.btn_BoltElement.setText(_translate("DC", "BoltElement", None))
        self.btn_FixPoint.setText(_translate("DC", "FixPoint", None))
        self.btn_LoadingPoint.setText(_translate("DC", "LoadingPoint", None))
        self.btn_MeasuredPoint.setText(_translate("DC", "MeasuredPoint", None))
        self.btn_HolePoint.setText(_translate("DC", "HolePoint", None))
        self.btn_Preivew.setText(_translate("DC", "Preivew", None))
        self.btn_Calculate.setText(_translate("DC", "Calculate", None))

