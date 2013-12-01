######################################################################
#This file is used to generate *.ts file using 'pylupdate4' cmd
#to generate *.ts file. Run cmd: "pylpudate4 DDA.pro"
#Silver 2013-11-27
######################################################################

TEMPLATE = app
TARGET = DDA
INCLUDEPATH += .

# Input

SOURCES += Base.py DDADatabase.py DDADisplay.py DDAPanel.py DGPlayer.py\
			DDAShapes.py DDAToolbars.py DDATools.py DDA_rc.py DFCalculation.py DGPlayer.py Graph.py \
			InitGui.py loadDataTools.py storeScene.py ui_BoltParasManually.py ui_BoltsParameters.py \
			ui_DC.py ui_DF.py ui_DFCalcProcess.py ui_DL.py ui_tunnelBolts.py ui_TunnelSelection.py 
TRANSLATIONS += ./Resources/translations/DDA_zh-CN.ts
