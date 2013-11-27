# coding=gbk



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


#####################################################
#
#  all shapes are inherited from classes in DDATools
#
#####################################################

from DDATools import *
try:
    from PyQt4 import QtCore, QtGui, QtSvg    
except:
    FreeCAD.Console.PrintError("Error: Python-qt4 package must be installed on your system to use the Draft module.")

import FreeCADGui
import DDADatabase
import DDADisplay
from Base import showErrorMessageBox


class BoundaryLines( Line ):
    '''
    The DDA Boundary Line definition.
    Most operations are inherited from DDATools.Line
    '''
    def __init__( self , wiremode = True ):
        Line.__init__( self , wiremode = True ,shapeType = 'BoundaryLine' , mustColse=True )
        
        
    def GetResources(self):
        return {
                'MenuText':  'BoundaryLine',
                'ToolTip': "Creates Boundary Line of DL."}
        
    def finish(self, closed=False, ifSave=True):
        Line.finish(self, closed)
        if len(DDADatabase.dl_database.boundaryNodes)>0:
            Base.__currentStep__ = 'ShapesAvailable'
            from DDAPanel import DLPanel
            DLPanel.refreshButtons()

class BorderGenerator:
    def GetResources(self):
        return {
                'MenuText':  'GenerateBorder',
                'ToolTip': "generate border for current boundary."}
    
    def drawFixedPoints(self , pts):
        '''
        draw fixed points for border
        :param pts:
        '''
        from Base import addCircles2Document
        from loadDataTools import DDAPoint
        addCircles2Document('FixedPoint', ifStore2Database=True \
                            , pts=[DDAPoint(t[0],t[1]) for t in pts], ifRecord = True)
    
    def getIntersectX(self,p1 , p2 , y):
        k1 = float(p1[1]-p2[1])/float(p1[0]-p2[0])
        b1 = p1[1]-k1*p1[0]
        print k1 , '  ' , b1
        newX1 = (y-float(b1))/float(k1)
        return newX1        
    
    def Activated(self):
        from interfaceTools import BorderCalculator
        border = BorderCalculator()

        from DDADatabase import dl_database
        boundary = dl_database.boundaryNodes
        
        assert boundary
        pts = border.calcualteBorder(boundary[0].pts)
        
        assert pts        
        
        Base.addPolyLine2Document('BorderLine' , ifStore2Database=True , pointsList=pts)
        
        # generate fixed points coordinate
        fps = range(4)
        x1 = 0.9*pts[1][0]+0.1*pts[0][0]
        x2 = 0.9*pts[4][0]+0.1*pts[5][0]
        fps[0] = (x1 , 0.9*pts[1][1]+0.1*pts[2][1])
        fps[1] = (x1 , 0.1*pts[1][1]+0.9*pts[2][1])
        fps[2] = (x2 , 0.9*pts[3][1]+0.1*pts[4][1])
        fps[3] = (x2 , 0.1*pts[3][1]+0.9*pts[4][1])
        self.drawFixedPoints(fps)
        
    def finish(self):
        pass

class TunnelBoltsGenerator:
    def GetResources(self):
        return {
                'MenuText':  'GenerateTunnelBolts',
                'ToolTip': "generate bolts for tunnel."}

    def Activated(self):
        from interfaceTools import TunnelBoltsGenerator

#        bolts = TunnelBoltsGenerator.generateBolts4Tunnel1( centerX=20.0 , centerY=50.0 
#                      , hAxesLength=10.0 , vAxesLength=8.0 \
#                      , boltLength=4.0 , boltLength2=6.0 , boltsDistance=5.0)
#        bolts2 = TunnelBoltsGenerator.generateBolts4Tunnel2( centerX=40 , centerY=50 \
#            , halfWidth=8 , halfHeight=6 , arcHeight=12 \
#            , boltLength=5 , boltLength2=7 , boltsDistance=4 )
#        bolts3 = TunnelBoltsGenerator.generateBolts4Tunnel3(centerX=80 , centerY=50 \
#                      , hAxesLength=8 , vAxesLength=9 \
#                      , cornerHeight=4 , boltLength=5 , boltLength2=4 , boltsDistance=2)
#        bolts4 = TunnelBoltsGenerator.generateBolts4Tunnel4( centerX=120 , centerY=50 \
#                      , radius=15 , cornerHeight=6 \
#                      , ifRotate=0 , boltLength=5 , boltLength2=7 , boltsDistance=4)
        
#        import Base
#        Base.addLines2Document(shapeType = 'BoltElement', ifStore2Database=True, args=bolts)
#        print len(bolts)
#        import Base
#        Base.addLines2Document(shapeType = 'BoltElement', ifStore2Database=True, args=bolts2)
#        import Base
#        Base.addLines2Document(shapeType = 'BoltElement', ifStore2Database=True, args=bolts3)
#        import Base
#        Base.addLines2Document(shapeType = 'BoltElement', ifStore2Database=True, args=bolts4)

#        box = QtGui.QMessageBox( QtGui.QMessageBox.Information , 'Information' \
#                         , 'The function to generate bolts for tunnel is available. But now the core calculation module which could calculate is testing. The funcion will come soon. Sorry for this.' , QtGui.QMessageBox.Ok) 
#        box.exec_()
#        

        from DDATools import TunnelSelectionTool , CalculateTunnelBoltsWithParameters
        dialog = TunnelSelectionTool()
        idx = dialog.select()
        if idx!=0 and idx==None:
            return
        else:
            calculator = CalculateTunnelBoltsWithParameters()
            from DDADatabase import dl_database
            calculator.calculateBolts4Tunnel(dl_database.tunnels[idx])
            calculator.exec_()
        
        
#        
#        boltsDialog = TunnelBoltsSelectionTool()
#        boltsDialog.configure(idx)
#        print 'abc'
        
    def finish(self):
        pass
    

class BoltElements( Line ):
    '''
    Draw one bolt element every time
    '''
    def __init__( self , wiremode = False , shapeType = 'BoltElement' , mustColse=False):
        Line.__init__( self , wiremode = False , shapeType = shapeType, mustColse= mustColse )
        
        
    def GetResources(self):
        return {
                'MenuText':  'AdditionalLine',
                'ToolTip': "Creates Additional Line of DL."}
                
    def Activated(self):
        Line.Activated(self)
                
    def action(self, arg):
        Line.action(self , arg)
    
    def initDialog(self):
        self.dialog = QtGui.QDialog()
        layout = QtGui.QVBoxLayout(self.dialog)
        layout2 = QtGui.QHBoxLayout(self.dialog)
        self.spinbox = QtGui.QSpinBox(self.dialog)
        self.spinbox.setRange ( 1, 10 )
        button = QtGui.QPushButton(self.dialog)
        button.setText('OK')
        layout2.addWidget(self.spinbox)
        layout2.addWidget(button)        
        label = QtGui.QLabel(self.dialog)
        label.setText('set material for bolt element :')
        layout.addWidget(label )
        layout.addLayout(layout2 )
        self.dialog.setLayout(layout)
        QtCore.QObject.connect( button , QtCore.SIGNAL("pressed()"),self.getMaterialNumber)
        QtCore.QObject.connect( button , QtCore.SIGNAL("pressed()"),self.dialog.accept)
        
    def getMaterialNumber(self):
        return self.spinbox.value()
        
    def clearDialog(self):
        self.dialog = None
        self.spinbox = None
                
    def finish(self , closed=False, ifSave=True , materialNo=1):
        flag = False
        if len(self.node)>1 :   # 绘制结束时再弹出选择材质的对话框
            FreeCAD.Console.PrintError('finishing additional line\n')
            self.initDialog()
            self.dialog.exec_()
            flag = True
            
        FreeCAD.Console.PrintError('Additional line finishing\n')
        if flag:  # 绘制结束时再存入database
            materialNo = self.getMaterialNumber()
            obj = Line.finish(self , closed , ifSave=True , materialNo=materialNo)
            assert obj            
            self.clearDialog()



class AdditionalLines( Line ):
    '''
    The DDA Boundary Line definition.
    Most operations are inherited from DDATools.Line
    '''
    
    def __init__( self , wiremode = False , shapeType = 'AdditionalLine' , mustColse=False):
        Line.__init__( self , wiremode = False , shapeType = shapeType, mustColse= mustColse )
        
        
    def GetResources(self):
        return {
                'MenuText':  'AdditionalLine',
                'ToolTip': "Creates Additional Line of DL."}
                
    def Activated(self):
        Line.Activated(self)
                
    def action(self, arg):
        Line.action(self , arg)
    
    def initDialog(self):
        self.dialog = QtGui.QDialog()
        layout = QtGui.QVBoxLayout(self.dialog)
        layout2 = QtGui.QHBoxLayout(self.dialog)
        self.spinbox = QtGui.QSpinBox(self.dialog)
        self.spinbox.setRange ( 1, 10 )
        button = QtGui.QPushButton(self.dialog)
        button.setText('OK')
        layout2.addWidget(self.spinbox)
        layout2.addWidget(button)        
        label = QtGui.QLabel(self.dialog)
        label.setText('select material Number :')
        layout.addWidget(label )
        layout.addLayout(layout2 )
        self.dialog.setLayout(layout)
        QtCore.QObject.connect( button , QtCore.SIGNAL("pressed()"),self.getMaterialNumber)
        QtCore.QObject.connect( button , QtCore.SIGNAL("pressed()"),self.dialog.accept)
        
    def getMaterialNumber(self):
        return self.spinbox.value()
        
    def clearDialog(self):
        self.dialog = None
        self.spinbox = None
                
    def finish(self , closed=False, ifSave=True , materialNo=1):
        flag = False
        if len(self.node)>1 :   # 绘制结束时再弹出选择材质的对话框
            FreeCAD.Console.PrintError('finishing additional line\n')
            self.initDialog()
            self.dialog.exec_()
            flag = True
            
        FreeCAD.Console.PrintError('Additional line finishing\n')
        if flag:  # 绘制结束时再存入database
            materialNo = self.getMaterialNumber()
            obj = Line.finish(self , closed , ifSave=True , materialNo=materialNo)
            assert obj            
            self.clearDialog()
        

class MaterialLines( AdditionalLines ):
    '''
    The DDA Boundary Line definition.
    Most operations are inherited from DDATools.Line
    '''
    
    def __init__( self , wiremode = False ,shapeType = 'MaterialLine' , mustColse=False):
        AdditionalLines.__init__( self , wiremode = False ,shapeType = shapeType , mustColse = mustColse )
        
        
    def GetResources(self):
        return {
                'MenuText':  'MaterialLine',
                'ToolTip': "Creates Material Line of DL."}
                
    def Activated(self):
        AdditionalLines.Activated(self)
                
    def action(self, arg):
        AdditionalLines.action(self , arg)

    def generateBlockName(self , index):
        '''
        generate block names
        :param index: block No.
        '''
        if index==0:
            return 'Block'
        elif index <1000:
            return 'Block%03d'%index
        else:
            return "Block%d"%index
            

    def setBlocksMat(self , nodes , material):
        '''
        set material to blocks that intersect with the line ( nodes[0] , nodes[1] )
        :param nodes: 0: start point , 1: end point
        '''
        from interfaceTools import rectSelection
        import checkConcave_and_triangulate as Py
        blocksIdxes = rectSelection.getIntersectedRectsNo(nodes[0][0], nodes[0][1], nodes[1][0], nodes[1][1])
        from DDADatabase import df_inputDatabase
        blocks = df_inputDatabase.blocks
        for idx in blocksIdxes:
            if not Py.ifSegmentAndPolygonIntersect(nodes, blocks[idx].getPoints()):
                if blocks[idx].holePointsCount==0:
                    blocks[idx].materialNo = material

        obj = FreeCAD.ActiveDocument.getObject('Block')
        obj.ViewObject.RedrawTrigger = True # trigger material changes
    
    def finish(self , closed=False, cont=False):
        tmpMaterialNo = 0
        if (not self.isWire and len(self.node) == 2) or cont == False:   # 绘制结束时再弹出选择材质的对话框
            print 'finishing material line\n'
            self.initDialog()
            self.dialog.exec_()
            tmpMaterialNo = self.getMaterialNumber()
            self.setBlocksMat(self.node, tmpMaterialNo)
            import Base
            from loadDataTools import DDALine
            Base.addLines2Document(self.shapeType, ifStore2Database = True 
                    , args=[DDALine(self.node[0] , self.node[1] ,tmpMaterialNo )] , ifTriggerRedraw=True)

            self.clearDialog()
#            FreeCADGui.runCommand('DDA_StoreBlocksMaterial')
            
        print ' line finishing'
        
        obj = Line.finish(self , closed, cont)
#        FreeCAD.ActiveDocument.removeObject(obj.Label)

#        obj.ViewObject.
#        FreeCADGui.runCommand('DDA_DCChangesConfirm')
#        todo.delay(self.doc.removeObject , obj.Label)


class JointSets(Creator):
    def __init__(self):
        self.__columnNum = 7
        self.__initWidgets()
        self.__initConnections()

        
    def __initWidgets(self):
        self.strList = QtCore.QStringList()
        self.strList<<QtCore.QString('dip')<<QtCore.QString('dip direction')<<QtCore.QString('')
    
        self.label1 = QtGui.QLabel('Slope')
        self.slopeDataTable = DataTable(1,2,self.strList , False , False)
        self.table1 = self.slopeDataTable.table
        self.table1.setColumnWidth(2 , 50)
        self.table1.setFixedSize(220,60)
        self.table1.setHorizontalHeaderLabels(self.strList)
        self.layout1 = QtGui.QVBoxLayout()
        self.layout1.addWidget(self.label1)
        self.layout1.addWidget(self.table1)
        self.__table1Valid = False
        
        self.strList2 = QtCore.QStringList()
        self.strList2<<QtCore.QString('dip')<<QtCore.QString('dip direction')<<QtCore.QString('spacing')<<QtCore.QString('length')<<QtCore.QString('bridge')<<QtCore.QString('random')<<QtCore.QString('')
        self.label2 = QtGui.QLabel('JointSet')
        self.dataTable = DataTable(1 , self.__columnNum ,self.strList2)
        self.table2 = self.dataTable.table
        self.table2.setColumnWidth(6 , 50)
        self.table2.setFixedSize(690,130)
        self.__table2Valid = False
        
        self.layout2 = QtGui.QVBoxLayout()
        self.layout2.addWidget(self.label2)
        self.layout2.addWidget(self.table2)
        
        self.layout3 = QtGui.QHBoxLayout()
        self.addButton = QtGui.QPushButton('Add JointSet')
        self.viewButton = QtGui.QPushButton('ViewResult')
        self.viewButton.setEnabled(False)
        self.layout3.addWidget(self.addButton)
        self.layout3.addWidget(self.viewButton)
        
        self.layout4 = QtGui.QVBoxLayout()
        self.layout4.addLayout(self.layout1)
        self.layout4.addLayout(self.layout2)
        self.layout4.addLayout(self.layout3)
        
        self.mainWidget = QtGui.QWidget()
        self.mainWidget.setLayout(self.layout4)
        
    def __initConnections(self):
        QtCore.QObject.connect(self.viewButton, QtCore.SIGNAL("pressed()"), self.viewResult)
        QtCore.QObject.connect(self.addButton, QtCore.SIGNAL("pressed()"), self.addRow)
        self.slopeDataTable.dataInvalidSignal.connect(self.checkTable1)
        self.dataTable.dataInvalidSignal.connect(self.checkTable2)

    def __addDelButton4Row(self, row):
        'add the del button for the row'
        self.dataTable.addDelButton4Row(row)
        
    def IsSlopeTableBlank(self):
        try:
            a = float(self.table1.item(0,0).text())
            b = float(self.table1.item(0,1).text())
        except:            
            return True         
    
    def checkTable1(self , flag):
        self.__table1Valid = flag
        self.confirmPreviewButton()
    
    def checkTable2(self , flag):
        self.__table2Valid = flag
        self.confirmPreviewButton()

    def confirmPreviewButton(self):
        if self.__table1Valid and self.__table2Valid:
            self.viewButton.setEnabled(True)
        else:
            self.viewButton.setEnabled(False)

    def saveSlope(self):
        database = DDADatabase.dl_database
        database.slope = []
        a = float(self.table1.item(0,0).text())
        b = float(self.table1.item(0,1).text())
        database.slope.append((a , b))
        print 'get slope : ' , (a ,b )
        
    def saveJointSets(self):
        database = DDADatabase.dl_database
        database.jointSets = []        
        array = [1,2,3,4,5,6]
        for i in range( self.table2.rowCount()) :
            try:
                for j in range(6):
                    array[j] = float(self.table2.item(i,j).text())
            except:  # 出现错误，因为格是空的，跳过这一行
                continue
                
            tuple = (array[0],array[1],array[2],array[3],array[4],array[5])
            database.jointSets.append(tuple)
            print 'get joint :' , tuple
                
                
    def save2Database(self):
        self.saveSlope()
        self.saveJointSets()

    def viewResult(self):
        print '#############################\n############  preview##########\n#####################\n'
#        FreeCADGui.runCommand('DDA_CheckSaveJointSetsAndTunnels')
#        if not DDACheckSaveJointSetsAndTunnels.isDataValid() :
#            return
#        FreeCADGui.runCommand("DDA_StoreData")
#        FreeCADGui.DDADisplayCmd.preview()

        import Base
        re = Base.showWaringMessageBox('Warning', 'Joint lines will calculated again. All changes made manually will be lost, are your sure?')

        if re== QtGui.QMessageBox.Ok:
            FreeCADGui.runCommand('DDA_DLCalculate')
            
    def checkTable(self):
        print 'JointSets begin check data'
        return self.slopeDataTable.checkTable() and self.dataTable.checkTable()
               
    def addRow(self):
        self.dataTable.addRow()

    def show(self):
        self.mainWidget.show()
        
    def GetResources(self):
        return {
                'MenuText':  'JointSet',
                'ToolTip': "manage joint sets of DL."}
                
    def Activated(self, name="None"):
        FreeCAD.Console.PrintMessage( 'Joint Set activing\n')
        if FreeCAD.activeDDACommand:
            FreeCAD.activeDDACommand.finish()
        
        #dlDatabase = DDADatabase.dl_database
        self.mainWidget.show()
        
    def finish(self):
        self.mainWidget.hide()

class Tunnels(Creator):
    def __init__(self):
        self.__columnNum = 8
        self.__initWidgets()
        self.__initConnections()
        
    def __initWidgets(self):
        self.headers = ['Type' , 'a' , 'b' , 'c' , 'r' , 'centerX' , 'centerY','']
        self.label = QtGui.QLabel('Tunnel')
        self.dataTable = DataTable(1 , self.__columnNum , self.headers , True)
        self.table = self.dataTable.table
#        self.table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)  #一次只能选单个目标
        self.table.setColumnWidth(0 , 50)
        self.table.setColumnWidth(7 , 50)
        self.table.setFixedSize(740,130)        

        self.layout2 = QtGui.QHBoxLayout()
        self.addButton = QtGui.QPushButton('Add Tunnel')
        self.previewButton = QtGui.QPushButton('ViewResult')
        self.previewButton.setEnabled(False)
        self.layout2.addWidget(self.addButton)
        self.layout2.addWidget(self.previewButton)
        
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.table)
        self.layout.addLayout(self.layout2)
        
        self.mainWidget = QtGui.QWidget()
        self.mainWidget.setLayout(self.layout)    

    def __initConnections(self):
        QtCore.QObject.connect(self.previewButton, QtCore.SIGNAL("pressed()"), self.preview)
        QtCore.QObject.connect(self.addButton, QtCore.SIGNAL("pressed()"), self.addRow)
        self.dataTable.dataInvalidSignal.connect(self.confirmPreviewButton)
#        self.dataTable.saveDataSignal.connect(self.save2Database)

        
    def confirmPreviewButton(self , flag):
        self.previewButton.setEnabled(flag)

    def checkTable(self):
        print 'Tunnels begin check data'
        return self.dataTable.checkTable()

    def preview(self):
        print '#############################\n############  preview##########\n#####################\n'
        
        import Base
        re = Base.showWaringMessageBox('Warning', 'Joint lines will calculated again. All changes made manually will be lost, are your sure?')

        if re== QtGui.QMessageBox.Ok:
            FreeCADGui.runCommand('DDA_DLCalculate')
        
    def save2Database(self):
        database = DDADatabase.dl_database
        database.tunnels = []        
        
        array = [1,2,3,4,5,6,7]
        for i in range( self.table.rowCount() ):
            try:
                for j in range(1,7):
                    array[j] = float(self.table.item(i,j).text())
            except:
                continue
            
            tuple = (self.table.cellWidget(i,0).currentIndex()+1,array[1],array[2],array[3],array[4],array[5],array[6])
            print 'new tunnel : ' , tuple
            database.tunnels.append(tuple)
                 
    def addRow(self):
        self.dataTable.addRow()

    def show(self):
        self.mainWidget.show()
        
    def GetResources(self):
        return {
                'MenuText':  'Tunnel',
                'ToolTip': "Manage Tunnel of DL."}
                
                
    def Activated(self, name="None"):
        FreeCAD.Console.PrintMessage( 'Tunnel activing\n')
        if FreeCAD.activeDDACommand:
            FreeCAD.activeDDACommand.finish()
        
        FreeCAD.activeDDACommand = self
#        Creator.Activated(self)
        #dlDatabase = DDADatabase.dl_database
        self.mainWidget.show()
        
    def finish(self):
        self.mainWidget.hide()
        
class CheckSaveJointSetsAndTunnels():
    '''
    检测并保存  joint sets 和 tunnels ， 隐形命令，中介工具，不用database与jointSet和tunnel类直接打交道，又完成功能
    '''
    
    def __init__(self):
        self.valid = False
    
    def GetResources(self):
        return {
                'MenuText':  'SaveJointSetsAndTunnels',
                'ToolTip': "save joint sets and tunnels."}
 
    def Activated(self):
        '''
        这个命令是工具，不要清除其它命令
        '''
        print 'begin check validation joint sets and tunnels'
        self.valid = True
        if not DDAJointSets.checkTable():
            self.valid = False
            showErrorMessageBox('Input Error' , 'JointSets data unvalid.\nPlease correct it first.')
        else:
            if DDAJointSets.IsSlopeTableBlank():
                Base.showErrorMessageBox('InputError', 'slope data not found .\nPlease input it first.')
                self.valid = False
            else:
                DDAJointSets.save2Database()
            
        if not DDATunnels.checkTable():
            self.valid = False
            showErrorMessageBox('Input Error' , 'Tunnels data unvalid.\nPlease correct it first.')
        else:
            DDATunnels.save2Database()
        
    def isDataValid(self):
        return self.valid
    
    def finish(self):
        pass

            
class StoreBlocksMaterial:
    def GetResources(self):
        return {
                'MenuText':  'StoreBlocksMaterial',
                'ToolTip': "save joint sets and tunnels."}
 
    def getBlocksMaterial(self):
        '''
        scan objects of FreeCAD and then get blocks' material
        '''
        from Base import __blocksMaterials__
        return __blocksMaterials__
        
    def storeBlocksMaterial(self, materials):
        
        assert materials
        
        filename = Base.__currentProjectPath__+'/data.df'
        
        file = open( filename , 'rb')
        f = file.read(-1)
        lines = f.split('\n')
        for i in range(len(lines)):
            lines[i]  = lines[i].strip()
        file.close()
        
        from loadDataTools import BaseParseData
        parseData = BaseParseData()
        blocksNum = parseData.parseIntNum(lines[0].split()[0])
        print 'blocksNum: ' , blocksNum
        
        for i in range(blocksNum):
            ss = lines[i+2].split()
            ss[0] = str(materials[i])
            lines[i+2] = '%s %s %s'%(ss[0] , ss[1] , ss[2])
        
        file = open( filename , 'wb')
        file.write('\n'.join(lines))
        file.close()
 
    def Activated(self):
        '''
        scan objects of FreeCAD and then store blocks material
        '''
        materials = self.getBlocksMaterial()
        self.storeBlocksMaterial(materials)
        
    def finish(self):
        pass
        
        

            
class FixedPoint(Circle):
    def __init__(self, shapeType = 'FixedPoint'):
        Circle.__init__(self , shapeType)
        
    def GetResources(self):
        return {
                'MenuText':  'FixedPoint',
                'ToolTip': "Creates Fixed Point of DL."}
 
    def Activated(self):
        Circle.Activated(self)
                
    def action(self, arg):
        Circle.action(self , arg)    
        
class LoadingPoint(Circle):
    def __init__(self, shapeType = 'LoadingPoint'):
        Circle.__init__(self , shapeType)
        
    def GetResources(self):
        return {
                'MenuText':  'LoadingPoint',
                'ToolTip': "Creates Loading Point of DL."}
 
    def Activated(self):
        Circle.Activated(self)
                
    def action(self, arg):
        Circle.action(self , arg)    
    
class MeasuredPoint(Circle):
    def __init__(self, shapeType = 'MeasuredPoint'):
        Circle.__init__(self , shapeType)
        
    def GetResources(self):
        return {
                'MenuText':  'MeasuredPoint',
                'ToolTip': "Creates Measured Point of DL."}
 
    def Activated(self):
        Circle.Activated(self)
                
    def action(self, arg):
        Circle.action(self , arg)    

class HolePoint(Circle):
    def __init__(self, shapeType = 'HolePoint'):
        Circle.__init__(self , shapeType)
        
    def GetResources(self):
        return {
                'MenuText':  'HolePoint',
                'ToolTip': "Creates Hole Point of DL."}
 
    def Activated(self):
        Circle.Activated(self)
                
    def action(self, arg):
        Circle.action(self , arg)    
        
    def finish(self):
        if self.center:
            import Base
            view=FreeCADGui.ActiveDocument.ActiveView
            obj = view.getObjectInfo(view.getCursorPos())
            objName , objIdx = Base.getRealTypeAndIndex(obj['Object'])
            assert objName == 'Block'
            subName , subIdx = Base.getRealTypeAndIndex(obj['Component'])
            from DDADatabase import df_inputDatabase
            df_inputDatabase.blocks[subIdx-1].materialNo=11
            df_inputDatabase.blocks[subIdx-1].holePointsCount+=1
#            Base.__blocksMaterials__[subIdx-1] = 11 # white color, same to the background
            FreeCAD.ActiveDocument.getObject('Block').ViewObject.RedrawTrigger=1 # trigger colors changes
            print 'Block with hole point hided'
            
            
            ###############################
            # temporary code , for speech
            
            fps = df_inputDatabase.fixedPoints
            if len(fps)>0:
                if subIdx-1 < fps[0].blockNo:
                    for p in fps:
                        p.blockNo -=1
            
            # tepmorary code ends
            ###############################
            
        super(HolePoint,self).finish()

class ShapeModifierBase(object):
    def __init__(self,shapeType='ShapeModifierBase'):
        super(ShapeModifierBase , self).__init__()
        self.shapeType = shapeType
        self.docName = None
        self.objName = None
        self.subElement = None

    def Activated(self):
        pass

    def finish(self):
        pass
#        super(ShapeModifierBase , self).finish()
#        FreeCADGui.Selection.clearSelection()
#        Base.recomputeDocument()

        
class ShapeModifierTrigger(ShapeModifierBase):
    '''
    this class will trigger  relevant modifier to shapes.
    For example, trigger CircleModifier to HolePoint
    '''
    def __init__(self , shapeType='ShapeModifierTrigger'):
        super(ShapeModifierTrigger , self).__init__(shapeType)
        
    def GetResources(self):
        return {
                'MenuText':  'ShapeModifierTrigger',
                'ToolTip': "Trigger relevant shape modifier."}
        
         
    def Activated(self):
        super(ShapeModifierTrigger , self).Activated()
        import Base
        if Base.__currentStage__ != 'DL' : # not 'DL' stage
            print Base.__currentStage__
            self.finish() 
            return
        
        
        sels=FreeCADGui.Selection.getSelectionEx()
        if len(sels)!=1  : # select more than 2 objects
            return
        s = sels[0]
        count = 0
        for subName in sels[0].SubElementNames:
            if 'Edge' in subName :  # FreeCAD may get error object selected, this code confirm the object is valid
                count+=1
        if count>1 :
            return 
        
        if s.ObjectName=='ShapeMover' or s.ObjectName=='ShapeModifier':
            return
        
        import Base
        obj = sels[0].Object
        name , idx = Base.getRealTypeAndIndex(obj.Label)    
        print 'trigger modifier for %s --> %d'%(name , idx)

        self.docName = s.DocumentName
        self.objName = s.ObjectName
        self.subElement = s.SubElementNames[0]
        Base.__shapeBeModifying__ = [self.docName , self.objName , self.subElement]
        print 'prepare done in ShapeModifierTrigger'
        
        if name=='JointLine':
            FreeCADGui.runCommand('DDA_JointLineModifier')
            
class LineModifier(Creator):
    def __init__(self , shapeType='LineModifier'):
        super(LineModifier,self).__init__(shapeType)
        from DDATools import lineTracker
        self.p1 = None
        self.p2 = None
        self.docName = None
        self.objName = None
        self.subElement = None
        self.owner = None
            
    def GetResources(self):
        return {
                'MenuText':  'LineModifier',
                'ToolTip': "Modify 1 line."}
 
    def Activated(self):   
        print 'LineModifier Activating'
        super(LineModifier,self).Activated()
        self.linetrack = lineTracker()
        print '\t\t\t ========= line track', self.linetrack
        obj = FreeCAD.ActiveDocument.getObject('ShapeModifier')
        assert obj
        self.docName = obj.RelatedDocumentName
        self.objName =  obj.RelatedObjectName
        self.subElement =  obj.RelatedSubElement
        assert self.p1
        assert self.p2
        self.startTracking()
        self.call = self.view.addEventCallback("SoEvent", self.action)
        
    def setPoints(self , p1 , p2 ):
        self.p1 = p1
        self.p2 = p2
        
    def startTracking(self):
        self.linetrack.p1(self.p1)
        self.linetrack.p2(self.p2)
        self.linetrack.on()
        
    def refreshPoints(self):
        self.linetrack.p2(self.p2)
#        print self.p1 ,' <---> ',self.p2
        
    def action(self, arg):
        if arg["Type"] == "SoKeyboardEvent":
            FreeCAD.Console.PrintMessage('keyboardEvent')
            if arg["Key"] == "ESCAPE":
                FreeCAD.Console.PrintError('Escape pressed, finising\n')
                self.finish()
        elif arg["Type"] == "SoLocation2Event":  # mouse movement detection
            point, ctrlPoint = getPoint(self, arg)
#                self.ui.cross(True)
            self.p2 = point
            self.refreshPoints()
                
        elif arg["Type"] == "SoMouseButtonEvent":
            if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):# left button
                print 'LineModifier left button clicked'
                self.saveResult()
                self.finish()
            if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):# right button
                self.finish()

    def saveResult(self):
        if not self.p1 or not self.p2:
            print 'data unvalid in JointLineModifier. finishing. '
            assert False
            return 
        if self.shapeType=='LineModifier':
            self.owner.saveResult(self.p1 , self.p2)
        elif self.shapeType=='LineMover':
            subVector = self.p2 - self.p1
            p1 = self.originP1 + subVector
            p2 = self.originP2 + subVector            
            self.owner.saveResult(p1 , p2)
                     
    def finish(self):
        print 'LineModifier finish'
        if self.linetrack:
            self.linetrack.finalize()
            self.linetrack = None
            super(LineModifier,self).finish()
#        self.owner.finish()
            import Base
            Base.removeShapeModifier()
            Base.removeShapeMover()
        self.p1 = None
        self.p2 = None
        
class JointLineModifier(ShapeModifierBase):
    def __init__(self , shapeType='JointLineModifier'):
        super(JointLineModifier,self).__init__(shapeType)
        self.lineModifier = None
        self.__selectedAssistantNodeName = None
        
    def GetResources(self):
        return {
                'MenuText':  'JointLineModifier',
                'ToolTip': "Modify 1 joint line."}

    def Activated(self):
        print 'JointLineModifier Activating'
        if self.lineModifier:
            del self.lineModifier
        self.lineModifier = None
        self.getPointsAndCreateNodes()
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.call = self.view.addEventCallback("SoEvent", self.action)
        
    def __checkClickValid(self):
        view=FreeCADGui.ActiveDocument.ActiveView
        objs = view.getObjectsInfo(view.getCursorPos())
        if not objs or len(objs)==0: # click on blank
            print 'click on blank in ', self.shapeType
            return False

        findNeededShape = False        
        getOriginalObject = False        
        for obj in objs:
            if obj['Document']==self.docName and obj['Object']==self.objName \
                     and obj['Component']==self.subElement : # get original object
                print 'get original object in ' , self.shapeType
                getOriginalObject = True
            if  obj['Object']=='ShapeModifier' or obj['Object']=='ShapeMover':
                print 'get needed object in ' , self.shapeType
                findNeededShape = True
        return findNeededShape and getOriginalObject

    def action(self, arg):
        if arg["Type"] == "SoKeyboardEvent":
            FreeCAD.Console.PrintMessage('keyboardEvent')
            if arg["Key"] == "ESCAPE":
                FreeCAD.Console.PrintError('Escape pressed, finising\n')
                self.finish()
        elif arg["Type"] == "SoMouseButtonEvent":
            if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):# left button
                view=FreeCADGui.ActiveDocument.ActiveView
                obj = view.getObjectInfo(view.getCursorPos())
                if not self.__checkClickValid(): # click unvalid
                    print 'click on other object or blank section, exiting'
                    self.finish()
                    self.clearAssistanceNodes()
                    return
                
                p1 , p2 = self.getPoints()
                assert p1 
                assert p2
                if self.__selectedAssistantNodeName == 'ShapeModifier':
                    self.lineModifier = LineModifier()
                elif self.__selectedAssistantNodeName == 'ShapeMover':
                    self.lineModifier = LineMover()
                else:
                    raise
                
                print '\t\t\t line Modifier : ' ,self.lineModifier
                
                self.lineModifier.owner = self
                self.lineModifier.setPoints(p1, p2)                
                print p1 , p2
                print 'JointLineModifier start LineModifier tracking'
                self.finish()
                self.lineModifier.Activated()
            elif (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON2"):# left button
                self.finish()

    def clearAssistanceNodes(self):
        import Base
        Base.__clearShapeModifyingNodes__ = True
        Base.hideShapeModifier()
        Base.hideShapeMover()
        print 'hide assist nodes in JointLineModifier'

    def getPoints(self):
        view=FreeCADGui.ActiveDocument.ActiveView
        objs = view.getObjectsInfo(view.getCursorPos())
        obj = None
        for o in objs:
            if o['Object']=='ShapeModifier' or o['Object']=='ShapeMover':
                obj = o
                break
        self.__selectedAssistantNodeName = obj['Object']
        assert obj
        name , idx = Base.getRealTypeAndIndex(obj['Object'])
        print 'jointline modifier triggered by %s -> %d'%(name,idx)
        pName , pIdx = Base.getRealTypeAndIndex(obj['Component'])
        print 'jointline modifier triggered by subelement %s -> %d'%(pName,pIdx)
        object = FreeCAD.getDocument(self.docName).getObject(self.objName)
        subName , subIdx = Base.getRealTypeAndIndex(self.subElement)
        print 'jointline modifier selected sub line %s -> %d'%(subName,subIdx)

        from DDADatabase import dc_inputDatabase
        from loadDataTools import DDALine
        tmpLine = dc_inputDatabase.jointLines[subIdx-1]

        p1 = None 
        p2 = None
        if pIdx==2:
            p1 = FreeCAD.Vector(tmpLine.startPoint)
            p2 = FreeCAD.Vector(tmpLine.endPoint)
        else:  
            # pIdx==1 maybe ShapeMover or ShapeModifier, 
            # but ShapeMover doesn't care about order of p1 and p2
            p1 = FreeCAD.Vector(tmpLine.endPoint)
            p2 = FreeCAD.Vector(tmpLine.startPoint)
        return p1 , p2
            
    def createAssistanceNodes(self, p1 , p2 , mid):
        if self.docName==None or self.objName==None or self.subElement==None:
            print 'data unvalid, stop assistance node in ', self.shapeType
            return
        Base.addShapeMover( self.docName , self.objName , self.subElement , mid)
        Base.addShapeModifier(  self.docName , self.objName , self.subElement , p1, p2)
        
    def getPointsAndCreateNodes(self):
        import Base
        sel = Base.__shapeBeModifying__
        self.docName = sel[0]
        self.objName = sel[1]
        self.subElement = sel[2]
        subName , subIdx = Base.getRealTypeAndIndex(self.subElement)
        obj = FreeCAD.ActiveDocument.getObject(self.objName)
        from DDADatabase import dc_inputDatabase
        line = dc_inputDatabase.jointLines[subIdx-1]
        p1 = line.startPoint
        p2 = line.endPoint
        mid = FreeCAD.Vector((p1[0]+p2[0])/2 , (p1[1]+p2[1])/2 , 0)
        self.createAssistanceNodes(p1, p2, mid)
        
    def finish(self):
        super(JointLineModifier,self).finish()
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)
            self.call = None
        if self.view:
            self.view = None
        print 'JointLineModifier finish'
    
    def saveResult(self , p1 , p2):
        obj = FreeCAD.getDocument(self.docName).getObject(self.objName)
        assert obj
        if not p1 or not p2:
            print 'data unvalid in JointLineModifier. finishing. '
            return 
        import Base
        print 'p1 : ' , p1 , ' p2 : ', p2 , ' in JointLineModifier.finish'
        objName , objNo = Base.getRealTypeAndIndex(self.objName)
        subName , subIdx = Base.getRealTypeAndIndex(self.subElement)

        from DDADatabase import dc_inputDatabase
        from loadDataTools import DDALine
        tmpLine = dc_inputDatabase.jointLines[subIdx-1]
        sp = (p1[0] , p1[1] , 0)
        ep = (p2[0] , p2[1] , 0)
        dc_inputDatabase.changeVertices('JointLine', [subIdx-1]\
                    , [DDALine(sp,ep,tmpLine.materialNo)] , ifRecord=True)

        self.clearAssistanceNodes()
        obj.ViewObject.RedrawTrigger = True
        print 'JointLineModifier save result successfully. '


class LineMover(LineModifier):

    def __init__(self , shapeType='LineMover'):
        super(LineMover,self).__init__(shapeType)
        self.linetrack2 = lineTracker()
        print 'linetrack2 added'
        self.originP1 = None
        self.originP2 = None
        
    def GetResources(self):
        return {
                'MenuText':  'LineMover',
                'ToolTip': "Move line."}
 
    def Activated(self):   
        super(LineMover,self).Activated()
        print 'Activated in ', self.shapeType
        
    def setPoints(self , p1 , p2 ):
        self.originP1 = p1
        self.originP2= p2
        self.p1 =  self.p2 = (p1+p2).multiply(0.5)
        
    def refreshPoints(self):
        self.linetrack.p2(self.p2)
        subVector = self.p2.sub(self.p1)
        self.linetrack2.p1(self.originP1.add(subVector))
        self.linetrack2.p2(self.originP2.add(subVector))
        
    def startTracking(self):
        self.linetrack.p1(self.p1)
        self.linetrack.p1(self.p2)
        self.refreshPoints()
        self.linetrack.on()
        self.linetrack2.on()
        self.iftracking = True
            
    def finish(self):
        if self.linetrack2:
            self.linetrack2.finalize()
            self.linetrack2 = None
            super(LineMover,self).finish()
        self.originP1 = None
        self.originP2 = None
        
#class JointLineMover(JointLineModifier):
#    def __init__(self , shapeType='JointLineMover'):
#        super(JointLineMover).__init__(self,shapeType)
#        
#    def GetResources(self):
#        return {
#                'MenuText':  'JointLineMover',
#                'ToolTip': "Modify 1 joint line."}
#
#    def Activated(self):
#        print 'JointLineModifier Activating'
#        self.lineModifier = LineMover()
#        self.lineModifier.owner = self
#        self.getPointsAndCreateNodes()
#        self.view = FreeCADGui.ActiveDocument.ActiveView
#        self.call = self.view.addEventCallback("SoEvent", self.action)
#        
#    def action(self, arg):
#        super(JointLineMover,self).action(arg)
#        
#    def getPoints(self):
#        view=FreeCADGui.ActiveDocument.ActiveView
#        objs = view.getObjectsInfo(view.getCursorPos())
#        obj = None
#        for o in objs:
#            if o['Object'] =='ShapeMover':
#                obj = o
#                break
#        assert obj
#        name , idx = Base.getRealTypeAndIndex(obj['Object'])
#        print obj['Object']    
#        print 'jointline mover for %s -> %d'%(name,idx)
#        pName , pIdx = Base.getRealTypeAndIndex(obj['Component'])
#        print obj['Component']
#        print 'jointline mover for subelement %s -> %d'%(pName,pIdx)
#        object = self.doc.getObject(self.objName)
#        pts = object.ViewObject.Points
#        subName , subIdx = Base.getRealTypeAndIndex(self.subElement)
#        print 'jointline mover selected sub linet %s -> %d'%(subName,subIdx)
#        originP1 = None
#        originP2 = None
#        originP1 = pts[2*(subIdx-1)]
#        originP2 = pts[2*(subIdx-1)+1]
#        return originP1 , originP2
#
#    def finish(self):
#        super(JointLineMover,self).finish() 
#               
#    def saveResult(self , p1 , p2):
#        super(JointLineMover,self).finish()
#        obj = FreeCAD.getDocument(self.docName).getObject(self.objName)
#        pts = obj.ViewObject.Points
#        if not self.p1 or not self.p2:
#            print 'data unvalid in JointLineMover. finising. '
#            return 
#        import Base
#        subName , subIdx = Base.getRealTypeAndIndex(self.subElement)
#        subVector = self.p2 - self.p1
#        pts[2*(subIdx-1)] = self.originP1 + subVector
#        pts[2*(subIdx-1)+1] = self.originP2 + subVector
#        obj.ViewObject.Points = pts 
#        print 'JointLineMover finishes successfully. '
    
    
class CircleMover(ShapeModifierBase):
    def __init__(self , shapeType='CircleMover'):
        super(CircleMover,self).__init__(shapeType)
        
    def GetResources(self):
        return {
                'MenuText':  'CircleMover',
                'ToolTip': "Move circle."}

    def Activated(self):   
        super(CircleMover,self).Activated() 
                
                
DDAJointSets = JointSets()
DDATunnels = Tunnels()
DDACheckSaveJointSetsAndTunnels = CheckSaveJointSetsAndTunnels()

FreeCADGui.addCommand('DDA_ShapeModifierTrigger', ShapeModifierTrigger())
FreeCADGui.addCommand('DDA_JointLineModifier', JointLineModifier())
FreeCADGui.addCommand('DDA_GenerateBorder', BorderGenerator())
FreeCADGui.addCommand('DDA_GenerateTunnelBolts', TunnelBoltsGenerator())
FreeCADGui.addCommand('DDA_BoundaryLine', BoundaryLines())
FreeCADGui.addCommand('DDA_AdditionalLine', AdditionalLines())
FreeCADGui.addCommand('DDA_MaterialLine', MaterialLines())
FreeCADGui.addCommand('DDA_JointSet', DDAJointSets )
FreeCADGui.addCommand('DDA_Tunnel', DDATunnels)
FreeCADGui.addCommand('DDA_FixedPoint', FixedPoint())
FreeCADGui.addCommand('DDA_LoadingPoint', LoadingPoint())
FreeCADGui.addCommand('DDA_MeasuredPoint', MeasuredPoint())
FreeCADGui.addCommand('DDA_HolePoint', HolePoint())
FreeCADGui.addCommand('DDA_CheckSaveJointSetsAndTunnels' , DDACheckSaveJointSetsAndTunnels)
FreeCADGui.addCommand('DDA_StoreBlocksMaterial' , StoreBlocksMaterial())
#FreeCADGui.addCommand('DDA_Table', TestTable())