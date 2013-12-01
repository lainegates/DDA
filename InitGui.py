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


class DDA (Workbench):
    MenuText = "DDA"
    ToolTip = "DDA workbench"

    def Initialize(self):
        # run self-tests
        depsOK = False
        try:
            from pivy import coin
            if FreeCADGui.getSoDBVersion() != coin.SoDB.getVersion():
                raise AssertionError("FreeCAD and Pivy use different versions of Coin. This will lead to unexpected behaviour.")
        except AssertionError:
            FreeCAD.Console.PrintWarning("Error: FreeCAD and Pivy use different versions of Coin. This will lead to unexpected behaviour.\n")
        except ImportError:
            FreeCAD.Console.PrintWarning("Error: Pivy not found, DDA workbench will be disabled.\n")
        except:
            FreeCAD.Console.PrintWarning("Error: Unknown error while trying to load Pivy\n")
        else:
            try:
                import PyQt4
            except ImportError:
                FreeCAD.Console.PrintWarning("Error: PyQt4 not found, DDA workbench will be disabled.\n")
            else:
                depsOK = True

#        import FreeCAD , FreeCADGui

        import DDA_rc
        import FreeCADGui

        FreeCADGui.addLanguagePath(":/translations")
        FreeCADGui.addIconPath(":/icons")


#            try:
        import DDAShapes
#            except:
#                FreeCAD.Console.PrintWarning("'DDAShapes' moudle import failed.")

        import DGPlayer , DFCalculation , DDAPanel
#            try:
        import drawGui 
#            except:
#                FreeCAD.Console.PrintWarning("'drawGui' moudle import failed.")
        import DDAToolbars

        import interfaceTools
        import storeScene
        import loadDataTools
#        FreeCADGui.addPreferencePage(":/DDA-preferences.ui","DDA")
#        FreeCADGui.addPreferencePage(":/userprefs-base.ui","DDA")
#        FreeCAD.Console.PrintMessage('Loading DDA GUI...\n')
        
        import DDAGui
        list = ['DDA_ChooseProjectPath' , 'DDA_SetPanelSize' , 'DDA_DL' , 'DDA_DC','DFCalculation','PlayDF']
        self.appendToolbar('DDACmds' , list)
#        self.appendMenu("My Command",list)
        
    def resetCamera(self):
        import FreeCADGui
        camera = '#Inventor V2.1 ascii\n\n\nOrthographicCamera {\n  viewportMapping ADJUST_CAMERA\n  position 0 0 1\n  orientation 0 0 1  0\n  aspectRatio 1\n  focalDistance 5\n  height 40\n\n}\n'
        FreeCADGui.activeDocument().activeView().setCamera(camera)
      
    def Activated(self):
        import FreeCAD , FreeCADGui
        if hasattr(FreeCADGui,"draftToolBar"):
            FreeCADGui.draftToolBar.Deactivated()

        if not FreeCAD.ActiveDocument:
            FreeCAD.newDocument('DDA')
        
        import Base
        Base.enableSeletionObserver(True)
        import DDADatabase
        DDADatabase.enableOperationObverser(True)
        
        FreeCADGui.runCommand('DDA_ResetCamera')
        
        self.resetWorkbench()

    def resetWorkbench(self):
        import os
        path = os.getcwd()
        path = path.replace('\\','/')
        path = path.replace('bin' , 'Mod/DDA')
        import Base
        Base.__workbenchPath__ = path
        print Base.__workbenchPath__ 

    def Deactivated(self):
#        if DDAGui.__currentPanel__ != None :
#            DDAGui.__currentPanel__.hide()
#        FreeCADGui.DDADockWidget.Deactivated()
        import Base
        Base.enableSeletionObserver(False)
        import DDADatabase
        DDADatabase.enableOperationObverser(False)

Gui.addWorkbench(DDA())
