# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/Projects/QtCreator/DDA_UIs/BoltsParameters.ui'
#
# Created: Mon Nov 25 17:52:38 2013
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(510, 261)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(140, 220, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 481, 111))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(20, 14, 441, 31))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.layoutWidget = QtGui.QWidget(self.groupBox)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 50, 451, 48))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_length1 = QtGui.QLabel(self.layoutWidget)
        self.label_length1.setObjectName(_fromUtf8("label_length1"))
        self.gridLayout_2.addWidget(self.label_length1, 0, 0, 1, 1)
        self.spinBox_length1 = QtGui.QDoubleSpinBox(self.layoutWidget)
        self.spinBox_length1.setMaximum(999999999.0)
        self.spinBox_length1.setProperty("value", 12.0)
        self.spinBox_length1.setObjectName(_fromUtf8("spinBox_length1"))
        self.gridLayout_2.addWidget(self.spinBox_length1, 0, 1, 1, 1)
        self.label_lenght2 = QtGui.QLabel(self.layoutWidget)
        self.label_lenght2.setObjectName(_fromUtf8("label_lenght2"))
        self.gridLayout_2.addWidget(self.label_lenght2, 0, 2, 1, 1)
        self.spinBox_length2 = QtGui.QDoubleSpinBox(self.layoutWidget)
        self.spinBox_length2.setMaximum(999999999.0)
        self.spinBox_length2.setProperty("value", 10.0)
        self.spinBox_length2.setObjectName(_fromUtf8("spinBox_length2"))
        self.gridLayout_2.addWidget(self.spinBox_length2, 0, 3, 1, 1)
        self.label_boltDistance = QtGui.QLabel(self.layoutWidget)
        self.label_boltDistance.setObjectName(_fromUtf8("label_boltDistance"))
        self.gridLayout_2.addWidget(self.label_boltDistance, 1, 0, 1, 1)
        self.spinBox_boltDistance = QtGui.QDoubleSpinBox(self.layoutWidget)
        self.spinBox_boltDistance.setMaximum(999999999.0)
        self.spinBox_boltDistance.setProperty("value", 4.0)
        self.spinBox_boltDistance.setObjectName(_fromUtf8("spinBox_boltDistance"))
        self.gridLayout_2.addWidget(self.spinBox_boltDistance, 1, 1, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 130, 481, 80))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.layoutWidget1 = QtGui.QWidget(self.groupBox_2)
        self.layoutWidget1.setGeometry(QtCore.QRect(20, 20, 452, 48))
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget1)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_elasticity = QtGui.QLabel(self.layoutWidget1)
        self.label_elasticity.setObjectName(_fromUtf8("label_elasticity"))
        self.gridLayout.addWidget(self.label_elasticity, 0, 0, 1, 1)
        self.spinBox_elasticity = QtGui.QDoubleSpinBox(self.layoutWidget1)
        self.spinBox_elasticity.setMaximum(999999999.0)
        self.spinBox_elasticity.setProperty("value", 16889.0)
        self.spinBox_elasticity.setObjectName(_fromUtf8("spinBox_elasticity"))
        self.gridLayout.addWidget(self.spinBox_elasticity, 0, 1, 1, 1)
        self.label_extension = QtGui.QLabel(self.layoutWidget1)
        self.label_extension.setObjectName(_fromUtf8("label_extension"))
        self.gridLayout.addWidget(self.label_extension, 0, 2, 1, 1)
        self.spinBox_extension = QtGui.QDoubleSpinBox(self.layoutWidget1)
        self.spinBox_extension.setMaximum(999999999.0)
        self.spinBox_extension.setObjectName(_fromUtf8("spinBox_extension"))
        self.gridLayout.addWidget(self.spinBox_extension, 0, 3, 1, 1)
        self.label_prestress = QtGui.QLabel(self.layoutWidget1)
        self.label_prestress.setObjectName(_fromUtf8("label_prestress"))
        self.gridLayout.addWidget(self.label_prestress, 1, 0, 1, 1)
        self.spinBox_prestress = QtGui.QDoubleSpinBox(self.layoutWidget1)
        self.spinBox_prestress.setMaximum(999999999.0)
        self.spinBox_prestress.setObjectName(_fromUtf8("spinBox_prestress"))
        self.gridLayout.addWidget(self.spinBox_prestress, 1, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.groupBox.setTitle(_translate("Dialog", "Bolt Element Generation Parameters", None))
        self.label_3.setText(_translate("Dialog", "Adjacent bolt elements use different lengths is helpful to reinforcement.", None))
        self.label_length1.setText(_translate("Dialog", "length 1:", None))
        self.label_lenght2.setText(_translate("Dialog", "length 2:", None))
        self.label_boltDistance.setText(_translate("Dialog", "Bolt Distance :", None))
        self.groupBox_2.setTitle(_translate("Dialog", "Bolt Element Physical Parameters", None))
        self.label_elasticity.setText(_translate("Dialog", "elasticity modulus :", None))
        self.label_extension.setText(_translate("Dialog", "extension strength :", None))
        self.label_prestress.setText(_translate("Dialog", "Prestress :", None))

