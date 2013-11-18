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


import FreeCAD

FreeCAD.Console.PrintMessage( 'DDATools moudle begin\n')
__title__ = "FreeCAD DDA Workbench GUI Tools"
__author__ = "Cheng Xiaolong"

FreeCAD.Console.PrintMessage ('Importing DDATools moudle\n')

#---------------------------------------------------------------------------
# Generic stuff
#---------------------------------------------------------------------------
import os, FreeCAD, FreeCADGui, Part, WorkingPlane, math, re
from pivy import coin
from FreeCAD import Vector
#from draftlibs import fcvec, fcgeo
import fcvec, fcgeo
from functools import partial
import Base
from drawGui import todo , QtCore, QtGui
from TrackerTools import *

FreeCAD.Console.PrintMessage ('base moudles import done\n')

def translate(context, text):
    "convenience function for Qt translator"
    return QtGui.QApplication.translate(context, text, None, QtGui.QApplication.UnicodeUTF8).toUtf8()

def msg(text=None, mode=None):
    "prints the given message on the FreeCAD status bar"
    if not text: FreeCAD.Console.PrintMessage("")
    else:
        if mode == 'warning':
            FreeCAD.Console.PrintWarning(text)
        elif mode == 'error':
            FreeCAD.Console.PrintError(text)
        else:
            FreeCAD.Console.PrintMessage(text)
            

# last snapped objects, for quick intersection calculation
lastObj = [0, 0]

# set modifier keys
MODS = ["shift", "ctrl", "alt"]
MODCONSTRAIN = MODS[Base.getParam("modconstrain")]
MODSNAP = MODS[Base.getParam("modsnap")]
MODALT = MODS[Base.getParam("modalt")]

def getSupport(args):
    "returns the supporting object and sets the working plane"
    snapped = FreeCADGui.ActiveDocument.ActiveView.getObjectInfo((args["Position"][0], args["Position"][1]))
    if not snapped: return None
    obj = None
    plane.save()
    try:
        obj = FreeCAD.ActiveDocument.getObject(snapped['Object'])
        shape = obj.Shape
        component = getattr(shape, snapped["Component"])
        if plane.alignToFace(component, 0) \
                or plane.alignToCurve(component, 0):  # 这一句要研究下，‘0’是什么意思，度数吗？
            self.display(plane.axis)
    except:
        FreeCAD.Console.PrintWarning("function 'getSupport' get Exceptions\n")
        
    return obj

def hasMod(args, mod):
    "checks if args has a specific modifier"
    if mod == "shift":
        return args["ShiftDown"]
    elif mod == "ctrl":
        return args["CtrlDown"]
    elif mod == "alt":
        return args["AltDown"]

def setMod(args, mod, state):
    "sets a specific modifier state in args"
    if mod == "shift":
        args["ShiftDown"] = state
    elif mod == "ctrl":
        args["CtrlDown"] = state
    elif mod == "alt":
        args["AltDown"] = state



def snapPoint(target, point, cursor, ctrl=False):
    '''
    Snap function used by the Draft tools
    
    Currently has two modes: passive and active. Pressing CTRL while 
    clicking puts you in active mode:
    
    - In passive mode (an open circle appears), your point is
    snapped to the nearest point on any underlying geometry.
    
    - In active mode (ctrl pressed, a filled circle appears), your point
    can currently be snapped to the following points:
        - Nodes and midpoints of all Part shapes
        - Nodes and midpoints of lines/wires
        - Centers and quadrant points of circles
        - Endpoints of arcs
        - Intersection between line, wires segments, arcs and circles
        - When constrained (SHIFT pressed), Intersections between
        constraining axis and lines/wires
    '''
        
    def getConstrainedPoint(edge, last, constrain):
        "check for constrained snappoint"
        p1 = edge.Vertexes[0].Point
        p2 = edge.Vertexes[-1].Point
        ar = []
        if (constrain == 0):
            if ((last.y > p1.y) and (last.y < p2.y) or (last.y > p2.y) and (last.y < p1.y)):
                pc = (last.y - p1.y) / (p2.y - p1.y)  # 按比例计算，如为线段，下行中的cp计算结果应该就在edge上
                cp = (Vector(p1.x + pc * (p2.x - p1.x), p1.y + pc * (p2.y - p1.y), p1.z + pc * (p2.z - p1.z)))
                ar.append([cp, 1, cp])  # constrainpoint
        if (constrain == 1):
            if ((last.x > p1.x) and (last.x < p2.x) or (last.x > p2.x) and (last.x < p1.x)):
                pc = (last.x - p1.x) / (p2.x - p1.x)
                cp = (Vector(p1.x + pc * (p2.x - p1.x), p1.y + pc * (p2.y - p1.y), p1.z + pc * (p2.z - p1.z)))
                ar.append([cp, 1, cp])  # constrainpoint
        return ar

    def getPassivePoint(info):
        "returns a passive snap point"
        cur = Vector(info['x'], info['y'], info['z'])
        return [cur, 2, cur]

    def getScreenDist(dist, cursor):
        "returns a 3D distance from a screen pixels distance"
        p1 = FreeCADGui.ActiveDocument.ActiveView.getPoint(cursor)
        p2 = FreeCADGui.ActiveDocument.ActiveView.getPoint((cursor[0] + dist, cursor[1]))
        return (p2.sub(p1)).Length  # 好像计算结果是屏幕上两个点的x方向距离，为什么    ，后面在计算snapRadius时用到，用来计算半径

    def getGridSnap(target, point):
        "returns a grid snap point if available"
        if target.grid:
            return target.grid.getClosestNode(point)
        return None

    def getPerpendicular(edge, last):
        "returns a point on an edge, perpendicular to the given point"
        dv = last.sub(edge.Vertexes[0].Point)
        nv = fcvec.project(dv, fcgeo.vec(edge))
        np = (edge.Vertexes[0].Point).add(nv)  # 将edge作直线看，np是线外点到些直线的垂点
        return np

    # checking if alwaySnap setting is on
    extractrl = False
    if Base.getParam("alwaysSnap"):
        extractrl = ctrl
        ctrl = True                

    # setting Radius    , the raius is for snapping , not radius of circle
    radius = getScreenDist(Base.getParam("snapRange"), cursor)
    
    # checking if parallel to one of the edges of the last objects
    target.snap.off()
    target.extsnap.off()
    if (len(target.node) > 0):
        for o in [lastObj[1], lastObj[0]]:  # 前文中申明，last snapped objects ， 用来快速求交
            if o:
                ob = target.doc.getObject(o)
                if ob:
                    edges = ob.Shape.Edges
                    if len(edges) < 10:
                        for e in edges:
                            if isinstance(e.Curve, Part.Line):
                                last = target.node[len(target.node) - 1]
                                de = Part.Line(last, last.add(fcgeo.vec(e))).toShape()
                                np = getPerpendicular(e, point)  # point为函数参数，计算point到e的垂点
                                if (np.sub(point)).Length < radius:  # snap  成功
                                    target.snap.coords.point.setValue((np.x, np.y, np.z))
                                    target.snap.setMarker("circle")
                                    target.snap.on()  # target.snap和target.extsnap区别
                                    target.extsnap.p1(e.Vertexes[0].Point)
                                    target.extsnap.p2(np)
                                    target.extsnap.on()
                                    point = np
                                else:
                                    last = target.node[len(target.node) - 1]
                                    de = Part.Line(last, last.add(fcgeo.vec(e))).toShape()  
                                    np = getPerpendicular(de, point)
                                    if (np.sub(point)).Length < radius:  # 取edge首尾端点所成线段算距离，为何有效
                                        target.snap.coords.point.setValue((np.x, np.y, np.z))
                                        target.snap.setMarker("circle")
                                        target.snap.on()
                                        point = np

    # check if we snapped to something
    snapped = target.view.getObjectInfo((cursor[0], cursor[1]))

    if (snapped == None):
        # nothing has been snapped, check fro grid snap
        gpt = getGridSnap(target, point)  # 选取最近点
        if gpt:
            if radius != 0:
                dv = point.sub(gpt)
                if dv.Length <= radius:
                    target.snap.coords.point.setValue((gpt.x, gpt.y, gpt.z))
                    target.snap.setMarker("point")
                    target.snap.on()  
                    return gpt
        return point
    else:
        # we have something to snap
        obj = target.doc.getObject(snapped['Object'])
        if hasattr(obj.ViewObject, "Selectable"):
                        if not obj.ViewObject.Selectable:
                                return point
        if not ctrl:
                        # are we in passive snap?
                        snapArray = [getPassivePoint(snapped)]
        else:
            snapArray = []
            comp = snapped['Component']  # 'Component'保存什么？
            if obj.isDerivedFrom("Part::Feature"):
                if "Edge" in comp:
                    # get the stored objects to calculate intersections
                    intedges = []
                    if lastObj[0]:
                        lo = target.doc.getObject(lastObj[0])
                        if lo:
                            if lo.isDerivedFrom("Part::Feature"):
                                intedges = lo.Shape.Edges
                                                           
                    nr = int(comp[4:]) - 1  # 这计算的是什么？
                    edge = obj.Shape.Edges[nr]
                    for v in edge.Vertexes:
                        snapArray.append([v.Point, 0, v.Point])  # 点和数放在一起，中间这一位什么意思？
                    if isinstance(edge.Curve, Part.Line):
                        # the edge is a line
                        midpoint = fcgeo.findMidpoint(edge)
                        snapArray.append([midpoint, 1, midpoint])  # 点和数放在一起，中间这一位什么意思？
                        if (len(target.node) > 0):
                            last = target.node[len(target.node) - 1]  # target.node 中保存的是点
                            snapArray.extend(getConstrainedPoint(edge, last, target.constrain))
                            np = getPerpendicular(edge, last)
                            snapArray.append([np, 1, np])

                    elif isinstance (edge.Curve, Part.Circle):
                        # the edge is an arc
                        rad = edge.Curve.Radius
                        pos = edge.Curve.Center
                        for i in [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]:
                            ang = math.radians(i)
                            cur = Vector(math.sin(ang) * rad + pos.x, math.cos(ang) * rad + pos.y, pos.z)
                            snapArray.append([cur, 1, cur])
                        for i in [15, 37.5, 52.5, 75, 105, 127.5, 142.5, 165, 195, 217.5, 232.5, 255, 285, 307.5, 322.5, 345]:
                            ang = math.radians(i)
                            cur = Vector(math.sin(ang) * rad + pos.x, math.cos(ang) * rad + pos.y, pos.z)
                            snapArray.append([cur, 0, pos])  # 点和数放在一起，中间这一位什么意思？保存东西还可以不一样

                    for e in intedges:
                        # get the intersection points
                        pt = fcgeo.findIntersection(e, edge)
                        if pt:
                            for p in pt:
                                snapArray.append([p, 3, p])
                elif "Vertex" in comp:
                    # directly snapped to a vertex
                    p = Vector(snapped['x'], snapped['y'], snapped['z'])
                    snapArray.append([p, 0, p])
                elif comp == '':
                    # workaround for the new view provider
                    p = Vector(snapped['x'], snapped['y'], snapped['z'])
                    snapArray.append([p, 2, p])
                else:
                    snapArray = [getPassivePoint(snapped)]
            elif Base.getType(obj) == "Dimension":
                for pt in [obj.Start, obj.End, obj.Dimline]:
                    snapArray.append([pt, 0, pt])
            elif Base.getType(obj) == "Mesh":
                for v in obj.Mesh.Points:
                    snapArray.append([v.Vector, 0, v.Vector])
        if not lastObj[0]:  # 为什么
            lastObj[0] = obj.Name
            lastObj[1] = obj.Name
        if (lastObj[1] != obj.Name):
            lastObj[0] = lastObj[1]
            lastObj[1] = obj.Name

        # calculating shortest distance
        shortest = 1000000000000000000
        spt = Vector(snapped['x'], snapped['y'], snapped['z'])
        newpoint = [Vector(0, 0, 0), 0, Vector(0, 0, 0)]
        for pt in snapArray:
            if pt[0] == None: FreeCAD.Console.PrintMessage ("snapPoint: debug 'i[0]' is 'None'")
            di = pt[0].sub(spt)
            if di.Length < shortest:
                shortest = di.Length
                newpoint = pt
        if radius != 0:
            dv = point.sub(newpoint[2])
            if (not extractrl) and (dv.Length > radius):
                newpoint = getPassivePoint(snapped)
        target.snap.coords.point.setValue((newpoint[2].x, newpoint[2].y, newpoint[2].z))
        if (newpoint[1] == 1):
            target.snap.setMarker("square")
        elif (newpoint[1] == 0):
            target.snap.setMarker("point")
        elif (newpoint[1] == 3):
            target.snap.setMarker("square")
        else:
            target.snap.setMarker("circle")
        target.snap.on()                                
        return newpoint[2]

def getPoint(target, args, mobile=False, sym=False, workingplane=True):
    '''
    Function used by the Draft Tools.
    returns a constrained 3d point and its original point.
    if mobile=True, the constraining occurs from the location of
    mouse cursor when Shift is pressed, otherwise from last entered
    point. If sym=True, x and y values stay always equal. If workingplane=False,
    the point wont be projected on the Working Plane.
    '''
    ui = FreeCADGui.DDAToolbar
    view = FreeCADGui.ActiveDocument.ActiveView
    point = view.getPoint(args["Position"][0], args["Position"][1])
    point = snapPoint(target, point, args["Position"], hasMod(args, MODSNAP))

    if (not plane.weak) and workingplane:
        # working plane was explicitely selected - project onto it
        viewDirection = view.getViewDirection()
        if FreeCADGui.ActiveDocument.ActiveView.getCameraType() == "Perspective":
            camera = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()
            p = camera.getField("position").getValue()
            # view is from camera to point:
            viewDirection = point.sub(Vector(p[0], p[1], p[2]))
        # if we are not snapping to anything, project along view axis,
        # otherwise perpendicularly
        if view.getObjectInfo((args["Position"][0], args["Position"][1])):
            pass
            # point = plane.projectPoint(point)
        else:
            point = plane.projectPoint(point, viewDirection)
    ctrlPoint = Vector(point.x, point.y, point.z)
    if (hasMod(args, MODCONSTRAIN)):  # constraining
        if mobile and (target.constrain == None):
            target.node.append(point)  # target.node中保存的是点，竟然这样添加
        point = constrainPoint(target, point, mobile=mobile, sym=sym)
    else:
        target.constrain = None
        ui.xValue.setEnabled(True)
        ui.yValue.setEnabled(True)
#        ui.zValue.setEnabled(True)
    if target.node:
        if target.featureName == "Rectangle":
            ui.displayPoint(point, target.node[0], plane=plane)
        else:
            ui.displayPoint(point, target.node[-1], plane=plane)
    else: ui.displayPoint(point, plane=plane)
    return point, ctrlPoint

        
def getSupport(args):
    "returns the supporting object and sets the working plane"
    snapped = FreeCADGui.ActiveDocument.ActiveView.getObjectInfo((args["Position"][0], args["Position"][1]))
    if not snapped: return None
    obj = None
    plane.save()
    try:
        obj = FreeCAD.ActiveDocument.getObject(snapped['Object'])
        shape = obj.Shape
        component = getattr(shape, snapped["Component"])
        if plane.alignToFace(component, 0) \
                or plane.alignToCurve(component, 0):  # 这一句要研究下，‘0’是什么意思，度数吗？
            self.display(plane.axis)
    except:
        pass
    return obj


#---------------------------------------------------------------------------
# Geometry constructors
#---------------------------------------------------------------------------

class Creator(object):
    "A generic DDA Shape Creator used by creation tools such as line or arc"
    
    def __init__(self,shapeType = 'xxx'):
#        self.commitList = []
        self.shapeType = shapeType
        
    def Activated(self, name="None"):
        FreeCAD.Console.PrintMessage( 'Creator activing\n')
        if FreeCAD.activeDDACommand:
            FreeCAD.activeDDACommand.finish()
        self.ui = None
        self.call = None
        self.doc = None
        self.support = None
#        self.commitList = []
        self.doc = FreeCAD.ActiveDocument
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.featureName = name
        
        # debug message
        print self.shapeType , ' in Creator'
        
#        import Base
#        Base.__lastShapeName__=self.shapeType
#        
        if not self.doc:
            FreeCAD.Console.PrintMessage( 'FreeCAD.ActiveDocument get failed\n')
            self.finish()
        else:
            FreeCAD.activeDDACommand = self  # FreeCAD.activeDDACommand 在不同的时间会接收不同的命令 
#            self.ui = FreeCADGui.DDADockWidget
            FreeCAD.Console.PrintMessage('setting mouse cursor in Creator\n')
#            self.ui.cross(True)
#            self.ui.sourceCmd = self
            FreeCAD.Console.PrintMessage('self.ui works fine\n')
#            self.ui.setTitle(name)
#            self.ui.show()
            rot = self.view.getCameraNode().getField("orientation").getValue()  # camera 的朝向，一个matrix
            upv = Vector(rot.multVec(coin.SbVec3f(0, 1, 0)).getValue())  # camera 的朝上方向
            plane.setup(fcvec.neg(self.view.getViewDirection()), Vector(0, 0, 0), upv)
            self.node = []
            self.pos = []
            self.constrain = None
            self.obj = None
            self.snap = snapTracker()
            self.extsnap = lineTracker(dotted=True)
            self.planetrack = PlaneTracker()
            # 源代码中使用Draft.getParam(...)作判断来确定是否使用gridTracker()
            self.grid = gridTracker()

            import Base
            Base.enableSelectionObserver(False)
            

                        
            import DDAToolbars
            FreeCADGui.DDAToolBar = DDAToolbars.lineToolbar
            FreeCADGui.DDAToolBar.on()
            self.ui = FreeCADGui.DDAToolBar
            self.ui.sourceCmd = self
            
    def IsActive(self):
        if FreeCADGui.ActiveDocument:
            return True
        else:
            return False

    def finish(self):
        self.snap.finalize()
        self.extsnap.finalize()
        self.node = []
        self.planetrack.finalize()
        if self.grid: self.grid.finalize()
        if self.support: plane.restore()
        FreeCAD.activeDDACommand = None
        if self.ui:
            FreeCAD.Console.PrintMessage('closing UI\n')
            self.ui.offUi()
            self.ui.cross(False)
            self.ui.sourceCmd = None
#        msg("")
        if self.call:
            self.view.removeEventCallback("SoEvent", self.call)
            self.call = None
#        if self.commitList:
#            todo.delayCommit(self.commitList)
#        self.commitList = []
        import Base
        Base.enableSelectionObserver(True)


#    def commit(self, name, func):
#        "stores partial actions to be committed to the FreeCAD document"
#        self.commitList.append((name, func))

class Line(Creator):
    "The Line FreeCAD command definition"

    def __init__(self, wiremode=False , shapeType = 'xxx' , mustColse=False):
        self.isWire = wiremode
        self.shapeType = shapeType
        self.mustColse = mustColse
        self.ifPolyLine = True
        if shapeType == 'MaterialLine':
            self.ifPolyLine = False

    def GetResources(self):
        return {
        #'Pixmap'  : 'Draft_Line',
        #'Accel' : "L,I",
                'MenuText':  "Line",
                'ToolTip': "Creates a 2-point line. CTRL to snap, SHIFT to constrain"}

    def Activated(self, name="Line"):
        FreeCAD.Console.PrintMessage( 'Line activing\n')
        Creator.Activated(self, name)
        if self.doc:
            self.obj = None
            self.linetrack = lineTracker()
            self.constraintrack = lineTracker(dotted=True)
            
            self.obj = self.doc.getObject('Line')
            if not self.obj:
                self.obj = self.doc.addObject("Part::Feature", 'Line')  # 新建一个用于显示的object

            # self.obj.ViewObject.Selectable = False
            #Draft.formatObject(self.obj)
            #if not Draft.getParam("UiMode"): self.makeDumbTask()
            self.call = self.view.addEventCallback("SoEvent", self.action)
            msg( "Pick first point:\n")
            
#            import DDAToolbars
#            FreeCADGui.DDAToolBar = DDAToolbars.lineToolbar
#            FreeCADGui.DDAToolBar.on()
#            self.ui = FreeCADGui.DDAToolBar
#            self.ui.sourceCmd = self
            
    def finish(self, closed=False, ifSave=True , materialNo=1):
        "terminates the operation and closes the poly if asked"
        #if not Draft.getParam("UiMode"):
        FreeCAD.Console.PrintMessage( 'finishing\n')
        FreeCADGui.Control.closeDialog()
        if self.obj:
            self.obj.Shape = Part.Shape([])
            self.obj.ViewObject.Visibility = False
#            old = self.obj.Name
#            todo.delay(self.doc.removeObject, old)

        self.obj = None  # 可能到些都是辅助图元，下面if里的内容才是真正的最终图元 ,self.commit(...)里的内容才是真正的图元
        tmpObj = None
#        if self.shapeType == 'BoundaryLine' and len(self.node) > 2:
#            Base.addLines2Document(self.node , True , face=False, support=self.support , fname = self.shapeType)
#        elif(len(self.node) > 1):  
#            tmpObj = Base.addLines2Document(self.node , True , face=False, support=self.support , fname = self.shapeType)

        from loadDataTools import DDALine
        if ifSave:
            import Base
            if self.shapeType!= 'MaterialLine':
                tmpObj = Base.addPolyLine2Document(self.shapeType, ifStore2Database = True , pointsList=self.node , materialNo=materialNo , closed=closed)

        if self.ui:
            self.linetrack.finalize()
            self.constraintrack.finalize()
        Creator.finish(self)

        return tmpObj

    def action(self, arg):
        "scene event handler"
        if arg["Type"] == "SoKeyboardEvent":
            FreeCAD.Console.PrintMessage('keyboardEvent')
            if arg["Key"] == "ESCAPE":
                FreeCAD.Console.PrintError('Escape pressed, finising\n')
                self.finish(closed = self.mustColse)
        elif arg["Type"] == "SoLocation2Event":  # mouse movement detection
            point, ctrlPoint = getPoint(self, arg)
            #FreeCAD.Console.PrintMessage('setting mouse cursor in Line action\n')
            self.ui.cross(True)
            self.linetrack.p2(point)
            # Draw constraint tracker line.
#            if hasMod(arg, MODCONSTRAIN):
#                self.constraintrack.p1(point)
#                self.constraintrack.p2(ctrlPoint)
#                self.constraintrack.on()
#            else:
#                self.constraintrack.off()
        elif arg["Type"] == "SoMouseButtonEvent":
            if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):
                if (arg["Position"] == self.pos):
                    FreeCAD.Console.PrintError('same point, finising\n')
                    self.finish(closed=self.mustColse, cont=True)
                else:
                    if not self.node: self.support = getSupport(arg)
                    point, ctrlPoint = getPoint(self, arg)
                    self.pos = arg["Position"]
                    self.node.append(point)
                    self.linetrack.p1(point)
                    self.drawSegment(point)
                    
                    if len(self.node)==2 and not self.ifPolyLine:  # currently, materialLine need this
                        self.finish(closed = self.mustColse)
                    
                    
#                    if (not self.isWire and len(self.node) == 2):
#                        FreeCAD.Console.PrintError('not Wire and len(node)==2, finising\n')
#                        self.finish(closed=False, cont=True)
#                    if (len(self.node) > 2):
#                        # DNC: allows to close the curve
#                        # by placing ends close to each other
#                        # with tol = Draft tolerance
#                        # old code has been to insensitive
#                        # if fcvec.equals(point,self.node[0]):
#                        if ((point - self.node[0]).Length < Base.tolerance()):
#                            self.undolast()
#                            FreeCAD.Console.PrintError('< tolerance, finising\n')
#                            self.finish(closed=True, cont=True)
#                            msg( "Wire has been closed\n")

    def drawSegment(self, point):
        "draws a new segment"
        if (len(self.node) == 1):
            self.linetrack.on()
            msg(translate("draft", "Pick next point:\n"))
            self.planetrack.set(self.node[0])
        elif (len(self.node) == 2):
            last = self.node[len(self.node) - 2]  # 参数中的point是最新的点，取倒数第二个点和point绘线
            newseg = Part.Line(last, point).toShape()
            self.obj.Shape = newseg
            self.obj.ViewObject.Visibility = True
            if self.isWire:
                msg(translate("draft", "Pick next point, or (F)inish or (C)lose:\n"))
        else:
            currentshape = self.obj.Shape
            last = self.node[len(self.node) - 2]  
            newseg = Part.Line(last, point).toShape()
            if not currentshape:
                newshape = newseg
            else :
                newshape = currentshape.fuse(newseg)
            self.obj.Shape = newshape
            msg(translate("draft", "Pick next point, or (F)inish or (C)lose:\n"))

#    def wipe(self):
#        "removes all previous segments and starts from last point"
#        if len(self.node) > 1:
#            FreeCAD.Console.PrintMessage ("nullifying")
#            # self.obj.Shape.nullify() - for some reason this fails
#            self.obj.ViewObject.Visibility = False
#            self.node = [self.node[-1]]  # 清空了除最后一个点外保存的所有点
#            FreeCAD.Console.PrintMessage ("setting trackers")
#            self.linetrack.p1(self.node[0])
#            self.planetrack.set(self.node[0])
#            msg(translate("draft", "Pick next point:\n"))
#            FreeCAD.Console.PrintMessage ("done\n")
                        
    def numericInput(self, numx, numy, numz):
        "this function gets called by the toolbar when valid x, y, and z have been entered there"
        point = Vector(numx, numy, numz)
        self.node.append(point)
        self.linetrack.p1(point)
        self.drawSegment(point)
#        if (not self.isWire and len(self.node) == 2):
#            self.finish(False, cont=True)
        #self.ui.setNextFocus()

    
class Rectangle(Creator):
    "the DDA_Rectangle FreeCAD command definition"
    
    def GetResources(self):
        return {
        #'Pixmap'  : 'Draft_Rectangle',
         #       'Accel' : "R, E",
                'MenuText': "Rectangle",
                'ToolTip': "Creates a 2-point rectangle. CTRL to snap"}

    def Activated(self):
        Creator.Activated(self, "Rectangle")
        if self.ui:
            self.refpoint = None
            self.ui.pointUi()
            #self.ui.extUi()
            self.call = self.view.addEventCallback("SoEvent", self.action)
            self.rect = rectangleTracker()
            msg( "Pick first point:\n")

    def finish(self, closed=False, cont=False):
        "terminates the operation and closes the poly if asked"
        Creator.finish(self) 
        if self.ui:
            self.rect.off()
            self.rect.finalize()
        if cont and self.ui:
            if self.ui.continueMode:
                self.Activated()

    def createObject(self):
        "creates the final object in the current doc"
        p1 = self.node[0]
        p3 = self.node[-1]
        diagonal = p3.sub(p1)      # diagonal  对角线
        p2 = p1.add(fcvec.project(diagonal, plane.v))  # 添加plane.v方向的偏移量
        p4 = p1.add(fcvec.project(diagonal, plane.u))
        length = p4.sub(p1).Length
        if abs(fcvec.angle(p4.sub(p1), plane.u, plane.axis)) > 1: length = -length
        height = p2.sub(p1).Length
        if abs(fcvec.angle(p2.sub(p1), plane.v, plane.axis)) > 1: height = -height
        p = plane.getRotation()
        p.move(p1)
#        try:
        self.commit("Create Rectangle",
                    partial(Base.makeRectangle, length, height,
                            p, False, support=self.support))
#        except:
#            print "Draft: error delaying commit"
        self.finish(cont=True)

    def action(self, arg):
        "scene event handler"
        if arg["Type"] == "SoKeyboardEvent":
            if arg["Key"] == "ESCAPE":
                self.finish()
        elif arg["Type"] == "SoLocation2Event":  # mouse movement detection
            point, ctrlPoint = getPoint(self, arg, mobile=True)
            self.rect.update(point)
            self.ui.cross(True)
        elif arg["Type"] == "SoMouseButtonEvent":
            if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):
                if (arg["Position"] == self.pos):
                    self.finish()
                else:
                    if not self.node: self.support = getSupport(arg)
                    point, ctrlPoint = getPoint(self, arg)
                    self.appendPoint(point)

    def numericInput(self, numx, numy, numz):
        "this function gets called by the toolbar when valid x, y, and z have been entered there"
        point = Vector(numx, numy, numz)
        self.appendPoint(point)

    def appendPoint(self, point):
        self.node.append(point)
        if (len(self.node) > 1):
            FreeCAD.Console.PrintMessage('DDA_Rectangle create object\n')
            self.rect.update(point)
            self.createObject()
        else:
            msg("Pick opposite point:\n")
#            self.ui.setRelative()
            self.rect.setorigin(point)
            self.rect.on()
            self.planetrack.set(point)



class Circle(Creator):
    "the Draft_Arc FreeCAD command definition"
        
    def __init__(self , shapeType = 'xxx'):
        self.closedCircle = True
        self.featureName = "Circle"
        self.shapeType = shapeType
        self.center = None
        
    def GetResources(self):
        return {
                'MenuText': "Circle",
                'ToolTip': "Creates a circle"}
            
    def Activated(self):
        Creator.Activated(self, self.featureName)
        if self.ui:
            self.step = 0
            self.center = None
            self.rad = None
            self.call = self.view.addEventCallback("SoEvent", self.action)
            msg("Pick center point:\n")

    def finish(self, closed=True, cont=False):
        "finishes the arc"
        Creator.finish(self)
        
        tmpObj = None
        if self.center :
            import Base
            print 'Circle ending'
            view=FreeCADGui.ActiveDocument.ActiveView
            obj = view.getObjectInfo(view.getCursorPos())
            objName , objIdx = Base.getRealTypeAndIndex(obj['Object'])
            assert objName == 'Block'
            subName , subIdx = Base.getRealTypeAndIndex(obj['Component'])
            tmpObj = self.drawCircle(subIdx)
            
#            from loadDataTools import DDAPoint
#            Base.addCircles2Document(self.shapeType, ifStore2Database=True \
#                            , pts=[DDAPoint(self.center[0],self.center[1])], ifRecord = True)
#            
            print 'DDAPoint with center (%f , %f) is drawn'%(self.center[0],self.center[1])
#            FreeCADGui.runCommand('DDA_DCChangesConfirm')
        return tmpObj
    
    def drawCircle(self , blockNo):        
        from loadDataTools import DDAPoint
        import Base
        point = DDAPoint(self.center[0],self.center[1])
        point.blockNo = blockNo
        return Base.addCircles2Document(self.shapeType, ifStore2Database=True \
                      , pts= [point], ifRecord = True)
    
    
    def action(self, arg):
        "scene event handler"
        if arg["Type"] == "SoKeyboardEvent":
            if arg["Key"] == "ESCAPE":
                self.finish()
        elif arg["Type"] == "SoLocation2Event":
            point, ctrlPoint = getPoint(self, arg)
            # this is to make sure radius is what you see on screen
            self.ui.cross(True)

        elif arg["Type"] == "SoMouseButtonEvent":
            if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):
                point, ctrlPoint = getPoint(self, arg)
                self.center = FreeCAD.Vector(point[0],point[1],0)
                import Base
                self.rad = Base.__radius4Points__
                self.finish()
#
#    def drawArc(self):
#        "actually draws the FreeCAD object"
#        print '**********draw Circle*************\n'
#        p = plane.getRotation()
#        p.move(self.center)
#        tmpObj = None
##        tmpObj = Base.makeCircle( self.center , self.rad, p , face=False, support=self.support , fname = self.shapeType)
#        if self.closedCircle:
#            tmpObj = Base.makeCircle( self.center , self.rad, p , face=False, support=self.support , fname = self.shapeType)
#        else:
#            print "Draft: error delaying commit"
#        return tmpObj

    def numericInput(self, numx, numy, numz):
        "this function gets called by the toolbar when valid x, y, and z have been entered there"
        self.center = Vector(numx, numy, numz)
        self.node = [self.center]
        self.arctrack.setCenter(self.center)
        self.arctrack.on()
        self.ui.radiusUi()
        self.ui.setNextFocus()
        msg("Pick radius:\n")
        
class DataTable(QtCore.QObject):
    '''
    for jointSets , tunnels , format the table manipulations
    '''
    dataInvalidSignal = QtCore.pyqtSignal( int )
    saveDataSignal = QtCore.pyqtSignal()
    def __init__(self , row , column , headers , firstColumnDropDown = False , lastColumnNoEdit = True , columnWidth = None , VHeaders = None):
        super(DataTable, self).__init__()
        self.__dataValid = False
        self.__firstColumnDropDown = firstColumnDropDown
        self.__lastColumnNoEdit = lastColumnNoEdit
        self.__normalColorBrush = QtGui.QBrush(QtGui.QColor(255,255,255))
        self.__errorColorBrush = QtGui.QBrush(QtGui.QColor(255,160,30))
        self.table = QtGui.QTableWidget(0 , column)
        self.table.setHorizontalHeaderLabels(headers)
#        print 'row : %d  , column : %d'%(row,column)
        for i in range(row):
            self.addRow()
            
        if VHeaders:
            self.table.setVerticalHeaderLabels(VHeaders)
            
        self.__columnWidth = columnWidth
        if columnWidth != None :
#            print 'set column width to ' , columnWidth
            for i in range(column):
                self.table.setColumnWidth( i , columnWidth)
            
        self.table.cellChanged.connect(self.checkCell)
        self.table.cellClicked.connect(self.handleClick)
        
    def getColumnStartIndex(self):
        if self.__firstColumnDropDown : 
            return 1
        return 0
        
    def getColumnEndIndex(self):
        if self.__lastColumnNoEdit : 
            return self.table.columnCount()-1
        return self.table.columnCount()
        
    def addDelButton4Row(self, row):
        'add the del button for the row'
        newItem = QtGui.QTableWidgetItem("Del") 
        newItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.table.setItem(row, self.table.columnCount()-1, newItem)    

    def addComboBox4Row(self, row , column):
        'add the del button for the row'
        newItem = QtGui.QComboBox() 
        newItem.addItems(['1' , '2' , '3' , '4'])
        self.table.setCellWidget(row, column, newItem)    

        
    def addBlankItem4Cell(self, row , column):
        'add the del button for the row'
        newItem = QtGui.QTableWidgetItem() 
        self.table.setItem(row, column, newItem)    
        newItem.setBackground(self.__errorColorBrush)

        
    def deleteRow(self , row):
        if self.table.rowCount()==0:
            FreeCAD.Console.PrintError('deleting row that doesnot exist\n')
            return

        print '****** DataTable deleting row : ' , self.table.currentRow() , ' ***********'
        
        dataList = []
        self.saveData(dataList)
        
        self.table.setRowCount(self.table.rowCount()-1)
        del dataList[row]
        self.refreshData(dataList)
        
    def saveData(self , dataList):
        num = self.table.columnCount()
        if self.__lastColumnNoEdit:
            num = num-1
        for i in range( self.table.rowCount()):
            array = range(num)
            start = 0
            if self.__firstColumnDropDown:
                start = 1
                array[0] = str(self.table.cellWidget(i,0).currentText())
            for j in range(start , num):
                array[j] = self.table.item(i,j).text()
                
#            print 'new tuple : ' , array
            dataList.append(array)
            
    def handleClick(self , row , column):
        if self.__lastColumnNoEdit == True and column == self.table.columnCount()-1 :
            self.deleteRow(row)        
        
    def checkCell ( self, row , column):
#        print 'checking cell : (%d , %d)'%(row , column)
        if self.__firstColumnDropDown == True and column==0 :
            return
            
        if self.__lastColumnNoEdit == True and column == self.table.columnCount()-1 :
            return
        
        try:
            num = float(self.table.item(row , column).text())
        except:
            self.__dataValid = False
            self.table.item(row , column).setBackground(self.__errorColorBrush)
            self.dataInvalidSignal.emit(0)   # data in table is invalid
        else :
            self.table.item(row , column).setBackground(self.__normalColorBrush)
            valid = self.checkTable()
            self.dataInvalidSignal.emit(valid)   # data in table is invalid
            
    def writeData2Table(self , data):
        for i in range(len(data)):
            print data[i]
        start = self.getColumnStartIndex()
        end = self.getColumnEndIndex()       
        if (len(data)!=self.table.rowCount()) or (len(data[0])!=end - start) : #  行数 或者 列数不相等
#            print 'data table column count and row count unvalid ( %d , %d ) <-->(%d , %d)'\
#                %( len(data) , len(data[0]) , self.table.rowCount() , end-start ) 
            raise
        for i in range(self.table.rowCount()):
            for j in range(start , end):
                self.table.item(i,j).setText(str(data[i][j]))
             
            
    def checkTable( self ):
#        print '******** begining check table *********'
        valid = True
        for i in range(self.table.rowCount()):
            start = 0
            if self.__firstColumnDropDown : 
                start = 1
                
            end = self.table.columnCount()
            if self.__lastColumnNoEdit :
                end = end-1
            
            for j in range(start , end):
                try:
#                    print '    checking (%d , %d) , content : %s , len :%d'%(i,j , self.table.item(i , j).text(),len(self.table.item(i , j).text()))
                    num = float(self.table.item(i , j).text())
                except:
                    tmpInvalid = True
#                    print '    except occured at column : %d .start : %d , end %d'%(j , start , end)
                    if j==start:
                        tmpInvalid = False    # 测试本行，如果全是未填写数据的空格，则此行检测正确
                        for k in range(start , end):
                            if len(self.table.item(i,k).text())>0:
#                                print '    except text : ' , self.table.item(i,k).text() 
                                tmpInvalid = True
                                break
                    if tmpInvalid :
#                        print '   cell (%d , %d) :  %s  parse failed.'%(i , j ,self.table.item(i , j).text())
                        valid = False
                        break
                    else : # this is a blank line , check next line
                        break
            
            if not valid :
                break
        
#        print 'table check result : ' , valid
        return valid
            
        
    def addRow(self):
        self.table.setRowCount(self.table.rowCount()+1)
        row = self.table.rowCount()-1
        
        start =    self.getColumnStartIndex()
        end = self.getColumnEndIndex()

        if self.__firstColumnDropDown : 
            self.addComboBox4Row(row , 0)
            
        if self.__lastColumnNoEdit :
            self.addDelButton4Row(row)
        
        for j in range(start , end):
            self.addBlankItem4Cell( row, j )
        
    def refreshData(self , dataList):
        '''
        refresh data in table , the data comes from 'dataList'
        :param dataList: source data
        '''
        
        # 当读入数据时，需要完全重写数据，所以要事先检查一次，如果行列数符合，便不再处理table本身，直接读入数据
        if self.table.rowCount()!= len(dataList):
            self.clearTable()
            for i in range(len(dataList)):
                self.addRow()
                
        for i in range(len(dataList)) :
            tuple = dataList[i]
            start = self.getColumnStartIndex()
            end = self.getColumnEndIndex()
            for j in range( start , end ):
                if start ==1 :
                    self.table.cellWidget(i,0).setCurrentIndex(int(tuple[0]))
                self.table.item( i , j ).setText(str(tuple[j]))

    def clearTable(self):
        '''
        clear data in the table
        '''
        self.table.setRowCount(0)

class TunnelSelectionTool(QtGui.QDialog):
    '''
    tools to choose tunnel
    '''
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.initUI()
        
    def initUI(self):
        
        import ui_TunnelSelection
        self.ui = ui_TunnelSelection.Ui_Dialog()
        self.ui.setupUi(self)
        headers = ['type','a','b','c','r','centerX','centerY']
        self.ui.tableWidget.setHorizontalHeaderLabels(headers)
        
    def select(self):
        import DDADatabase
        database = DDADatabase.dl_database
        tunnels = database.tunnels
        if len(tunnels)==0: return None

        table = self.ui.tableWidget
        table.setRowCount(len(tunnels))
        for i , t in enumerate(tunnels):
            for j , v in enumerate(t):
                item = QtGui.QTableWidgetItem()
                item.setText(str(v))
                table.setItem(i, j, item)
        
        flag = self.exec_()
        if QtGui.QDialog.Accepted==flag:
            return table.currentRow()
        return None
        
    def getSelectedTunnelNo(self):
        if self.ui.tableWidget.rowCount()>0:
            return self.ui.tableWidget.currentRow()

class TunnelBoltsSelectionTool(QtGui.QDialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.initUI()
        self.bolts = []
        
        
    def initUI(self):
        import ui_tunnelBolts
        self.ui = ui_tunnelBolts.Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.spinBox_startBoltIdx.valueChanged.connect(self.refreshBolts)
        self.ui.spinBox_endBoltIdx.valueChanged.connect(self.refreshBolts)
        
    def calcBolts(self):
        a = float(self.ui.a.text())
        b = float(self.ui.b.text())
        c = float(self.ui.c.text())
        centerX = float(self.ui.centerX.text())
        centerY = float(self.ui.centerY.text())
        
        length = self.ui.spinBox_boltLength.value()
        length2 = self.ui.spinBox_boltLength2.value()
        
        print 'generate bolt elements for Tunnel (%f ,  %f , %f , %f , %f ,%f , %f)' \
                %( a , b , c , centerX , centerY , length , length2 )
        
        from interfaceTools import Tunnel2BoltsGenerator
        
        self.bolts = Tunnel2BoltsGenerator.generateBolts( centerX=centerX , centerY=centerY \
            , halfWidth=a , halfHeight=b , arcRadius=c \
            , boltsDistance=1 , boltLength=length , boltLength2=length2)
        
        # set panel
        self.ui.spinBox_startBoltIdx.setValue(1)
        self.ui.spinBox_startBoltIdx.setRange(1 , len(self.bolts))
        self.ui.spinBox_endBoltIdx.setValue(len(self.bolts))
        self.ui.spinBox_endBoltIdx.setRange(1 , len(self.bolts))
        
        # store tmp result
        import DDADatabase , Base
        DDADatabase.tmpBoltElements = self.bolts[:]
#        Base.addLines2Document(shapeType='TmpBoltElement', ifStore2Database=False, args=None)
#        FreeCAD.ActiveDocument.getObject('TmpBoltElement').ViewObject.Visibility = True
        Base.updateTmpBoltElements()


    def storeData2Panel(self, tunnelIdx):
        from DDADatabase import dl_database
        tunnels = dl_database.tunnels
        
        assert tunnels and tunnelIdx< len(tunnels)
        t = tunnels[tunnelIdx]

        self.ui.tunnelNo.setText(str(tunnelIdx))
        self.ui.tunnelType.setText('2')
        self.ui.a.setText(str(t[1]))
        self.ui.b.setText(str(t[2]))
        self.ui.c.setText(str(t[3]))
        self.ui.centerX.setText(str(t[5]))
        self.ui.centerY.setText(str(t[6]))
        
        self.ui.spinBox_boltLength.setValue(12)
        self.ui.spinBox_boltLength2.setValue(10)
        self.ui.spinBox_boltDistance.setValue(1)
        
    def refreshBolts(self , idx):
        startIdx = self.ui.spinBox_startBoltIdx.value()
        endIdx = self.ui.spinBox_endBoltIdx.value()
        import DDADatabase
        bolts = self.bolts[startIdx-1:endIdx]
        if endIdx == idx: 
            t = bolts[-1]
            bolts[-1] = bolts[0]
            bolts[0] = t
#            bolts.reverse()
        DDADatabase.tmpBoltElements = bolts 
#        obj = FreeCAD.ActiveDocument.getObject('TmpBoltElement') 
#        if obj: obj.ViewObject.RedrawTrigger = True
        import Base
        Base.updateTmpBoltElements()
        
    def accept(self):
        QtGui.QDialog.accept(self)
        import DDADatabase , Base
        bolts = self.bolts[ self.ui.spinBox_startBoltIdx.value()-1:\
                           self.ui.spinBox_endBoltIdx.value() ]
        Base.addLines2Document(shapeType = 'BoltElement' \
                   , ifStore2Database=True, args=bolts)

    def done(self , r):
        QtGui.QDialog.done(self , r)
        import DDADatabase , Part
        DDADatabase.tmpBoltElements = []
        FreeCAD.ActiveDocument.getObject('TmpBoltElement').Shape=Part.Shape()
#        FreeCAD.ActiveDocument.getObject('TmpBoltElement').ViewObject.RedrawTrigger = True
#        FreeCAD.ActiveDocument.getObject('TmpBoltElement').ViewObject.Visibility = False
        
    def configure(self , tunnelIdx):
        import DDADatabase
        from DDADatabase import dl_database
        tunnels = dl_database.tunnels
        assert tunnelIdx < len(tunnels)
        self.storeData2Panel(tunnelIdx)
        self.calcBolts()
        self.exec_()

class ChooseProjectPath:
    '''
    choose workbench for DDA
    '''
    def GetResources(self):
        return {
                'MenuText': "Choose Workbench",
                'ToolTip': "choose"}

    def Activated(self):
        if FreeCAD.activeDDACommand:
            FreeCAD.activeDDACommand.finish()
        dialog = QtGui.QFileDialog()
        dialog.setDirectory('D:/')
        dialog.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        dir =  str(dialog.getExistingDirectory())
        if dir:
            print 'change to new project path : ', dir
            import Base
            Base.__currentProjectPath__ = dir
            import PyDDA
            PyDDA.setCurrentProjectPath(dir)


class SetPanelSize:
    '''
    choose workbench for DDA
    '''
    def __init__(self):
        self.initSettingPanel()
    
    def GetResources(self):
        return {
                'MenuText': "SetPanelSize",
                'ToolTip': "Set Panel Size"}
        
    def initSettingPanel(self):
        self.mainDialog = QtGui.QWidget()
        layout = QtGui.QGridLayout(self.mainDialog)
        
        startPointLabel = QtGui.QLabel('please input the left-bottom corner coordinate.')
        layout.addWidget(startPointLabel , 0 , 0 , 1 , 4 , QtCore.Qt.AlignLeft)
        
        xLabel = QtGui.QLabel('X      :')
        layout.addWidget(xLabel , 1 , 0 , QtCore.Qt.AlignLeft)
        self.xValue = QtGui.QDoubleSpinBox()
        self.xValue.setDecimals(2)
        self.xValue.setRange(-99999.99 , 9999.99)
        self.xValue.setSingleStep(0.01)
        self.xValue.setValue(50)
        layout.addWidget(self.xValue , 1 , 1 , QtCore.Qt.AlignLeft)
        
        yLabel = QtGui.QLabel('Y      :')
        layout.addWidget(yLabel , 1 , 2 , QtCore.Qt.AlignLeft)
        self.yValue = QtGui.QDoubleSpinBox()
        self.yValue.setDecimals(2)
        self.yValue.setRange(-99999.99 , 9999.99)
        self.yValue.setSingleStep(0.01)
        self.yValue.setValue(10)
        layout.addWidget(self.yValue , 1 , 3 , QtCore.Qt.AlignLeft)
        
        sizeLabel = QtGui.QLabel('please input size of work panel.')
        layout.addWidget(sizeLabel , 2 , 0 , 1 ,4 , QtCore.Qt.AlignLeft)
        
        
        widthLabel = QtGui.QLabel('Width  :')
        layout.addWidget(widthLabel , 3 , 0 , QtCore.Qt.AlignLeft)
        self.widthValue = QtGui.QDoubleSpinBox()
        self.widthValue.setDecimals(2)
        self.widthValue.setRange(1 , 9999.99)
        self.widthValue.setSingleStep(0.01)
        self.widthValue.setValue(200)
        layout.addWidget(self.widthValue , 3 , 1 , QtCore.Qt.AlignLeft)
        
        heightLabel = QtGui.QLabel('Hieght :')
        layout.addWidget(heightLabel , 3 , 2 , QtCore.Qt.AlignLeft)
        self.heightValue = QtGui.QDoubleSpinBox()
        self.heightValue.setDecimals(2)
        self.heightValue.setRange(1 , 9999.99)
        self.heightValue.setSingleStep(0.01)
        self.heightValue.setValue(150)
        layout.addWidget(self.heightValue , 3 , 3 , QtCore.Qt.AlignLeft)
        
        okBtn = QtGui.QPushButton(text='OK')
        layout.addWidget(okBtn , 4 , 2 , QtCore.Qt.AlignLeft)
        cancelBtn = QtGui.QPushButton(text='Cancel')
        layout.addWidget(cancelBtn , 4 , 3 , QtCore.Qt.AlignLeft)
        
        okBtn.pressed.connect(self.saveResult)
        okBtn.pressed.connect(self.mainDialog.hide)
        cancelBtn.pressed.connect(self.mainDialog.hide)
        
        self.mainDialog.setLayout(layout)
        
    def saveResult(self):
        import Base
        Base.__windowInfo__ = \
            [self.xValue.value() , self.xValue.value()+self.widthValue.value()\
            ,self.yValue.value() , self.yValue.value()+self.heightValue.value()]
            
        print Base.__windowInfo__
        FreeCADGui.runCommand('DDA_ResetCamera')
    
    def Activated(self):
        self.mainDialog.show()



#---------------------------------------------------------------------------
# Adds the icons & commands to the FreeCAD command manager, and sets defaults
#---------------------------------------------------------------------------
        
# drawing commands
FreeCAD.Console.PrintMessage ('add command\n')
FreeCADGui.addCommand('Line', Line())
FreeCADGui.addCommand('Circle',Circle())
FreeCAD.Console.PrintMessage ('command added done\n')

FreeCADGui.addCommand('DDA_ChooseProjectPath', ChooseProjectPath())
FreeCADGui.addCommand('DDA_SetPanelSize', SetPanelSize())

# a global place to look for active draft Command
FreeCAD.Console.PrintMessage ('set active command\n')
FreeCAD.activeDDACommand = None 
