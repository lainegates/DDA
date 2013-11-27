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


import FreeCAD, FreeCADGui, Part, math, sys, os, Image, Drawing, WorkingPlane
from FreeCAD import Vector
#from draftlibs import fcvec, fcgeo
import fcvec, fcgeo
from pivy import coin
from PyQt4 import QtGui , QtCore
import PartGui


#---------------------------------------------------------------------------
# General functions
#---------------------------------------------------------------------------

__currentProjectPath__ = None
__workbenchPath__ = None
__radius4boltEndpoint__ = 0.01
__radius4Points__ = 1
__windowInfo__ = []  # xmin , xmax , ymin , ymax

DDAStages = ['PreDL','DL','DC','DF','DG']
__currentStage__ = None

StepForStage = ['FirstStep' , 'ShapesAvailable' , 'SpecialStep']
__currentStep__ = None



__ifGraphLatest__ = False

# brush colors come from Mr. Shi's code
__brushColors__ = [( 0.0 , 0.0 , 0.0 , 1.0 ) ,( 0.0 , 0.4 , 0.4 , 1.0 ) ,( 0.0 , 0.4 , 0.0 , 1.0 ) 
                   ,( 0.0 , 0.6 , 0.0 , 1.0 ) ,( 0.0 , 0.8 , 0.0 , 1.0 ) ,( 0.0 , 1.0 , 0.0 , 1.0 )
                   ,( 0.0 , 1.0 , 0.2 , 1.0 ) ,( 0.0 , 0.6 , 0.6 , 1.0 ) ,( 0.0 , 0.4 , 0.8 , 1.0 ) 
                   ,( 0.0 , 0.4 , 0.8 , 1.0 ) ,( 0.0 , 0.2 , 1.0 , 1.0 ) ,(1.0 , 1.0 , 1.0 , 1.0)]

# pen colors come from Mr. Shi's code
__penColors__ = [( 0.0 , 0.0 , 0.0 , 1.0 ) ,( 0.0 , 0.0 , 0.0 , 1.0 ) ,( 0.0 , 1.0 , 0.0 , 1.0 ) 
                 ,( 0.0 , 0.0 , 1.0 , 1.0 ) ,( 1.0 , 0.0 , 0.0 , 1.0 ) ,( 1.0 , 0.0 , 1.0 , 1.0 ) ] 

__shapeBeModifying__ = [None , None , None] # docName , objName , subElement
__clearShapeModifyingNodes__ = False

def ifGraphLatest():
    return __ifGraphLatest__
    
    
        
def sleepQT(seconds):
    t=QtCore.QTimer()
    e=QtCore.QEventLoop()
    QtCore.QObject.connect(t,QtCore.SIGNAL("timeout()"),e,QtCore.SLOT("quit()"))
    t.setSingleShot(True)
    t.start(seconds*1000) # make a pause of 20 s
    e.exec_() # stops here until the timeout() signal is emitted

    
def getRealTypeAndIndex(objName):
    name = objName
    for i in range(1 , len(name)):
        if not name[-i] in '1234567890':
            if i==1:
                break
            else:
                No = int(name[len(name)-i+1:])
            return name[:len(name)-i+1] , No
    return name , 0
    
def setGraphLatest():
    '''
    graph is latest
    '''
    __ifGraphLatest__ = True
    
def getDatabaser4CurrentStage():
    import DDADatabase
    if __currentStage__=='PreDL':
        return DDADatabase.dl_database
    elif __currentStage__ == 'DL':
        return DDADatabase.dc_inputDatabase
    elif  __currentStage__== 'DC' or __currentStage__== 'DF':
        return DDADatabase.df_inputDatabase
    return None
        
    
def changeStage(stage):
    '''
    there are 4 stages for DDA : 'DL','DC','DF','DG' 
    :param id: stage index
    '''
    assert stage in DDAStages
    global __currentStage__
    __currentStage__ = stage
    print '##############\n#change to tage : ' , __currentStage__ , '\n############' 
    
def changeStep4Stage(step):
    '''
    there are 3 steps for one stage : 'FirstStep' , 'ShapesAvailable' , 'SpecialStep'
    :param id: stage index
    '''
    assert step in StepForStage
    global __currentStage__ , __currentStep__
    __currentStep__ = step
    print '##############\n#change to step \'' , step , '\' in stage : ' , __currentStage__ , '\n############' 
    
    
def setGraphRevised():
    '''
    graph has been revised
    '''
    __ifGraphLatest__ = False
    
	
def showErrorMessageBox( title , text):
    box = QtGui.QMessageBox( QtGui.QMessageBox.Critical , title , text )  # 3个参数分别为图标，title，和text
    box.exec_()

def showWaringMessageBox( title , text):
    box = QtGui.QMessageBox( QtGui.QMessageBox.Warning , title , text , QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel )
    ret = box.exec_()
    return ret

def typecheck (args_and_types, name="?"):
    "typecheck([arg1,type),(arg2,type),...]): checks arguments types"
    for v, t in args_and_types:
        if not isinstance (v, t):
            w = "typecheck[" + str(name) + "]: "
            w += str(v) + " is not " + str(t) + "\n"
            FreeCAD.Console.PrintWarning(w)
            raise TypeError("Draft." + str(name))


def tolerance():
    "tolerance(): returns the tolerance value from Draft user settings"
    return 0.01
    
def getParam(param , index = 0):
    '''
    all the parameters are from Draft.getParam
    :param param: parameter name
    :param index: if param is color , index is colorIndex
    '''
    if param == "snapRange" : 
        return 4
    elif param == "gridSpacing":
        return 1
    elif param == "gridEvery":
        return 10
    elif param == "UiMode":
        return 0        
    elif param == "linewidth":
        return 2        
    elif param == "textheight":
        return 10        
    elif param == "constructioncolor":
        return 746455039        
    elif param == "color":
        return 255        
    elif param == "snapcolor":
        return 255
    elif param == "modconstrain":
        return 0
    elif param == "modsnap":
        return 1
    elif param == "modalt":
        return 2
    elif param == "BorderLineColor":
        return ( 0.0 , 0.0 , 0.0 )
    elif param == "BoundaryLineColor":
        return ( 0.0 , 0.0 , 0.0 )
    elif param == "BlockColor":
        return __brushColors__[index]
    elif param == "BlockBoundaryLineColor":
        return __penColors__[index]
    elif param == "JointLineColor":
        return __penColors__[index]
    elif param == "TunnelLineColor":
        return __penColors__[index]
    elif param == "AdditionalLineColor":
        return ( 0.0 , 0.0 , 0.0 )
    elif param == "MaterialLineColor":
        return ( 0.0 , 0.0 , 1.0)
    elif param == "TmpBoltElementColor":
        return ( 0.0 , 1.0 , 0.0)
    elif param == "BoltElementColor":
        return ( 0.0 , 1.0 , 0.0)
    elif param == "FixedPointColor":
#        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DDA")
#        print 'fixed point color :' , p.GetUnsigned('fixedpointcolor')
        return ( 1.0 , 0.0 , 0.0)
    elif param == "LoadingPointColor":
#        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DDA")
#        print 'loading point color :' , p.GetUnsigned('loadingpointcolor')
        return ( 1.0 , 0.0 , 1.0)
    elif param == "MeasuredPointColor":
        return ( 0.0 , 1.0 , 1.0)
    elif param == "HolePointColor":
        return ( 0.8 , 0.8 , 0.0)
#    else :
#        FreeCAD.Console.PrintError('type \'%s\' not found\n'% param)
        
def getType(obj):
    "getType(object): returns the Draft type of the given object"
    if "Proxy" in obj.PropertiesList:
        if hasattr(obj.Proxy, "Type"):
            return obj.Proxy.Type
    if obj.isDerivedFrom("Part::Feature"):
        return "Part"
    if (obj.Type == "App::Annotation"):
        return "Annotation"
    if obj.isDerivedFrom("Mesh::Feature"):
        return "Mesh"
    return "Unknown"

def dimSymbol():
    "returns the current dim symbol from the preferences as a pivy SoMarkerSet"
    s = getParam("dimsymbol")
    marker = coin.SoMarkerSet()
    if s == 0: marker.markerIndex = coin.SoMarkerSet.CIRCLE_FILLED_5_5
    elif s == 1: marker.markerIndex = coin.SoMarkerSet.CIRCLE_FILLED_7_7
    elif s == 2: marker.markerIndex = coin.SoMarkerSet.CIRCLE_FILLED_9_9
    elif s == 3: marker.markerIndex = coin.SoMarkerSet.CIRCLE_LINE_5_5
    elif s == 4: marker.markerIndex = coin.SoMarkerSet.CIRCLE_LINE_7_7
    elif s == 5: marker.markerIndex = coin.SoMarkerSet.CIRCLE_LINE_9_9
    elif s == 6: marker.markerIndex = coin.SoMarkerSet.SLASH_5_5
    elif s == 7: marker.markerIndex = coin.SoMarkerSet.SLASH_7_7
    elif s == 8: marker.markerIndex = coin.SoMarkerSet.SLASH_9_9
    elif s == 9: marker.markerIndex = coin.SoMarkerSet.BACKSLASH_5_5
    elif s == 10: marker.markerIndex = coin.SoMarkerSet.BACKSLASH_7_7
    elif s == 11: marker.markerIndex = coin.SoMarkerSet.BACKSLASH_9_9
    return marker

    
def formatObject(target, origin=None):
    '''
    formatObject(targetObject,[originObject]): This function applies
    to the given target object the current properties 
    set on the toolbar (line color and line width),
    or copies the properties of another object if given as origin.
    It also places the object in construction group if needed.
    '''
    pass
    
def getSelection():
    "getSelection(): returns the current FreeCAD selection"
    return FreeCADGui.Selection.getSelection()

def select(objs):
    "select(object): deselects everything and selects only the passed object or list"
    FreeCADGui.Selection.clearSelection()
    if not isinstance(objs, list):
        objs = [objs]
    for obj in objs:
        FreeCADGui.Selection.addSelection(obj)
        
def recomputeDocument():
    '''
    recompute FreeCAD.ActiveDocument
    '''
    FreeCAD.ActiveDocument.recompute()

    
def makeWire(pointslist, closed=False, placement=None, face=True, support=None , fname = 'Line' , colorIndex = 0):
    '''makeWire(pointslist,[closed],[placement]): Creates a Wire object
    from the given list of vectors. If closed is True or first
    and last points are identical, the wire is closed. If face is
    true (and wire is closed), the wire will appear filled. Instead of
    a pointslist, you can also pass a Part Wire.'''
    if not isinstance(pointslist, list):
        nlist = []
        for v in pointslist.Vertexes:
            nlist.append(v.Point)
        if fcgeo.isReallyClosed(pointslist):
            nlist.append(pointslist.Vertexes[0].Point)
        pointslist = nlist
    if placement: typecheck([(placement, FreeCAD.Placement)], "makeWire")
    obj = FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython", fname)  
    _Wire(obj)
    _ViewProviderWire(obj.ViewObject)
    obj.Points = pointslist
    obj.Closed = closed
    if closed:
        if pointslist[0] != pointslist[-1]:
            pointslist.append(pointslist[0])
    obj.Support = support
    obj.ViewObject.LineColor = getParam(fname+'Color' , colorIndex)
    if not face: obj.ViewObject.DisplayMode = "Wireframe"
    if placement: obj.Placement = placement
    formatObject(obj)
    select(obj)
    FreeCAD.ActiveDocument.recompute()
    
    setGraphRevised()
    
    return obj

def addShapeMover(docName , objName , subName , point):
    assert isinstance(docName , str) and isinstance(objName , str) and isinstance(subName , str) 
    removeShapeMover()
    import Part
    
    # create only one for the node. Create node every time will occur bugs
    # for that FreeCAD updates graphs only when script done, this will occure bugs 
    # if user click objects one by one. For this situation, FreeCAD will create
    # 'ABC', 'ABC001' ... at end of script before I delete the first 'ABC'
    # I will try to fix the bug later by adding node actually
    obj =  FreeCAD.ActiveDocument.getObject("ShapeMover")
    if not obj:
        obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ShapeMover")
        _ShapeModifier(obj)
        _ViewProviderDDA(obj.ViewObject)
    obj.RelatedDocumentName = docName
    obj.RelatedObjectName = objName
    obj.RelatedSubElement = subName
    shape = Part.Vertex(point)
    obj.Shape = shape
    obj.ViewObject.PointSize = 10
    obj.ViewObject.Visibility = True
    print '\tShapeMover added'
        
def removeShapeMover():
    hideShapeMover()
#    objName = None
#    for obj in FreeCAD.ActiveDocument.Objects:
#        shapeType , idx = getRealTypeAndIndex(obj.Label)
#        if shapeType=='ShapeMover':
#            objName = obj.Label
#            break
#    if objName:
#        from drawGui import todo
#        todo.delay(FreeCAD.ActiveDocument.removeObject, objName)
#        print '\tShapeMover remove ' , objName

def hideShapeMover():
    tmp = FreeCAD.ActiveDocument.getObject('ShapeMover')
    if tmp:
        tmp.ViewObject.Visibility = False

    
def addShapeModifier(docName , objName , subName , point1 , point2):
    assert isinstance(docName , str) and isinstance(objName , str) and isinstance(subName , str) 
    removeShapeModifier()
    import Part
    # create only one for the node. Create node every time will occur bugs
    # for that FreeCAD updates graphs only when script done, this will occure bugs 
    # if user click objects one by one. For this situation, FreeCAD will create
    # 'ABC', 'ABC001' ... at end of script before I delete the first 'ABC'
    # I will try to fix the bug later by adding node actually
    obj =  FreeCAD.ActiveDocument.getObject("ShapeModifier")
    if not obj:
        obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ShapeModifier")
        _ShapeModifier(obj)
        _ViewProviderDDA(obj.ViewObject)
    obj.Points = [point1 , point2]
    obj.ViewObject.PointSize = 10
    obj.ViewObject.Visibility = True
    print '\tShapeModifier added'

def removeShapeModifier():
    hideShapeModifier()
#    objName = None
#    for obj in FreeCAD.ActiveDocument.Objects:
#        shapeType , idx = getRealTypeAndIndex(obj.Label)
#        if shapeType=='ShapeModifier':
#            objName = obj.Label
#            break
#    if objName:
#        from drawGui import todo
#        todo.delay(FreeCAD.ActiveDocument.removeObject, objName)
#        print '\tShapeModifier remove ' , objName

def hideShapeModifier():
    tmp = FreeCAD.ActiveDocument.getObject('ShapeModifier')
    if tmp:
        tmp.ViewObject.Visibility = False

def checkIfAnyObjectsExisting():
    return len(FreeCAD.ActiveDocument.Objects)>0


#def __confirmViewProvider4Lines(fname , viewObject):
#    if fname=='AdditionalLine':
#        _ViewProviderAdditionalLines(viewObject)
#    elif fname == 'MaterialLine':
#        _ViewProviderMaterialLine(viewObject)
#    elif fname == 'BoltElement':
#        _ViewProviderBoltElement(viewObject)
#    elif fname == 'TmpBoltElement':
#        _ViewProviderBoltElement(viewObject)
#    elif fname == 'JointLine':
#        _ViewProviderJointLines(viewObject)
##    elif fname == 'BoundaryLine':
##        _ViewProviderBoundaryLines(viewObject)
#    else:
#        raise Exception('unkown shapes')

def addLines2Document(shapeType , ifStore2Database=False , args=None, closed=False , ifTriggerRedraw=True):
    obj = FreeCAD.ActiveDocument.getObject(shapeType)
    if not obj:    
        obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", shapeType)
        _Lines(obj)
        _ViewProviderDDALines(obj.ViewObject)
    
    if ifStore2Database:
        database = getDatabaser4CurrentStage()
        database.add(shapeType=shapeType, idxes=[0], args=args, ifRecord=True)
    
    if ifTriggerRedraw:
        obj.ViewObject.RedrawTrigger = True
    return obj

def addPolyLine2Document(shapeType , ifStore2Database=False , pointsList=None, materialNo=1 , closed=False , ifTriggerRedraw=True):
    obj = FreeCAD.ActiveDocument.getObject(shapeType)
    if not obj:    
        obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", shapeType)
        _Lines(obj)
        _ViewProviderDDAPolyLines(obj.ViewObject)
    
    if closed:
        if pointsList[0] != pointsList[-1]:
            pointsList.append(pointsList[0])
    
    if ifStore2Database:  # polyLines only lives in DL part
        database = getDatabaser4CurrentStage()
        from loadDataTools import DDAPolyLine
        database.add(shapeType, [0] ,[DDAPolyLine(pointsList,materialNo)] , ifRecord = True)
    
    if ifTriggerRedraw:
        obj.ViewObject.RedrawTrigger = True
    return obj


def addCircles2Document(shapeType , ifStore2Database=False , pts=None , ifRecord=False):
    obj = FreeCAD.ActiveDocument.getObject(shapeType)
    if not obj:    
        obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", shapeType)
        _Lines(obj)
        _ViewProviderDDAPoint(obj.ViewObject)
    
    if ifStore2Database:
        from loadDataTools import DDAPoint
        for p in pts:
            assert isinstance(p , DDAPoint)
            
        database = getDatabaser4CurrentStage()
        assert database
        database.add(shapeType, [0] , pts,ifRecord)
    
    obj.ViewObject.RedrawTrigger = True
    return obj
    
  
def makeCircle(center , radius, placement=None, face=False, support=None, fname = 'Circle'):
    '''makeCircle(radius,[placement,face,startangle,endangle]): Creates a circle
    object with given radius. If placement is given, it is
    used. If face is False, the circle is shown as a
    wireframe, otherwise as a face. If startangle AND endangle are given
    (in degrees), they are used and the object appears as an arc.'''
#    if placement: typecheck([(placement, FreeCAD.Placement)], "makeCircle")
    obj = FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython", fname)
    _Circle(obj)
    _ViewProviderDDAPoint(obj.ViewObject)
    obj.Radius = radius
    obj.ViewObject.Center = center
    obj.ViewObject.BlockNo = -1
    
    if not face: obj.ViewObject.DisplayMode = "Wireframe"
    color = getParam(fname+'Color')
#    if color:
    obj.ViewObject.LineColor = color
#    else:
#        FreeCAD.Console.PrintError('in DDA.makeCircle. color not found.\n')
#        obj.ViewObject.LineColor =( 0.0 , 0.0 , 0.0 , 1.0 )
    if placement: 
        print '**********placement is not None ************\n'
    else:
        print '**********placement is None ************\n'
    obj.Placement = placement
    formatObject(obj)
    select(obj)
    FreeCAD.ActiveDocument.recompute()
    
    setGraphRevised()
    
    return obj

def addCircle2Document(center , radius, placement=None, face=False, support=None, fname = 'Circle'):
#    if placement: typecheck([(placement, FreeCAD.Placement)], "addCircle2Document")
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", fname)
    _Circle(obj)
    _ViewProviderDDAPoint(obj.ViewObject)
    obj.Radius = radius
    obj.ViewObject.Center = center

#    if not face: obj.ViewObject.DisplayMode = "Wireframe"
#    color = getParam(fname+'Color')
#    obj.ViewObject.LineColor = color
#
#    formatObject(obj)
#    select(obj)    
#    setGraphRevised()    
    return obj
    
def addPolygon2Document(points , placement=None , support=None , fname = 'Polygon' , materialIndex = 0 , ifColorGradual = False):
    if not isinstance(points, list):
        nlist = []
        for v in points.Vertexes:
            nlist.append(v.Point)
        if fcgeo.isReallyClosed(points):
            nlist.append(points.Vertexes[0].Point)
        points = nlist
    obj = FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython", fname)  
    _Polygon(obj)
    _ViewProviderPolygon(obj.ViewObject)
    obj.Points = points
#    obj.ViewObject.ShapeColor = getParam(fname+'Color' , colorIndex)
#    obj.ViewObject.FaceColor = getParam(fname+'Color' , colorIndex)
    obj.ViewObject.Material = 1
    obj.ViewObject.DisplayMode = "Polygon"
    formatObject(obj)
    select(obj)
    setGraphRevised()    
    return obj
    
    
def refreshShape4Type(shapeType):
    obj = FreeCAD.ActiveDocument.getObject(shapeType)
    if obj:
        obj.ViewObject.RedrawTrigger = True
    
def refreshAllShapes():
    from DDADatabase import __allShapeTypes__
    for shapeType in __allShapeTypes__:
        refreshShape4Type(shapeType)

def updateTmpBoltElements():
    '''
    tmp function for compromise.
    setting a array of points to coin, coin didn't update if first n points is the same.
    use _ViewProviderDDALines.updateGeometry() and 'TunnelBoltsSelectionTool' for detail problem
    '''
    import DDADatabase
    import Part
    bolts = DDADatabase.tmpBoltElements
    lines = []
    for bolt in bolts:
        lines.append(Part.makeLine(bolt.startPoint , bolt.endPoint))
    shape = Part.Compound(lines)

    obj = FreeCAD.ActiveDocument.getObject('TmpBoltElement')
    if not obj:    
        obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", 'TmpBoltElement')
        _Lines(obj)
        obj.ViewObject.Proxy = 0
    obj.Shape = shape
    FreeCADGui.ActiveDocument.getObject("TmpBoltElement").LineColor = (1.0,0.0,0.0)

     
    
        
    
def refreshPolygons():
    obj = FreeCAD.ActiveDocument.getObject('Block')
    if not obj:    
        obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", 'Block')
    
    _Polygons(obj)
    _ViewProviderPolygons(obj.ViewObject)
    obj.Points = []   # trigger redraw
    
    obj.ViewObject.DisplayMode = "Shaded"
    obj.ViewObject.RedrawTrigger = True # trigger update colors
    
    return obj
    
def refreshBlockBoundaryLines():
    obj = FreeCAD.ActiveDocument.getObject('BlockBoundaryLines')
    if not obj:    
        obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", 'BlockBoundaryLines')
    
    _BlockBoundaryLines(obj)
    _ViewProviderBlockBoundaryLines(obj.ViewObject)
    obj.Points = []   # trigger redraw
    
    obj.ViewObject.RedrawTrigger = True # trigger update colors
    
##################################################
##
## there is a list contains points of all polygons 
##
##################################################
#    
#__polygons__ = []
#__blocksMaterials__ = []
#    
    
#    
#def initPolygonSets():
#    __polygons__ = []
#    
#def addPolygons2Document(points , placement=None , support=None , fname = 'Polygon'):
#    __polygons__.append(points)
#
#
#    
#def polygonsAddedDone():            
#    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", 'Block')  
#    _Polygons(obj)
#    obj.Points = []
#
#    import Part
#    faces = []
#    for pts in __polygons__:
#        edges = []
#        for i in range(len(pts)-1):
#            edges.append(Part.makeLine(pts[i] , pts[(i+1)]))
#            
#        wire = Part.Wire(edges)     
#        faces.append(Part.Face(wire))
##        print 'one face done'
#    obj.Shape = Part.Compound(faces)
#
#    
#    colors = []
##    __blocksMaterials__ = [1]*len(__polygons__)
#    for i in range(len(__polygons__)):
#        colors.append(__brushColors__[__blocksMaterials__[i]])
#        
#    _ViewProviderPolygons(obj.ViewObject)
#    obj.ViewObject.DisplayMode = "Shaded"
#    obj.ViewObject.Material = 1
#    
##    _ViewProviderPolygons(obj.ViewObject)
##    obj.ViewObject.Proxy = 0
##    formatObject(obj)
##    select(obj)
##    setGraphRevised()    
#    return obj
#            
#            

#---------------------------------------------------------------------------
# Python Features definitions
#---------------------------------------------------------------------------

class _ViewProviderDDA:
    "A generic View Provider for Draft objects"
        
    def __init__(self, obj):
        obj.Proxy = self
        self.appPart = obj.Object  # obj.Object.ViewObject is obj 
        self.owner = obj  # obj is ViewObject
        
        obj.setEditorMode('Deviation' , 2)
        obj.setEditorMode('BoundingBox' , 2)
        obj.setEditorMode('ControlPoints' , 2)
        obj.setEditorMode('DrawStyle' , 2)
        obj.setEditorMode('DisplayMode' , 2)
        obj.setEditorMode('Lighting' , 2)
        obj.setEditorMode('LineWidth' , 2)
        obj.setEditorMode('PointColor' , 2)
        obj.setEditorMode('PointSize' , 2)
        obj.setEditorMode('Selectable' , 2)
        obj.setEditorMode('ShapeColor' , 2)
        obj.setEditorMode('Transparency' , 2)
        obj.setEditorMode('Visibility' , 2)
        obj.setEditorMode('LineColor' , 2)

        obj.addProperty("App::PropertyBool", "IfShowAssist", "Base", "if show StartPoint and EndPoint")
        obj.setEditorMode('IfShowAssist' , 2)
        obj.addProperty("App::PropertyBool", "RedrawTrigger", "Base", "if show StartPoint and EndPoint")
        obj.setEditorMode('RedrawTrigger' , 2)
                
    def attach(self, obj):
        self.Object = obj.Object
        return

    def updateData(self, fp, prop):
        return

    def getDisplayModes(self, obj):
        modes = []
        return modes

    def setDisplayMode(self, mode):
        return mode

    def onChanged(self, vp, prop):
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

#    def setEdit(self, vp, mode):
#        FreeCADGui.runCommand("Draft_Edit")
#        return True
#
#    def unsetEdit(self, vp, mode):
#        if FreeCAD.activeDraftCommand:
#            FreeCAD.activeDraftCommand.finish()
#        return
    
#    def getIcon(self):
#        return(":/icons/Draft_Draft.svg")

class _ShapeModifier:
    '''
    shape modifier
    '''
    def __init__(self, obj):
        obj.addProperty("App::PropertyString", "RelatedDocumentName", "Base",
                        "document name")
        obj.addProperty("App::PropertyString", "RelatedObjectName", "Base",
                        "object name and No.")
        obj.addProperty("App::PropertyString", "RelatedSubElement", "Base",
                        "sub element name and No.")
        obj.addProperty("App::PropertyVectorList", "Points", "Base", 
                        "Vertexes of the polygon")
        obj.Proxy = self
        self.owner = obj
        
    def execute(self, fp):
        self.createGeometry(fp)

    def onChanged(self, fp, prop):
        if prop in ["Points"]:
            self.createGeometry(fp)
                        
    def createGeometry(self, fp):
        pts = self.owner.Points
        if len(pts)==2:
            p1 = Part.Vertex(pts[0])
            p2 = Part.Vertex(pts[1])
            fp.Shape = Part.Compound([p1,p2])

    
class _Wire:
    "The Wire object"
        
    def __init__(self, obj):
        obj.addProperty("App::PropertyVectorList", "Points", "Base",
                        "The vertices of the wire")
        obj.addProperty("App::PropertyBool", "Closed", "Base",
                        "If the wire is closed or not")
        obj.addProperty("App::PropertyLink", "Base", "Base",
                        "The base object is the wire is formed from 2 objects")
        obj.addProperty("App::PropertyLink", "Tool", "Base",
                        "The tool object is the wire is formed from 2 objects")
        obj.addProperty("App::PropertyVector","Start","Base",
                        "The start point of this line")
        obj.addProperty("App::PropertyVector","End","Base",
                        "The end point of this line")
        obj.addProperty("App::PropertyDistance","FilletRadius","Base","Radius to use to fillet the corners")
        obj.Proxy = self
        obj.Closed = False
        self.Type = "Wire"

    def execute(self, fp):
        self.createGeometry(fp)

    def onChanged(self, fp, prop):
        if prop in ["Points", "Closed", "Base", "Tool"]:
            self.createGeometry(fp)
                        
    def createGeometry(self, fp):
        plm = fp.Placement
        if fp.Base and (not fp.Tool):    #  make face
            FreeCAD.Console.PrintError("Checking , In DDA.py 's makeWire use fp.Base\n")
            if fp.Base.isDerivedFrom("Sketcher::SketchObject"):
                shape = fp.Base.Shape.copy()
                if fp.Base.Shape.isClosed():
                    shape = Part.Face(shape)
                fp.Shape = shape
                p = []
                for v in shape.Vertexes: p.append(v.Point)
                if fp.Points != p: fp.Points = p
        elif fp.Base and fp.Tool:       # concatenate 2 shapes : fp.Tool and fp.Base
            if ('Shape' in fp.Base.PropertiesList) and ('Shape' in fp.Tool.PropertiesList):
                sh1 = fp.Base.Shape.copy()
                sh2 = fp.Tool.Shape.copy()
                shape = sh1.fuse(sh2)
                if fcgeo.isCoplanar(shape.Faces):
                    shape = fcgeo.concatenate(shape)
                    fp.Shape = shape
                    p = []
                    for v in shape.Vertexes: p.append(v.Point)
                    if fp.Points != p: fp.Points = p
        elif fp.Points:
            if fp.Points[0] == fp.Points[-1]: 
                if not fp.Closed: fp.Closed = True
                fp.Points.pop()
            if fp.Closed and (len(fp.Points) > 2):
                shape = Part.makePolygon(fp.Points + [fp.Points[0]])
                shape = Part.Face(shape)
            else:
                edges = []
                pts = fp.Points[1:]
                lp = fp.Points[0]
                for p in pts:
                    edges.append(Part.Line(lp, p).toShape())
                    lp = p
                shape = Part.Wire(edges)
            fp.Shape = shape
        fp.Placement = plm

class _Lines:
    '''
    data class for _ViewProviderLines , 
    '''
    def __init__(self , obj):
#        obj.addProperty("App::PropertyVectorList", "Points", "Base", "Vertexes of the polygon")
        obj.Proxy = self
        self.Type = "Lines"
       
    def onChanged(self, fp, prop):
        "Do something when a property has changed"
        if prop in ["Points"]:
            self.createGeometry(fp)
 
    def execute(self, fp):
        "Do something when doing a recomputation, this method is mandatory"
        pass

    def createGeometry(self, fp):
        pass

class _BlockBoundaryLines:
    '''
    data class for _ViewProviderLines , 
    '''
    def __init__(self , obj):
        obj.addProperty("App::PropertyVectorList", "Points", "Base", "Vertexes of the polygon")
        obj.Proxy = self
        self.Type = "Lines"
       
    def onChanged(self, fp, prop):
        "Do something when a property has changed"
        if prop in ["Points"]:
            self.createGeometry(fp)
 
    def execute(self, fp):
        "Do something when doing a recomputation, this method is mandatory"
        pass

    def createGeometry(self, fp):
        pass

        
class _Polygons:
    def __init__(self , obj):
        obj.addProperty("App::PropertyVectorList", "Points", "Base", "Vertexes of the polygon")
        obj.Proxy = self
        self.Type = "Polygon"
       
    def onChanged(self, fp, prop):
        "Do something when a property has changed"
        if prop in ["Points"]:
            self.createGeometry(fp)
 
    def execute(self, fp):
        "Do something when doing a recomputation, this method is mandatory"
        FreeCAD.Console.PrintMessage("Recompute Python Box feature\n")
        self.createGeometry(fp)

    def createGeometry(self, fp):
        import Part
        from DDADatabase import df_inputDatabase
        blocks = df_inputDatabase.blocks
        
        faces = []
        for block in blocks:
            pts = [(p[1],p[2],-1) for p in block.vertices]
            if pts[0]!=pts[-1]:
                pts.append(pts[0])
            edges = []
            for i in range(len(pts)-1):
                edges.append(Part.makeLine(pts[i] , pts[(i+1)]))
                

            try:
                wire = Part.Wire(edges)     
                faces.append(Part.Face(wire))
            except:
                raise
#            print 'one face done'
        fp.Shape = Part.Compound(faces)

        
class _Circle:
    "The Circle object"
        
    def __init__(self, obj):
        obj.Proxy = self
        self.owner = obj
        obj.addProperty("App::PropertyDistance","Radius","Base",
                        "Radius of the circle")


    def execute(self, fp):
        self.createGeometry(fp)

    def onChanged(self, fp, prop):
        if prop in ["Radius"]:
            self.createGeometry(fp)
                        
    def createGeometry(self,fp):
        return
        import Part
        c = self.owner.ViewObject.Center
        shape = Part.makeCircle(fp.Radius,self.owner.ViewObject.Center,Vector(0,0,1))
#        center = Part.Vertex(self.owner.ViewObject.Center)
        tmp = Vector(c[0] , c[1] , c[2])
        p1 = Vector(tmp[0]-self.owner.Radius/2 , tmp[1] , tmp[2])
        p2 = Vector(tmp[0]+self.owner.Radius/2 , tmp[1] , tmp[2])
        p3 = Vector(tmp[0] , tmp[1]-self.owner.Radius/2 , tmp[2])
        p4 = Vector(tmp[0] , tmp[1]+self.owner.Radius/2 , tmp[2])
        line1 = Part.makeLine(p1 , p2)
        line2 = Part.makeLine(p3 , p4)

#        print self.owner.ViewObject.Center
#        self.owner.ViewObject.PointSize = 100
        fp.Shape = Part.Compound([shape,line1 , line2])
#        fp.Shape = center

class _ViewProviderDDAPoint(_ViewProviderDDA):
    def __init__(self, obj ):
        obj.Proxy = self
        self.owner = obj  # this viewObject
        obj.addProperty("App::PropertyVector", "Center", "Base", "material of the additional lines")
        _ViewProviderDDA.__init__(self, obj)

    def onChanged(self, vp, prop):
        if prop == "RedrawTrigger":
            self.updateGeometry()

    def updateGeometry(self):
        label = self.appPart.Label
        
        # confirm color
        color = getParam(label+'Color')
        assert color
        self.color.rgb.setValue(color[0],color[1],color[2])
        
        # get centers
        import DDADatabase
        database = getDatabaser4CurrentStage()
        assert database
        
        if label=='FixedPoint':
            points = database.fixedPoints
        elif label=='MeasuredPoint':
            points = database.measuredPoints
        elif label=='LoadingPoint':
            points = database.loadingPoints
        elif label=='HolePoint':
            points = database.holePoints
            
        pts = [ p for p in points if p.visible]
        self.updateCircels(pts)
        
    def updateCircels(self, points):
        import math
        rad = math.pi/180.0
        pts = []
        nums = []
        sum = 0
        
        radius = __radius4Points__
        for p in points:
            tpts = []
            # circle
            for angle in [i*4 for i in range(91)]:
                tpts.append((p.x+radius*math.cos(float(angle)*rad) \
                            , p.y+radius*math.sin(float(angle)*rad) , 0))
            # cross
            tpts.append((p.x-radius , p.y , 0))
            tpts.append((p.x , p.y , 0))
            tpts.append((p.x , p.y+radius , 0))
            tpts.append((p.x , p.y-radius , 0))
            
            pts.extend(tpts)
            nums.extend(range(sum , sum+len(tpts)))
            sum+=len(tpts)
            nums.append(-1)
            
        if len(pts)==0:
            self.rootNode.whichChild = coin.SO_SWITCH_NONE
        else:
            self.rootNode.whichChild = 0
            self.data.point.setValues(0 , len(pts),pts)
            self.lineset.coordIndex.setValues(0,len(nums), nums)   
        
    def attach(self , obj):
        self.pointMaker = coin.SoSeparator()
        
        self.drawStyle = coin.SoDrawStyle()
#        self.drawStyle.style = coin.SoDrawStyle.LINES
        self.drawStyle.lineWidth = 1
#        self.drawStyle.pointSize = 3
        self.pointMaker.addChild(self.drawStyle)
        
        self.norm = coin.SoNormal()
        self.norm.vector.setValue(0,0,1)
        self.pointMaker.addChild(self.norm)
        
        coin.SoNormalBinding()  # without this , color will be very ugly
        self.normalBinding = coin.SoNormalBinding()
        self.normalBinding.value = coin.SoNormalBinding.OVERALL
        self.pointMaker.addChild(self.normalBinding)
        
        self.color = coin.SoBaseColor()
        self.color.rgb.setValue(1,0,0)
        self.pointMaker.addChild(self.color)

        self.data = coin.SoCoordinate3()
        self.pointMaker.addChild(self.data)
        
        t=coin.SoType.fromName("SoBrepEdgeSet")
        self.lineset = t.createInstance()
        self.pointMaker.addChild(self.lineset)
         
        self.rootNode = coin.SoSwitch()
        self.rootNode.addChild(self.pointMaker)
         
        obj.addDisplayMode(self.rootNode,"PointMaker")        

    def getDisplayModes(self,obj):
        
        "Return a list of display modes."
        modes=[]
        modes.append("PointMaker")
        return modes
    
    def getDefaultDisplayMode(self):
        "Return the name of the default display mode. It must be defined in getDisplayModes."
        return "PointMaker"
    
    def setDisplayMode(self,mode):
        return mode

class _ViewProviderDDALines(_ViewProviderDDA):
    def __init__(self, obj ):
        obj.Proxy = self
        self.owner = obj  # this viewObject
        obj.addProperty("App::PropertyInteger", "Material", "Base", "material of the additional lines")
        obj.addProperty("App::PropertyVector", "StartPoint", "Base", "start point of the line")
        obj.addProperty("App::PropertyVector", "EndPoint", "Base", "end point of the line")
        obj.setEditorMode("StartPoint" , 2)
        obj.setEditorMode("EndPoint" , 2)
        
        
        self.ifUpdateLine4StartEndPoint=True
        _ViewProviderDDA.__init__(self, obj)        
        
    def attach(self , obj):
        self.lines = coin.SoSeparator()
        
        self.drawStyle = coin.SoDrawStyle()
#        self.drawStyle.style = coin.SoDrawStyle.LINES
        self.drawStyle.lineWidth = 1
        self.drawStyle.pointSize = 3
        self.lines.addChild(self.drawStyle)
        
        self.norm = coin.SoNormal()
        self.norm.vector.setValue(0,0,1)
        self.lines.addChild(self.norm)
        
        coin.SoNormalBinding()  # without this , color will be very ugly
        self.normalBinding = coin.SoNormalBinding()
        self.normalBinding.value = coin.SoNormalBinding.OVERALL
        self.lines.addChild(self.normalBinding)
        
        # set color for block
        self.matColors = coin.SoMaterial()
        self.lines.addChild(self.matColors)

        self.tmpMatBind = coin.SoMaterialBinding()
        self.tmpMatBind.value = coin.SoMaterialBinding.PER_PART
        self.lines.addChild(self.tmpMatBind)

        # point
        self.data = coin.SoCoordinate3()
        self.lines.addChild(self.data)
        
        t=coin.SoType.fromName("SoBrepEdgeSet")
        self.lineset = t.createInstance()
        self.lines.addChild(self.lineset)
        
        self.rootNode = coin.SoSwitch()
        self.rootNode.addChild(self.lines)
         
        obj.addDisplayMode(self.rootNode,"Lines")        

    def updateGeometry(self):
        label = self.appPart.Label
        import DDADatabase
        
        if label == 'JointLine':
            assert __currentStage__ == 'DL'
            
            jointLines = DDADatabase.dc_inputDatabase.jointLines 
            lines = [line for line in jointLines if line.visible]
            self.updateLines(lines)
        elif label == 'BoltElement':
            database = getDatabaser4CurrentStage()
            bolts = database.boltElements
            lines = [line for line in bolts if line.visible]
            self.updateLines(lines)
#        elif label == 'TmpBoltElement':
#            bolts = DDADatabase.tmpBoltElements
#            lines = [line for line in bolts if line.visible]
##            if len(lines)>1:  # if the first point stay same ,coin won't update
##                idx = -1
##                t = lines[idx]
##                lines[idx] = lines[0]
##                lines[idx] = t
#            for line in lines:
#                print line.startPoint , ' ' , line.endPoint
#            self.updateLines(lines)
            
    def updateLines(self, lines):  
        '''
        :param lines: DDALines
        '''
        colors = []
        pts = []
        
        if len(lines)==0:
            self.rootNode.whichChild = coin.SO_SWITCH_NONE
        else:
            self.rootNode.whichChild = 0
        
        for line in lines:
            pts.extend([line.startPoint , line.endPoint])
            col = getParam( self.appPart.Label+'Color' , line.materialNo)
            assert col
            colors.append(col) 
           
        self.data.point.setValues(0 , len(pts),pts)
        self.data.point.startEditing()
        self.data.point.finishEditing()
        self.matColors.diffuseColor.setValues(0,len(colors),colors)
        
        nums = []
        for i in range(len(pts)/2):
            nums.append(2*i)
            nums.append(2*i+1)
            nums.append(-1)
        
        self.lineset.coordIndex.setValues(0,len(nums), nums)
        self.lineset.coordIndex.startEditing()
        self.lineset.coordIndex.finishEditing()

    def showAssistance(self):
        '''
        show selected line's StartPoint and EndPoint
        '''
        self.owner.setEditorMode('StartPoint' , 0)
        self.owner.setEditorMode('EndPoint' , 0)
        
        self.ifUpdateLine4StartEndPoint = False
        try:
            objName , objNo , no = self.getOjbName_No_EdgeNo()
        except:
            return
#            print objName , objNo , no
            
        from DDADatabase import dc_inputDatabase

        if no == -1 :
            return
        try:
            pnt= dc_inputDatabase.jointLines[no-1].startPoint
            self.owner.StartPoint = Vector(pnt[0] , pnt[1] , pnt[2])
        except:
            print 'whowAssistance point error : ' , pnt , ' no : ' , no
        try:
            pnt= dc_inputDatabase.jointLines[no-1].endPoint
            self.owner.EndPoint = Vector(pnt[0] , pnt[1] , pnt[2])
        except:
            print 'whowAssistance point error : ' , pnt , ' no : ' , no
            
        try:
            self.owner.Material = dc_inputDatabase.jointLines[no-1].materialNo
        except:
            print  'whowAssistance material error : idxes No. ' , no-1 
            
        self.ifUpdateLine4StartEndPoint = True

    def hideAssistance(self):
        '''
        show selected line's StartPoint and EndPoint
        '''
        self.owner.setEditorMode('StartPoint' , 2)
        self.owner.setEditorMode('EndPoint' , 2)      
    
    def getOjbName_No_EdgeNo(self):
        '''
        Gui.Seletion's selected edge of this object
        '''
        sel=FreeCADGui.Selection.getSelectionEx() ## give a list of SelectionObject. Note, this is empty if nothing is selected!
        s=sel[0]
        objNo = 0
        objName = s.Object.Label
        tmp = len(objName)-1
        while tmp>0:
            if not(objName[tmp]>='0' and objName[tmp]<='9'):
                break
            tmp-=1
        tmpNo = objName[tmp+1:]
        if len(tmpNo)>0:
            objNo = int(tmpNo)
        objName = objName[:tmp+1]
        
        
        names = s.SubElementNames # sub-element names
        if len(names)<2 and len(names[0])==0:
            print 'obj : ' ,  objName , ' sub : ' , names
            FreeCAD.Console.PrintError('unknown edge in _ViewProviderJointLines')
            return objName , -1 , -1
        i = 0
        name = names[0]
        for i in range(len(name)):
            if name[i] >='0' and name[i]<='9':
                break
            i+=1
        num = name[i:]
        print 'selected Edge : ' , name , '  ->  ' , num
        return objName , objNo , int(num)        
    
    def updateLine4StartEndPoint(self, vp, prop):
        from DDADatabase import dc_inputDatabase
        from loadDataTools import DDALine
        objName , objNo , num = self.getOjbName_No_EdgeNo()
        tmpLine = dc_inputDatabase.jointLines[num-1]
        p1 = vp.getPropertyByName('StartPoint')
        p2 = vp.getPropertyByName('EndPoint') 
        sp = (p1[0] , p1[1] , 0)
        ep = (p2[0] , p2[1] , 0)
        dc_inputDatabase.changeVertices('JointLine', [num-1]\
                    , [DDALine(sp,ep,tmpLine.materialNo)] , ifRecord=True)
        self.updateGeometry()
    
    def onChanged(self, vp, prop):
        "Here we can do something when a single property got changed"
        FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
        
        from DDADatabase import dc_inputDatabase
        from loadDataTools import DDALine
        
        if prop == "RedrawTrigger":
            self.updateGeometry()     
        elif prop == 'Material':
            if not self.ifUpdateLine4StartEndPoint:
                return
            objName , objNo , subIdx = self.getOjbName_No_EdgeNo()
            materialNo = vp.getPropertyByName('Material')
            material2 = dc_inputDatabase.jointLines[subIdx].materialNo
            if dc_inputDatabase.jointLines[subIdx].materialNo \
                == materialNo:
                return
            
            dc_inputDatabase.changeMaterial(self.appPart.Label, [subIdx-1]\
                    , materialNo , ifRecord=True)
            self.updateGeometry() 
        elif prop == 'StartPoint':
            if self.ifUpdateLine4StartEndPoint:
                self.updateLine4StartEndPoint(vp, prop)
        elif prop == 'EndPoint':
            if self.ifUpdateLine4StartEndPoint:
                self.updateLine4StartEndPoint(vp, prop)
        elif prop == 'IfShowAssist':
            if self.owner.IfShowAssist:
                self.showAssistance()
            else:
                self.hideAssistance()         
       
    def getDisplayModes(self,obj):
        
        "Return a list of display modes."
        modes=[]
        modes.append("Lines")
        return modes
    
    def getDefaultDisplayMode(self):
        "Return the name of the default display mode. It must be defined in getDisplayModes."
        return "Lines"
    
    def setDisplayMode(self,mode):
        return mode

class _ViewProviderDDAPolyLines(_ViewProviderDDA):
    def __init__(self, obj ):
        obj.Proxy = self
        self.owner = obj  # this viewObject
        obj.addProperty("App::PropertyInteger", "Material", "Base", "material of the additional lines")
        _ViewProviderDDA.__init__(self, obj)        
        
    def attach(self , obj):
        self.lines = coin.SoSeparator()
        
        self.drawStyle = coin.SoDrawStyle()
#        self.drawStyle.style = coin.SoDrawStyle.LINES
        self.drawStyle.lineWidth = 1
        self.drawStyle.pointSize = 3
        self.lines.addChild(self.drawStyle)
        
        self.norm = coin.SoNormal()
        self.norm.vector.setValue(0,0,1)
        self.lines.addChild(self.norm)
        
        coin.SoNormalBinding()  # without this , color will be very ugly
        self.normalBinding = coin.SoNormalBinding()
        self.normalBinding.value = coin.SoNormalBinding.OVERALL
        self.lines.addChild(self.normalBinding)
        
        # set color for block
        self.matColors = coin.SoMaterial()
        self.lines.addChild(self.matColors)

        self.tmpMatBind = coin.SoMaterialBinding()
        self.tmpMatBind.value = coin.SoMaterialBinding.OVERALL
        self.lines.addChild(self.tmpMatBind)
        
        # points
        self.data = coin.SoCoordinate3()
        self.lines.addChild(self.data)
        
        t=coin.SoType.fromName("SoBrepEdgeSet")
        self.lineset = t.createInstance()
        self.lines.addChild(self.lineset)
         
        self.rootNode = coin.SoSwitch()
        self.rootNode.addChild(self.lines)
        
        obj.addDisplayMode(self.rootNode,"PolyLines")        

    def updateGeometry(self):
        import DDADatabase
        
        lines = None
        label = self.appPart.Label  # get object' name
         
        if label == 'BoundaryLine':
            lines = DDADatabase.dl_database.boundaryNodes
        elif label == 'BorderLine':
            lines = DDADatabase.dl_database.borderNodes
        elif label == 'AdditionalLine':
            database = getDatabaser4CurrentStage()
            lines = database.additionalLines
        assert lines
        
        tmpLines = [line for line in lines if line.visible]
        
        color = getParam(label+'Color')
        assert color
        self.matColors.diffuseColor.setValue(color)
        self.updateLines(tmpLines)
    
            
    def updateLines(self, lines):
        '''
        :param lines: DDAPolyLines
        '''
        nums = []
        sum = 0
        pts = []
        
        if len(lines)==0:
            self.rootNode.whichChild = coin.SO_SWITCH_NONE
        else:
            self.rootNode.whichChild = 0
        
        for pline in lines:
            tpts = list(pline.pts)
            pts.extend(tpts)
            nums.extend(range(sum , sum+len(tpts)))
            nums.append(-1)
            sum+= len(tpts)
            
        self.data.point.setValues(0 , len(pts),pts)
        self.lineset.coordIndex.setValues(0,len(nums), nums)  
         
    def onChanged(self, vp, prop):
        "Here we can do something when a single property got changed"
        FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
        if prop == "RedrawTrigger":
            self.updateGeometry()
        elif prop == 'Material':
            from DDADatabase import dc_inputDatabase
            objName , objNo , subIdx = self.getOjbName_No_EdgeNo()
            materialNo = p2 = vp.getPropertyByName('Material')
            dc_inputDatabase.changeMaterial(self.appPart.Label, [subIdx-1]\
                    , materialNo , ifRecord=True)
            self.updateGeometry()

       
    def getDisplayModes(self,obj):
        
        "Return a list of display modes."
        modes=[]
        modes.append("PolyLines")
        return modes
    
    def getDefaultDisplayMode(self):
        "Return the name of the default display mode. It must be defined in getDisplayModes."
        return "PolyLines"
    
    def setDisplayMode(self,mode):
        return mode

class _ViewProviderBlockBoundaryLines(_ViewProviderDDA):
    def __init__(self, obj ):        
        _ViewProviderDDA.__init__(self, obj)        
        
    def attach(self , obj):
        self.Object = obj.Object
        self.lines = coin.SoSeparator()
        
        self.drawStyle = coin.SoDrawStyle()
#        self.drawStyle.style = coin.SoDrawStyle.LINES
        self.drawStyle.lineWidth = 1
        self.drawStyle.pointSize = 3
        self.lines.addChild(self.drawStyle)
        
        self.norm = coin.SoNormal()
        self.norm.vector.setValue(0,0,1)
        self.lines.addChild(self.norm)
        
        coin.SoNormalBinding()  # without this , color will be very ugly
        self.normalBinding = coin.SoNormalBinding()
        self.normalBinding.value = coin.SoNormalBinding.OVERALL
        self.lines.addChild(self.normalBinding)
        
        # set color for lines
        __baseColor__ = coin.SoBaseColor()
        __baseColor__.rgb.setValue( 0.0 , 0.0 , 0.0 )        
        self.lines.addChild(__baseColor__)
        
        # point
        self.data = coin.SoCoordinate3()
        self.lines.addChild(self.data)
        
        self.lineset=coin.SoLineSet()
        self.lines.addChild(self.lineset)
         
        obj.addDisplayMode(self.lines,"Lines")        

    def updateGeometry(self):
        import DDADatabase
        
        blocks = DDADatabase.df_inputDatabase.blocks
        self.updateLines(blocks)
        
            
    def updateLines(self, blocks):  
        '''
        :param lines: DDALines
        '''
        colors = []
        pts = []
        nums = []
        for block in blocks:
            tpts = [(p[1],p[2],0) for p in block.vertices]
            if tpts[0] != tpts[-1]: tpts.append(tpts[0])
            pts.extend(tpts)
            nums.append(len(tpts))
           
        self.data.point.setValues(0 , len(pts),pts)
        self.lineset.numVertices.setValues(0,len(nums), nums)
    
    def onChanged(self, vp, prop):
        "Here we can do something when a single property got changed"
        FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
        
        from DDADatabase import dc_inputDatabase
        
        if prop == "RedrawTrigger":
            self.updateGeometry()
       
    def getDisplayModes(self,obj):
        
        "Return a list of display modes."
        modes=[]
        modes.append("Lines")
        return modes
    
    def getDefaultDisplayMode(self):
        "Return the name of the default display mode. It must be defined in getDisplayModes."
        return "Lines"
    
    def setDisplayMode(self,mode):
        return mode
    

class _ViewProviderAdditionalLines(_ViewProviderDDALines):
    '''
    provide graph for additional lines
    '''
    def __init__(self, obj ):
        _ViewProviderDDALines.__init__(self, obj)
        obj.setEditorMode("Points" , 0)    
        
        
class _ViewProviderBoundaryLines(_ViewProviderDDALines):
    '''
    provide graph for additional lines
    '''
    def __init__(self, obj ):
        _ViewProviderDDALines.__init__(self, obj)
        obj.setEditorMode("Points" , 0)    


class _ViewProviderBoltElement(_ViewProviderDDALines):
    def __init__(self, obj ):
        obj.Proxy = self
        self.owner = obj  # this viewObject
        obj.addProperty("App::PropertyVector", "StartPoint", "Base", "start point of the line")
        obj.addProperty("App::PropertyVector", "EndPoint", "Base", "end point of the line")
        obj.setEditorMode("Points" , 2)
        _ViewProviderDDALines.__init__(self, obj)    

    def updateLines(self, vp, prop):  
        _ViewProviderDDALines.updateLines(self, vp, prop)

class _ViewProviderMaterialLine(_ViewProviderDDALines):
    def __init__(self, obj ):
        obj.Proxy = self
        obj.addProperty("App::PropertyVector", "StartPoint", "Base", "start point of the line")
        obj.addProperty("App::PropertyVector", "EndPoint", "Base", "end point of the line")
        obj.addProperty("App::PropertyInteger", "Material", "Base", "material")
        
#class _ViewProviderJointLines(_ViewProviderDDALines):
#    '''
#    A view provider for the polygon object
#    '''
#    def __init__(self, obj ):
#        obj.Proxy = self
#        self.owner = obj  # this viewObject
#        obj.addProperty("App::PropertyVector", "StartPoint", "Base", "start point of the line")
#        obj.addProperty("App::PropertyVector", "EndPoint", "Base", "end point of the line")
#        obj.setEditorMode("Points" , 2)
#        obj.setEditorMode("StartPoint" , 2)
#        obj.setEditorMode("EndPoint" , 2)
#        _ViewProviderDDALines.__init__(self, obj)
#
#    def updateLines(self , fp , prop):
#        '''
#        "If a property of the handled feature has changed we have the chance to handle this here"
#        :param fp:  the handled feature
#        :param prop: property name
#        '''
#        if prop == "Points":
##            s = fp.getPropertyByName("Points")
##            pts = s
#            
#            from DDADatabase import dc_inputDatabase
#            pts = []
#            for line in dc_inputDatabase.jointLines:
#                pts.append(line.startPoint)
#                pts.append(line.endPoint)
#                        
#            self.data.point.setValues(0 , len(pts),pts)
#            
#            nums = []
#            for i in range(len(pts)/2):
#                nums.append(2*i)
#                nums.append(2*i+1)
#                nums.append(-1)
#            
#            self.lineset.coordIndex.setValues(0,len(nums), nums)
#
#        
#        file = open(__currentProjectPath__+'/testVector.txt' , 'ab')
#        for i in range(len(pts)/2):
#            file.write('%f %f %f %f\n'%(pts[2*i].x,pts[2*i].y,pts[2*i+1].x,pts[2*i+1].y))
#        file.close()                
#
#
#    def showAssistance(self):
#        '''
#        show selected line's StartPoint and EndPoint
#        '''
#        self.owner.setEditorMode('StartPoint' , 0)
#        self.owner.setEditorMode('EndPoint' , 0)
#        try:
#            objName , objNo , no = self.getOjbName_No_EdgeNo()
#        except:
#            return
##            print objName , objNo , no
#            
#        if no == -1 :
#            return
#        try:
#            pnt= self.data.point[2*(no-1)]
#            self.owner.StartPoint = Vector(pnt[0] , pnt[1] , pnt[2])
#        except:
#            print pnt , ' no : ' , no
#        try:
#            pnt= self.data.point[2*(no-1)+1]
#            self.owner.EndPoint = Vector(pnt[0] , pnt[1] , pnt[2])
#        except:
#            print pnt , ' no : ' , no
#
#    def hideAssistance(self):
#        '''
#        show selected line's StartPoint and EndPoint
#        '''
#        self.owner.setEditorMode('StartPoint' , 2)
#        self.owner.setEditorMode('EndPoint' , 2)      
#    
#    def getOjbName_No_EdgeNo(self):
#        '''
#        Gui.Seletion's selected edge of this object
#        '''
#        sel=FreeCADGui.Selection.getSelectionEx() ## give a list of SelectionObject. Note, this is empty if nothing is selected!
#        s=sel[0]
#        objNo = 0
#        objName = s.Object.Label
#        tmp = len(objName)-1
#        while tmp>0:
#            if not(objName[tmp]>='0' and objName[tmp]<='9'):
#                break
#            tmp-=1
#        tmpNo = objName[tmp+1:]
#        if len(tmpNo)>0:
#            objNo = int(tmpNo)
#        objName = objName[:tmp+1]
#        
#        
#        names = s.SubElementNames # sub-element names
#        if len(names)<2 and len(names[0])==0:
#            print 'obj : ' ,  objName , ' sub : ' , names
#            FreeCAD.Console.PrintError('unknown edge in _ViewProviderJointLines')
#            return objName , -1 , -1
#        i = 0
#        name = names[0]
#        for i in range(len(name)):
#            if name[i] >='0' and name[i]<='9':
#                break
#            i+=1
#        num = name[i:]
#        print 'selected Edge : ' , name , '  ->  ' , num
#        return objName , objNo , int(num)        
#    
#    def onChanged(self, vp, prop):
#        "Here we can do something when a single property got changed"
#        FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
#        _ViewProviderDDALines.onChanged(self, vp, prop)   # handle color or all lines
#        
#        from DDADatabase import dc_inputDatabase
#        
#        if prop == 'StartPoint':
#            objName , objNo , num = self.getOjbName_No_EdgeNo()
#            pts = vp.getPropertyByName('Points')
#            pts[2*(num-1)] = vp.getPropertyByName('StartPoint')
#            self.owner.Points = pts 
#            jointLineChanges = dc_inputDatabase.jointLinesChanges
#            jointLineChanges[(objNo , num)] = (vp.getPropertyByName('StartPoint'),vp.getPropertyByName('EndPoint'))
##            recomputeDocument()
#        elif prop == 'EndPoint':
#            objName , objNo , num = self.getOjbName_No_EdgeNo()
#            pts = vp.getPropertyByName('Points')
#            pts[2*(num-1)+1] = vp.getPropertyByName('EndPoint')
#            self.owner.Points = pts
#            jointLineChanges = dc_inputDatabase.jointLinesChanges
#            jointLineChanges[(objNo , num)] = (vp.getPropertyByName('StartPoint'),vp.getPropertyByName('EndPoint'))
##            recomputeDocument()
#        elif prop == 'IfShowAssist':
#            if self.owner.IfShowAssist:
#                self.showAssistance()
#            else:
#                self.hideAssistance()         

       
class _ViewProviderPolygons(_ViewProviderDDA):
    '''
    A view provider for the polygon object
    '''
    def __init__(self, obj ):
        obj.addProperty("App::PropertyInteger","Material","Base","Material of the block")
        obj.addProperty("App::PropertyInteger","BlockNo","Base","Material of the block")
        obj.setEditorMode("Material" , 0)
        obj.setEditorMode("BlockNo" , 1)
        obj.Proxy = self
        _ViewProviderDDA.__init__(self, obj)
        self.ifUpdateLine4StartEndPoint=True

    def updateData(self , fp , prop):
        '''
        "If a property of the handled feature has changed we have the chance to handle this here"
        :param fp:  the handled feature
        :param prop: property name
        '''
        pass
    
    def getObjName_SubIdx(self):
        sels=FreeCADGui.Selection.getSelectionEx()
        assert len(sels)>0 
        objName = sels[0].SubElementNames[0]
        obj , idx = getRealTypeAndIndex(objName)
        return sels[0].ObjectName , idx 

    def showAssistance(self):
        '''
        show selected line's StartPoint and EndPoint
        '''
        self.ifUpdateLine4StartEndPoint=False

        sels=FreeCADGui.Selection.getSelectionEx()
        assert len(sels)>0 and len(sels[0].SubElementNames)==1
        objName = sels[0].SubElementNames[0]
        
        self.owner.setEditorMode('BlockNo' , 1)
        self.owner.setEditorMode('Material' , 0)
        objN , idx = getRealTypeAndIndex(objName)
        
        self.owner.BlockNo = idx

        from DDADatabase import df_inputDatabase
        self.owner.Material = df_inputDatabase.blocks[idx-1].materialNo
        
        self.ifUpdateLine4StartEndPoint=True

    def hideAssistance(self):
        '''
        show selected line's StartPoint and EndPoint
        '''
        self.owner.setEditorMode('BlockNo' , 2)
        self.owner.setEditorMode('Material' , 2)      

    def updateGeometry(self):
        colors = []
        from DDADatabase import df_inputDatabase
        blocks = df_inputDatabase.blocks
        for i in [block.materialNo for block in blocks]:
            colors.append(__brushColors__[i])
        self.owner.DiffuseColor = colors

    def onChanged(self, vp, prop):
        "Here we can do something when a single property got changed"
        FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
        import random
        if prop == "RedrawTrigger":
            self.updateGeometry()
        elif prop == 'IfShowAssist':
            if self.owner.IfShowAssist:
                self.showAssistance()
            else:
                self.hideAssistance()
        elif prop == 'Material':
            if self.ifUpdateLine4StartEndPoint:
                from DDADatabase import df_inputDatabase
                objName , subIdx = self.getObjName_SubIdx()
                subIdx-=1
                materialNo = vp.getPropertyByName('Material')
                material2 = df_inputDatabase.blocks[subIdx].materialNo
                if df_inputDatabase.blocks[subIdx].materialNo == materialNo:
                    return
                
                df_inputDatabase.changeMaterial('Block', [subIdx], materialNo , ifRecord=True)
                self.updateGeometry()                          
            
class _ViewProviderWire(_ViewProviderDDA):
    "A View Provider for the Wire object"
    def __init__(self, obj):
        _ViewProviderDDA.__init__(self, obj)

    def attach(self, obj):
        self.Object = obj.Object
        col = coin.SoBaseColor()
        col.rgb.setValue(obj.LineColor[0],
                         obj.LineColor[1],
                         obj.LineColor[2])
        self.coords = coin.SoCoordinate3()
        self.pt = coin.SoAnnotation()
        self.pt.addChild(col)
        self.pt.addChild(self.coords)
        self.pt.addChild(dimSymbol())
        
    def updateData(self, obj, prop): # updataData 就是增加结点，所以只处理最后一个就行了
        if prop == "Points":
#            if obj.Points:
#                p = obj.Points[-1]
#                self.coords.point.setValue((p.x, p.y, p.z))
            if obj.Points:
                self.coords.point.setValues(0 , len(obj.Points),obj.Points)
            
        return

    def onChanged(self, vp, prop):
        if prop == "EndArrow":
            rn = vp.RootNode
            if vp.EndArrow:
                rn.addChild(self.pt)
            else:
                rn.removeChild(self.pt)
        return

    def claimChildren(self):
        return [self.Object.Base, self.Object.Tool]
    
class SelectionObserver:
    def __init__(self):
        self.lock = False   #  同步锁
        
        self.__docName = None
        self.__objName = None
        self.__subElementName = None
        
        
    def __refreshObjs(self):
        '''
        remove and add objs that obj.ViewObject.IfShowAssist == True
        '''
        for tmp in self.objs:  
            obj = tmp[0] 
            names = tmp[1]
            FreeCADGui.Selection.removeSelection(obj , names[0])
            FreeCADGui.Selection.addSelection(obj , names[0])
         
    def __hideProperties(self,sels):
        print 'SelectionObserver -> hide properties '
        FreeCAD.Console.PrintMessage('FreeCAD Message : Seleted objects num > 1\n')
        for s in sels:  # 获取还在显示辅助信息的对象
            if s.Object.ViewObject.IfShowAssist == True and len(s.SubElementNames)>0 :
                s.Object.ViewObject.IfShowAssist = False
                self.objs.append(( s.Object , s.SubElementNames[0] ))
        self.__refreshObjs()
        
    def __showproperties4OneObject(self , sels):
        if sels[0].Object.ViewObject.IfShowAssist == True: # tigger the 'ViewObject.IfShowAssist' 
            sels[0].Object.ViewObject.IfShowAssist = False
        
        sels[0].Object.ViewObject.IfShowAssist = True
        self.objs.append(( sels[0].Object , sels[0].SubElementNames[0] ))
        self.__refreshObjs()
        
    def __keepObjectNames(self , docName , objName , subElementName):
        self.__docName = docName
        self.__objName = objName   
        self.__subElementName = subElementName 
        print 'selected ObjectName saved %s -> %s ->%s'%(docName , objName , subElementName)
        
    def __clearObjectNames(self):     
        self.__docName = None
        self.__objName = None
        self.__subElementName = None   
        print 'selected ObjectName cleared'
        
        
    def __clearShapeModifiers(self):
        removeShapeModifier()
        removeShapeMover()
        print 'clear shape modifying nodes successfully'
        
#    def clearSelection(self,doc):
#        global __clearShapeModifyingNodes__
#        if __clearShapeModifyingNodes__:
#            self.__clearShapeModifiers()
#            __clearShapeModifyingNodes__ = False

    def __checkIfShapeModifyingNodesSelected(self):
        flag = False
        sels=FreeCADGui.Selection.getSelectionEx()
        for sel in sels:
            if sel.ObjectName =='ShapeModifier' or sel.ObjectName == 'ShapeMover':
                flag = True
                break
        return flag
        
    def addSelection(self, doc, obj, sub, pos=None):
        print 'entering SelectionObserver'
        print '%s ->  %s  -> %s'%(doc , obj , sub)
        if not doc or len(doc)==0  or not obj or len(obj)==0 :
            return
        if self.lock==True:  # 由于FreeCAD先更新propertybrowser，后调用此函数，所以为了正确显示，有时需要连续两次从selectionNode添加或删除obj
            print 'addSelecion locked, return'
            return
        
        self.lock = True
        self.objs = []
        sels=FreeCADGui.Selection.getSelectionEx()
        
        # handle selection
        if len(sels)>1 or len(sels[0].SubElementNames)>1:  # 当被选物体多于两个，隐藏坐标信息
            self.__clearShapeModifiers()
            self.__hideProperties(sels)
        elif len(sels[0].SubElementNames)>0: #  only one object is selected , update messages in properties in property browser
            self.__keepObjectNames(doc, obj , sub)
            self.__showproperties4OneObject(sels)
            
            # telling selected object
            shapeType , idx = getRealTypeAndIndex(self.__objName)
            print 'Object name : %s  index : %d'%(shapeType,idx)
            
            subName , subIdx = getRealTypeAndIndex(self.__subElementName)
            print 'SubObject name : %s  index : %d'%(subName , subIdx)
            
            if shapeType=='JointLine' or 'Point' in shapeType:
                FreeCADGui.runCommand('DDA_ShapeModifierTrigger')
                
            self.__clearObjectNames()

        else :
            FreeCAD.Console.PrintError('unkwon condition in Base.SelectionObserver')            
        print 'SelectionObserver done'
        self.lock = False

DDAObserver = SelectionObserver()

def enableSelectionObserver(flag):
    DDAObserver.lock = not flag
    print '\tFreeCAD selection observer locked : ' , not flag

def enableSeletionObserver(flag):
    if flag:
        FreeCADGui.Selection.addObserver(DDAObserver)
    else:
        FreeCADGui.Selection.removeObserver(DDAObserver)
#pts = [ (6,13,0) , (7,13,0) , (7,-2,0) , (35,-2,0) , (35,13,0) , (36,13,0) , (36,-3,0) , (6,-3,0) ]
#addPolygon2Document(pts, None, None, 'FixedPoint', 2)

p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DDA")
print 'fixed point color :' , p.GetUnsigned('fixedpointcolor')