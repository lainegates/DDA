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


def calcIntersection(list1 , list2):
    '''
    calculate intersection of list1  and list2
    :param list1:
    :param list2:
    '''
    result = []
#        print 'list1 : ' , list1 , ' list2 : ' , list2
    i = j = 0
    if len(list1)>0 and len(list2)>0:
        while True:
            if list1[i] == list2[j]:
                result.append(list1[i])
                i+=1
                j+=1
            elif list1[i]>list2[j]:
                j+=1
            elif list1[i]<list2[j]:
                i+=1
            if i== len(list1) or j==len(list2):
                break
#        print 'result : ' , result
#        print '================================'
    return result

def calcUnion(list1 , list2):
    '''
    calculate intersection of list1  and list2
    :param list1:
    :param list2:
    '''
    result = []
#    print 'list1 : ' , list1 , ' list2 : ' , list2
    i = j = 0
    if len(list1)==0:
        result = list2[:]
    elif len(list2)==0:
        result = list1[:]
    else: 
        while True:
            if list1[i] == list2[j]:
                result.append(list1[i])
                i+=1
                j+=1
            elif list1[i]>list2[j]:
                result.append(list2[j])
                j+=1
            elif list1[i]<list2[j]:
                result.append(list1[i])
                i+=1                
            if i== len(list1) or j==len(list2):
                break
        if i<len(list1):
            result.extend(list1[i:])
        elif j<len(list2):
            result.extend(list2[j:])
#        print 'result : ' , result
#        print '================================'
    return result

class BlockRectangles:
    
    def __init__(self):
        self.blockRects = []
    
    def getXYRange(self,points):
        '''
        get xmin , xmax , ymin , ymax
        '''
#        xmin = points[0].x
#        xmax = points[0].x 
#        ymin = points[0].y
#        ymax = points[0].y
#        for i in range(1,len(points)):
#            if xmin>points[i].x:
#                xmin = points[i].x
#            elif xmax<points[i].x:
#                xmax = points[i].x
#            
#            if ymin>points[i].y:
#                ymin = points[i].y
#            elif ymax<points[i].y:
#                ymax = points[i].y

        xmin = points[0][0]
        xmax = points[0][0] 
        ymin = points[0][1]
        ymax = points[0][1]
        for i in range(1,len(points)):
            if xmin>points[i][0]:
                xmin = points[i][0]
            elif xmax<points[i][0]:
                xmax = points[i][0]
            
            if ymin>points[i][1]:
                ymin = points[i][1]
            elif ymax<points[i][1]:
                ymax = points[i][1]
                
        return xmin , xmax , ymin , ymax
    
    def addBlockRect(self, xmin , ymax , xmax , ymin):
        '''
        left-top and right-bottom vertex
        :param xmin:
        :param ymax:
        :param xmax:
        :param ymin:
        '''
        self.blockRects.append((xmin,ymax,xmax,ymin))

        
    def handleBlockXYRange(self,polygon):
        xmin , xmax , ymin , ymax = self.getXYRange(polygon)
        self.addBlockRect(xmin, ymax, xmax, ymin)
        
    def resetXYRange(self):
        self.blockRects = []

class LineSelection:
    def __init__(self):
        self.segments = [] # format of segments : [ ( startValue , endValue , blockNo ) ... ]
        
    def cmp(self , t):
        return t[0]  # use t[0] as base to compare
    
    def setData(self , tmpData):
        data = tmpData[:]
        data.sort(key=self.cmp)
        self.segments = data 
        
    def getIntersectedBlockNo(self , startValue , endValue):
        assert endValue > startValue
        result = []
        endIdx = self.getIndex(endValue)
        s=0
        while s<=endIdx :
            if startValue < self.segments[s][1]:
                result.append(self.segments[s][2]) # self.segments[s][2] is blockNo 
            s+=1
        result.sort()
        return result
        
    def getIndex(self , num):
        '''
        this function will find 'num''s index in 'coords'
        if 'num' is not in 'coords' , return i that coords[i]< 'num' < coords[i+1] 
        :param num:
        :param coords:
        '''
        t = len(self.segments)-1 
        while t>=0:
            if num>self.segments[t][0]:
                break
            t-=1
        return t
        
class RectangleSelection:
    def __init__(self):
        self.XSelection = LineSelection()
        self.YSelection = LineSelection()
        
    def setData(self , rects):
        XCoords , YCoords = self.convertData(rects)
        assert len(XCoords)>0 and len(YCoords)>0
        self.XSelection.setData(XCoords)
        self.YSelection.setData(YCoords)
        
    def convertData(self, rects):
        XCoords = []
        YCoords = []
        rects = self.getNormalizedRects(rects)
        for i , r in enumerate(rects):
            XCoords.append(( r[0] , r[2] , i))
            YCoords.append(( r[1] , r[3] , i ))
#        print 'rects : ' , rects
#        print 'XCoords : ' , XCoords
#        print 'YCoords : ' , YCoords
        return XCoords , YCoords
        
    def getIntersectedRectsNo(self , X1 , Y1 , X2 , Y2):
        if X1>X2:
            X1 , X2 = X2 , X1
        if Y1>Y2:
            Y1 , Y2 = Y2 , Y1
        s1 = self.XSelection.getIntersectedBlockNo(X1, X2)
        s2 = self.YSelection.getIntersectedBlockNo(Y1, Y2)
#        print 'X intersects : ' , s1
#        print 'Y intersects : ' , s2
        return calcIntersection(s1,s2)
    
    def getNormalizedRects(self , rects):
        for i , r in enumerate(rects):
            rects[i] = self.normalizeRect(r)
        return rects

    def normalizeRect(self , rect):
        '''
        rect if format of (X1 , Y1 , X2 , Y2) , this function's result will guanrantee ( X1 , Y1 ) and ( X2 , Y2)
        are left-bottom and right-top vertices
        :param rect:
        '''
        r = rect
        if rect[0] > rect[2]:
            r = ( rect[2] , rect[1] , rect[0] , rect[3])
        if rect[1] > rect[3]: # left-top and right-bottom vertices , so rect[1] > rect[3]
            r = ( rect[0] , rect[3] , rect[2] , rect[1])
        return r


rectSelection = RectangleSelection()
blocksRects = BlockRectangles()
            
            
            
##########################################################
# the following class is used to calculate border.
# R1 _R6                          R5_ R4
#    ||  J________________________I ||
#    || /                         \ ||
#    ||/                           \||
#    ||A                          H| |
#    ||                            | |
#    || B                          | |
#    | \                          G/ |
#    |  \  _____________________  /  |
#    |  C\/D                   E\/F  |
#    |_______________________________|                           
#    R2                               R3
#  in this graph . A-B-C-D-E-F-G-H-I-J is the original boundary.
#  A-R6-R1-R2-R3-R4-R5-H is the result 
##########################################################

class BorderCalculator:
    def __init__(self):
        self.up = None  # the max y
        self.down = None # the min y
        self.left = None # the min x
        self.right = None # the max x
        
        self.leftIdx = None   # index of the most left and most up point . mainly to left 
        self.rightIdx = None  # index of the most right and most up point . mainly to right
        
        self.zValue = 0 # the z value of the points in result
        
        self.marginRatio = 0.05  # the ratio of border thickness to max(self.up-self.down , self.right-self.left)

    def __updateRadius4PointsInBase(self):
        import Base
        difference = self.up - self.down
        tmp = self.right - self.left
        if difference <tmp:
            difference = tmp        
        
        Base.__radius4Points__ = difference*0.02

    def __calculateRange(self , pts):
        '''
        in the former graph , this function return the indexes of point 'A' and point 'H'
        :param points: boundary points
        '''
        self.leftIdx = 0
        self.rightIdx = 0
        self.up = pts[0][1]
        self.down = pts[0][1]
        self.left = pts[0][0]
        self.right = pts[0][0]
        for i in range(1, len(pts)):
            p = pts[i]
            if p[0]<self.left or (p[0]==self.left and p[1] > pts[self.leftIdx][1]):
                self.leftIdx = i
                self.left = p[0]
                    
            if p[0]>self.right or (p[0]==self.right and p[1] > pts[self.rightIdx][1]):
                self.rightIdx = i
                self.right = p[0]
            
            if p[1]<self.down:
                self.down = p[1]
                    
            if p[1]>self.up:
                self.up = p[1]
                
#        print 'left : %f    index  %f'%(self.left , self.leftIdx)
#        print 'right : %f    index  %f'%(self.right , self.rightIdx)
#        print 'up : %f'%self.up
#        print 'down : %f'% self.down
        self.__updateRadius4PointsInBase()

    def __calculateNewBoundaries(self , pts):
        '''
        in the former graph , this function calculate the 'A-R6-R1-R2-R3-R4-R5-H'
        the len(result) is also 8
        '''
        margin = self.right - self.left
        tmp = self.up - self.down
        if tmp>margin:
            margin = tmp
        minX = self.left - margin*self.marginRatio
        maxX = self.right + margin*self.marginRatio
        minY = self.down - margin*self.marginRatio
        maxY = self.up + margin*self.marginRatio
        
        p = pts[self.leftIdx]
        result = [(p[0] , p[1], self.zValue)]
        
        result.append((minX , pts[self.leftIdx][1] , self.zValue))
        result.append((minX , minY , self.zValue))
        result.append((maxX , minY , self.zValue))
        result.append((maxX , pts[self.rightIdx][1] , self.zValue))
        
        p = pts[self.rightIdx]
        result.append((p[0] , p[1], self.zValue))
        
        t = self.rightIdx
        while t!=self.leftIdx:
            t=(t+1)%len(pts)
            result.append((pts[t][0] , pts[t][1] , self.zValue))
        
        return result
    
    def calcualteBorder(self, pts):
        self.__calculateRange(pts)
        return self.__calculateNewBoundaries(pts)

####################################################
#
#   tunnel bolt elements generator
#     (currently only tunnel of type 2 has the bolt element generator)
#
####################################################

class TunnelBoltsGenerator:
    @staticmethod
    def generateBolts4Tunnel1(centerX , centerY , hAxesLength , vAxesLength \
                      , boltLength , boltLength2 , boltsDistance ):
        import DDACalcTools
        bolts = DDACalcTools.pyBolts()
        print bolts.size()
#        DDACalcTools.calcBolts4Type2Tunnel( float(centerX) , float(centerY) , float(hAxesLength) \
#              , float(vAxesLength) , float(boltLength) , float(boltLength2) , float(boltsDistance) , bolts)
        DDACalcTools.calcBolts4Type1Tunnel( centerX , centerY , hAxesLength \
              , vAxesLength , boltLength , boltLength2 , boltsDistance , bolts)
        
        return TunnelBoltsGenerator._convert2BoltElements(bolts)
        
    @staticmethod
    def generateBolts4Tunnel2(centerX , centerY , halfWidth , halfHeight \
                      , arcHeight , boltLength , boltLength2 , boltsDistance ):
        import DDACalcTools
        bolts = DDACalcTools.pyBolts()
        print bolts.size()
        DDACalcTools.calcBolts4Type2Tunnel( float(centerX) , float(centerY) , float(halfWidth), float(halfHeight) \
            , float(arcHeight) , float(boltLength) , float(boltLength2) , float(boltsDistance) , bolts)
        
        return TunnelBoltsGenerator._convert2BoltElements(bolts)
        
    @staticmethod
    def generateBolts4Tunnel3(centerX , centerY , hAxesLength , vAxesLength \
                      , cornerHeight , boltLength , boltLength2 , boltsDistance ):
        import DDACalcTools
        bolts = DDACalcTools.pyBolts()
        print bolts.size()
        DDACalcTools.calcBolts4Type3Tunnel( float(centerX) , float(centerY) , float(hAxesLength) , float(vAxesLength) \
            , float(cornerHeight) , float(boltLength) , float(boltLength2) , float(boltsDistance) , bolts)
        
        return TunnelBoltsGenerator._convert2BoltElements(bolts)
        
    @staticmethod
    def generateBolts4Tunnel4(centerX , centerY , radius , cornerHeight \
                      , ifRotate , boltLength , boltLength2 , boltsDistance ):
        import DDACalcTools
        bolts = DDACalcTools.pyBolts()
        print bolts.size()
        DDACalcTools.calcBolts4Type4Tunnel( float(centerX) , float(centerY) , float(radius), float(cornerHeight) \
            , float(ifRotate) , float(boltLength) , float(boltLength2) , float(boltsDistance) , bolts)
        
        return TunnelBoltsGenerator._convert2BoltElements(bolts)
        
        
    @staticmethod
    def _convert2BoltElements( bolts):
        from loadDataTools import BoltElement
        resultBolts=[]
        for bolt in bolts:
            p1 = ( bolt.startPoint.x , bolt.startPoint.y , 0 )
            p2 = ( bolt.endPoint.x , bolt.endPoint.y , 0 )
            resultBolts.append(BoltElement(p1 , p2 , 0 , 0 , 0))
            print "(%lf , %lf) (%lf , %lf)"%(bolt.startPoint.x  \
                    ,bolt.startPoint.y , bolt.endPoint.x,bolt.endPoint.y)
        return resultBolts

class ReadustCamera:
    def GetResources(self):
        return {
                'MenuText':  'adjustCamera',
                'ToolTip': "adjust camera."}
    
    def Activated(self):
        import FreeCADGui

        centerX = 20
        centerY = 5
        height = 15
        
        import Base
        windowInfo = Base.__windowInfo__
        if windowInfo!=None and len(windowInfo)==4:
            centerX = (windowInfo[0]+windowInfo[1])/2
            centerY = (windowInfo[2]+windowInfo[3])/2
            height = (windowInfo[1]-windowInfo[0])*0.75
            
        print windowInfo
        print 'camera center : ( %f , %f )'% (centerX,centerY)
        camera = '#Inventor V2.1 ascii\n\n\nOrthographicCamera {\n  viewportMapping ADJUST_CAMERA\n  position %f %f 3\n  orientation 0 0 1  0\n  aspectRatio 1\n  focalDistance 5\n  height %f\n\n}\n'%(centerX,centerY,height)
        FreeCADGui.activeDocument().activeView().setCamera(camera)        
        
    def finish(self):
        pass

import FreeCADGui  
FreeCADGui.addCommand('DDA_ResetCamera', ReadustCamera())













