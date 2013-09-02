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

import os
import time
import FreeCADGui , FreeCAD
from FreeCAD import Base
from pivy import coin
from PyQt4 import QtCore , QtGui

from ui_DF import Ui_Dialog
from ui_DFCalcProcess import Ui_DF_Calculation
#from loadDataTools import ParseDFData
from Base import showErrorMessageBox , __currentProjectPath__ , __workbenchPath__
from DDATools import DataTable
from DDAPanel import __currentDDAPanel__
import PyDDA

tmpCount = 0


class Ui_DFConfigurationPanel(QtGui.QDialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.initUI()
        
    def initUI(self):
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
class Ui_DFCalculationProcess(QtGui.QWidget):
    '''
    DF Calculation Process 
    '''
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.initUI()
    
    def initUI(self):
        self.ui = Ui_DF_Calculation()
        self.ui.setupUi(self)
        self.ui.pushButton.pressed.connect(self.printNum)
        
    def printNum(self):
        print 'Cancel button pressed'
        
class Ui_DFMatParaConfigPanel(QtGui.QWidget):
    '''
    DF Material Parameters Configuration Panel
    '''
    def __init__(self , rowsBlocks , rowsLoadingPoints , rowsJoints ,parent = None):
        self.rowsBlocks = rowsBlocks
        self.rowsLoadingPoints = rowsLoadingPoints
        self.rowsJoints = rowsJoints
        QtGui.QWidget.__init__(self,parent)
        self.__initUI()
        
    def ifMatConfigPanelOK(self):
        '''
        check if 3 tables's data is valid
        '''
        return self.dataTableBLocksMats.checkTable() and self.dataTableJointsMats.checkTable() \
            and self.dataTableLoadingPointsMats.checkTable()
        
    def __initUI(self):
        from DDADatabase import df_inputDatabase
        
        headers = ['mass','wx','wy','elasticity\nmodule','Poisson\'s\n ratio','stress\nxx','stress\nyy'\
                   ,'stress\nxy','friction\nangle','cohesion','extension\nstrength','speedX','speedY','speedR']
        VHeaders = list(df_inputDatabase.blockMatCollections)
        VHeaders.sort()
        for i ,t in enumerate(VHeaders): VHeaders[i] = str(t)
        self.label1 = QtGui.QLabel('Block Materials \n(only used material No. shown)')
        self.dataTableBLocksMats = DataTable( self.rowsBlocks , len(headers) ,headers , False , False,80,VHeaders)
        self.tableBLocksMats = self.dataTableBLocksMats.table
        self.tableBLocksMats.setFixedSize(1180,150)
        layout1 = QtGui.QVBoxLayout()
        layout1.addWidget(self.label1)
        layout1.addWidget(self.tableBLocksMats)
        
        headers2 = ['friction\nangle','cohesion','extension\nstrength']
        VHeaders2 = list(df_inputDatabase.jointMatCollections)
        VHeaders2.sort()
        for i ,t in enumerate(VHeaders2): VHeaders2[i] = str(t)
        self.label2 = QtGui.QLabel('Joint Materials\n(only used material No. shown)')
        self.dataTableJointsMats = DataTable(self.rowsJoints , len(headers2) ,headers2 , False , False,80,VHeaders2)
        self.tableJointsMats = self.dataTableJointsMats.table
        self.tableJointsMats.setFixedSize(300,150)
        layout2 = QtGui.QVBoxLayout()
        layout2.addWidget(self.label2)
        layout2.addWidget(self.tableJointsMats)
        
        headers3 = ['start\ntime','stressX','stressY','end\ntime','stressX','stressY']
        VHeaders3 = range(1,len(df_inputDatabase.loadingPoints)+1)
        for i ,t in enumerate(VHeaders3): VHeaders3[i] = str(t)
        self.label3 = QtGui.QLabel('Loading Points Parameters')
        self.dataTableLoadingPointsMats = DataTable(self.rowsLoadingPoints , len(headers3) ,headers3 , False , False,80,VHeaders3)
        self.tableLoadingPointsMats = self.dataTableLoadingPointsMats.table
        self.tableLoadingPointsMats.setFixedSize(520,150)
        layout3 = QtGui.QVBoxLayout()
        layout3.addWidget(self.label3)
        layout3.addWidget(self.tableLoadingPointsMats)
        
        layout4 = QtGui.QHBoxLayout()
        layout4.addLayout(layout2)
        layout4.addLayout(layout3)
        
        self.blockMatWidget = QtGui.QWidget()
        self.blockMatWidget.setLayout(layout1)
        
        self.otherMatsWidget = QtGui.QWidget()
        self.otherMatsWidget.setLayout(layout4)
        
        self.label5 = QtGui.QLabel('Blocks\' Materials')
        self.btn_configBlocks = QtGui.QPushButton('Configure')
        layout5 = QtGui.QVBoxLayout()
        layout5.addWidget(self.label5)
        layout5.addWidget(self.btn_configBlocks)
        
        self.label6 = QtGui.QLabel('Joints\' and Loading Points\' Materials')
        self.btn_configOthers = QtGui.QPushButton('Configure') 
        layout6 = QtGui.QVBoxLayout()
        layout6.addWidget(self.label6)
        layout6.addWidget(self.btn_configOthers)

        layout7 = QtGui.QVBoxLayout()
        layout7.addLayout(layout5)
        layout7.addLayout(layout6)
        self.setLayout(layout7)
        self.btn_configBlocks.pressed.connect(self.blockMatWidget.show)
        self.btn_configOthers.pressed.connect(self.otherMatsWidget.show)

class DFCalculation:
    '''
    process DF
    '''
    def __init__(self):
        self.current_path = __workbenchPath__
        self.origin_path = os.getcwd()
        self.dataParser = None
        self.__initConfigUI()
        self.__initConnections()
        self.__enableConfigPanel(False)
                
        
    def __initConfigUI(self):
        '''
        init the DF configuration Panel
        '''
        self.configUI = Ui_DFConfigurationPanel()
        self.matConfigUI = None
        
    def __initMatConfigUI(self):
        if self.matConfigUI:
            self.configUI.ui.btn_Config.pressed.disconnect(self.matConfigUI.show)
        
        import Base
        
        from DDADatabase import df_inputDatabase
        self.matConfigUI = Ui_DFMatParaConfigPanel(len(df_inputDatabase.blockMatCollections) \
                    , self.dataParser.loadingPointsNum, len(df_inputDatabase.jointMatCollections) )
        
        self.configUI.ui.btn_Config.pressed.connect(self.matConfigUI.show)        
        
        
    def __initConnections(self):
        '''
        init connections in self.configUI.ui
        '''
        self.configUI.ui.btn_ReadPara.pressed.connect(self.__readParameters)
        self.configUI.ui.btn_ReadData.pressed.connect(self.__readBlocksData)
        self.configUI.ui.btn_Calc.pressed.connect(self.__calculateDF)
    
    def __enableConfigPanel(self , flag):
        print 'set configuration panel : ' , flag
        self.configUI.ui.btn_ReadPara.setEnabled(flag)
        self.configUI.ui.btn_Config.setEnabled(flag)
        self.configUI.ui.btn_Calc.setEnabled(flag)
        self.configUI.ui.doubleSpinBox_IFStatic.setEnabled(flag)
        self.configUI.ui.spinBox__NumStep.setEnabled(flag)
        self.configUI.ui.spinBox_Ratio.setEnabled(flag)
        self.configUI.ui.spinBox_timeInterval.setEnabled(flag)
        self.configUI.ui.spinBox_SpringStiffness.setEnabled(flag)
        self.configUI.ui.spinBox_SOR.setEnabled(flag)

    
    def __readBlocksData(self):
        '''
        read block data from file
        '''
        import Base
        filename = str( QtGui.QFileDialog.getOpenFileName(None , 'please select input file' , Base.__currentProjectPath__) )
        if not filename:
            return
        
        from loadDataTools import ParseDFInputGraphData
        self.dataParser = ParseDFInputGraphData()
        
        if not self.dataParser.parse(str(filename)):
            showErrorMessageBox('Data Error' , 'the schema of file is incorrected')
            return

        print 'DF data parse successfully'    
        self.__enableConfigPanel(True)
        
        from DDADatabase import df_inputDatabase
        data = df_inputDatabase
        self.configUI.ui.lineE_Path.setText(filename)                
        self.configUI.ui.lineE_BlockNum.setText(str(len(df_inputDatabase.blockMatCollections)))
        self.configUI.ui.lineE_JointNum.setText(str(len(df_inputDatabase.jointMatCollections)))
        self.__initMatConfigUI()
        
        self.dataParser = None
        
    def __readParameters(self):
        '''
        read parameters from file
        '''
        import Base
        filename = str( QtGui.QFileDialog.getOpenFileName(None , 'please select input file' , Base.__currentProjectPath__) )
        if not filename:
            return
        from loadDataTools import ParseDFInputParameters
        parasParser = ParseDFInputParameters()
        
        if not parasParser.parse(str(filename)):
            showErrorMessageBox('Data Error' , 'the schema of file is incorrected')
            return        
        self.__storePara2Panel()
        
    def __storePara2Panel(self):
        from DDADatabase import df_inputDatabase
        paras = df_inputDatabase.paras
        
        self.configUI.ui.doubleSpinBox_IFStatic.setValue(paras.ifDynamic)
        self.configUI.ui.spinBox__NumStep.setValue(paras.stepsNum)
        self.configUI.ui.spinBox_Ratio.setValue(paras.ratio)
        self.configUI.ui.spinBox_timeInterval.setValue(paras.OneSteptimeLimit)
        self.configUI.ui.spinBox_SpringStiffness.setValue(paras.springStiffness)
        self.configUI.ui.spinBox_SOR.setValue(paras.SOR)
        self.matConfigUI.dataTableBLocksMats.writeData2Table(paras.blockMats)
        print 'blocks mats import done'
        self.matConfigUI.dataTableJointsMats.writeData2Table(paras.jointMats)
        print 'joints mats import done'
        if(len(paras.loadingPointMats))>0:
            self.matConfigUI.dataTableLoadingPointsMats.writeData2Table(paras.loadingPoints)
            print 'loading points import done'
        
    def __saveParameters2File(self):
        '''
        save parameters to self.current_path/parameters.df,and revise df_Ff.c
        '''
        import Base
        outfile = open(Base.__currentProjectPath__+'/parameters.df',  'wb' )
        if not outfile:
            showErrorMessageBox('File open failed' , 'Can\'t open parameters.df')
            return
        
        # schema
        tmpUI = self.configUI.ui
        outfile.write('%s\n%s\n%s\n%s\n%s\n%s\n%s\n'%(str(tmpUI.doubleSpinBox_IFStatic.text())\
                        , str(tmpUI.spinBox__NumStep.text()) , str(tmpUI.lineE_BlockNum.text())\
                        , str(tmpUI.lineE_JointNum.text()) , str(tmpUI.spinBox_Ratio.text())\
                        , str(tmpUI.spinBox_timeInterval.text()) , str(tmpUI.spinBox_SpringStiffness.text())))
        print 'schema store done.'
        
        # fixed points and loading points
        from DDADatabase import df_inputDatabase
        if len(df_inputDatabase.fixedPoints)>0:
            fps = len(df_inputDatabase.fixedPoints)
            outfile.write('0 '*fps +'\n')
            print 'fixed points : ' ,fps 
        if len(df_inputDatabase.loadingPoints)>0:
            lps = len(df_inputDatabase.loadingPoints)
            outfile.write('2 '*lps +'\n')
            print 'loading points : ' , lps 
        tmpTable = self.matConfigUI.tableLoadingPointsMats
        nums = [1]*6
        for i in range(len(df_inputDatabase.loadingPoints)):
            for j in range(6):
                nums[j] = str(tmpTable.item(i,j).text())
            outfile.write( '%s %s %s\n%s %s %s\n'%(nums[0] ,nums[1] ,nums[2] ,nums[3] ,nums[4] ,nums[5] ))
        print 'fixed points and loading points materials store done.'
         
        # block materials
        tmpTable = self.matConfigUI.tableBLocksMats
        nums = [1]*14
        for i in range(tmpTable.rowCount()):
            for j in range(14):
                nums[j] = str(tmpTable.item(i,j).text())
            outfile.write( '%s %s %s %s %s\n%s %s %s\n%s %s %s\n%s %s %s\n'%(nums[0] ,nums[1] ,nums[2]\
                               ,nums[3] ,nums[4] ,nums[5] ,nums[6] ,nums[7] ,nums[8] ,nums[9] ,nums[10]\
                               ,nums[11] ,nums[12] ,nums[13]))
        print 'block materials store done.'
        
        # joints materials
        tmpTable = self.matConfigUI.tableJointsMats
        nums = [1]*3
        for i in range(tmpTable.rowCount()):
            for j in range(3):
                nums[j] = str(tmpTable.item(i,j).text())
            outfile.write( '%s %s %s\n'%(nums[0] ,nums[1] ,nums[2]))
        print 'joint materials store done.'
        
        # rest parameters
        outfile.write('%s\n0 0 0'%str(self.configUI.ui.spinBox_SOR.text()))
        print 'all parameters store done.'
        
        outfile.close()
        
        import Base
        outfile = open(Base.__workbenchPath__+'/df_Ff.c' , 'wb')
        outfile.write(str(self.configUI.ui.lineE_Path.text())+'\n')
        outfile.write(Base.__currentProjectPath__+'/parameters.df')
        outfile.close()

    def __calculateDF(self):
        '''
        save parameters to self.current_path/parameters.df , and then start calculation
        '''
        if not self.matConfigUI.ifMatConfigPanelOK(): # all 3 tables' parameters are valid
            showErrorMessageBox('Data Error' , 'check recorrect parameters in tables')
            return
        self.__saveParameters2File()

        print 'Calculation button pressed'
        
        import os
        originPath = os.getcwd() 
        import Base
        print 'change dir to ' , Base.__workbenchPath__
        os.chdir(Base.__workbenchPath__)
        
        
        # begin to calculation

        processDialog =  Ui_DFCalculationProcess()
        print 'processbar widget showed'
        
        import Base
        f = open(Base.__currentProjectPath__+'/data.dg' , 'wb')  # clear file
        f.close()
        
        maxSteps = int(str(self.configUI.ui.spinBox__NumStep.text()))
#        maxSteps = 20000
        processDialog.ui.progressBar.setMaximum(maxSteps)
        processDialog.show()
        process = PyDDA.DF()
        process.calculationInit()
        for i in range(maxSteps):
            process.calculate1Step()
            processDialog.ui.progressBar.setValue(i)
            processDialog.ui.label_rate.setText('steps : %d /%d '%(i , maxSteps))
            e=QtCore.QEventLoop()
            e.processEvents()
        
        file = open('dg_ff.c' , 'wb')
        file.write(Base.__currentProjectPath__+'/data.dg')
        file.close()
        
        print 'change dir to ' , originPath
        os.chdir(originPath)        
        
    def GetResources(self):
        return {
                'MenuText':  'DFCalculation',
                'ToolTip': "DF calculation process."}
                
    def Activated(self, name="None"):
        FreeCAD.Console.PrintMessage( 'Creator activing\n')
        if FreeCAD.activeDDACommand:
            FreeCAD.activeDDACommand.finish()
        self.doc = FreeCAD.ActiveDocument
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.featureName = name
        self.ui = None
        
        if not self.doc:
            FreeCAD.Console.PrintMessage( 'FreeCAD.ActiveDocument get failed\n')
            self.finish()
        else:
            FreeCAD.activeDDACommand = self  # FreeCAD.activeDDACommand 在不同的时间会接收不同的命令
            import Base
            Base.__currentStage__ = 'DF' 
            #self.ui.show()

        # Hide Panel
        if __currentDDAPanel__ != None :
            __currentDDAPanel__.hide()
        
        self.configUI.show()        
        
    def IsActive(self):
        if FreeCADGui.ActiveDocument:
            import Base
            if len(Base.__workbenchPath__)>1 and len(Base.__currentProjectPath__)>0:
                return True
        else:
            return False
        
    
    def finish(self):
        pass

FreeCADGui.addCommand('DFCalculation', DFCalculation())