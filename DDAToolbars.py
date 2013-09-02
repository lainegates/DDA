
#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2009, 2010                                              *  
#*   Xiaolong Cheng <lainegates@163.com>                                   *  
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

from PyQt4 import QtCore, QtGui
import FreeCADGui

__errorStyleSheet__ = "background-color:rgba(255,160,30,255)"
__normalStyleSheet__ = "background-color:rgba(255,255,255,255)"

def getMainWindow():
    "returns the main window"
    # using QtGui.qApp.activeWindow() isn't very reliable because if another
    # widget than the mainwindow is active (e.g. a dialog) the wrong widget is
    # returned
    toplevel = QtGui.qApp.topLevelWidgets()
    for i in toplevel:
        if i.metaObject().className() == "Gui::MainWindow":
            return i
    raise Exception("No main window found")


class LineToolbar:
    def __init__(self):
        self.__initToolbar()
        self.sourceCmd = None
        self.crossedViews = []
        
    def __initToolbarStyle(self):
        self.__toolbar.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.__toolbar.setFloatable(True)
        self.__toolbar.setMovable(True)
        
    def __initToolbar(self):
        # init self.__toolbar style
        mainWindow = getMainWindow()
        self.__toolbar = QtGui.QToolBar('LineToolbar',mainWindow)
        self.__toolbar.setAllowedAreas(QtCore.Qt.NoToolBarArea)
        self.__toolbar.setFixedSize(400,40)
        self.__toolbar.setVisible(False)
        self.__initToolbarStyle()
        mainWindow.addToolBar(self.__toolbar)
        
        self.__xlabel = QtGui.QLabel('x : ')
        self.__act_xLabel = self.__toolbar.addWidget(self.__xlabel)
        self.__act_xLabel.setVisible(True)
        
        self.xValue = QtGui.QLineEdit()
        self.__act_xValue = self.__toolbar.addWidget(self.xValue)
        self.__act_xValue.setVisible(True)
        
        self.__ylabel = QtGui.QLabel('y : ')
        self.__act_yLabel = self.__toolbar.addWidget(self.__ylabel)
        self.__act_yLabel.setVisible(True)
        
        self.yValue = QtGui.QLineEdit()
        self.__act_yValue = self.__toolbar.addWidget(self.yValue)
        self.__act_yValue.setVisible(True)
        
        self.__toolbar.addSeparator()
        
        self.__actFinish = self.__toolbar.addAction(QtCore.QString('Finish'))
        self.__actClose = self.__toolbar.addAction(QtCore.QString('Close'))
        
        # connection
        self.xValue.textEdited.connect(self.checkDataValid)
        self.yValue.textEdited.connect(self.checkDataValid)
        
    def on(self):
        self.__toolbar.show()
#        self.__initToolbarStyle()
#        self.__toolbar.move(100,100)
        
    def offUi(self):
        self.__toolbar.hide()
        
    def checkDataValid(self,text):
        if not self.xValue.hasFocus() and not self.yValue.hasFocus():
            return
        
        tmpError = False
        try:
            tmp = float(self.xValue.text())
        except ValueError:
            self.xValue.setStyleSheet(__errorStyleSheet__)
            tmpError = True
        else:
            self.xValue.setStyleSheet(__normalStyleSheet__)

        try:
            tmp = float(self.yValue.text())
        except ValueError:
            self.yValue.setStyleSheet(__errorStyleSheet__)
            tmpError = True
        else:
            self.yValue.setStyleSheet(__normalStyleSheet__)
            
        if not tmpError:
            import Base
            Base.showErrorMessageBox('ValueError', 'please input float number')
            return
        else:
            self.validatePoint()
            
    def validatePoint(self):
        "function for checking and sending numbers entered manually"
        assert self.sourceCmd
        self.sourceCmd.numericInput(float(self.xValue.text())\
                                        , float(self.yValue.text()), 0)
        

    def cross(self, on=True):
        if on:
            if not self.crossedViews:
                mw = getMainWindow()
                self.crossedViews = mw.findChildren(QtGui.QFrame, "SoQtWidgetName")
                for w in self.crossedViews:
                    w.setCursor(QtCore.Qt.CrossCursor)
            else:
                for w in self.crossedViews:
                    w.unsetCursor()
                self.crossedViews = []

    def displayPoint(self, point, last=None, plane=None):
        "this function displays the passed coords in the x, y, and z widgets"
        dp = point
        self.xValue.setText("%.6f" % dp.x)
        self.yValue.setText("%.6f" % dp.y)

lineToolbar = LineToolbar()
lineToolbar.offUi()
FreeCADGui.DDAToolbar = lineToolbar
#    def setVisible(self , flag):
#        if flag:
#            self.__toolbar.show()
#            self.__initToolbarStyle()
#        else:
#            self.__toolbar.hide()

        
#toolbar = LineToolbar()
#toolbar.setVisible(True)
#print toolbar