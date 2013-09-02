# coding=gbk

import FreeCAD, FreeCADGui, os , sys , Base
try:
    from PyQt4 import QtCore, QtGui, QtSvg    
except:
    FreeCAD.Console.PrintMessage("Error: Python-qt4 package must be installed on your system to use the Draft module.")

#import Base

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

FreeCAD.Console.PrintMessage( 'MyDockWidget begin\n')



class todo:
    ''' static todo class, delays execution of functions.  Use todo.delay
    to schedule geometry manipulation that would crash coin if done in the
    event callback'''

    '''List of (function, argument) pairs to be executed by
    QtCore.QTimer.singleShot(0,doTodo).'''
    itinerary = []
    commitlist = []
    
    @staticmethod
    def doTasks():
        # print "debug: doing delayed tasks: commitlist: ",todo.commitlist," itinerary: ",todo.itinerary
        for f, arg in todo.itinerary:
            try:
                # print "debug: executing",f
                if arg:
                    f(arg)
                else:
                    f()
            except:
                wrn = "[Draft.todo] Unexpected error:" , sys.exc_info()[0]
                FreeCAD.Console.PrintWarning (wrn)
                print f , arg
        todo.itinerary = []
#        if todo.commitlist:
#            for name, func in todo.commitlist:
#                # print "debug: committing ",str(name)
# #               try:
#                name = str(name)
#                FreeCAD.ActiveDocument.openTransaction(name)
#                func()
#                FreeCAD.ActiveDocument.commitTransaction()
##               except:
##                    wrn = "[Draft.todo] Unexpected error:" + sys.exc_info()[0]
##                    FreeCAD.Console.PrintWarning (wrn)
#        todo.commitlist = []

    @staticmethod
    def delay (f, arg):
        #print "debug: delaying",f
        if todo.itinerary == []:
            QtCore.QTimer.singleShot(0, todo.doTasks)
        todo.itinerary.append((f, arg))

#    @staticmethod
#    def delayCommit (cl):
#        #print "debug: delaying commit",cl
#        QtCore.QTimer.singleShot(0, todo.doTasks)
#        todo.commitlist = cl

    
class DDALineEdit(QtGui.QLineEdit):
    "custom QLineEdit widget that has the power to catch Escape keypress"
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.emit(QtCore.SIGNAL("escaped()"))
        elif event.key() == QtCore.Qt.Key_Up:
            self.emit(QtCore.SIGNAL("up()"))
        elif event.key() == QtCore.Qt.Key_Down:
            self.emit(QtCore.SIGNAL("down()"))
        elif (event.key() == QtCore.Qt.Key_Z) and QtCore.Qt.ControlModifier:
            self.emit(QtCore.SIGNAL("undo()"))
        else:
            QtGui.QLineEdit.keyPressEvent(self, event)

    
class MyDockWidget:
    "main DockWidget"
    def __init__(self):
        FreeCAD.Console.PrintMessage( 'MyDockWidget init begin\n')
        self.taskmode = Base.getParam("UiMode")
        self.paramcolor = Base.getParam("color")>>8
        self.color = QtGui.QColor(self.paramcolor)
        self.facecolor = QtGui.QColor(204, 204, 204)
        self.linewidth = Base.getParam("linewidth")
        self.fontsize = Base.getParam("textheight")
        self.paramconstr = Base.getParam("constructioncolor")>>8
        self.constrMode = False
        self.continueMode = False
        self.state = None
        self.textbuffer = []
        self.crossedViews = []
        self.tray = None
        self.sourceCmd = None
        self.dockWidget = QtGui.QDockWidget()
        self.mw = getMainWindow()
        self.mw.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dockWidget)
        self.centralWidget = QtGui.QWidget()
        #self.label = QtGui.QLabel(self.dockWidget)
        #self.label.setText("abc")
        self.dockWidget.setWidget(self.centralWidget)
        self.dockWidget.setVisible(False)
        self.dockWidget.toggleViewAction().setVisible(False)
        self.layout = QtGui.QHBoxLayout(self.centralWidget)
        self.layout.setObjectName("layout")
        self.setupToolBar()
        self.setupTray()
        self.setupStyle()
        FreeCAD.Console.PrintMessage( 'MyDockWidget init done\n')

#---------------------------------------------------------------------------
# General UI setup
#---------------------------------------------------------------------------
    def _pushbutton (self, name, layout, hide=True, icon=None, width=66, checkable=False):
        button = QtGui.QPushButton(self.dockWidget)
        button.setObjectName(name)
        button.setMaximumSize(QtCore.QSize(width, 26))
        if hide:
            button.hide()
        if icon:
            button.setIcon(QtGui.QIcon(':/icons/' + icon + '.svg'))
            button.setIconSize(QtCore.QSize(16, 16))
        if checkable:
            button.setCheckable(True)
            button.setChecked(False)
        layout.addWidget(button)
        return button

    def _label (self, name, layout, hide=True):
        label = QtGui.QLabel(self.dockWidget)
        label.setObjectName(name)
        if hide: label.hide()
        layout.addWidget(label)
        return label

    def _lineedit (self, name, layout, hide=True, width=None):
        lineedit = DDALineEdit(self.dockWidget)
        lineedit.setObjectName(name)
        if hide: lineedit.hide()
        if not width: width = 800
        lineedit.setMaximumSize(QtCore.QSize(width, 22))
        layout.addWidget(lineedit)
        return lineedit

    def _spinbox (self, name, layout, val=None, vmax=None, hide=True, double=False, size=None):
        if double:
            sbox = QtGui.QDoubleSpinBox(self.dockWidget)
            sbox.setDecimals(2)
        else:
            sbox = QtGui.QSpinBox(self.dockWidget)
        sbox.setObjectName(name)
        if val: sbox.setValue(val)
        if vmax: sbox.setMaximum(vmax)
        if size: sbox.setMaximumSize(QtCore.QSize(size[0], size[1]))
        if hide: sbox.hide()
        layout.addWidget(sbox)
        return sbox

    def _checkbox (self, name, layout, checked=True, hide=True):
        chk = QtGui.QCheckBox(self.dockWidget)
        chk.setChecked(checked)
        chk.setObjectName(name)
        if hide: chk.hide()
        layout.addWidget(chk)
        return chk
     
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
            
    def setTitle(self, title):
        if self.taskmode:
            self.dockWidget.setWindowTitle(title)
        else:
            self.cmdlabel.setText(title)

    def setupToolBar(self, task=False):
        "sets the draft toolbar up"
        
        # command
        
        self.promptlabel = self._label("promptlabel", self.layout, hide=task)
        self.cmdlabel = self._label("cmdlabel", self.layout, hide=task)
        boldtxt = QtGui.QFont()
        boldtxt.setWeight(75)
        boldtxt.setBold(True)
        self.cmdlabel.setFont(boldtxt)
        
        # point
        
        xl = QtGui.QHBoxLayout()
        yl = QtGui.QHBoxLayout()
        zl = QtGui.QHBoxLayout()
        self.layout.addLayout(xl)
        self.layout.addLayout(yl)
        self.layout.addLayout(zl)
        self.labelx = self._label("labelx", xl)
        self.xValue = self._lineedit("xValue", xl, width=60)
        self.xValue.setText("0.00")
        self.labely = self._label("labely", yl)
        self.yValue = self._lineedit("yValue", yl, width=60)
        self.yValue.setText("0.00")
        self.labelz = self._label("labelz", zl)
        self.zValue = self._lineedit("zValue", zl, width=60)
        self.zValue.setText("0.00")
        self.textValue = self._lineedit("textValue", self.layout)

        
        # circle radius
        self.labelRadius = self._label("labelRadius", self.layout)
        self.radiusValue = self._lineedit("radiusValue", self.layout, width=60)
        self.radiusValue.setText("0.00")
        
        # spacer
        if not self.taskmode:
            spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding,
                                           QtGui.QSizePolicy.Minimum)
        else:
            spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum,
                                           QtGui.QSizePolicy.Expanding)
        self.layout.addItem(spacerItem)
    
                            
    def offUi(self):
        if self.taskmode:
            self.isTaskOn = False
            todo.delay(FreeCADGui.Control.closeDialog, None)
            self.baseWidget = QtGui.QWidget()
            # print "UI turned off"
        else:
            self.setTitle("None")
            self.labelx.setText( "X")
            self.labelx.hide()
            self.labely.hide()
            self.labelz.hide()
            self.xValue.hide()
            self.yValue.hide()
            self.zValue.hide()
    
    def setupTray(self):
        FreeCAD.Console.PrintMessage( 'MyDockWidget setting tray\n')
        pass
        
    def setupStyle(self):
        style = "#constrButton:Checked {background-color: "
        style += self.getDefaultColor("constr", rgb=True) + " } "
        style += "#addButton:Checked, #delButton:checked {"
        style += "background-color: rgb(20,100,250) }"
        self.dockWidget.setStyleSheet(style)

    def displayPoint(self, point, last=None, plane=None):
        "this function displays the passed coords in the x, y, and z widgets"
        dp = point
        self.xValue.setText("%.2f" % dp.x)
        self.yValue.setText("%.2f" % dp.y)
        if self.zValue.isEnabled(): self.zValue.setText("%.2f" % dp.z)
        if self.xValue.isEnabled():
            #self.xValue.setFocus()                    #不关闭些项，按Ecaspe等键的操作便无法再使用
            self.xValue.selectAll()
        else:
            #self.yValue.setFocus()
            self.yValue.selectAll()
        
    def getDefaultColor(self, type, rgb=False):
        "gets color from the preferences or toolbar"
        if type == "snap":
            color = Base.getParam("snapcolor")
            r = ((color >> 24) & 0xFF) / 255
            g = ((color >> 16) & 0xFF) / 255
            b = ((color >> 8) & 0xFF) / 255
        elif type == "ui":
            r = float(self.color.red() / 255.0)
            g = float(self.color.green() / 255.0)
            b = float(self.color.blue() / 255.0)
        elif type == "face":
            r = float(self.facecolor.red() / 255.0)
            g = float(self.facecolor.green() / 255.0)
            b = float(self.facecolor.blue() / 255.0)
        elif type == "constr":
            color = QtGui.QColor(Base.getParam("constructioncolor") >> 8)
            r = color.red() / 255.0
            g = color.green() / 255.0
            b = color.blue() / 255.0
        else: print "draft: error: couldn't get a color for ", type, " type."
        if rgb:
            return("rgb(" + str(int(r * 255)) + "," + str(int(g * 255)) + "," + str(int(b * 255)) + ")")
        else:
            return (r, g, b)

#---------------------------------------------------------------------------
# Processing functions
#---------------------------------------------------------------------------
    def checkx(self):
        if self.yValue.isEnabled():
            self.yValue.setFocus()
            self.yValue.selectAll()
        else:
            self.checky()

    def checky(self):
        if self.zValue.isEnabled():
            self.zValue.setFocus()
            self.zValue.selectAll()
        else:
            self.validatePoint()

    def validatePoint(self):
        "function for checking and sending numbers entered manually"
        if self.sourceCmd != None:
            if self.labelx.isVisible()  and self.labely.isVisible() and self.labelz.isVisible():
                errorTags = []
                try:
                    numx = float(self.xValue.text())
                except ValueError:
                    errorTags.append('x')
                    
                try:
                    numy = float(self.yValue.text())
                except ValueError:
                    errorTags.append('y')
                    
                try:
                    numz = float(self.zValue.text())
                except ValueError:
                    errorTags.append('z')
                
                if len(errorTags) > 0:
                    msg = 'please input float for '
                    for str in errorTags:
                        msg = msg + str + ' '
                        
                    box = QtGui.QMessageBox(QtGui.QMessageBox.Critical , "ValueError" , msg)
                    box.show()
                    self.xValue.setFocus()
                    self.xValue.selectAll()
                else:    
                    self.sourceCmd.numericInput(numx, numy, numz)
            
            
            
    def setRadiusValue(self, val):
        self.radiusValue.setText("%.2f" % val)
        self.radiusValue.setFocus()
        self.radiusValue.selectAll()

#---------------------------------------------------------------------------
# Interface modes
#---------------------------------------------------------------------------

    def taskUi(self, title):
        if self.taskmode:
            self.isTaskOn = True
            FreeCADGui.Control.closeDialog()
            self.baseWidget = QtGui.QWidget()
            self.setTitle(title)
            self.layout = QtGui.QVBoxLayout(self.baseWidget)
            self.setupToolBar(task=True)
            self.retranslateUi(self.baseWidget)
            self.panel = DraftTaskPanel(self.baseWidget)
            FreeCADGui.Control.showDialog(self.panel)
        else:
            self.setTitle(title)  

    def lineUi(self):
        self.pointUi("Line")
        self.xValue.setEnabled(True)
        self.yValue.setEnabled(True)
        self.zValue.setEnabled(False)

    def pointUi(self, title= "Point"):
        self.taskUi(title)
        self.xValue.setEnabled(True)
        self.yValue.setEnabled(True)
        self.labelx.setText("X")
        self.labelx.show()
        self.labely.setText("Y")
        self.labely.show()
        self.labelz.setText("Z")
        self.labelz.show()
        self.xValue.show()
        self.yValue.show()
        self.zValue.show()
        self.xValue.setFocus()
        self.xValue.selectAll()
        
    def circleUi(self):
        self.pointUi("Circle")
        self.labelx.setText( "Center X")

    def radiusUi(self):
        self.labelx.hide()
        self.labely.hide()
        self.labelz.hide()
        self.xValue.hide()
        self.yValue.hide()
        self.zValue.hide()
        self.labelRadius.setText( "Radius")
        self.labelRadius.show()
        self.radiusValue.show()

            
#---------------------------------------------------------------------------
# TaskView operations
#---------------------------------------------------------------------------
                    
    def setWatchers(self):  # 工具栏的内容
        print "adding draft widgets to taskview..."
        class DDACreateWatcher:
            def __init__(self):
                self.commands = ["DDA_Line"]
                self.title = "Create objects"
                FreeCAD.Console.PrintMessage( 'MyDockWidget watchers init done\n')
            def shouldShow(self):
                sign = (FreeCAD.ActiveDocument != None) and (not FreeCADGui.Selection.getSelection())
                if sign:
                    FreeCAD.Console.PrintMessage( 'MyDockWidget watchers showing\n')
                return sign
        FreeCADGui.Control.addTaskWatcher([DDACreateWatcher()])  # 添加的watcher会做功能显示出来，被FreeCAD监控
        FreeCAD.Console.PrintMessage( 'MyDockWidget watchers added\n')

    def show(self):
        if not self.taskmode:
            self.dockWidget.setVisible(True)

        
    def Activated(self):
        FreeCAD.Console.PrintMessage( 'MyDockWidget activing\n')
        if self.taskmode:
            FreeCAD.Console.PrintMessage( 'MyDockWidget setting watchers\n')
            self.setWatchers()
        else:
            FreeCAD.Console.PrintMessage( 'MyDockWidget visible\n')
            self.dockWidget.setVisible(True)
            self.dockWidget.toggleViewAction().setVisible(True)

    def Deactivated(self):
        if (FreeCAD.activeDDACommand != None):
            FreeCAD.activeDDACommand.finish()
        if self.taskmode:
            FreeCADGui.Control.clearTaskWatcher()
            self.tray = None
        else:
            self.dockWidget.setVisible(False)
            self.dockWidget.toggleViewAction().setVisible(False)
        
p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DDA")
print 'fixed point color :' , p.GetUnsigned('fixedpointcolor')
print 'loading point color :' , p.GetUnsigned('loadingpointcolor')
#t = p.GetFloat("snapRange")
#print t
FreeCADGui.DDADockWidget  = MyDockWidget()