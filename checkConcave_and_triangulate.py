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


import PyTriangulation as Py
from PyTriangulation import Vector2d as point
from PyTriangulation import pyvector_point2 as pl
from FreeCAD import Vector
#plist = pl()
#plist.append( point(0,0))
#plist.append( point(4,0))
#plist.append( point(1,1))
#plist.append( point(0,4))
#result = pl()
#Py.triangulate(plist , result)
#
#print result.size()
#t = result.size()/3
#for i in range(t):
#    p1 = result[i*3]
#    p2 = result[i*3+1]
#    p3 = result[i*3+2]
#    print 'Triangle %d : (%f , %f )  (%f , %f ) , (%f , %f )'%(i,p1.x , p1.y , p2.x , p2.y , p3.x , p3.y)


def getUp(p1 , p2 , p3):
    ax = p1[0]-p2[0]
    ay = p1[1]-p2[1]
    bx = p2[0]-p3[0]
    by = p2[1]-p3[1]
    tmpRe = ax*by - bx*ay
    if tmpRe>0:
        tmpRe=1
    elif tmpRe<=0:
        tmpRe = -1
    else:
        print 'error'
#    print tmpRe
    return tmpRe

def IfConcave(plist2):
    if len(plist2)<3:
#        raise Exception('vertices number < 3')
        print '***************vertices number < 3*******************'
        return
    if plist2[0]==plist2[-1]:
        plist = plist2[:-1]
    else:
        plist = plist2
        
    res = getUp(plist[0],plist[1],plist[2])
    length = len(plist)
    for i in range(1,length-1):
        p1 = plist[i]
        p2 = plist[(i+1)%length]
        p3 = plist[(i+2)%length]

        tmp = getUp(p1,p2,p3)
#        print res , tmp
        if res != tmp:
            return True           
    return False

def triangulate(plist2):
    pnts = pl()
    if plist2[0]==plist2[-1]:
        plist = plist2[:-1]
    else:
        plist = plist2
        
    for t in plist:
        pnts.append(point(t[0],t[1]))
    result = pl()
    Py.triangulate(pnts , result)
    tmpRe = []
    for i , t in enumerate(result):
        tmpRe.append(Vector(t.x,t.y,-1))
    return tmpRe

def ifSegmentAndPolygonIntersect(segment2 , polygon2):
    seg = pl()
    poly = pl()
    polygon = polygon2
    if polygon2[0]==polygon2[-1]:
        polygon = polygon2[:-1]
        
    for t in segment2:
        seg.append(point(t[0],t[1]))
    for t in polygon:
        poly.append(point(t[0],t[1]))
    
    return Py.ifIntersection(seg , poly)

#pts = [Vector (22.7365, 8.45805, -7), Vector (25.2035, 10.0582, -7), Vector (24.8621, 7.91085, -7), Vector (24.018, 7.7756, -7), Vector (23.4091, 8.19992, -7), Vector (22.7365, 8.45805, -7)]
#print IfConcave(pts)
#print triangulate(pts)
