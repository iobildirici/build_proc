#-----------------------------------------------------------
# Copyright (C) 2024 İbrahim Öztuğ Bildirici
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from PyQt5.QtWidgets import QAction, QMessageBox
from PyQt5.QtGui import QIcon
from .preproc import Pdiyalog
from .resources import *
from qgis.core import *
import qgis.utils



def classFactory(iface):
    return BinaPreProc(iface)


class BinaPreProc:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        icon=QIcon(':/plugins/build_proc/ikon1.png')
        self.action = QAction(icon,'BP', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.action.setToolTip("Bina verileri ön hazılık!")
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        #QMessageBox.information(None, 'Alan Parametreler', 'Alan parametreleri hesaplama aracı')
        self.p=Pdiyalog(self.iface)
        self.p.show()
        self.p.exec_()
        
