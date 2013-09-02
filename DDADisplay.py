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


from PyQt4 import QtCore, QtGui
import FreeCAD
import FreeCADGui
import Base
import PyDDA
from Graph import *
import sys
import os
import time

import DDAShapes
from Base import showErrorMessageBox

def clearDocument():
    '''
    remove all objects from view
    '''
    
    print '###########################\n######### clearing document ####'
    import DDADatabase
    DDADatabase.enableOperationObverser(False)

    label = FreeCAD.ActiveDocument.Label
    FreeCAD.closeDocument(label)
    FreeCAD.newDocument(label)
    print '##############################'
    FreeCADGui.runCommand('DDA_ResetCamera')
    DDADatabase.enableOperationObverser(True)
        
        
class DisplayDL():
    '''
    this class only has on object at one time and calculate for DDA .It has different stages for different processes such as Dl , DC , DF , DG
    '''
    def __init__(self):
        self.original_path = os.getcwd()
            
    def calculate(self):
        import Base
        Base.__currentStage__ = 'DL'
        
        self.process = PyDDA.DL()
        self.graph = DLGraph()
        
        print 'change dir to ' , Base.__workbenchPath__
        os.chdir(Base.__workbenchPath__)
        
#        print 'calculating file : ' , self.current_path+'\\'+open('Ff.c','r').read()
        print 'calculating file : ' , open('Ff.c','r').read()
        
        self.process.calculateStage2()
#        import Base
#        file = open(Base.__currentProjectPath__+'/data.dc' , 'rb')
#        content = file.read(-1) # read all
#        file.close()
#        
#        file = open(Base.__currentProjectPath__+'/tmpData.dc' , 'wb')
#        file.write(content)
#        file.close()

        print 'change dir to ' , self.original_path
        os.chdir(self.original_path)
            
    def preview(self):
        clearDocument()
        self.calculate()
        self.graph.showStage1Graph(self.process)
#        Base.setGraphLatest()
        
    def GetResources(self):
        return {
                'MenuText':  'Caluclate',
                'ToolTip': "Calculate DL."}
        
    def Activated(self):
        from DDAShapes import DDACheckSaveJointSetsAndTunnels
        from storeScene import DLStoreData
        FreeCADGui.runCommand('DDA_CheckSaveJointSetsAndTunnels')
        if not DDACheckSaveJointSetsAndTunnels.isDataValid() :
            return
        FreeCADGui.runCommand("DDA_StoreData")
        if not DLStoreData.isDataValid():
            return

        clearDocument()
        self.calculate()            
        print 'calculate done'
        FreeCADGui.runCommand('DDA_ShowDCInputGraph')
#        self.graph.showStage2Graph(self.process)
        
        FreeCADGui.runCommand('DDA_ResetCamera')
        
        import DDADatabase
        DDADatabase.clearDLRedoUndoList()
        
                        
    def finish(self):
        pass
    
class DCPreview(): 
    '''
    temporary class , provide DC preview function
    '''
    def __init__(self):
        self.original_path = os.getcwd()
        self.current_path = Base.__workbenchPath__
        self.ifOnlyCalculate = False
       
    def calculate(self , stageID = 1):
        self.process = PyDDA.DC()
        self.graph = DCGraph()
        
        import os
        originPath = os.getcwd()
        
        try:
            import Base
            file = open(Base.__workbenchPath__+'/dc_ff.c','wb')
            file.write(Base.__currentProjectPath__+'/data.dc')
            file.close()
        except:
            print 'dc_ff.c read failed.'
            return
        
        print 'change dir to ' , Base.__workbenchPath__
        os.chdir(Base.__workbenchPath__)
    
        print 'calculating file : ' , open('dc_ff.c','r').read()
        
        if stageID ==1 :
            self.process.calculateStage1()
        else:
            self.process.calculateStage2()

        print 'change dir to ' , originPath
        os.chdir(originPath)
            
    def GetResources(self):
        return {
                'MenuText':  'DC_Preview',
                'ToolTip': "preview DC."}
 
    def Activated(self):
#        if not Base.ifGraphLatest():
        clearDocument()
        self.calculate(1)            
        if not self.ifOnlyCalculate:
            self.graph.showStage1Graph(self.process)

                        
    def finish(self):
        pass
        
class DCCalculate(DCPreview):
    '''
    temporary class , provide DC calculate function and display
    '''
    def GetResources(self):
        return {
                'MenuText':  'DC_Calculate',
                'ToolTip': "Calculate DC."}
 
    def Activated(self):
        import Base
        Base.__currentStage__ = 'DC'
        self.calculate(2)   
        if not self.ifOnlyCalculate:         
            clearDocument()
            FreeCADGui.runCommand('DDA_DisplayDFInputGraph')
            
        FreeCADGui.runCommand('DDA_ResetCamera')
            
        print 'DC data draw done in DCCalculate'
            
    def finish(self):
        pass
    
class DisplayDFInputData:
    '''
    load df input data , and show it.
    '''
    def GetResources(self):
        return {
                'MenuText':  'DisplayDFInputData',
                'ToolTip': "Display DF Input Data"}   
         
    def Activated(self):
        from Base import __currentProjectPath__
        FreeCADGui.runCommand('DDA_LoadDFInputGraphData')
        clearDocument()
        graph = DCGraph()
        graph.showGraph4File()
        
    def finish(self):
        pass    
    

class DCOnlyCalculate:
    '''
    temporary class , provide DC calculate function 
    '''
    def GetResources(self):
        return {
                'MenuText':  'DC_OnlyCalculate',
                'ToolTip': "Calculate DC."}   
         
    def Activated(self):
        DDADCCalculatCmd.ifOnlyCalculate = True
        FreeCADGui.runCommand('DDA_DCCalculate')
        DDADCCalculatCmd.ifOnlyCalculate = False
        
    def finish(self):
        pass

class DisplayDCInputData:
    '''
    load dc input data , and show it.
    '''
    def GetResources(self):
        return {
                'MenuText':  'DisplayDCInputData',
                'ToolTip': "Display DC Input Data"}   
         
    def Activated(self):
        from Base import __currentProjectPath__
        Base.changeStage('DL')
        FreeCADGui.runCommand('DDA_LoadDCInputData')
        graph = DLGraph()
        graph.showGraph4File()
        
    def finish(self):
        pass    

class DisplayDLInputData:
    '''
    load dc input data , and show it.
    '''
    def GetResources(self):
        return {
                'MenuText':  'DisplayDCInputData',
                'ToolTip': "Display DC Input Data"}   
         
    def Activated(self):
        from Base import __currentProjectPath__
        Base.changeStage('PreDL')
        FreeCADGui.runCommand('DDA_LoadDLInputData')
        graph = DLInputGraph()
        graph.showGraph4File()
        
    def finish(self):
        pass    




DDADisplayCmd = DisplayDL()
#DDADCPreviewCmd = DCPreview()
DDADCCalculatCmd = DCCalculate()


#DDADFCalculatCmd = DFCalculation()
#DDADFCalculation1StepCmd = DFCalculation1Step()
FreeCADGui.DDADisplayCmd = DDADisplayCmd
FreeCADGui.addCommand('DDA_DLCalculate', DDADisplayCmd)
#FreeCADGui.addCommand('DDA_DCPreview', DDADCPreviewCmd)
FreeCADGui.addCommand('DDA_DCCalculate', DDADCCalculatCmd)
FreeCADGui.addCommand('DDA_DCOnlyCalculate', DCOnlyCalculate())
#FreeCADGui.addCommand('DDA_DFCalculat', DDADFCalculatCmd)
#FreeCADGui.addCommand('DDA_DFCalculate1Step', DDADFCalculation1StepCmd)
FreeCADGui.addCommand('DDA_ShowDLInputGraph', DisplayDLInputData())
FreeCADGui.addCommand('DDA_ShowDCInputGraph', DisplayDCInputData())
FreeCADGui.addCommand('DDA_DisplayDFInputGraph', DisplayDFInputData())