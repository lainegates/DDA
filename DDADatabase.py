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


'''
DDA part , store related information 
every part (DLDataBase , DCDataBase ...) store related dictionaries for specified items . For example , for additional line , DLDatabase store 2 dictionaries , 'shape2id' and  'id2materialNumber'(every material has a different material number)
'''

import FreeCAD

__allShapeTypes__ = ["BorderLine","BoundaryLine","JointLine","AdditionalLine"\
                     ,"Block","MaterialLine","BoltElement","FixedPoint"\
                     ,"LoadingPoint","MeasuredPoint","HolePoint"]


class BaseDatabase(object):
    def __init__(self):
        self.shapeTypes = []
        self.operationTypes = ['ADD' , 'DELETE' , 'MOVE' , 'CHANGEMATERIAL'\
                , 'CHANGEVERTICES']
        #
        # schema   operationType(str)  shapeType(str) idxes(int in tuple) objects
        #
        # operationType 'ADD' and 'DELETE'
        #    shapeTypes : work with all shapes except 'JointLine' and 'Block' 
        #    objects    : maybe one or more,but not objects needed be transmitted
        #                 as parameter. just shapeType and idxes is enough 
        #
        # operationType 'MOVE'
        #    shapeTypes : work with 'JointLines' and  4 kinds of points
        #    objects    : only one object at one time, and be kinds of DDALines
        #                 and DDAPoint
        #
        # operationType 'CHANGEMATERIAL'
        #    shapeTypes : all shpes except 'BoundaryLine' and 4 kinds of point
        #    objects    : maybe one or more , but not objects needed be transmitted
        #                 as parameter. just shapeType and idxes is enough
        #
        # operationType 'CHANGEVERTICES'
        #    shapeTypes : all shapeTyps except 'Block' and 4 kinds of points
        #    objects    : one object one time, and must be kinds of DDALine and DDAPolyline
        #
        
        self.undoList = []
        self.redoList = []
        self.operationIdx = 0 # [0:len(self.undoList)]
        
        self.ifDisplayDatabase = True
        
    def displayRedoAndUndoList(self):
        if self.ifDisplayDatabase:
            print '####### undo/redo list#######'
            for t1 , t2 in zip(self.undoList , self.redoList):
                print '# ' , t1 , ' <-----> ' , t2
            print '#############################'
        
    def clearRedoUndoList(self):
        self.undoList = []
        self.redoList = []    
        
    def checkShapeType(self , shapeType):
        assert shapeType in self.shapeTypes
        
    def getData4Type(self , shapeType):
        if shapeType == "BorderLine": return self.borderNodes
        elif shapeType == "BoundaryLine": return self.boundaryNodes
        elif shapeType == "JointLine":   return self.jointLines
        elif shapeType == "AdditionalLine": return self.additionalLines
        elif shapeType == "Block": return self.blocks
        elif shapeType == "MaterialLine": return self.materialLines
        elif shapeType == "BoltElement": return self.boltElements
        elif shapeType == "FixedPoint": return self.fixedPoints
        elif shapeType == "LoadingPoint":  return self.loadingPoints
        elif shapeType == "MeasuredPoint":  return self.measuredPoints
        elif shapeType == "HolePoint": return self.holePoints
    
    def handleAdd(self , operation):
        objs = self.getData4Type(operation[1])
        for idx in operation[2]:
            objs[idx].visible = True
            
    def handleDelete(self , operation):
        t = operation
        objs = self.getData4Type(t[1])
        for idx in t[2]:
            objs[idx].visible = False
            
    def handleChangeVertices(self , operation):
        objs = self.getData4Type(operation[1])
        assert len(operation[2])==1
        objs[operation[2][0]] = operation[3]
        
    def handleChangeMaterial(self , operation):
        objs = self.getData4Type(operation[1])
        assert len(operation[2])==1
        objs[operation[2][0]].materialNo = operation[3]
        
    def handle4Operation(self , operation):
        if operation[0] == 'ADD' :self.handleAdd(operation)
        elif operation[0] == 'DELETE' :self.handleDelete(operation)
        elif operation[0] ==  'CHANGEMATERIAL':self.handleChangeMaterial(operation)
        elif operation[0] == 'CHANGEVERITCES':self.handleChangeVertices(operation)
        
    def undo(self):
        assert self.operationIdx>=0
        if self.operationIdx==0:
            return
        
        self.operationIdx-=1
        operation = self.undoList[self.operationIdx]
        self.handle4Operation(operation)
        
        print 'undo ' , self.operationIdx , ' ' , operation
        
        return operation[1]
    
    def redo(self):
        assert self.operationIdx <= len(self.redoList)
        if self.operationIdx==len(self.redoList):
            return
        
        operation = self.redoList[self.operationIdx]
        self.handle4Operation(operation)

        print 'redo ' , self.operationIdx , ' ' , operation
            
        self.operationIdx+=1
        return operation[1]
        
    def checkParaTyps(self , shapeType , idxes , args ):
        self.checkShapeType(shapeType)
        assert isinstance( idxes , list)
        
        
    
    def add(self , shapeType , idxes , args , ifRecord=False):
        '''
        add object for database
        :param operation: 'ADD' or 'DELETE' or 'MOVE' or 'CHANGEMATERIAL'
        :param shapeType: in self.shapeTypes
        :param idxes: the index of handle node in self.$shapeType
        :param args: content
        '''
        self.checkParaTyps(shapeType, idxes, args)
        if ifRecord:
            length = len(self.getData4Type(shapeType))
            newIdxes = tuple(range(length , length+len(args)))
            op1 = ('DELETE' , shapeType , newIdxes , None)
            op2 = ('ADD' , shapeType , newIdxes , None)
            self.undoList.append(op1)
            self.redoList.append(op2)
            self.operationIdx = len(self.undoList)
            self.displayRedoAndUndoList()
    
    def remove(self , shapeType , idxes , args , ifRecord=False):
        '''
        paras are same to self.remove(...)
        '''
        self.checkParaTyps(shapeType, idxes, args)
        if ifRecord:
            op1 = ('ADD' , shapeType , tuple(idxes) , None)
            op2 = ('DELETE' , shapeType , tuple(idxes) , None)
            self.undoList.append(op1)
            self.redoList.append(op2)
            self.operationIdx = len(self.undoList)
            self.displayRedoAndUndoList()
        
        
    def changeVertices(self , shapeType , idxes , args , ifRecord=False):
        '''
        paras are same to self.add(...)
        '''
        self.checkParaTyps(shapeType, idxes, args)
        if ifRecord:
            objs = self.getData4Type(shapeType)
            op1 = ('CHANGEVERITCES' , shapeType , idxes , objs[idxes[0]])
            op2 = ('CHANGEVERITCES' , shapeType , idxes , args[0])
            self.undoList.append(op1)
            self.redoList.append(op2)
            self.operationIdx = len(self.undoList)
            self.displayRedoAndUndoList()
        
    def changeMaterial(self , shapeType , idxes , args , ifRecord=False):
        '''
        paras are same to self.add(...)
        '''
        self.checkParaTyps(shapeType, idxes, args)
        if ifRecord:
            objs = self.getData4Type(shapeType)
            op1 = ('CHANGEMATERIAL' , shapeType , idxes , objs[idxes[0]].materialNo)
            op2 = ('CHANGEMATERIAL' , shapeType , idxes , args)
            self.undoList.append(op1)
            self.redoList.append(op2)
            self.operationIdx = len(self.undoList)
            self.displayRedoAndUndoList()
    
class DLDatabase(BaseDatabase):
    '''
    store DL data
    '''
    def __init__(self):
        super(DLDatabase , self ).__init__()
        self.reset()
        self.shapeTypes = __allShapeTypes__[:]
        
    def reset(self):
        self.jointSets = []                # 保存 (dip , dip direction , spacing , length , bridge , random)
        self.slope = []                    # 保存 (dip , dip direction)
        self.tunnels = []                    # 保存 (ShapeNumber , a , b , c, r , centerX , centerY)
        self.additionalLines = []
        self.materialLines = []
        self.boltElements = []
        self.fixedPoints = []
        self.loadingPoints = []
        self.measuredPoints = []
        self.holePoints = []      
        self.boundaryNodes = []  
        self.borderNodes = []
        
    def add(self , shapeType , idxes , args , ifRecord=False):
        super( DLDatabase , self).add(shapeType , idxes , args , ifRecord)
        
        from loadDataTools import DDAPolyLine , FixedPoint , MeasuredPoint , LoadingPoint , Graph , HolePoint
  
        if shapeType == "BorderLine":
            self.borderNodes = args
        elif shapeType == "AdditionalLine":
            self.additionalLines.extend(args)
        elif shapeType == "BoundaryLine":
            self.boundaryNodes = args
        elif shapeType == "BoltElement":
            self.boltElements = args
        elif shapeType == "FixedPoint":
            self.fixedPoints.extend(args)
        elif shapeType == "LoadingPoint":
            self.loadingPoints.extend(args)
        elif shapeType == "MeasuredPoint":
            self.measuredPoints.extend(args)
        elif shapeType == "HolePoint":
            self.holePoints.extend(args)
            
class DCInputDatabase(BaseDatabase):
    '''
    store DL data
    '''
    def __init__(self):
        super(DCInputDatabase , self).__init__()
        self.reset()
        self.resetShapeTypes()
        
    def resetShapeTypes(self):
        self.shapeTypes = __allShapeTypes__[5:] + __allShapeTypes__[2:4]
        
    def reset(self):
        self.boundaryLinesNum = 0 # special number, currently I don't fully understand it in data.dc, I will learn it later 
        self.additionalLines = []
        self.jointLines = []
        self.materialLines = []
        self.fixedPoints = []
        self.loadingPoints = []
        self.measuredPoints = []
        self.holePoints = []
        # key:value is { (int(obj.LabelNo),int(subElementNo)) : (startPoint,endPoint) } for data change
        # or key:value is { (int(obj.LabelNo),int(subElementNo)) : 'Delete'} for delete
        self.jointLinesChanges = {}

    def add(self , shapeType , idxes=[0] , args=None , ifRecord=False):
        super( DCInputDatabase , self).add(shapeType , idxes , args , ifRecord)
        
        from loadDataTools import DDAPolyLine , FixedPoint , MeasuredPoint , LoadingPoint , Graph , HolePoint
  
        if shapeType == "AdditionalLine":
            self.additionalLines.extend(args)
        elif shapeType == "FixedPoint":
            self.fixedPoints.extend(args)
        elif shapeType == "LoadingPoint":
            self.loadingPoints.extend(args)
        elif shapeType == "MeasuredPoint":
            self.measuredPoints.extend(args)
        elif shapeType == "HolePoint":
            self.holePoints.extend(args)

    def changeVertices(self , shapeType , idxes , args , ifRecord=False):
        '''
        :param shapeType:
        :param idxes: index of args
        :param args: one shape object , maybe a DDALine object
        :param ifRecord:
        '''
        assert shapeType=='JointLine'
        
        super( DCInputDatabase , self).changeVertices(shapeType, idxes , args , ifRecord)
        self.jointLines[idxes[0]] = args[0]
        
    def changeMaterial(self , shapeType , idxes , args , ifRecord=False):
        '''
        :param shapeType:
        :param idxes: index of args
        :param args: one shape object , maybe a DDALine object
        :param ifRecord:
        '''
        assert len(idxes)==1 and isinstance(args , int)
        objs = self.getData4Type(shapeType)
        if objs[idxes[0]].materialNo==args:
            # Whenever user change Material using property browser
            # ,FreeCAD run this property changing twice
            return
        super( DCInputDatabase , self).changeMaterial(shapeType, idxes , args , ifRecord)
        objs[idxes[0]].materialNo = args

class DFParameters:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.ifDynamic = 0   # 0 :static  1:dynamic
        self.stepsNum = 0
        self.blockMatsNum = 0
        self.jointMatsNum = 0
        self.ratio = 0
        self.OneSteptimeLimit = 0
        self.springStiffness = 0
        self.SOR = 0
        
        self.blockMats = []
        self.jointMats = []
        self.loadingPointMats = []

class DFInputDatabase(BaseDatabase):
    def __init__(self):
        super(DFInputDatabase , self).__init__()
        self.reset()
        self.shapeTypes = __allShapeTypes__[4:] # 4 kinds of points , material lines , blocks
        
    def reset(self):
        from loadDataTools import Block , FixedPoint , MeasuredPoint , LoadingPoint , Graph , HolePoint
#        self.graphData = Graph()
        self.blocks = []
        self.materialLines = []
        self.fixedPoints = []
        self.measuredPoints = []
        self.loadingPoints = []
        self.holePoints = []
        self.boltElements = []
        self.paras = DFParameters()
        self.blockMatCollections = set()
        self.jointMatCollections = set()

    def add(self , shapeType , idxes , args , ifRecord=False):
        super( DFInputDatabase , self).add(shapeType , idxes , args , ifRecord)
        
        from loadDataTools import DDAPolyLine , FixedPoint , MeasuredPoint , LoadingPoint , Graph , HolePoint
  
        if shapeType == "FixedPoint":
            self.fixedPoints.extend(args)
        elif shapeType == "LoadingPoint":
            self.loadingPoints.extend(args)
        elif shapeType == "MeasuredPoint":
            self.measuredPoints.extend(args)
        elif shapeType == "HolePoint":
            self.holePoints.extend(args)
        elif shapeType == 'MaterialLine':
            self.materialLines.extend(args)

    def changeVertices(self , shapeType , idxes , args , ifRecord=False):
        '''
        :param shapeType:
        :param idxes: index of args
        :param args: one shape object , maybe a DDALine object
        :param ifRecord:
        '''
        super( DCInputDatabase , self).changeVertices(shapeType, idxes , args , ifRecord)
        self.jointLines[idxes[0]] = args[0]
        
    def changeMaterial(self , shapeType , idxes , args , ifRecord=False):
        '''
        :param shapeType:
        :param idxes: index of args
        :param args: one shape object , maybe a DDALine object
        :param ifRecord:
        '''
        assert len(idxes)==1 and isinstance(args , int)
        objs = self.getData4Type(shapeType)
        if objs[idxes[0]].materialNo==args:
            # Whenever user change Material using property browser
            # ,FreeCAD run this property changing twice
            return
        super( DFInputDatabase , self).changeMaterial(shapeType, idxes , args , ifRecord)
        objs[idxes[0]].materialNo = args

        
dl_database = DLDatabase()
dc_inputDatabase = DCInputDatabase()
df_inputDatabase = DFInputDatabase()


def clearDLRedoUndoList():
    dl_database.clearRedoUndoList()
    
def clearDCRedoUndoList():
    dc_inputDatabase.clearRedoUndoList()

def clearDFRedoUndoList():
    df_inputDatabase.clearRedoUndoList()


#############################################
#
# used to configure bolts elements
#
#############################################
tmpBoltElements = []


#############################################
#
#  DDA redo/undo observer
#
#############################################
from pivy import coin
class OperationObverser:
    '''
    observe the operation, catch keyboard event to supply redo/undo application
    '''
    def __init__(self):
        self.call = None
        self.on = False
        self.zDown = False
        self.yDown = False
    
    def Activated(self, name="None"):
        self.on = True
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.call = self.view.addEventCallback("SoEvent", self.action)
        
    def IsActive(self):
        return self.on

    def RedrawObject(self , objName):
        if not objName:
            return
        print 'trigger obj \'%s\' in OperationObverser'%objName
        obj = FreeCAD.ActiveDocument.getObject(objName)
        assert obj
        obj.ViewObject.RedrawTrigger = True
        
    def handleDelete(self):
        import Base
        sels=FreeCADGui.Selection.getSelectionEx()
        sel = sels[0]
        objName = sel.ObjectName
        assert len(sel.SubElementNames)==1
        type , idx = Base.getRealTypeAndIndex(sel.SubElementNames[0])
        database =  Base.getDatabaser4CurrentStage()
        database.remove(objName, [idx], args=None, ifRecord=True)

    def action(self, arg):
        "scene event handler"
        if arg["Type"] == "SoKeyboardEvent":
            if arg["CtrlDown"] and arg["Key"] == 'z':
                if arg['State'] == 'DOWN' and not self.zDown:
                    print 'ctrl z'
                    import Base
                    database = Base.getDatabaser4CurrentStage()
                    self.RedrawObject(database.undo())
            if arg["CtrlDown"] and arg["Key"] == 'y':
                if arg['State'] == 'DOWN' and not self.yDown:
                    print 'ctrl y'
                    import Base
                    database = Base.getDatabaser4CurrentStage()
                    self.RedrawObject(database.redo())
            if arg["Key"] == 'DELETE':
                if arg['State'] == 'UP':
                    print 'Delete pressed'
#                    self.handleDelete()

            if arg["Key"] == 'z':
                if arg['State'] == 'DOWN': self.zDown = True
                elif arg['State'] == 'UP': self.zDown = False
                
            if arg["Key"] == 'y':
                if arg['State'] == 'DOWN': self.yDown = True
                elif arg['State'] == 'UP': self.yDown = False

    def Deactivated(self):
        if self.call:
            self.view.removeEventCallback("SoEvent", self.call)
        self.call=None
        self.on = False
        self.view = None
    
    
import FreeCADGui 
FreeCADGui.DDAOperationObverser = OperationObverser()

def enableOperationObverser(flag):
    if flag:
        FreeCADGui.DDAOperationObverser.Activated()
    else:
        FreeCADGui.DDAOperationObverser.Deactivated()
    
#from loadDataTools import Graph
#dc_database = Graph()