# coding=gbk
#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2011                                                    *  
#*   Yorik van Havre <yorik@uncreated.net>                                 *  
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

import FreeCADGui , WorkingPlane1, math, re
from pivy import coin
from FreeCAD import Vector
from drawGui import *
#from draftlibs import fcvec, fcgeo
import fcvec, fcgeo
from functools import partial
import Part
            
# sets the default working plane
plane = WorkingPlane1.plane()
FreeCAD.DDADockWidget = plane
plane.alignToPointAndAxis(Vector(0, 0, 0), Vector(0, 0, 1), 0)


#---------------------------------------------------------------------------
# Trackers
#---------------------------------------------------------------------------

class Tracker:
    "A generic Draft Tracker, to be used by other specific trackers"
    # 辅助绘图工具
    def __init__(self, dotted=False, scolor=None, swidth=None, children=[], ontop=False):
        self.ontop = ontop
        color = coin.SoBaseColor()
        color.rgb = scolor or FreeCADGui.DDADockWidget.getDefaultColor("ui")
        drawstyle = coin.SoDrawStyle()
        if swidth:
            drawstyle.lineWidth = swidth
        if dotted:
            drawstyle.style = coin.SoDrawStyle.LINES
            drawstyle.lineWeight = 3
            drawstyle.linePattern = 0x0f0f  # 0xaa ， 虚线的具体样式
        node = coin.SoSeparator()
        for c in [drawstyle, color] + children:  # openInventor的处理方式，前两决定后续children的样式
            node.addChild(c)
        self.switch = coin.SoSwitch()  # this is the on/off switch
        self.switch.addChild(node)
        self.switch.whichChild = -1
        self.Visible = False
        todo.delay(self._insertSwitch, self.switch)

    def finalize(self):
        todo.delay(self._removeSwitch, self.switch)
        self.switch = None

    def _insertSwitch(self, switch):
        '''insert self.switch into the scene graph.  Must not be called
        from an event handler (or other scene graph traversal).'''
        sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
        if self.ontop:
            sg.insertChild(switch, 0)
        else:
            sg.addChild(switch)

    def _removeSwitch(self, switch):
        '''remove self.switch from the scene graph.  As with _insertSwitch,
        must not be called during scene graph traversal).'''
        sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
        sg.removeChild(switch)

    def on(self):
        self.switch.whichChild = 0
        self.Visible = True

    def off(self):
        self.switch.whichChild = -1
        self.Visible = False
                
class snapTracker(Tracker):
    "A Snap Mark tracker, used by tools that support snapping"
    def __init__(self):
        color = coin.SoBaseColor()
        color.rgb = FreeCADGui.DDADockWidget.getDefaultColor("snap")
        self.marker = coin.SoMarkerSet()  # this is the marker symbol
        self.marker.markerIndex = coin.SoMarkerSet.CIRCLE_FILLED_9_9
        self.coords = coin.SoCoordinate3()  # this is the coordinate
        self.coords.point.setValue((0, 0, 0))
        node = coin.SoAnnotation()
        node.addChild(self.coords)
        node.addChild(color)
        node.addChild(self.marker)
        Tracker.__init__(self, children=[node])

    def setMarker(self, style):
        if (style == "point"):
            self.marker.markerIndex = coin.SoMarkerSet.CIRCLE_FILLED_9_9
        elif (style == "square"):
            self.marker.markerIndex = coin.SoMarkerSet.DIAMOND_FILLED_9_9
        elif (style == "circle"):
            self.marker.markerIndex = coin.SoMarkerSet.CIRCLE_LINE_9_9

class lineTracker(Tracker):
    "A Line tracker, used by the tools that need to draw temporary lines"
    def __init__(self, dotted=False, scolor=None, swidth=None):
        line = coin.SoLineSet()  # 辅助图元，用coin显示，不是openCASCADE结构的
        line.numVertices.setValue(2)
        self.coords = coin.SoCoordinate3()  # this is the coordinate
        self.coords.point.setValues(0, 2, [[0, 0, 0], [1, 0, 0]])
        Tracker.__init__(self, dotted, scolor, swidth, [self.coords, line])

    def p1(self, point=None):
        "sets or gets the first point of the line"
        if point:
            self.coords.point.set1Value(0, point.x, point.y, point.z)
        else:
            return Vector(self.coords.point.getValues()[0].getValue())

    def p2(self, point=None):
        "sets or gets the second point of the line"
        if point:
            self.coords.point.set1Value(1, point.x, point.y, point.z)
        else:
            return Vector(self.coords.point.getValues()[-1].getValue())
                        
    def getLength(self):
        "returns the length of the line"
        p1 = Vector(self.coords.point.getValues()[0].getValue())
        p2 = Vector(self.coords.point.getValues()[-1].getValue())
        return (p2.sub(p1)).Length
        
class rectangleTracker(Tracker):
    "A Rectangle tracker, used by the rectangle tool"
    def __init__(self, dotted=False, scolor=None, swidth=None):
        self.origin = Vector(0, 0, 0)
        line = coin.SoLineSet()
        line.numVertices.setValue(5)
        self.coords = coin.SoCoordinate3()  # this is the coordinate
        self.coords.point.setValues(0, 5, [[0, 0, 0], [2, 0, 0], [2, 2, 0], [0, 2, 0], [0, 0, 0]])
        Tracker.__init__(self, dotted, scolor, swidth, [self.coords, line])
        self.u = plane.u
        self.v = plane.v

    def setorigin(self, point):
        "sets the base point of the rectangle"
        self.coords.point.set1Value(0, point.x, point.y, point.z)
        self.coords.point.set1Value(4, point.x, point.y, point.z)
        self.origin = point

    def update(self, point):
        "sets the opposite (diagonal) point of the rectangle"
        diagonal = point.sub(self.origin)
        inpoint1 = self.origin.add(fcvec.project(diagonal, self.v))
        inpoint2 = self.origin.add(fcvec.project(diagonal, self.u))
        self.coords.point.set1Value(1, inpoint1.x, inpoint1.y, inpoint1.z)
        self.coords.point.set1Value(2, point.x, point.y, point.z)
        self.coords.point.set1Value(3, inpoint2.x, inpoint2.y, inpoint2.z)

    def setPlane(self, u, v=None):
        '''sets given (u,v) vectors as working plane. You can give only u
        and v will be deduced automatically given current workplane'''
        self.u = u
        if v:
            self.v = v
        else:
            norm = plane.u.cross(plane.v)
            self.v = self.u.cross(norm)

    def p1(self, point=None):
        "sets or gets the base point of the rectangle"
        if point:
            self.setorigin(point)
        else:
            return Vector(self.coords.point.getValues()[0].getValue())

    def p2(self):
        "gets the second point (on u axis) of the rectangle"
        return Vector(self.coords.point.getValues()[3].getValue())

    def p3(self, point=None):
        "sets or gets the opposite (diagonal) point of the rectangle"
        if point:
            self.update(point)
        else:
            return Vector(self.coords.point.getValues()[2].getValue())

    def p4(self):
        "gets the fourth point (on v axis) of the rectangle"
        return Vector(self.coords.point.getValues()[1].getValue())
                
    def getSize(self):
        "returns (length,width) of the rectangle"
        p1 = Vector(self.coords.point.getValues()[0].getValue())
        p2 = Vector(self.coords.point.getValues()[2].getValue())
        diag = p2.sub(p1)
        return ((fcvec.project(diag, self.u)).Length, (fcvec.project(diag, self.v)).Length)

    def getNormal(self):
        "returns the normal of the rectangle"
        return (self.u.cross(self.v)).normalize()

class arcTracker(Tracker):
    "An arc tracker"
    def __init__(self, dotted=False, scolor=None, swidth=None, start=0, end=math.pi * 2):
        self.circle = None
        self.startangle = math.degrees(start)
        self.endangle = math.degrees(end)
        self.trans = coin.SoTransform()
        self.trans.translation.setValue([0, 0, 0])
        self.sep = coin.SoSeparator()
        self.recompute()
        Tracker.__init__(self, dotted, scolor, swidth, [self.trans, self.sep])

    def setCenter(self, cen):
        "sets the center point"
        self.trans.translation.setValue([cen.x, cen.y, cen.z])

    def setRadius(self, rad):
        "sets the radius"
        self.trans.scaleFactor.setValue([rad, rad, rad])

    def getRadius(self):
        "returns the current radius"
        return self.trans.scaleFactor.getValue()[0]

    def setStartAngle(self, ang):
        "sets the start angle"
        self.startangle = math.degrees(ang)
        self.recompute()

    def setEndAngle(self, ang):
        "sets the end angle"
        self.endangle = math.degrees(ang)
        self.recompute()

    def getAngle(self, pt):
        "returns the angle of a given vector"
        c = self.trans.translation.getValue()
        center = Vector(c[0], c[1], c[2])
        base = plane.u
        rad = pt.sub(center)
        return(fcvec.angle(rad, base, plane.axis))

    def getAngles(self):
        "returns the start and end angles"
        return(self.startangle, self.endangle)
                
    def setStartPoint(self, pt):
        "sets the start angle from a point"
        self.setStartAngle(-self.getAngle(pt))

    def setEndPoint(self, pt):
        "sets the end angle from a point"
        self.setEndAngle(self.getAngle(pt))
                
    def setApertureAngle(self, ang):
        "sets the end angle by giving the aperture angle"
        ap = math.degrees(ang)
        self.endangle = self.startangle + ap
        self.recompute()

    def recompute(self):
        if self.circle: self.sep.removeChild(self.circle)
        self.circle = None
        c = Part.makeCircle(1, Vector(0, 0, 0), plane.axis)
        buf = c.writeInventor(2, 0.01)
        ivin = coin.SoInput()
        ivin.setBuffer(buf)
        ivob = coin.SoDB.readAll(ivin)
        # In case reading from buffer failed
        if ivob and ivob.getNumChildren() > 1:
            self.circle = ivob.getChild(1).getChild(0)
            self.circle.removeChild(self.circle.getChild(0))# 材料属性
            self.circle.removeChild(self.circle.getChild(0))# 绘制属性
            self.sep.addChild(self.circle)  # 留下的有coin.SoCoordinate3和coin.SoLineSet
        else:
            FreeCAD.Console.PrintWarning("arcTracker.recompute() failed to read-in Inventor string\n")

		

class PlaneTracker(Tracker):
    "A working plane tracker"
    def __init__(self):
        # getting screen distance
        p1 = FreeCADGui.ActiveDocument.ActiveView.getPoint((100, 100))
        p2 = FreeCADGui.ActiveDocument.ActiveView.getPoint((110, 100))
        bl = (p2.sub(p1)).Length * (Base.getParam("snapRange") / 2)
        self.trans = coin.SoTransform()
        self.trans.translation.setValue([0, 0, 0])
        m1 = coin.SoMaterial()
        m1.transparency.setValue(0.8)
        m1.diffuseColor.setValue([0.4, 0.4, 0.6])
        c1 = coin.SoCoordinate3()
        c1.point.setValues([[-bl, -bl, 0], [bl, -bl, 0], [bl, bl, 0], [-bl, bl, 0]])
        f = coin.SoIndexedFaceSet()
        f.coordIndex.setValues([0, 1, 2, 3])
        m2 = coin.SoMaterial()
        m2.transparency.setValue(0.7)
        m2.diffuseColor.setValue([0.2, 0.2, 0.3])
        c2 = coin.SoCoordinate3()
        c2.point.setValues([[0, bl, 0], [0, 0, 0], [bl, 0, 0], [-.05 * bl, .95 * bl, 0], [0, bl, 0],
                            [.05 * bl, .95 * bl, 0], [.95 * bl, .05 * bl, 0], [bl, 0, 0], [.95 * bl, -.05 * bl, 0]])
        l = coin.SoLineSet()
        l.numVertices.setValues([3, 3, 3])
        s = coin.SoSeparator()
        s.addChild(self.trans)
        s.addChild(m1)
        s.addChild(c1)
        s.addChild(f)
        s.addChild(m2)
        s.addChild(c2)
        s.addChild(l)
        Tracker.__init__(self, children=[s])

    def set(self, pos=None):
        if pos:                        
            Q = plane.getRotation().Rotation.Q
        else:
            plm = plane.getPlacement()
            Q = plm.Rotation.Q
            pos = plm.Base
        self.trans.translation.setValue([pos.x, pos.y, pos.z])
        self.trans.rotation.setValue([Q[0], Q[1], Q[2], Q[3]])
        self.on()


class gridTracker(Tracker):
    "A grid tracker"
    def __init__(self):
        # self.space = 1
        self.space = Base.getParam("gridSpacing")
        # self.mainlines = 10
        self.mainlines = Base.getParam("gridEvery")
        self.numlines = 100
        col = [0.2, 0.2, 0.3]
        
        self.trans = coin.SoTransform()
        self.trans.translation.setValue([0, 0, 0])
                
        bound = (self.numlines / 2) * self.space
        pts = []
        mpts = []
        for i in range(self.numlines + 1):
            curr = -bound + i * self.space
            z = 0
            if i / float(self.mainlines) == i / self.mainlines:
                mpts.extend([[-bound, curr, z], [bound, curr, z]])
                mpts.extend([[curr, -bound, z], [curr, bound, z]])
            else:
                pts.extend([[-bound, curr, z], [bound, curr, z]])
                pts.extend([[curr, -bound, z], [curr, bound, z]])
        idx = []
        midx = []
        for p in range(0, len(pts), 2):
            idx.append(2)
        for mp in range(0, len(mpts), 2):
            midx.append(2)

        mat1 = coin.SoMaterial()
        mat1.transparency.setValue(0.7)
        mat1.diffuseColor.setValue(col)
        self.coords1 = coin.SoCoordinate3()
        self.coords1.point.setValues(pts)
        lines1 = coin.SoLineSet()
        lines1.numVertices.setValues(idx)
        mat2 = coin.SoMaterial()
        mat2.transparency.setValue(0.3)
        mat2.diffuseColor.setValue(col)
        self.coords2 = coin.SoCoordinate3()
        self.coords2.point.setValues(mpts)
        lines2 = coin.SoLineSet()
        lines2.numVertices.setValues(midx)
        s = coin.SoSeparator()
        s.addChild(self.trans)
        s.addChild(mat1)
        s.addChild(self.coords1)
        s.addChild(lines1)
        s.addChild(mat2)
        s.addChild(self.coords2)
        s.addChild(lines2)
        Tracker.__init__(self, children=[s])
        self.update()

    def update(self):
        bound = (self.numlines / 2) * self.space
        pts = []
        mpts = []
        for i in range(self.numlines + 1):
            curr = -bound + i * self.space
            if i / float(self.mainlines) == i / self.mainlines:
                mpts.extend([[-bound, curr, 0], [bound, curr, 0]])
                mpts.extend([[curr, -bound, 0], [curr, bound, 0]])
            else:
                pts.extend([[-bound, curr, 0], [bound, curr, 0]])
                pts.extend([[curr, -bound, 0], [curr, bound, 0]])
        self.coords1.point.setValues(pts)
        self.coords2.point.setValues(mpts)

    def setSpacing(self, space):
        self.space = space
        self.update()

    def setMainlines(self, ml):
        self.mainlines = ml
        self.update()

    def set(self):
        Q = plane.getRotation().Rotation.Q
        self.trans.rotation.setValue([Q[0], Q[1], Q[2], Q[3]])
        self.on()

    def getClosestNode(self, point):
        "returns the closest node from the given point"
        # get the 2D coords.
        point = plane.projectPoint(point)
        u = fcvec.project(point, plane.u)
        lu = u.Length
        if u.getAngle(plane.u) > 1.5:
            lu = -lu
        v = fcvec.project(point, plane.v)
        lv = v.Length
        if v.getAngle(plane.v) > 1.5:
            lv = -lv
        # print "u = ",u," v = ",v
        # find nearest grid node
        pu = (round(lu / self.space, 0)) * self.space
        pv = (round(lv / self.space, 0)) * self.space
        rot = FreeCAD.Rotation()
        rot.Q = self.trans.rotation.getValue().getValue()
        return rot.multVec(Vector(pu, pv, 0))
