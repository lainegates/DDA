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

import interfaceTools

#########################################
#  test  tools
#
#########################################
#s1 = [1 , 3 , 6 , 9 , 11]
#s2 = [0 , 2 , 3 , 10]
#s3 = [2 , 4 , 9 , 13]
#s4 = [1 , 3 , 6 , 9 , 11]
#print interfaceTools.calcIntersection(s1, s2)
#print interfaceTools.calcIntersection(s1, s3)
#print interfaceTools.calcIntersection(s1, s4)
#
#print interfaceTools.calcUnion(s1, s2)
#print interfaceTools.calcUnion(s1, s3)
#print interfaceTools.calcUnion(s1, s4)


#########################################
#  test  LineSelection
#
#########################################
#m = interfaceTools.LineSelection()
#
#segLists = [[1,3],[1,2,3,4],[1,2,4],[3,4]]
#m.setData(segLists)
#matrix = m.matrix
#for i in range(len(matrix)):
#    print '======== line ' , i
#    for j in range(len(matrix[i])):
#        print '\t' , matrix[i][j]
#        

########################################
# test RectangleSelection
########################################

rects = interfaceTools.RectangleSelection()
rectangles = [(0,4,4,0),(4,6,6,4),(3,7,7,3),(7,5,9,2)]
rects.setData(rectangles)
print rects.getIntersectedRectsNo(3, 4, 4 , 3)
print '==============='
print rects.getIntersectedRectsNo(3, 5, 5 , 3)

######################################
# 折半查找测试
######################################
#coords = [0 , 3 , 5 , 7 , 9 , 10 , 11]
#print rects.getIndex(-2, coords)
#print rects.getIndex(12, coords)
#print rects.getIndex(3, coords)
#print rects.getIndex(10, coords)
#print rects.getIndex(2, coords)
#print rects.getIndex(4, coords)
#print rects.getIndex(8, coords)
#print rects.getIndex(4.6, coords)

#########################################
#  test BorderCalculator
#########################################
#pts = [(0,0,0),(1,1,0),(2,0,0),(3,0,0),(4,1,0),(5,0,0),(6,1,0),(4,4,0),(3,2,0),(2,4,0),(0,2,0)]
#border = interfaceTools.BorderCalculator()
#print border.calcualteBorder(pts)