# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/CalculationProcess.ui'
#
# Created: Mon Mar 11 17:07:40 2013
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

class Ui_DF_Calculation(object):
    def setupUi(self, DF_Calculation):
        DF_Calculation.setObjectName(_fromUtf8("DF_Calculation"))
        DF_Calculation.resize(316, 147)
        self.progressBar = QtGui.QProgressBar(DF_Calculation)
        self.progressBar.setGeometry(QtCore.QRect(30, 50, 261, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.pushButton = QtGui.QPushButton(DF_Calculation)
        self.pushButton.setGeometry(QtCore.QRect(210, 110, 75, 23))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.label = QtGui.QLabel(DF_Calculation)
        self.label.setGeometry(QtCore.QRect(30, 20, 261, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_rate = QtGui.QLabel(DF_Calculation)
        self.label_rate.setGeometry(QtCore.QRect(30, 80, 141, 16))
        self.label_rate.setObjectName(_fromUtf8("label_rate"))

        self.retranslateUi(DF_Calculation)
        QtCore.QMetaObject.connectSlotsByName(DF_Calculation)

    def retranslateUi(self, DF_Calculation):
        DF_Calculation.setWindowTitle(_translate("DF_Calculation", "DF Calculation", None))
        self.pushButton.setText(_translate("DF_Calculation", "Cancel", None))
        self.label.setText(_translate("DF_Calculation", "This may take serval minutes , please wait.", None))
        self.label_rate.setText(_translate("DF_Calculation", "TextLabel", None))

