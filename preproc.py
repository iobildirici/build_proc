from .gdalbildirici import geom2list,kirp,cokgenKontrol
import math
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
import qgis.utils
    
#lyr=iface.activeLayer()
def proc1(lyr,kn,ac,al):
    """Küçük çıkıntıları kırpma """
    crs=lyr.crs()
    vl = QgsVectorLayer("MultiPolygon", lyr.name()+"_cropped", "memory")
    vl.setCrs(crs)
    pr = vl.dataProvider()
    # Mevcut kolonları taşıma
    pr.addAttributes(lyr.fields()) 
    vl.updateFields()
    for ft in lyr.getFeatures():
        geom=ft.geometry()
        nkt=geom2list(geom)[0]
        nkt.pop()
        noks=kirp(nkt,dk=kn,da=ac,df=al)  #açı kriteri bu aşamada 1 derece falan olmalı!   
        for rr in noks:    
            fet = QgsFeature()
            pxy=[QgsPointXY(rr[i][0],rr[i][1]) for i in range(len(rr)) ]
            #pxy.pop()
            geom2=QgsGeometry.fromPolygonXY([pxy])
            fet.setGeometry(geom2)
            attr=[ft[i] for i in range(len(lyr.fields()))]
            fet.setAttributes(attr)
            pr.addFeatures([fet])
    vl.commitChanges() 
    vl.updateExtents()
    QgsProject.instance().addMapLayer(vl)

def proc2(lyr,ac,al):
    crs=lyr.crs()
    vl = QgsVectorLayer("MultiPolygon", lyr.name()+"_checked", "memory")
    vl.setCrs(crs)
    pr = vl.dataProvider()
    # Mevcut kolonları taşıma
    pr.addAttributes(lyr.fields()) 
    vl.updateFields()
    for ft in lyr.getFeatures():
        geom=ft.geometry()
        nkt=geom2list(geom)[0]
        nkt.pop()
        noks=cokgenKontrol(nkt,da=ac,df=al)  #açı kriteri bu aşamada 1 derece falan olmalı!   
        for rr in noks:    
            fet = QgsFeature()
            pxy=[QgsPointXY(rr[i][0],rr[i][1]) for i in range(len(rr)) ]
            #pxy.pop()
            geom2=QgsGeometry.fromPolygonXY([pxy])
            fet.setGeometry(geom2)
            attr=[ft[i] for i in range(len(lyr.fields()))]
            fet.setAttributes(attr)
            pr.addFeatures([fet])
    vl.commitChanges() 
    vl.updateExtents()
    QgsProject.instance().addMapLayer(vl)

class Pdiyalog(QDialog):
    def __init__(self,iface,ebeveyn=None):
        super(Pdiyalog,self).__init__(ebeveyn)
        self.iface=iface
        katmanlar=self.katmanliste()
        etk1=QLabel("Bina Katmanı") 
        etk2=QLabel("Yapılacak İşlem")
        self.etk3=QLabel("Parametreler")
        etk4=QLabel("Min Alan")
        etk5=QLabel("Min Kenar")
        etk6=QLabel("Min Açı (d)")
        self.df=QLineEdit("1.0")
        self.dk=QLineEdit("0.5")
        self.da=QLineEdit("2")
        but=QPushButton("Uygula")
        but.clicked.connect(self.uygula)
        but.setToolTip("Uygula!")
        if len(katmanlar)==0:
            self.etk3.setText("Açık alan katmanı yok!")
            but.setEnabled(False)
        self.kombt1=QComboBox()
        self.kombt1.addItems(self.katmanliste()) #Katman listesini kombobox a alıyoruz.
        # self.kombt1.activated.connect(self.yenile)
        self.kombt2=QComboBox()
        self.kombt2.addItems(["Kontrol","Kırpma"])
        kut=QGridLayout()
        kut.addWidget(etk1,0,0)
        kut.addWidget(self.kombt1,0,1)
        kut.addWidget(etk2,1,0)
        kut.addWidget(self.kombt2,1,1)
        kut.addWidget(self.etk3,3,0)
        kut.addWidget(but,2,1)
        kut.addWidget(etk4,4,0)
        kut.addWidget(self.df,4,1)
        kut.addWidget(etk5,5,0)
        kut.addWidget(self.dk,5,1)
        kut.addWidget(etk6,6,0)
        kut.addWidget(self.da,6,1)
        self.setLayout(kut)
        self.setWindowTitle("Bina Veri Ön İşlemler") 
        self.setGeometry(50,50,100,100) 
    def uygula(self):
        for lyr in self.iface.mapCanvas().layers():
            if self.kombt1.currentText()==lyr.name():
                self.lyr1=lyr
        aln=float(self.df.text())
        knr=float(self.dk.text())
        aci=math.radians(float(self.da.text()))
        if self.kombt2.currentText()=="Kontrol":
            proc2(self.lyr1,aci,aln)
        else:
            proc1(self.lyr1,knr,aci,aln)
        self.yenile()
        #self.kombt1.setItemText(self.katmanliste())
        #print(aln,knr,aci)
    def katmanliste(self):
        katmanlar=[]
        for lyr in self.iface.mapCanvas().layers():
            if lyr.geometryType() == QgsWkbTypes.PolygonGeometry:
                katmanlar.append(lyr.name())
        return katmanlar
    def yenile(self):
        self.kombt1.clear()
        self.kombt1.addItems(self.katmanliste())
        

 
