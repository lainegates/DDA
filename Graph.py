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


import Part
from FreeCAD import Base
import Base
from TrackerTools import plane
import DDADatabase
from Base import showErrorMessageBox

class BaseGraph():
    '''
    base graph class , which will be inherited by DLGraph etc for specific process
    '''
    def getPointInBaseVectorType(self , p , zValue = 0):
        if isinstance(p , Base.Vector):
            v1 = p         
        elif isinstance(p , tuple) or isinstance(p , list):
            v1 = Base.Vector( p[0] , p[1] , p[2])
        else:
            v1 = Base.Vector( p.x , p.y , zValue)
#            print v1 ,
#            print '<----> %f %f <---->%.6f %.6f'%(p.x , p.y , p.x , p.y)
        
        #print '==========   ' , type(v1) , ' =================='
        return v1

    def getPointInTupleType(self , p , zValue = 0):
        if isinstance(p , tuple):
            v1 = p         
        elif isinstance(p , Base.Vector) or isinstance(p , list):
            v1 = ( p[0] , p[1] , p[2])
        else:
            v1 = ( p.x , p.y , zValue)
#            print v1 ,
#            print '<----> %f %f <---->%.6f %.6f'%(p.x , p.y , p.x , p.y)
        
        #print '==========   ' , type(v1) , ' =================='
        return v1

        
    def getPointListInBaseVectorType(self , pts , zValue = 0):
        vertices = range(len(pts))
        t = len(pts)
        #t1 = pts.size()
        for i in range(len(pts)):
            vertices[i] = self.getPointInBaseVectorType(pts[i])
            
        pts=vertices
        file = open('D:/DDAProject/testVector2.txt','ab')
        for i in range(len(pts)/2):
            file.write('%f %f %f %f\n'%(pts[2*i].x,pts[2*i].y,pts[2*i+1].x,pts[2*i+1].y))
        file.close()   
        
        return vertices
        
    def getPointListInTupleType(self , pts , zValue = 0):
        vertices = range(len(pts))
        t = len(pts)
        #t1 = pts.size()
        for i in range(len(pts)):
            vertices[i] = self.getPointInTupleType(pts[i])
        return vertices
        
    def drawLine( self , pts , shapeType , materialIndex = 0):
#        v1 = self.getPointInBaseVectorType(p1)
#        v2 = self.getPointInBaseVectorType(p2)
#            
        if shapeType == 'BoundaryLine':
            Base.addLines2Document( pts , closed=False, face=False, fname = 'BoundaryLine')
        elif shapeType == 'JointLine':
            Base.addLines2Document( pts , closed=False, face=False, fname = 'JointLine', materialIndex = materialIndex)
        elif shapeType == 'TunnelLine':
            Base.addLines2Document( pts , closed=False, face=False, fname = 'TunnelLine', materialIndex = materialIndex)
        elif shapeType == 'AdditionalLine':
            Base.addLines2Document( pts , closed=False, face=False, fname = 'AdditionalLine')
        elif shapeType == 'MaterialLine':
            Base.addLines2Document( pts , closed=False, face=False, fname = 'MaterialLine')
        elif shapeType == 'BoltElemnet':   
            Base.addLines2Document( pts , closed=False, face=False, fname = 'BoltElemnet')
        elif shapeType == 'Frame':   # frame 其实没有用
            Base.addLines2Document( pts , closed=False, face=False, fname = 'Frame')
        else :
            print 'Unkown Type : ' , shapeType
            
    def drawLines(self , points , shapeType , materialIndex = 0):
        vertices = self.getPointListInBaseVectorType(points)
#        vertices = self.getPointListInTupleType(points)
        print '********* %s **********points :%d  %d'%( shapeType ,len(points) ,len(vertices))
        if len(vertices)==0 :
            return 
        
#        print type(vertices) , '     ' , type(vertices[0])
        self.drawLine(vertices, shapeType, materialIndex)
        return vertices
        

    def drawCircle(self , center , radius , shapeType):
        import FreeCAD
        p = FreeCAD.Placement()
        vec = self.getPointInBaseVectorType(center)
#        vec = self.getPointInTupleType(center)
        p.move(vec)
        Base.addCircle2Document(vec , radius , placement=p , face=False, fname =shapeType)

    def drawCircles(self , centers , radius , shapeType):
        for center in centers :
            self.drawCircle(center, radius, shapeType)
                        
    def drawPolygon(self , points , shapeType , materialIndex = 0):
        p = plane.getRotation()
        vertices = range(len(points))
        for i in range(len(points)):
#            vertices[i] = (points[i].x , points[i].y , -1)
            vertices[i] = (points[i][1] , points[i][2] , -1)
            
#        import checkConcave_and_triangulate as triangulate
#        assert triangulate.IfConcave(vertices)
                
        if shapeType == 'Block':
            Base.addPolygons2Document(vertices , placement=p , fname = 'Block' )#, materialIndex = 1)#materialIndex)
            
    def drawPolygons(self , blocks):
        from loadDataTools import Block
        p = plane.getRotation()
        pts = []
        for block in blocks:
            pts.extend(block.vertices)
        Base.initPolygonSets()
        Base.addPolygons2Document(pts, placement=p, fname='Block')
        Base.polygonsAddedDone()

#    def showStage1Graph(self , a):
#        '''
#        DL , DC both have 2 stages , the second stage is the result , so this is the first stage
#        :param a: a object from PyDDA , maybe PyDDA.DL() , PyDDA.DC() , etc.
#        '''
#        pass
#
#    def showStage2Graph(self , a):        
#        '''
#        DL , DC both have 2 stages , the second stage is the result , so this is the second stage
#        :param a: a object from PyDDA , maybe PyDDA.DL() , PyDDA.DC() , etc , which does the real calculation process.
#        '''
#        pass
    
class DLInputGraph():
    def showGraph4File(self):
        import DDADisplay
        DDADisplay.clearDocument()
        
        Base.DDAObserver.lock = True
        
        from DDADatabase import dl_database as database
        boundaryNodes = database.boundaryNodes
        if len(boundaryNodes)>0:
            Base.addPolyLine2Document('BoundaryLine', ifStore2Database=False)
            print 'draw boundary lines : ' , len(boundaryNodes)

        points = database.fixedPoints
        if len(points)>0:
            Base.addCircles2Document('FixedPoint')
            print 'draw fixed points : ' , len(points)

        points = database.measuredPoints
        if len(points)>0:
            Base.addCircles2Document('MeasuredPoint')
            print 'draw measured points : ' , len(points)

        points = database.loadingPoints
        if len(points)>0:
            Base.addCircles2Document('LoadingPoint')
        print 'draw loading points : ' , len(points)

        points = database.holePoints
        if len(points)>0:
            Base.addCircles2Document('HolePoint')
        print 'draw hole points : ' , len(points)
        
        Base.DDAObserver.lock = False
    
class DLGraph(BaseGraph):
    def showGraph4File(self):
        import DDADisplay
        DDADisplay.clearDocument()

        from DDADatabase import dc_inputDatabase
        import Base
        
        Base.DDAObserver.lock = True

        from DDADatabase import dl_database as database
        boundaryNodes = database.boundaryNodes
        if len(boundaryNodes)>0:
            Base.addPolyLine2Document('BoundaryLine', ifStore2Database=False)
#            self.drawLines(boundaryNodes, 'BoundaryLine')
            print 'draw boundary lines : ' , len(boundaryNodes)
        
        nums = 0        
        lines = dc_inputDatabase.jointLines
        # the viewProvider will take data from dc_inputDatabase.jointLines 
#        self.drawLines( [lines[0].startPoint , lines[0].endPoint] ,'JointLine' , 0)
        if len(lines)>0:
            Base.addLines2Document('JointLine') 
            print 'draw joints : ' , len(lines)
        
        points = dc_inputDatabase.fixedPoints
#        self.drawCircles(points, Base.__radius4Points__, 'FixedPoint')
        if len(points)>0:
            Base.addCircles2Document('FixedPoint')
            print 'draw fixed points : ' , len(points)

        points = dc_inputDatabase.measuredPoints
#        self.drawCircles(points , Base.__radius4Points__, 'MeasuredPoint')
        if len(points)>0:
            Base.addCircles2Document('MeasuredPoint')
            print 'draw measured points : ' , len(points)

        points = dc_inputDatabase.loadingPoints
#        self.drawCircles(points , Base.__radius4Points__, 'LoadingPoint')
        if len(points)>0:
            Base.addCircles2Document('LoadingPoint')
        print 'draw loading points : ' , len(points)

        points = dc_inputDatabase.holePoints
#        self.drawCircles(points , Base.__radius4Points__, 'HolePoint')
        if len(points)>0:
            Base.addCircles2Document('HolePoint')
        print 'draw hole points : ' , len(points)
                                
        Base.recomputeDocument()
        
        Base.DDAObserver.lock = False
        
                                
class DCGraph(BaseGraph):
    '''
    draw scene for dc
    '''
    def showGraph4File(self):
        from DDADatabase import df_inputDatabase
        frame = df_inputDatabase

        from Base import DDAObserver
        DDAObserver.lock = True
        
        from interfaceTools import blocksRects , rectSelection
        
        from Base import __radius4Points__

        import Base
        Base.refreshPolygons()
        Base.refreshBlockBoundaryLines()
        nums = 0
        blocksRects.resetXYRange()
        blocks = frame.blocks
        for block in blocks:
            blocksRects.handleBlockXYRange(block.getPoints())
        print 'block number :  ' , len(blocks)
        rectSelection.setData(blocksRects.blockRects)

        points = frame.fixedPoints
#        self.drawCircles(points, Base.__radius4Points__, 'FixedPoint')
        if len(points)>0:
            Base.addCircles2Document('FixedPoint')
            print 'draw fixed points : ' , len(points)

        points = frame.measuredPoints
#        self.drawCircles(points , Base.__radius4Points__, 'MeasuredPoint')
        if len(points)>0:
            Base.addCircles2Document('MeasuredPoint')
            print 'draw measured points : ' , len(points)

        points = frame.loadingPoints
#        self.drawCircles(points , Base.__radius4Points__, 'LoadingPoint')
        if len(points)>0:
            Base.addCircles2Document('LoadingPoint')
        print 'draw loading points : ' , len(points)

        points = frame.holePoints
#        self.drawCircles(points , Base.__radius4Points__, 'HolePoint')
        if len(points)>0:
            Base.addCircles2Document('HolePoint')
        print 'draw hole points : ' , len(points)

        
        DDAObserver.lock = False