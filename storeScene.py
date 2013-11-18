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


from PyQt4 import QtGui , QtCore
import FreeCAD 
import FreeCADGui
import DDADatabase
import Base
from Base import showErrorMessageBox

from Base import __currentProjectPath__ , __workbenchPath__

def writeStr(file , str):
    file.write(str+'\n')
    
class BaseStore:
    ''' 
    base class to store scene information
    storeScene() is a virtual function , that will be overwrited in inherited classes to store 
        concrete information (for example , DL , DC)
    '''
    def storeScene(self):
        pass

    def getRealType(self , obj):
        name = obj.Label
        for i in range(1 , len(name)):
            if not name[-i] in '1234567890':
                return name[:len(name)-i+1]
        return name
        
    def Activated(self):
        if FreeCAD.activeDDACommand:
            FreeCAD.activeDDACommand.finish()
        self.storeScene()
    
    def Deactivated(self):
        self.finish()
        pass
            
    def finish(self):
        pass
        
        
class DLInformationStore(BaseStore):
    '''
    Data writer for DL , file path store in __filePath__
    '''
    
    def __init__(self):
        self.database = DDADatabase.dl_database
        self.valid = True
        
    def GetResources(self):
        return {
                'MenuText':  'DL_Store',
                'ToolTip': "store data for dl."}
        
    def checkDataValid(self):
#        if not (self.boundaryLines and len(self.boundaryLines)>0) :
        from DDADatabase import dl_database
        if not len(dl_database.boundaryNodes)>0 :
            FreeCAD.Console.PrintError('boundary lines store failed. \nPlease input boundary lines first.\n')
            showErrorMessageBox('Input Error' , 'Please input boundary lines first')
            return False
            
        return True

    def isDataValid(self):
        return self.valid

    def storeScene(self):
        FreeCAD.Console.PrintMessage('storing DL information\n')
        
        print '    object parsing done.'
        
        if not self.checkDataValid():
            self.valid =  False
            return
            
        print '    check passed.'
            
        database = DDADatabase.dl_database
        self.jointSets = database.jointSets            
        self.slope = database.slope            
        self.tunnels = database.tunnels        

        print '   joints , tunnels done.'
        
        self.write2DLFile()            
        FreeCAD.Console.PrintMessage('DL information store done.\n')
        
        self.valid = True

    def writePandect( self , file):
        '''
        write pandect information to file , for example , number of additional lines , material lines , hole points , etc 
        '''
        # minimum edge length e0
        writeStr( file , str(0.0220)) # the number comes from dl24        
        writeStr( file , str(len(self.jointSets)))
        
        from DDADatabase import dl_database
        pts = dl_database.boundaryNodes[0].pts
        num = len(pts)
        if pts[0]==pts[-1]:
            num = num-1
        writeStr( file , str(num))
        
        writeStr( file , str(len(self.tunnels)))
        
        num = 0
        for pline in dl_database.borderNodes+dl_database.additionalLines :
            num+=len(pline.pts)-1
        
        writeStr( file , str(num))
        writeStr( file , str(len(dl_database.materialLines)))    # material line    
        writeStr( file , str(len(dl_database.boltElements)))     # bolt element number
        writeStr( file , str(len(dl_database.fixedPoints)))    
        writeStr( file , str(len(dl_database.loadingPoints)))    
        writeStr( file , str(len(dl_database.measuredPoints)))    
        writeStr( file , str(len(dl_database.holePoints)))    

    def writeBoundaryNodes( self , file ):
        '''
        write boundary nodes
        '''
        from DDADatabase import dl_database
        pts = dl_database.boundaryNodes[0].pts
        if pts[0]==pts[-1]:
            pts = pts[:-1]
        for p in pts:
            writeStr( file , '%.6f  %.6f' % (p[0] , p[1]))
        
    def writeLines( self , file):
        '''
        write lines to file . For example , additional lines 
        '''
        # store additional lines
        database = DDADatabase.dl_database
        
        for pline in database.additionalLines + database.borderNodes:
            pts = pline.pts
            for i in range(len(pts)-1):
                p1 = pts[i]
                p2 = pts[i+1]
                writeStr( file , '%f  %f  %f  %f  %d'%(p1[0],p1[1],p2[0],p2[1] , pline.materialNo))

        # material line
        for line in database.materialLines:
            p1 = line.startPoint
            p2 = line.endPoint
            writeStr( file , '%f  %f  %f  %f  %d'%(p1[0],p1[1],p2[0],p2[1] , line.materialNo))
            
        # bolt element
        for bolt in database.boltElements:
            p1 = line.startPoint
            p2 = line.endPoint
            writeStr( file , '%f  %f  %f  %f  %f  %f  %f'%(p1[0],p1[1],p2[0],p2[1] , line.e0 , line.t0 , line.f0))
            
    def writeJointSetsAndSlope(self , file):
        for joint in self.jointSets:
            writeStr( file , '%f  %f'%(joint[0],joint[1]))
            
        if len(self.slope)>0:
            writeStr(file , '%f  %f'%(self.slope[0][0],self.slope[0][1]))
            
        for joint in self.jointSets:
            writeStr( file , '%f  %f  %f  %f'%(joint[2], joint[3], joint[4], joint[5]))
            
    def writeTunnels(self , file):
        for tunnel in self.tunnels:
            print 'tunnel ' , tunnel
            writeStr(file , '%d\n%f  %f  %f  %f\n%f  %f'%tunnel)
        
    def writePoints(self,file):

        from DDADatabase import dl_database
        tmpContent = []
        
        tmpContent.extend(['%f %f %f %f'%(p.x , p.y , p.x , p.y) for p in dl_database.fixedPoints])
        tmpContent.extend(['%f %f'%(p.x , p.y) for p in dl_database.loadingPoints])
        tmpContent.extend(['%f %f'%(p.x , p.y) for p in dl_database.measuredPoints])
        tmpContent.extend(['%f %f'%(p.x , p.y) for p in dl_database.holePoints])

        writeStr( file , '\n'.join(tmpContent) +'\n')
            
    def write2DLFile(self):
        print 'storing DL data'
        import Base
        filename = None
        try:
            filename = Base.__currentProjectPath__ + '/data.dl'
            file = open( filename , 'wb' , True)  #  使用缓存,flush时再写入硬盘
            print 'begin writing data to file %s'%filename
        except:
            FreeCAD.Console.PrintError(' %s open failed\n'%filename)
            return
            
        Base.setGraphRevised()  #  graph of active document has
            
        self.writePandect( file )
        self.writeJointSetsAndSlope(file)
        file.flush()
        self.writeBoundaryNodes(file)
        file.flush()        
        self.writeTunnels(file)
        self.writeLines( file )
        file.flush()
        self.writePoints( file )
            
        file.close()
        
#        import Base
#        
#        wholePath = Base.__workbenchPath__ + '\\Ff.c'
#        file = open( wholePath , 'wb' )            #保存文件名
#        file.write(filename)
#        file.close()
#        print 'file save done'
        
class JointLineChangesConfirm(BaseStore):
    '''
    对应于ParseAndLoadDCInputData 使用，这类要保存的数据都在 dc_inputDatabase 中
    '''
    def __init__(self):
        self.newFile = []
        
        self.materialLines = []
        
    def GetResources(self):
        return {
                'MenuText':  'Confirm',
                'ToolTip': "confirm the data changes."}   
        
    def storeScene(self):
        self.collectShapes()
        self.organizeContent()
        self.write2File()

        
    def storeShape( self , obj):
        type = self.getRealType(obj)
        print type
        if type == 'MaterialLine':
            self.materialLines.append(obj)

        
    def organizeContent(self):
        '''
        organize content that will be writen into file.
        self.oldFile is original file
        self.newFile is the new file
        '''
        file = open(Base.__currentProjectPath__+'/data.dc','rb')
        self.oldFile = file.read(-1).split('\n')
        for i,line in enumerate(self.oldFile):
            self.oldFile[i]=line.strip()
        file.close()
        
        from DDADatabase import dc_inputDatabase        
        # schema
        nums = self.oldFile[1].split()
        self.jointLinesNum = int(nums[0])
        self.BoundaryLinesNum = int(nums[1])
        
        self.newFile = []
        self.newFile.extend(self.oldFile[0:2])
        
        self.newFile.append('%d\n%d\n%d\n%d\n%d\n%d'%(len(dc_inputDatabase.materialLines) , 0 \
                                , len(dc_inputDatabase.fixedPoints) , len(dc_inputDatabase.loadingPoints) \
                                , len(dc_inputDatabase.measuredPoints) , len(dc_inputDatabase.holePoints)))
        
        # lines
        self.__addLines()
        
        # points
        for p in dc_inputDatabase.fixedPoints:
            self.newFile.append('%f %f %f %f'%(p[0],p[1] , p[0],p[1]))        
        
        self.__addPoints(dc_inputDatabase.loadingPoints)
        self.__addPoints(dc_inputDatabase.measuredPoints)
        self.__addPoints(dc_inputDatabase.holePoints)
        
        if len(dc_inputDatabase.holePoints)>0:
            self.newFile.append('0')
        else:
            self.newFile.append('0\n0 0')
        
    def __applyJointLinesChanges(self):
        from DDADatabase import dc_inputDatabase
        
        jointLinesChanges = []
        for i in range(len(dc_inputDatabase.jointLines)):
            jointLinesChanges.append([])
            
        for item in dc_inputDatabase.jointLinesChanges.items():
            # item --> refer to DCInputDatabase.__init__()
            jointSetNo = item[0][0]+1
            subElementNo = item[0][1]-1
            if item[1][0]!='D': # key is not 'Delete'
                dc_inputDatabase.jointLines[jointSetNo][subElementNo*2] = item[1][0]
                dc_inputDatabase.jointLines[jointSetNo][subElementNo*2+1] = item[1][1]
            else: # 'Delete'
                jointLinesChanges[jointSetNo].append(subElementNo)
                
        for i in range(len(jointLinesChanges)):
            jointLinesChanges[i].sort(reverse = True)
            
        for i in range(len(jointLinesChanges)):
            for j in range(len(jointLinesChanges[i])):
                del dc_inputDatabase.jointLines[i][2*j+1]  # 删除顺序不能错
                del dc_inputDatabase.jointLines[i][2*j]
            
        
    def __addLines(self):
        from DDADatabase import dc_inputDatabase
        
        # write joint lines
        self.__applyJointLinesChanges()
        nums = 0        
        for materialNo , pts in enumerate(dc_inputDatabase.jointLines):
            if pts==None:
                continue
            t = len(pts)/2
            nums+=t
            for i in range(t):
                p1 = pts[2*i]
                p2 = pts[2*i+1]
                self.newFile.append('%f  %f  %f  %f  %f'%(p1[0],p1[1],p2[0],p2[1],materialNo))
                
        # update self.jointLinesNum
        self.jointLinesNum = nums
        tmpN = self.newFile[1].split()
        self.newFile[1] = '%d %s'%(self.jointLinesNum, tmpN[1])
        
        # material lines
        for line in self.materialLines:
            start = line.ViewObject.StartPoint
            end = line.ViewObject.EndPoint
            self.newFile.append('%f %f %f %f %f'%(start[0],start[1],end[0],end[1],line.ViewObject.Material))
        
                
    def __addPoints(self , points):
        '''
        add points to self.newFile
        '''
        for p in points:
            self.newFile.append('%f %f'%(p[0],p[1]))
            
    def reset(self):
        self.materialLines = []
            
    def collectShapes(self):
        self.reset()
        doc = FreeCAD.ActiveDocument   #  获取当前活动视图
        objs = doc.Objects             #  获取当前对象列表，有时效性，如获得后列表更新，这个已获得不会改变
        for obj in objs :
            self.storeShape(obj)
            
    def write2File(self):
#        paraFile = open(Base.__workbenchPath__+'/dc_Ff.c', 'wb')
##        paraFile.write(Base.__currentProjectPath__+'/tmpData.dc')
#        paraFile.write(Base.__currentProjectPath__+'/data.dc')
#        paraFile.close()

#        outfile = open(Base.__currentProjectPath__+'/tmpData.dc', 'wb')
        outfile = open(Base.__currentProjectPath__+'/data.dc', 'wb')
        outfile.write('\n'.join(self.newFile))
        outfile.close()
        

class DCInputChangesConfirm(BaseStore):
    '''
    this class is used to add material lines, four kinds of points in DC process
    '''
    def __init__(self):
        self.database = None
        
        self.jointLinesNum = 0
        self.BoundaryLinesNum = 0
        
        self.oldFile = []
        self.newFile = []
        
    def GetResources(self):
        return {
                'MenuText': 'DCInputChangesConfirm' ,
                'ToolTip': 'store DC input changes'}   
             
    def reset(self):
        self.oldFile = []
        self.newFile = []
        
    def storeScene(self):
        self.organizeContent()
        self.write2File()

        
    def organizeContent(self):
        '''
        organize content that will be writen into file.
        self.oldFile is original file
        self.newFile is the new file
        '''
        file = open(Base.__currentProjectPath__+'/data.dc','rb')
        self.oldFile = file.read(-1).split('\n')
        for i,line in enumerate(self.oldFile):
            self.oldFile[i]=line.strip()
        file.close()
        
        from DDADatabase import df_inputDatabase
        
        # schema
        nums = self.oldFile[1].split()
        self.jointLinesNum = int(nums[0])
        self.BoundaryLinesNum = int(nums[1])
        
        self.newFile = []
        self.newFile.extend(self.oldFile[0:2])

        self.newFile.append('%d\n%d\n%d\n%d\n%d\n%d'%(len(df_inputDatabase.materialLines)  \
                                , len(df_inputDatabase.boltElements), len(df_inputDatabase.fixedPoints) \
                                , len(df_inputDatabase.loadingPoints) , len(df_inputDatabase.measuredPoints) \
                                , len(df_inputDatabase.holePoints)))
        
        # lines
        self.__addLines()
        
        # points
        for p in df_inputDatabase.fixedPoints:
            self.newFile.append('%f %f %f %f'%(p.x,p.y , p.x,p.y))        
        
        self.__addPoints(df_inputDatabase.loadingPoints)
        self.__addPoints(df_inputDatabase.measuredPoints)
        self.__addPoints(df_inputDatabase.holePoints)
        
        if len(df_inputDatabase.holePoints)>0:
            self.newFile.append('0')
        else:
            self.newFile.append('0\n0 0')
        
        
    def __addLines(self):
        self.newFile.extend(self.oldFile[8:8+self.jointLinesNum])
        
        # material lines
        from DDADatabase import df_inputDatabase
        for line in df_inputDatabase.materialLines:
            if line.visible:
                self.newFile.append('%f %f %f %f %f'%(line.startPoint[0],line.startPoint[1]\
                                ,line.endPoint[0],line.endPoint[1],line.materialNo))
        
        # bolt elements
        from DDADatabase import df_inputDatabase
        for line in df_inputDatabase.boltElements:
            if line.visible:
                self.newFile.append('%f %f %f %f %f %f %f'%(line.startPoint[0],line.startPoint[1]\
                                ,line.endPoint[0],line.endPoint[1],line.e0 , line.t0 , line.f0))
        
        
    def __addPoints(self , points):
        '''
        add points to self.newFile
        '''
        for p in points:
            self.newFile.append('%f %f'%(p.x,p.y))
        
    def write2File(self):
#        paraFile = open(Base.__workbenchPath__+'/dc_Ff.c', 'wb')
#        paraFile.write(Base.__currentProjectPath__+'/data.dc')
#        paraFile.close()
        
        outfile = open(Base.__currentProjectPath__+'/data.dc', 'wb')
        outfile.write('\n'.join(self.newFile))
        outfile.close()
        

class DCInputDataStore(BaseStore):
    '''
    this class is used to add material lines, four kinds of points in DC process
    '''
    def __init__(self):
        self.reset()
        
    def GetResources(self):
        return {
                'MenuText':  'DC_Store',
                'ToolTip': "store data for dc."}   
             
    def reset(self):
        self.database = None
        self.content = ''
    
    def getPandect(self):
        from DDADatabase import dc_inputDatabase , dl_database
        
        # count additional lines
        from DDADatabase import dc_inputDatabase 
        self.additionalLines = []
        for pline in dc_inputDatabase.additionalLines:
            pts = pline.pts
            for i in range(len(pts)-1):
                p1 = pts[i]
                p2 = pts[i+1]
                self.additionalLines.append('%f  %f  %f  %f  %d'%(p1[0],p1[1],p2[0],p2[1] , pline.materialNo))
        
        mine0 = 0.022000
        jointLinesCount = len(dc_inputDatabase.jointLines)
        boundaryLinesCount = dc_inputDatabase.boundaryLinesNum
        materialLinesNum = 0
        boltsNum = 0
        fps = len([p for p in dc_inputDatabase.fixedPoints if p.visible])
        lps = len([p for p in dc_inputDatabase.loadingPoints if p.visible])
        mps = len([p for p in dc_inputDatabase.measuredPoints if p.visible])
        hps = len([p for p in dc_inputDatabase.holePoints if p.visible])
        
        return '%f\n%d %d\n%d\n%d\n%d\n%d\n%d\n%d\n'%(mine0 , jointLinesCount+len(self.additionalLines)\
            , boundaryLinesCount , materialLinesNum , boltsNum , fps , lps , mps , hps)
        
    def getLines(self):
        from DDADatabase import dc_inputDatabase
        tmpContent = self.additionalLines[:]
        for line in dc_inputDatabase.jointLines:
#            if not line.visible:
            p1 = line.startPoint
            p2 = line.endPoint
            tmpContent.append('%f  %f  %f  %f  %f'%(p1[0] , p1[1] , p2[0] , p2[1] , line.materialNo))
        return ('\n'.join(tmpContent))+'\n'
   
    def getPoints(self):
        from DDADatabase import dc_inputDatabase
        tmpContent = []
        
        tmpContent.extend(['%f  %f  %f  %f'%(p.x , p.y , p.x , p.y) for p in dc_inputDatabase.fixedPoints if p.visible])
        tmpContent.extend(['%f  %f'%(p.x , p.y) for p in dc_inputDatabase.loadingPoints if p.visible])
        tmpContent.extend(['%f  %f'%(p.x , p.y) for p in dc_inputDatabase.measuredPoints if p.visible])
        tmpContent.extend(['%f  %f'%(p.x , p.y) for p in dc_inputDatabase.holePoints if p.visible])

        return ('\n'.join(tmpContent)) +'\n'
    
    def storeScene(self):
        '''
        organize content that will be writen into file.
        self.oldFile is original file
        self.newFile is the new file
        '''
        print 'start to store DL information'
        self.content = self.getPandect() + self.getLines() + self.getPoints()
        self.write2File()
        self.content = ''
        print 'DL information store done'
        
    def write2File(self):
        outfile = open(Base.__currentProjectPath__+'/data.dc', 'wb')
        outfile.write(self.content)
        outfile.close()
        
 
class DFInputGraphDataStore(BaseStore):
    '''
    this class is used to add material lines, four kinds of points in DC process
    '''
    def __init__(self):
        self.reset()
        
    def GetResources(self):
        return {
                'MenuText':  'DF_Store',
                'ToolTip': "store data for dc."}   
             
    def reset(self):
        self.database = None
        self.content = ''
    
    def getPandect(self):
        from DDADatabase import df_inputDatabase
        blocksNum = 0
        boltsNum = 0
        
        jointsNum = 0
        for block in  df_inputDatabase.blocks:
            if block.visible():
                blocksNum += 1
                jointsNum += len(block.vertices)
        jointsNum += blocksNum*4  # parameters for block
        
        fps = len([p for p in df_inputDatabase.fixedPoints if p.visible])
        lps = len([p for p in df_inputDatabase.loadingPoints if p.visible])
        mps = len([p for p in df_inputDatabase.measuredPoints if p.visible])
        
        return '%d %d %d\n%d %d %d\n'%(blocksNum , boltsNum , jointsNum\
                                         , fps , lps , mps)
        
    def getBlocksSchema(self):
        from DDADatabase import df_inputDatabase
        tmpContent = []
        jointsCount = 1
        for block in df_inputDatabase.blocks:
            if block.visible():
                tmpContent.append('%d %d %d'%(block.materialNo , jointsCount \
                                , jointsCount+len(block.vertices)-1))
                jointsCount = jointsCount+len(block.vertices)+4
        return ('\n'.join(tmpContent))+'\n'
    
    def getJoints(self):
        from DDADatabase import df_inputDatabase
        tmpContent = []
        for block in df_inputDatabase.blocks:
            if block.visible():
                tmpContent.extend(['%f %f %f'%(t[0],t[1],t[2]) for t in block.vertices])
                paras = block.parameters
                for i in range(4):
                    tmpContent.append('%f %f %f'%(paras[3*i],paras[3*i+1],paras[3*i+2]))
        return ('\n'.join(tmpContent))+'\n'
    
   
    def getPoints(self):
        from DDADatabase import df_inputDatabase
        tmpContent = []
        
        tmpContent.extend(['%f %f %f'%(p.x , p.y , p.blockNo) for p in df_inputDatabase.fixedPoints  if p.visible])
        tmpContent.extend(['%f %f %f'%(p.x , p.y , p.blockNo) for p in df_inputDatabase.loadingPoints  if p.visible])
        tmpContent.extend(['%f %f %f'%(p.x , p.y , p.blockNo) for p in df_inputDatabase.measuredPoints if p.visible])

        return ('\n'.join(tmpContent)) +'\n'
    
    def storeScene(self):
        '''
        organize content that will be writen into file.
        self.oldFile is original file
        self.newFile is the new file
        '''
        print 'start to store DC information'
        self.content = self.getPandect() + self.getBlocksSchema() \
                        + self.getJoints() + self.getPoints()
        self.write2File()
        self.content = ''
        print 'DC information store done'
        
    def write2File(self):
        outfile = open(Base.__currentProjectPath__+'/data.df', 'wb')
        outfile.write(self.content)
        outfile.close()


DLStoreData = DLInformationStore()
FreeCADGui.addCommand('DDA_StoreData', DLStoreData)
FreeCADGui.addCommand('DDA_JointLineChangesConfirm', JointLineChangesConfirm())
FreeCADGui.addCommand('DDA_DCInputChangesConfirm', DCInputChangesConfirm())
FreeCADGui.addCommand('DDA_DCInputDataStore', DCInputDataStore())
FreeCADGui.addCommand('DDA_DFInputGraphDataStore', DFInputGraphDataStore())