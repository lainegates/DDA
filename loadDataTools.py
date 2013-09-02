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

import FreeCADGui
from PyQt4 import QtCore , QtGui
import Base
from Base import showErrorMessageBox
import DDADatabase

def checkFileExists(path):
    import os
    if not os.path.isfile(path):
        showErrorMessageBox("FileError" , "File \"%s\" doesn't exist"%path)
        return False
    return True

class FileReader():
    '''
    read files , this class will omit the blank lines
    '''
    def __init__(self):
        self.__fileName = None
        self.__file = None
        
    def setFile(self, fileName):
        self.__fileName = fileName
        try:
            self.__file = open(self.__fileName , 'rb')
        except:
            showErrorMessageBox('file open error' , fileName + ' open failed')
            return False
        return True
    
    def getNextLine(self):
        line = self.__file.readline()
        while len(line)!=0:
            line = line.strip()
            if len(line)==0: # blank line with '\n'
                line = self.__file.readline()
            else:
                break   # this line is not blank
        if len(line)==0:  # file already ends
            import Base
            Base.showErrorMessageBox('file error' , 'unvalid data')
            raise
        return line
    
    def closeFile(self):
        self.__file.close()
            

class Block:
    def __init__(self):
        self.blockIndex = 0 # the index of this block
        self.startNo = 0 
        self.endNo = 0
        self.vertices = []
        self.parameters = []
        self.stressX = 0
        self.stressY = 0
        self.stressXY = 0
        self.materialNo = 0 # used in dc result
        
        # count how many hole points are on this block
        self.holePointsCount = 0
        
    def getPoints(self):
        return [(t[1],t[2],0) for t in self.vertices]
    
    def visible(self):
        if self.holePointsCount>0:
            return False
        elif self.holePointsCount==0:
            return True
        else :
            raise Exception('unvalid value %f'% self.holePointsCount)
        
class DDALine:
    def __init__(self , p1 , p2 , materialNo):
        self.startPoint = p1
        self.endPoint = p2
        self.materialNo = materialNo
        self.visible = True
        
class BoltElement(DDALine):
    def __init__(self , p1 , p2 , e , t , f):
        DDALine.__init__(self, p1, p2, 0)
        self.e = e
        self.t = t
        self.f = f
        
class DDAPolyLine:
    def __init__(self , pts , materialNo):
        self.pts = pts
        self.materialNo = materialNo
        self.visible = True
        
class DDAPoint:
    def __init__(self , x=0 , y=0):
        self.x = x
        self.y = y
        self.Xspeed = 0
        self.Yspeed = 0
        self.blockNo = 0
        self.visible = True
        
class FixedPoint(DDAPoint):
    pass

class LoadingPoint(DDAPoint):
    pass

class MeasuredPoint(DDAPoint):
    def __init__(self):
        DDAPoint.__init__(self)
        self.u = 0
        self.v = 0
        self.r = 0
        self.stressX = 0
        self.stressY = 0
        self.stressXY = 0

class HolePoint(DDAPoint):
    pass

class Graph:
    def __init__(self):
        self.blocks = []
        self.fixedPoints = []
        self.measuredPoints = []
        self.loadingPoints = []
        self.holePoints = []
        self.boltElements = []
        
    def reset(self):
        self.blocks = []
        self.fixedPoints = []
        self.measuredPoints = []
        self.loadingPoints = []
        self.boltElements = []

class BaseParseData():
    '''
    parse data loaded , data may be DL data , DC data etc.
    '''
    def parse(self , filename):
        '''
        abstract function , overwrited by subclass
        '''
        pass
    
    def parseFloatNum(self , numStr , itemName='None'):
        try:
            num = float(numStr)
        except:
            try:
                num = int(numStr)
            except:
                showErrorMessageBox( 'InputError' , itemName + ' should be a float number')
                return None
        return num
        
    def parseIntNum(self , numStr , itemName='None'):
        try:
            num = int(numStr)
        except:
            showErrorMessageBox( 'InputError' , itemName + ' should be a integer')
            return None
        return num
            
    
class ParseAndLoadDLData(BaseParseData):
    '''
    parse DL data
    '''
    def __init__(self):
        self.reset()
        self.__fileReader = FileReader()
        
    def GetResources(self):
        return {
                'MenuText':  'LoadDCInputData',
                'ToolTip': "Load DC Input Data"}
        
    def Activated(self):
        from Base import __currentProjectPath__
        if self.parse(__currentProjectPath__ + '/data.dl'):
            self.save2Database()
            import Base
            Base.changeStep4Stage('ShapesAvailable')
        
    def reset(self):
        self.checkStatus = False
        self.__miniLength = 0
        self.__jointSetNum = 0
        self.__boundaryNodeNum = 0
        self.__tunnelNum = 0
        self.__addtionalLineNum = 0
        self.__materialLineNum = 0
        self.__boltElementNum = 0
        self.__fixedPointNum = 0
        self.__loadingPointNum = 0
        self.__measuredPointNum = 0
        self.__holePointNum = 0
        self.__jointSets = []
        self.__slope = []
        self.__boundaryNodes = []
        self.__tunnels = []
        self.__additionalLines = []
        self.__materialLines = []
        self.__boltElements = []
        self.__fixedPoints = []
        self.__loadingPoints = []
        self.__measuredPoints = []
        self.__holePoints = []
        
    def parse(self , filename ):    
        '''
        parse DL data
        :param filename: the data file name
        '''
        self.reset()
        if not self.__fileReader.setFile(filename):
            return False
        if not self.__parsePandect():
            return False
        if not self.__parseJointSets():
            return False
        if not self.__parseBoundaryNodes():
            return False
        if not self.__parseTunnels():
            return False
        if not self.__parseLines():
            return False
        if not self.__parsePoints():
            return False
        self.__fileReader.closeFile()
        return True
        
        
    def __parseJointSets(self):
        '''
        parse joint sets
        '''
        # joint dip , dip direction
        for i in range(self.__jointSetNum):
            self.__jointSets.append(range(6))
            tmpNums = self.__jointSets[-1]
            str = self.__fileReader.getNextLine()
            nums = str.strip().split()
            tmpNums[0] = self.parseFloatNum(nums[0], 'joint dip')
            tmpNums[1] = self.parseFloatNum(nums[1], 'dip direction')
            if tmpNums[0] == None  or tmpNums[1] == None :
                return False
            print 'joint %d : ( %f , %f)'%( i , tmpNums[0],tmpNums[1])
          
        # slope dip , dip direction  
        tmpNumbers = [0 , 1]
        str = self.__fileReader.getNextLine()
        nums = str.strip().split()
        tmpNumbers[0] = self.parseFloatNum(nums[0], 'slope dip')
        tmpNumbers[1] = self.parseFloatNum(nums[1], 'dip direction')
        if tmpNumbers[0] == None or tmpNumbers[1] == None :
            return False
        print 'slope : ( %f , %f)'%(tmpNumbers[0],tmpNumbers[1])
        self.__slope.append((tmpNumbers[0],tmpNumbers[1]))
                
        for i in range(self.__jointSetNum):
            tmpNums = self.__jointSets[i]
            str = self.__fileReader.getNextLine()
            nums = str.strip().split()
            tmpNums[2] = self.parseFloatNum(nums[0], 'spacing')
            tmpNums[3] = self.parseFloatNum(nums[1], 'length')
            tmpNums[4] = self.parseFloatNum(nums[2], 'bridge')
            tmpNums[5] = self.parseFloatNum(nums[3], 'random')
            if tmpNums[2]  == None or tmpNums[3] == None  or tmpNums[4] == None  or tmpNums[5] == None :
                return False
            print 'joint %d parameter : ( %f , %f , %f , %f)'%(i , tmpNums[2],tmpNums[3],tmpNums[4],tmpNums[5])            
        return True
          
    def __parseBoundaryNodes(self ):
        '''
        parse boundary nodes
        '''
        for i in range(self.__boundaryNodeNum):
            str = self.__fileReader.getNextLine()
            nums = str.strip().split()
            tmpNums = [0 , 1 , 0]
            tmpNums[0] = self.parseFloatNum(nums[0], 'coordinate number')
            tmpNums[1] = self.parseFloatNum(nums[1], 'coordinate number')
            if tmpNums[0] == None or tmpNums[1] == None  :
                return False
            print 'boundary line %d : (%f , %f)'%(i , tmpNums[0] , tmpNums[1])
            self.__boundaryNodes.append(tmpNums)
        return True
        
    def __parseTunnels(self ):
        '''
        parse tunnels
        '''
        for i in range(self.__tunnelNum):
            # tunnel shape number
            str = self.__fileReader.getNextLine()
            shapeNo = self.parseIntNum(str, 'tunnel shape number')
            if shapeNo == None :
                return False
            
            # tunnel a b c r
            tmpNums = range(4)
            str = self.__fileReader.getNextLine()
            names = ['a' , 'b' , 'c' , 'r']
            nums = str.strip().split()
            for j in range(4):
                tmpNums[j] = self.parseFloatNum(nums[j], 'tunnel ' +names[j])
                if tmpNums[j] == None :
                    return False
                
            # tunnel center
            center = [0 , 1]
            str = self.__fileReader.getNextLine()
            nums = str.strip().split()
            for j in range(2):
                center[j] = self.parseFloatNum(nums[j], 'tunnel center number')
                if center[j] == None :
                    return False
            print 'tunnel %d : (%f , %f , %f , %f , %f , %f , %f)'%(i , shapeNo , tmpNums[0] , tmpNums[1] , tmpNums[2] , tmpNums[3] , center[0] , center[1])
            self.__tunnels.append((shapeNo , tmpNums[0] , tmpNums[1] , tmpNums[2] , tmpNums[3] , center[0] , center[1]))
        return True
    
    def __parseLines(self ):
        '''
        parse material lines , addtional lines
        '''
        tmpNums = range(4)
        # additional line
        for i in range(self.__addtionalLineNum):
            str = self.__fileReader.getNextLine()
            nums = str.strip().split()
            for j in range(4):
                tmpNums[j] = self.parseFloatNum(nums[j], 'additional line coordinate number')
                if tmpNums[j] == None :
                    return False
            materialNo = self.parseFloatNum(nums[4], 'additional line material number')
            if materialNo == None :
                return False
            print 'additional line %d :(%f , %f , %f , %f , %f)'%(i , tmpNums[0] , tmpNums[1] ,tmpNums[2] , tmpNums[3] , materialNo)
            self.__additionalLines.append((tmpNums[0] , tmpNums[1] ,tmpNums[2] , tmpNums[3] , materialNo))
        
        # material line 
        for i in range(self.__materialLineNum):
            str = self.__fileReader.getNextLine()
            nums = str.strip().split()
            for j in range(4):
                tmpNums[j] = self.parseFloatNum(nums[j], 'material line coordinate number')
                if tmpNums[j] == None :
                    return False
            materialNo = self.parseFloatNum(nums[4], 'block  material number')
            if materialNo == None :
                return False
            print 'block  material %d :(%f , %f , %f , %f , %f)'%(i , tmpNums[0] , tmpNums[1] ,tmpNums[2] , tmpNums[3] , materialNo)
            self.__materialLines.append((tmpNums[0] , tmpNums[1] ,tmpNums[2] , tmpNums[3] , materialNo))
        
        return True
        
    def __parsePoints(self):
        '''
        parse points , fixed points , loading points , measured points , hole points
        :param file: input dl file
        '''
        tmpNums = range(4)

        # fixed points
        for i in range(self.__fixedPointNum):
            str = self.__fileReader.getNextLine()
            nums = str.strip().split()
            for j in range(4):
                tmpNums[j] = self.parseFloatNum(nums[j], 'fixed point coordinate number')
                if tmpNums[j] == None :
                    return False
            print 'fixed line %d : (%f , %f , %f , %f)'%(i , tmpNums[0] , tmpNums[1] ,tmpNums[2] , tmpNums[3])
            self.__fixedPoints.append((tmpNums[0] , tmpNums[1] ,tmpNums[2] , tmpNums[3]))
                
        # measured points
        itemNames = ['loading point' , 'measured point' , 'hole point']
        realNums = [self.__loadingPointNum , self.__measuredPointNum , self.__holePointNum]
        for k in range(len(itemNames)):        
            for i in range(realNums[k]):
                str = self.__fileReader.getNextLine()
                nums = str.strip().split()
                for j in range(2):
                    tmpNums[j] = self.parseFloatNum(nums[j], itemNames[k] +' coordinate number')
                    if tmpNums[j] == None :
                        return False
                print '%s %d : (%f , %f)'%(itemNames[k] , i , tmpNums[0] , tmpNums[1])
                if k==0 : self.__loadingPoints.append((tmpNums[0] , tmpNums[1]))
                elif k==1 : self.__measuredPoints.append((tmpNums[0] , tmpNums[1]))
                elif k==2 : self.__holePoints.append((tmpNums[0] , tmpNums[1]))
        return True
        
    def __parsePandect(self):
        '''
        parse Numbers , for example , number of joint set
        '''
        self.__miniLength = self.parseFloatNum(self.__fileReader.getNextLine(), 'minimun edge length')
        if self.__miniLength == None :
            return False
        
        self.__jointSetNum = self.parseIntNum(self.__fileReader.getNextLine(), 'joint set number')
        if self.__jointSetNum == None:
            return False

        self.__boundaryNodeNum = self.parseIntNum(self.__fileReader.getNextLine(), 'boundary line number')
        if self.__boundaryNodeNum == None:
            return False

        self.__tunnelNum = self.parseIntNum(self.__fileReader.getNextLine(), 'tunnel number')
        if self.__tunnelNum == None:
            return False
        
        self.__addtionalLineNum = self.parseIntNum(self.__fileReader.getNextLine(), 'additional line number')
        if self.__addtionalLineNum == None:
            return False
        
        self.__materialLineNum = self.parseIntNum(self.__fileReader.getNextLine(), 'material line number')
        if self.__materialLineNum == None:
            return False

        self.__boltElementNum = self.parseIntNum(self.__fileReader.getNextLine(), 'bolt element number')
        if self.__boltElementNum == None:
            return False

        self.__fixedPointNum = self.parseIntNum(self.__fileReader.getNextLine(), 'fixed point number')
        if self.__fixedPointNum == None:
            return False

        self.__loadingPointNum = self.parseIntNum(self.__fileReader.getNextLine(), 'loading point number')
        if self.__loadingPointNum == None:
            return False

        self.__measuredPointNum = self.parseIntNum(self.__fileReader.getNextLine(), 'measured point number')
        if self.__measuredPointNum == None:
            return False

        self.__holePointNum = self.parseIntNum(self.__fileReader.getNextLine(), 'hole point number')
        if self.__holePointNum == None:
            return False
        
        return True
    
    def save2Database(self):
        '''
        save data to DDADatabase.dl_database
        '''
        from DDAShapes import DDAJointSets , DDATunnels
        DDADatabase.dl_database = DDADatabase.DLDatabase()
        
        database = DDADatabase.dl_database
        
        database.jointSets = self.__jointSets
        DDAJointSets.dataTable.refreshData(database.jointSets)
        database.slope = self.__slope
        DDAJointSets.slopeDataTable.refreshData(database.slope)
        
        database.tunnels = self.__tunnels
        DDATunnels.dataTable.refreshData(database.tunnels)
        
        # boundaryNodes
        pts = [tuple(p) for p in self.__boundaryNodes]
        pts.append(pts[0])
        database.boundaryNodes = [DDAPolyLine( pts, 1)] 
        
        # additional lines
        database.additionalLines = \
            [DDALine((p[0],p[1],0) , (p[2],p[3],0) , p[4]) for p in self.__additionalLines] 

        # material line
        database.materialLines = \
            [DDALine((p[0],p[1],0) , (p[2],p[3],0) , p[4]) for p in self.__materialLines] 

        # bolt element
        database.boltElements = \
            [DDALine((p[0],p[1],0) , (p[2],p[3],0) , p[4]) for p in self.__boltElements] 

        # points
        database.fixedPoints = [DDAPoint(t[0],t[1]) for t in self.__fixedPoints]
        database.loadingPoints = [DDAPoint(t[0],t[1]) for t in self.__loadingPoints]
        database.measuredPoints = [DDAPoint(t[0],t[1]) for t in self.__measuredPoints]
        database.holePoints = [DDAPoint(t[0],t[1]) for t in self.__holePoints]
        self.reset()
        import Base
        Base.refreshAllShapes()
        

#class ParseDFData(BaseParseData):
#    def __init__(self):
#        self.__file = FileReader()
#        self.refreshBlocksData()
#        
#    def refreshBlocksData(self):
#        self.graph = Graph()
#        
#        self.blocksNum = 0
#        self.blockVerticesNum = 0
#        self.fixedPointsNum = 0
#        self.loadingPointsNum = 0
#        self.measuredPointsNum = 0
#        self.boltElementsNum = 0
#        
#        self.ifDynamic = 0   # 0 :static  1:dynamic
#        self.stepsNum = 0
#        self.blockMatsNum = 0
#        self.jointMatsNum = 0
#        self.ratio = 0
#        self.OneSteptimeLimit = 0
#        self.springStiffness = 0
#        self.SOR = 0
#        
#        self.blockMats = []
#        self.jointMats = []
#        self.loadingPoints = []
#    
#    def refreshParas(self):
#        self.ifDynamic = 0   # 0 :static  1:dynamic
#        self.stepsNum = 0
#        self.ratio = 0
#        self.OneSteptimeLimit = 0
#        self.springStiffness = 0
#        self.SOR = 0
#        
#        self.blockMats = []
#        self.jointMats = []
#        self.loadingPoints = []        
#        
#    def __parseDataSchema(self , infile):
#        line = infile.readline()
#        nums = line.split()
#        self.blocksNum = self.parseIntNum(nums[0])
#        self.boltElementsNum = self.parseIntNum(nums[1])
#        self.blockVerticesNum = self.parseIntNum(nums[2])
#        
#        line = infile.readline()
#        nums = line.split()
#        self.fixedPointsNum = self.parseIntNum(nums[0])
#        self.loadingPointsNum = self.parseIntNum(nums[1])
#        self.measuredPointsNum = self.parseIntNum(nums[2])
#        
#        if None in [self.blocksNum , self.boltElementsNum , self.blockVerticesNum \
#                   , self.fixedPointsNum , self.loadingPointsNum , self.measuredPointsNum]:
#            return False
#        print 'DF data : blocks : %d    bolts : %d  vertices : %d fixed Pnts :%d LoadingPnts :%d MeasuredPnts: %d' \
#            %(self.blocksNum , self.boltElementsNum , self.blockVerticesNum \
#                   , self.fixedPointsNum , self.loadingPointsNum , self.measuredPointsNum)
#        return True
#        
#    def __parseBlocks(self , infile):
#        '''
#        parsing blocks and try to get the maximum material No
#        :param infile:
#        '''
#        for i in range(0 , self.blocksNum):
#            line = infile.readline()
#            nums = line.split()
#            t = int(self.parseFloatNum(nums[0] ,'block No.'))
#            if t==None or self.parseFloatNum(nums[1])==None or self.parseFloatNum(nums[2])==None: 
#                return False
#            if t>self.blockMatsNum : # get max. block material No
#                self.blockMatsNum = t
#                
##            self.blocksInfo.append((self.parseIntNum(nums[1]) , self.parseIntNum(nums[2])))
#            tmpB = Block()
#            tmpB.startNo = self.parseIntNum(nums[1])
#            tmpB.endNo = self.parseIntNum(nums[2])
#            self.graph.blocks.append(tmpB )
#            
##            print line ,
#            
#        print 'DF blocks Info done.'
#                
#        return True
#                
#    def __parseBlockVertices(self,infile):
#        '''
#        parsing blocks' vertices and try to get the maximum material No
#        :param infile:
#        '''
#        for i in range(self.blocksNum):
#            tmpB = self.graph.blocks[i]
#            for j in range(tmpB.endNo - tmpB.startNo +1): # read blocks vertices 
#                line = infile.readline()
#                nums = line.split()
#                
#                # get max. blocks' vertices' material No 
#                t = int(self.parseFloatNum(nums[0] ,'block vertex material No.'))
#                if t==None or self.parseFloatNum(nums[1])==None or self.parseFloatNum(nums[2])==None: 
#                    return False
#                if t>self.jointMatsNum : # get max. block material No
#                    self.jointMatsNum = t 
#
#                tmpB.vertices.append( (self.parseFloatNum(nums[0]) ,self.parseFloatNum(nums[1]) , self.parseFloatNum(nums[2])) )
#
#        print 'DF blocks vertices data done.'
#        return True
#           
#    def parse1Point(self  , line , point):
#        #print line , 
#        nums = line.split()
#        point.x = self.parseFloatNum(nums[0])
#        point.y = self.parseFloatNum(nums[1])
#        point.blockNo = int(self.parseFloatNum(nums[2]))
#                
#    def __parsePoints(self , infile):           
#        '''
#        parsing fixed , loading , and measured points 
#        :param infile:
#        '''
#        for i in range(self.fixedPointsNum):
#            pnt = FixedPoint()
#            line = infile.readline()
#            self.parse1Point(line , pnt)            
#            self.graph.fixedPoints.append(pnt)
#        print '    fixed points : %d done'%self.fixedPointsNum
#            
#        for i in range(self.loadingPointsNum):
#            pnt = LoadingPoint()
#            line = infile.readline()
#            self.parse1Point(line ,  pnt)            
#            self.graph.loadingPoints.append(pnt)
#        print '    loading points : %d done'%self.loadingPointsNum
#        
#        for i in range(self.measuredPointsNum):
#            pnt = MeasuredPoint()
#            line = infile.readline()
#            self.parse1Point(line , pnt)            
#            self.graph.measuredPoints.append(pnt)   
#        print '    measured points : %d done'%self.measuredPointsNum
#
#        print 'DF points done.'
#        return True     
#         
#    def parseDFData(self , path):
#        self.refreshBlocksData()
#        file = open(path , "rb")
#        if not self.__parseDataSchema(file) or not self.__parseBlocks(file) or \
#            not self.__parseBlockVertices(file) or  not self.__parsePoints(file):
#            return False
#        
#        return True
#    
#    def __parseParaSchema(self):
#        '''
#        parse parameters from DF parameters file
#        :param infile:
#        '''
#
#        for i in range(7):
#            line = self.__file.getNextLine()  
#            t =self.parseFloatNum(line)
#            if t==None: return False
#        
#            if   i==0:     self.ifDynamic = float(t)
#            elif i==1:     self.stepsNum = int(t)
#            elif i==2:     self.blockMatsNum = int(t)
#            elif i==3:     self.jointMatsNum = int(t)
#            elif i==4:     self.ratio = t
#            elif i==5:     self.OneSteptimeLimit = int(t)
#            else:          self.springStiffness = int(t)
#        
#        print 'DF Para : IfDynamic: %d  steps: %d  blockMats: %d  JointMats: %d  Ratio: %f  timeInterval: %d  stiffness: %d'\
#            %(self.ifDynamic, self.stepsNum , self.blockMatsNum , self.jointMatsNum \
#              , self.ratio, self.OneSteptimeLimit, self.springStiffness)
#            
#        print 'Df parameters schema done'
#        return True
#    
#    def __parsePointsParameters(self):
#        '''
#        parse parameters for fixed points and loading points
#        :param infile:
#        '''
#        # parse fixed points and loading points' type    0 : fixed points , 2: loading points
#        # fixed points 
#        if self.fixedPointsNum>0:
#            line = self.__file.getNextLine()    
#            nums = line.split()
#            for i in nums:
#                if self.parseIntNum(i)==None :
#                    return False
#            print nums
#        
#        # loading points
#        if self.loadingPointsNum>0:
#            line = self.__file.getNextLine()
#            nums = line.split()
#            for i in nums:
#                if self.parseIntNum(i)==None :
#                    return False
#            print nums            
#            
#        # parse loading points parameters  (starttime , stressX , stressY  , endtime , stressX , stressY)
#        for i in range(self.loadingPointsNum):
#            digits = [1]*6
#            line1 = self.__file.getNextLine()
#            nums1 = line1.split()
#            line2 = self.__file.getNextLine()
#            nums2 = line2.split()
#            for j in range(3):
#                digits[j] = self.parseIntNum(nums1[j])
#                digits[j+3] = self.parseIntNum(nums2[j])
#            if None in digits:
#                return False
#            self.loadingPoints.append(digits)
#            
#            print nums1 , nums2
#        
#        print 'fixed points and loading points done.'
#        
#        return True
#            
#    def __parseBlocksAndJointsPara(self):
#        '''
#        parse parameters for blocks and joints'
#        :param infile:
#        '''
#        for i in range(self.blockMatsNum):
#            digits = [1]*14
#            line1 = self.__file.getNextLine()
#            nums1 = line1.split()
#            for j in range(5):
#                 digits[j] = self.parseFloatNum(nums1[j])
#            line2 = self.__file.getNextLine()
#            nums2 = line2.split()
#            line3 = self.__file.getNextLine()
#            nums3 = line3.split()
#            line4 = self.__file.getNextLine()
#            nums4 = line4.split()    
#            for j in range(3):
#                digits[j+5] = self.parseFloatNum(nums2[j])                    
#                digits[j+8] = self.parseFloatNum(nums3[j])
#                digits[j+11] = self.parseFloatNum(nums4[j])
#            if None in digits:
#                return False
#            self.blockMats.append(digits)
#            print digits
#            
#        for i in range(self.jointMatsNum):
#            digits = [1]*3
#            line = self.__file.getNextLine()
#            nums = line.split()
#            for j in range(3):
#                digits[j] = self.parseFloatNum(nums[j])
#            if None in digits:
#                return False
#            self.jointMats.append(digits)
#            print digits
#            
#        print 'DF blocks and block vertices\' parameters done.' 
#        
#        return True
#    
#    def __parseRestPara(self ):
#        '''
#        parse SOR and axes
#        :param infile:
#        '''
#        # parse SOR
#        line = self.__file.getNextLine()
#        self.SOR = self.parseFloatNum(line)
#        if self.SOR==None: return False
#        print 'SOR : ' , self.SOR
#        
#        line = self.__file.getNextLine()
#        nums = line.split()
#        for i in range(3):
#            if self.parseFloatNum(nums[i])==None:
#                return False
#        print nums
#            
#        print 'DF parameters all done.'
#            
#        return True
#    
#    
#    def parseDFParameters(self , path):
#        self.refreshParas()
#        self.__file.setFile(path)
#        if not self.__parseParaSchema() or not self.__parsePointsParameters() \
#            or not self.__parseBlocksAndJointsPara() or not self.__parseRestPara():
#            return False
#        
#        return True

class ParseDFInputParameters(BaseParseData):
    def __init__(self):
        self.__file = None
        self.reset()
        
    def reset(self):
        from DDADatabase import df_inputDatabase
        self.paras = df_inputDatabase.paras
        self.paras.reset()
        
    def __parseParaSchema(self):
        '''
        parse parameters from DF parameters file
        :param infile:
        '''
        
        for i in range(7):
            line = self.__file.getNextLine()  
            t =self.parseFloatNum(line)
            if t==None: return False
        
            if   i==0:     self.paras.ifDynamic = float(t)
            elif i==1:     self.paras.stepsNum = int(t)
            elif i==2:     self.paras.blockMatsNum = int(t)
            elif i==3:     self.paras.jointMatsNum = int(t)
            elif i==4:     self.paras.ratio = t
            elif i==5:     self.paras.OneSteptimeLimit = int(t)
            else:          self.paras.springStiffness = int(t)
        
        print 'DF Para : IfDynamic: %d  steps: %d  blockMats: %d  JointMats: %d  Ratio: %f  timeInterval: %d  stiffness: %d'\
            %(self.paras.ifDynamic, self.paras.stepsNum , self.paras.blockMatsNum , self.paras.jointMatsNum \
              , self.paras.ratio, self.paras.OneSteptimeLimit, self.paras.springStiffness)
            
        print 'Df parameters schema done'
        return True
    
    def __parsePointsParameters(self):
        '''
        parse parameters for fixed points and loading points
        :param infile:
        '''
        # parse fixed points and loading points' type    0 : fixed points , 2: loading points
        # fixed points 
        from DDADatabase import df_inputDatabase
        
        if len(df_inputDatabase.fixedPoints)>0:
            line = self.__file.getNextLine()    
            nums = line.split()
            for i in nums:
                if self.parseIntNum(i)==None :
                    return False
            print nums
        
        # loading points
        if len(df_inputDatabase.loadingPoints)>0:
            line = self.__file.getNextLine()
            nums = line.split()
            for i in nums:
                if self.parseIntNum(i)==None :
                    return False
            print nums            
            
        # parse loading points parameters  (starttime , stressX , stressY  , endtime , stressX , stressY)
        for i in range(len(df_inputDatabase.loadingPoints)):
            digits = [1]*6
            line1 = self.__file.getNextLine()
            nums1 = line1.split()
            line2 = self.__file.getNextLine()
            nums2 = line2.split()
            for j in range(3):
                digits[j] = self.parseIntNum(nums1[j])
                digits[j+3] = self.parseIntNum(nums2[j])
            if None in digits:
                return False
            self.paras.loadingPointMats.append(digits)
            
            print nums1 , nums2
        
        print 'fixed points and loading points done.'
        
        return True
            
    def __parseBlocksAndJointsPara(self):
        '''
        parse parameters for blocks and joints'
        :param infile:
        '''
        for i in range(self.paras.blockMatsNum):
            digits = [1]*14
            line1 = self.__file.getNextLine()
            nums1 = line1.split()
            for j in range(5):
                digits[j] = self.parseFloatNum(nums1[j])
            line2 = self.__file.getNextLine()
            nums2 = line2.split()
            line3 = self.__file.getNextLine()
            nums3 = line3.split()
            line4 = self.__file.getNextLine()
            nums4 = line4.split()    
            for j in range(3):
                digits[j+5] = self.parseFloatNum(nums2[j])                    
                digits[j+8] = self.parseFloatNum(nums3[j])
                digits[j+11] = self.parseFloatNum(nums4[j])
            if None in digits:
                return False
            self.paras.blockMats.append(digits)
            print digits
            
        for i in range(self.paras.jointMatsNum):
            digits = [1]*3
            line = self.__file.getNextLine()
            nums = line.split()
            for j in range(3):
                digits[j] = self.parseFloatNum(nums[j])
            if None in digits:
                return False
            self.paras.jointMats.append(digits)
            print digits
            
        print 'DF blocks and block vertices\' parameters done.' 
        
        return True
    
    def __parseRestPara(self ):
        '''
        parse SOR and axes
        :param infile:
        '''
        # parse SOR
        line = self.__file.getNextLine()
        self.paras.SOR = self.parseFloatNum(line)
        if self.paras.SOR==None: return False
        print 'SOR : ' , self.paras.SOR
        
        line = self.__file.getNextLine()
        nums = line.split()
        for i in range(3):
            if self.parseFloatNum(nums[i])==None:
                return False
        print nums
            
        print 'DF parameters all done.'
            
        return True
    
    
    def parse(self , path = None):
        self.reset()
        if not path: Base.__currentProjectPath__+'/parameters.df'
        if not checkFileExists(path):
            return False
        
        import Base
        self.__file = FileReader()
        self.__file.setFile(path)
        if not self.__parseParaSchema() or not self.__parsePointsParameters() \
            or not self.__parseBlocksAndJointsPara() or not self.__parseRestPara():
            return False
        
        return True
    
        


class ParseDFInputGraphData(BaseParseData):
    def __init__(self):
        self.__fileReader = None

    def GetResources(self):
        return {
                'MenuText':  'LoadDFInputData',
                'ToolTip': "Load DF Input Data"}
        
    def Activated(self):
        self.parse()
        import Base
        Base.changeStep4Stage('ShapesAvailable')
        
    def finish(self):
        pass  

    def parse(self , path=None):
        self.refreshBlocksData()
        import Base
        if not path : path = Base.__currentProjectPath__+'/data.df'
        if not checkFileExists(path):
            return False
        
        file = open(path , "rb")
        if not self.__parseDataSchema(file) or not self.__parseBlocks(file) or \
            not self.__parseBlockVertices(file) or  not self.__parsePoints(file):
            Base.showErrorMessageBox("DataError", 'Data input unvalid')
            return False
        
        return True

    def refreshBlocksData(self):
        import Base
        self.graph = Base.getDatabaser4CurrentStage()
        self.graph.reset()
        
        self.blocksNum = 0
        self.blockVerticesNum = 0
        self.fixedPointsNum = 0
        self.loadingPointsNum = 0
        self.measuredPointsNum = 0
        self.boltElementsNum = 0
    def __parseDataSchema(self , infile):
        line = infile.readline()
        nums = line.split()
        self.blocksNum = self.parseIntNum(nums[0])
        self.boltElementsNum = self.parseIntNum(nums[1])
        self.blockVerticesNum = self.parseIntNum(nums[2])
        
        line = infile.readline()
        nums = line.split()
        self.fixedPointsNum = self.parseIntNum(nums[0])
        self.loadingPointsNum = self.parseIntNum(nums[1])
        self.measuredPointsNum = self.parseIntNum(nums[2])
        
        if None in [self.blocksNum , self.boltElementsNum , self.blockVerticesNum \
                   , self.fixedPointsNum , self.loadingPointsNum , self.measuredPointsNum]:
            return False
        print 'DF data : blocks : %d    bolts : %d  vertices : %d fixed Pnts :%d LoadingPnts :%d MeasuredPnts: %d' \
            %(self.blocksNum , self.boltElementsNum , self.blockVerticesNum \
                   , self.fixedPointsNum , self.loadingPointsNum , self.measuredPointsNum)
        return True
        
    def __parseBlocks(self , infile):
        '''
        parsing blocks and try to get the maximum material No
        :param infile:
        '''
        from DDADatabase import df_inputDatabase
        df_inputDatabase.blockMatCollections = set()
        blockMatCollection = df_inputDatabase.blockMatCollections
        
        for i in range(0 , self.blocksNum):
            line = infile.readline()
            nums = line.split()
            
            # get blocks' vertices' material No 
            t0 = self.parseIntNum(nums[0])
            t1 = self.parseIntNum(nums[1])
            t2 = self.parseIntNum(nums[2])                                
            if t0==None or t1==None or t2==None: 
                return False                

            tmpB = Block()
            tmpB.materialNo = t0
            tmpB.startNo = t1
            tmpB.endNo = t2
            blockMatCollection.add(t0)
            self.graph.blocks.append(tmpB )
            
#            print line ,
            
        print 'DF blocks Info done.'
                
        return True
                
    def __parseBlockVertices(self,infile):
        '''
        parsing blocks' vertices and try to get the maximum material No
        :param infile:
        '''
        from DDADatabase import df_inputDatabase
        df_inputDatabase.jointMatCollections =set()
        jointMatCollection = df_inputDatabase.jointMatCollections
        
        for i in range(self.blocksNum):
            tmpB = self.graph.blocks[i]
            for j in range(int(tmpB.endNo) - int(tmpB.startNo) +1): # read blocks vertices 
                line = infile.readline()
#                print line
                nums = line.split()
                
                # get joint material No 
                t0 = int(self.parseFloatNum(nums[0]))
                t1 = self.parseFloatNum(nums[1])
                t2 = self.parseFloatNum(nums[2])                                
                if t0==None or t1==None or t2==None: 
                    return False                
                tmpB.vertices.append( (t0,t1,t2) )
                jointMatCollection.add(t0)
                
            for i in range(4): # block parameters
                line = infile.readline()
#                print line
                nums = line.split()
                t0 = self.parseFloatNum(nums[0])
                t1 = self.parseFloatNum(nums[1])
                t2 = self.parseFloatNum(nums[2])
                if t0==None or t1==None or t2==None: 
                    return False
                
                tmpB.parameters.extend([t0,t1,t2])

        print 'DF blocks vertices data done.'
        return True

    def parse1Point(self  , line , point):
        #print line , 
        nums = line.split()
        point.x = self.parseFloatNum(nums[0])
        point.y = self.parseFloatNum(nums[1])
        point.blockNo = int(self.parseFloatNum(nums[2]))
                
    def __parsePoints(self , infile):           
        '''
        parsing fixed , loading , and measured points 
        :param infile:
        '''
        for i in range(self.fixedPointsNum):
            pnt = FixedPoint()
            line = infile.readline()
            self.parse1Point(line , pnt)            
            self.graph.fixedPoints.append(pnt)
        print '    fixed points : %d done'%self.fixedPointsNum
            
        for i in range(self.loadingPointsNum):
            pnt = LoadingPoint()
            line = infile.readline()
            self.parse1Point(line ,  pnt)            
            self.graph.loadingPoints.append(pnt)
        print '    loading points : %d done'%self.loadingPointsNum
        
        for i in range(self.measuredPointsNum):
            pnt = MeasuredPoint()
            line = infile.readline()
            self.parse1Point(line , pnt)            
            self.graph.measuredPoints.append(pnt)   
        print '    measured points : %d done'%self.measuredPointsNum

        print 'DF points done.'
        return True     
        
        
class ParseAndLoadDCInputData(BaseParseData):
    def __init__(self):
        self.reset()
        self.__fileReader = FileReader()
        
    def GetResources(self):
        return {
                'MenuText':  'LoadDCInputData',
                'ToolTip': "Load DC Input Data"}
        
    def Activated(self):
        self.parse()
        import Base
        Base.changeStep4Stage('SpecialStep')
        
        import Base
        database = Base.getDatabaser4CurrentStage()
        database.clearRedoUndoList()
                
    def finish(self):
        pass  
      
    def reset(self):
        self.jointLinesNum = 0
        self.materialLinesNum = 0
        self.additionalLinesNum = 0
        self.boltElementsNum = 0
        self.fixedPointsNum = 0
        self.loadingPointsNum = 0
        self.measuredPointsNum = 0
        self.holePointsNum = 0
    
    def __ParsePandect(self):
        from DDADatabase import dc_inputDatabase
        
        self.__fileReader.getNextLine()   # minimum edge length e0
        
        nums = self.__fileReader.getNextLine().split()
        self.jointLinesNum = self.parseIntNum(nums[0])
        
        # temperary code, I will try to revise this if I fully understand the data.dc 
        dc_inputDatabase.boundaryLinesNum = self.parseIntNum(nums[1])
        
        nums = self.__fileReader.getNextLine()
        self.materialLinesNum = self.parseIntNum(nums)

        nums = self.__fileReader.getNextLine()
        self.boltElementsNum = self.parseIntNum(nums)

        nums = self.__fileReader.getNextLine()
        self.fixedPointsNum = self.parseIntNum(nums)
        
        nums = self.__fileReader.getNextLine()
        self.loadingPointsNum = self.parseIntNum(nums)
        
        nums = self.__fileReader.getNextLine()
        self.measuredPointsNum = self.parseIntNum(nums)

        nums = self.__fileReader.getNextLine()
        self.holePointsNum = self.parseIntNum(nums)
        
    def __parseLines(self):
        from DDADatabase import dc_inputDatabase
        # joint lines
        dc_inputDatabase.jointLines = []
        for i in range(self.jointLinesNum):
            nums = self.__fileReader.getNextLine().split()
            jointMaterial = int(self.parseFloatNum(nums[4]))
            p1 = ( self.parseFloatNum(nums[0]) , self.parseFloatNum(nums[1]) , 0 ) 
            p2 = ( self.parseFloatNum(nums[2]) , self.parseFloatNum(nums[3]) , 0 )
            dc_inputDatabase.jointLines.append(DDALine(p1 , p2 , jointMaterial))
            
        # material lines
        dc_inputDatabase.materialLines = []
        for i in range(self.materialLinesNum):
            self.__fileReader.getNextLine()
            
            
        # bolt elements
        pass
        
    def __parsePoints(self):
        from DDADatabase import dc_inputDatabase
        import Base
        # fixed points
        windowInfo = [0 , 0 , 0 , 0]
        nums = self.__fileReader.getNextLine().split()
        p = (self.parseFloatNum(nums[0]) , self.parseFloatNum(nums[1]) , 0)
        dc_inputDatabase.fixedPoints.append( FixedPoint(p[0] , p[1]))
        windowInfo[0] = windowInfo[1] = p[0]
        windowInfo[2] = windowInfo[3] = p[1]
        for i in range(self.fixedPointsNum-1):
            nums = self.__fileReader.getNextLine().split()
            p = (self.parseFloatNum(nums[0]) , self.parseFloatNum(nums[1]) , 0)
            if p[0]<windowInfo[0]:windowInfo[0] = p[0]
            if p[0]>windowInfo[1]:windowInfo[1] = p[0]
            if p[1]<windowInfo[2]:windowInfo[2] = p[1]
            if p[1]>windowInfo[3]:windowInfo[3] = p[1]
            dc_inputDatabase.fixedPoints.append( FixedPoint(p[0] , p[1]))
            
        Base.__radius4Points__ = (windowInfo[1] - windowInfo[0]) * 0.01
        Base.__windowInfo__ = windowInfo
            
        # loading points
        for i in range(self.loadingPointsNum):
            nums = self.__fileReader.getNextLine().split()
            dc_inputDatabase.loadingPoints.append( \
                LoadingPoint(self.parseFloatNum(nums[0]) , self.parseFloatNum(nums[1])))
        # measured points
        for i in range(self.measuredPointsNum):
            nums = self.__fileReader.getNextLine().split()
            dc_inputDatabase.measuredPoints.append( \
                MeasuredPoint(self.parseFloatNum(nums[0]) , self.parseFloatNum(nums[1])))
        # hole points
        for i in range(self.holePointsNum):
            nums = self.__fileReader.getNextLine().split()
            dc_inputDatabase.holePoints.append( \
                HolePoint(self.parseFloatNum(nums[0]) , self.parseFloatNum(nums[1])))        
        
    def parse(self):
        import Base
        filename = Base.__currentProjectPath__ + '/data.dc'
        print 'try to read DC data from file : ' , filename
#        filename = Base.__currentProjectPath__ + '/tmpData.dc'
        self.__fileReader.setFile(filename)
        self.reset()
        self.__ParsePandect()
        self.__parseLines()
        self.__parsePoints()
        self.__fileReader.closeFile()
    

class DDALoadData():
    def __init__(self):
        self.current_path = Base.__currentProjectPath__
       
    def changeStage( self ):
        if Base.__currentStage__ == 'DL': # DL stage
            print 'switch to DL stage'
            self.parseData = ParseAndLoadDLData()
        elif Base.__currentStage__ == 'DC': # DC stage
            pass
                
    def GetResources(self):
        return {
                'MenuText':  'Load',
                'ToolTip': "Load DL data."}
 

    def __storeFileName(self , filename):
        '''
        store the name of file which is being loaded
        '''
        file = open(self.current_path+'\\Ff.c' , 'wb')
        file.write(filename.strip().split('/')[-1])
        file.close()
        
    def __confirmLoadFile(self):
        '''
        if a new data file loaded , old shapes will be cleared , so before this ,we have to make sure if user want to do this.
        '''
        box = QtGui.QMessageBox()
        box.setText('New data will be imported , and old shapes will be wipped.')
        box.setInformativeText('Do you want to do this?')
        box.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        box.setDefaultButton(QtGui.QMessageBox.Ok)
        ret = box.exec_()
        if ret == QtGui.QMessageBox.Ok:
            return True
        return False
    
    def Activated(self):
        self.changeStage()
        filename = str( QtGui.QFileDialog.getOpenFileName(None , 'please select input file' , self.current_path) )
        if not self.parseData.parse(filename):
            self.parseData.reset()
            print 'input data status : invalid'
            return False
        print 'input data status : ok'        
        if self.__confirmLoadFile():
            self.__storeFileName(filename)
            self.parseData.save2Database()
            FreeCADGui.DDADisplayCmd.preview()
                        
    def finish(self):
        pass
    
FreeCADGui.addCommand('DDA_LoadDLInputData', ParseAndLoadDLData())

FreeCADGui.addCommand('DDA_Load', DDALoadData())
FreeCADGui.addCommand('DDA_LoadDCInputData', ParseAndLoadDCInputData())
FreeCADGui.addCommand('DDA_LoadDFInputGraphData', ParseDFInputGraphData())