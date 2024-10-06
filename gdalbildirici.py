#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 16:28:45 2023

@author: iobildirici
"""
import matplotlib.pyplot as plt
import sys
import math
import os
from osgeo import ogr
import numpy as np
plt.axis("equal")
"""Burada kullanılan noktalar ogr.geometry den gelen ring (çokgeni oluşturan çoklu doğru)
   oluşturan noktalar ring.GetPoint(indis) şeklinde elde ediliyor. Bu noktalar 
   üç elemanlı bir tupple eleman sırası x,y,z"""
#TEMEL ANALİTİK GEOMETRİ FONKSİYONLARI
def dik(nk1,nk2,nk3):
    "1-2 doğrusuna 3 den inilen dik boy ve dik ayak"
    k=k=((nk2[0]-nk1[0])**2+(nk2[1]-nk1[1])**2)**0.5
    if k<1.e-14:
        print("Dik hata!")
        print(nk1,nk2,nk3)
        return 0,0,0
    s=(nk2[0]-nk1[0])*(nk3[0]-nk1[0])/k+(nk2[1]-nk1[1])*(nk3[1]-nk1[1])/k
    h=(nk2[1]-nk1[1])*(nk3[0]-nk1[0])/k-(nk2[0]-nk1[0])*(nk3[1]-nk1[1])/k
    ii= s>1.e-14 and s<(k-1.e-14)
    return h,s,ii
def ynok(nk1,nk2,s,h):
    """Yan nokta, 1-2 doğrusunda dik ayak dik boydan koordinata geçiş"""
    k,a=kenar(nk1,nk2)
    x=nk1[0]+s*math.sin(a)+h*math.cos(a)
    y=nk1[1]+s*math.cos(a)-h*math.sin(a)
    return x,y
def ynok2(nk1,nk2,s,h):
    """Yan nokta, 1-2 doğrusunda dik ayak dik 
    boydan koordinata geçiş z=0 ataması yapar."""
    k,a=kenar(nk1,nk2)
    x=nk1[0]+s*math.sin(a)+h*math.cos(a)
    y=nk1[1]+s*math.cos(a)-h*math.sin(a)
    return (x,y,0)
def vekt_yap(n1,n2):
    v=[]
    for i in range(len(n1)):
        v.append(n2[i]-n1[i])
    return v
def aci3nok(n0,n1,n2):
    """n0-n1 ve n0-n2 doğruları arasındaki açı"""
    v1=vekt_yap(n0,n1);v2=vekt_yap(n0,n2)
    return math.acos(vekt_skaler(v1,v2)/(vekt_norm(v1)*vekt_norm(v2)))
def vekt_norm(v):
    return (v[0]**2+v[1]**2)**0.5
def vekt_skaler(v1,v2):
    return v1[0]*v2[0]+v1[1]*v2[1]
def vekt_aci(v1,v2):
    a=vekt_skaler(v1, v2)/(vekt_norm(v1)*vekt_norm(v2))
    return math.acos(a)
def simetri(nk1,nk2,nk3):
    """1-2 eksenine göre 3 noktasının simetriği"""
    h,s,ii=dik(nk1,nk2,nk3)
    return ynok2(nk1,nk2,s,-h)
def kenar(nk1,nk2):
    "1-2 noktaları arası kenar ve açı"
    k=((nk2[0]-nk1[0])**2+(nk2[1]-nk1[1])**2)**0.5
    al=math.atan2(nk2[0]-nk1[0],nk2[1]-nk1[1])
    if al<0:
        al+=2*math.pi
    return k,al
def kenar_man(nk1,nk2):
    """Manhattan Uzaklığı"""
    return abs(nk1[0]-nk2[0])+abs(nk1[1]-nk2[1])
def kenar_oklid(nk1,nk2):
    return ((nk2[0]-nk1[0])**2+(nk2[1]-nk1[1])**2)**0.5
def ikinci(nk1,knr):
    nk2=[0,0,0]
    nk2[0]=nk1[0]+knr[0]*math.sin(knr[1])
    nk2[1]=nk1[1]+knr[0]*math.cos(knr[1])
    return tuple(nk2)
def makskenar(ring):
    """ring objesinde en büyük kenarı ve açısını bulma"""
    knr=[]
    k=0
    j=0
    for i in range(ring.GetPointCount()-1):
        knr.append(kenar(ring.GetPoint(i),ring.GetPoint(i+1)))
        if knr[i][0]>k:
            k=knr[i][0]
            j=i
    return knr[j]
def makskenarnok(nok):
    """listede en büyük kenarı ve açısını bulma"""
    kn=(0,0)
    for i in range(len(nok)):
        k,a=kenar(nok[i-1],nok[i])
        if k>kn[0]:
            kn=(k,a)
    return kn

def dondur(nok,p,a):
    """Listeyi nokta etrafında a kadar döndürme, açı radyan"""
    nok2=[]
    for n in nok:
        x=p[0]+(n[0]-p[0])*math.cos(a)+(n[1]-p[1])*math.sin(a)
        y=p[1]-(n[0]-p[0])*math.sin(a)+(n[1]-p[1])*math.cos(a)
        nok2.append((x,y))
    return nok2   
def merkez(ring):
    """ring objesi merkezi için bir kod, noktaların bir tarafta yığılmasından 
    etkilenmez."""
    xp=0
    yp=0
    pd=0
    for i in range(ring.GetPointCount()-1):
        xi=ring.GetX(i)
        yi=ring.GetY(i)
        xip=ring.GetX(i+1)
        yip=ring.GetY(i+1)
        t1=(xi*yip-xip*yi)
        pd+=t1
        xp+=t1*(xi+xip)
        yp+=t1*(yi+yip)
    xp/=3*pd
    yp/=3*pd
    return xp,yp
def merkeznok(nok):
    xp=0
    yp=0
    pd=0
    for i in range(len(nok)):
        t1=(nok[i-1][0]*nok[i][1]-nok[i][0]*nok[i-1][1])
        pd+=t1
        xp+=t1*(nok[i-1][0]+nok[i][0])
        yp+=t1*(nok[i-1][1]+nok[i][1])
    xp/=3*pd
    yp/=3*pd
    return (xp,yp)
def poly_area(nkt):
    """Çokgen Alanı liste ile çalışır."""
    f=0
    for i in range(len(nkt)):
        f+=(nkt[i][0]*nkt[i-1][1]-nkt[i][1]*nkt[i-1][0])
    return f/2
def line_intersect(i,j,k,l):
    """i,j ve k,l doğrularının kesişimi"""
    d=(j[0]-i[0])*(k[1]-l[1])-(j[1]-i[1])*(k[0]-l[0])
    if abs(d)<=1e-12:
        return (0,0,0),False
    p1=((k[0]-l[0])*(i[1]-k[1])-(k[1]-l[1])*(i[0]-k[0]))/d
    p2=((i[0]-k[0])*(j[1]-i[1])-(i[1]-k[1])*(j[0]-i[0]))/d
    arada=p1>0 and p1 <1 and p2>0 and p2<1
    nkes=(i[0]+p1*(j[0]-i[0]),i[1]+p1*(j[1]-i[1]),0)
    return nkes, arada
def donme(ring,a=5):
    """ring merkez etrafında a açısı kadar döndürülür. Açı birimi derece"""
    a=math.radians(a)
    x0,y0=merkez(ring)
    ring2 = ogr.Geometry(ogr.wkbLinearRing)
    for i in range(ring.GetPointCount()):
        x=x0+(ring.GetX(i)-x0)*math.cos(a)+(ring.GetY(i)-y0)*math.sin(a)
        y=y0-(ring.GetX(i)-x0)*math.sin(a)+(ring.GetY(i)-y0)*math.cos(a)
        ring2.AddPoint(x,y)
    return ring2
def olcekleme(ring,s=1):
    """ring merkeze göre s kadar ölçeklenir."""
    x0,y0=merkez(ring)
    ring2 = ogr.Geometry(ogr.wkbLinearRing)
    for i in range(ring.GetPointCount()):
        x=x0+(ring.GetX(i)-x0)*s
        y=y0+(ring.GetY(i)-y0)*s
        ring2.AddPoint(x,y)    
    return ring2
def otele_nok(nok,dx=(0,0)):
    nok2=[]
    for nk in nok:
        nk=(nk[0]+dx[0],nk[1]+dx[1])
        nok2.append(nk)
    return nok2
def nokesit(p1,p2):
    ii=True
    for i in range(3):
        ii=ii and abs(p1[i]-p2[i])<1.e-13
    return ii
def noktayaz(pnt):
    print("----",len(pnt))
    for p in pnt:
        print(*p)
def eksenbul(nokt,da=0.08):
    "Deneme amaçlı yapıldı. Kullanılmadı. "
    hmin=1e9
    hmax=0
    p0=merkeznok(nokt)
    jj=False
    kk=False
    for i in range(len(nokt)):
        h,s,ii=dik(nokt[i-1],nokt[i],p0)
        if ii and h<hmin:
            hmin=h
            p1=ynok(nokt[i-1],nokt[i],s,0)
            jj=True
        if ii and h>hmax:
            hmax=h
            p2=ynok(nokt[i-1],nokt[i],s,0)
            kk=True
    if jj and kk:
        k1,al1=kenar(p0,p1)
        k2,al2=kenar(p0,p2)
        # print(abs(al2-al1)-math.pi/2)
        ii=abs(abs(al2-al1)-math.pi/2)<da or abs(abs(al2-al1)-3*math.pi/2)<da
        return ii,p1,p2,k1,k2
    else:
        return False,(0,0),(0,0),0,0
def yonlu_mbr(nok):
    """Şekli içine alan yönlü en küçük dik dörtgen"""
    p0=nok[0]
    kn=makskenarnok(nok)
    nokd=dondur(nok, p0, -kn[1])
    x=[nk[0] for nk in nokd]
    y=[nk[1] for nk in nokd]
    drt=[]
    drt.append((min(x),min(y)))
    drt.append((min(x),max(y)))
    drt.append((max(x),max(y)))
    drt.append((max(x),min(y)))
    drtd=dondur(drt,p0,kn[1])
    return drtd

#RING ILE ILGILI DONUSUM-CIZIM FONKSİYONLARI

def dortgenyap2(ring,df=0.05):
    nokt=ring.GetPoints()
    nokt.pop(-1)
    #Zaten 4 köşeli ise...
    if len(nokt)<=4:
        return ring
    #MBR bul
    drtgn=yonlu_mbr(nokt)
    f=abs(poly_area(nokt))
    fd=abs(poly_area(drtgn))
    dff=1-f/fd
    if abs(dff)<df:
        #orijinal alana dönelim ve ring yapalım
        s=(f/fd)**0.5
        ring2=olcekleme(list2ring(drtgn),s=s)
    return ring2

def dortgenyap3(nokt,df=0.05,olc=True):
    #Zaten 4 köşeli ise...
    if len(nokt)<=4:
        return nokt
    #MBR bul
    drtgn=yonlu_mbr(nokt)
    f=abs(poly_area(nokt))
    fd=abs(poly_area(drtgn))
    dff=1-f/fd
    #print(f,fd,dff)
    if abs(dff)<df:
        return drtgn,True
    else:
        return nokt,False

def dortgenyap(ring,df=0.05,da=0.01):
    nokt=ring.GetPoints()
    nokt.pop(-1)
    #Zaten 4 köşeli ise...
    if len(nokt)<=4:
        return ring
    hmin=1e9
    hmax=0
    p0=merkeznok(nokt)
    jj=False
    kk=False
    #Merkez noktaya en uzak ve en yakın kenarlar 
    #üzerinde iki nokta oluşturuyoruz. 
    for i in range(len(nokt)):
        h,s,ii=dik(nokt[i-1],nokt[i],p0)
        if ii and h<hmin:
            hmin=h
            p1=ynok(nokt[i-1],nokt[i],s,0)
            jj=True
        if ii and h>hmax:
            hmax=h
            p2=ynok(nokt[i-1],nokt[i],s,0)
            kk=True
    # plt.plot((p1[0],p0[0],p2[0]),(p1[1],p0[1],p2[1]),'k--')
    # plt.scatter(p0[0],p0[1],c='k')
    #Dikler inildi ise incelemeye geç
    if jj and kk:
        daa=aci3nok(p0, p1, p2)
        #print(daa)
        #Açılar da toleransı içinde dik ise
        if abs(daa-math.pi/2)<da:
            b=kenar_oklid(p0,p1)
            a=kenar_oklid(p0,p2)
            f=poly_area(nokt)
            fd=4*a*b
            dff=1-f/fd
            #Alan değişimi verilen % tolerans içinde ise
            if abs(dff)<df:
                #Şimdi dörtgen yapabiliriz. 
                drtg=[]
                drtg.append(ynok(p0, p2, a,b))
                drtg.append(ynok(p0, p2, -a,b))
                drtg.append(ynok(p0, p2, -a,-b))
                drtg.append(ynok(p0, p2, a,-b))
                #orijinal alana dönelim ve ring yapalım
                s=(f/fd)**0.5
                ring2=olcekleme(list2ring(drtg),s=s)
                return ring2
    return ring

def ring2xy(ring):
    "ring x,y listelerine dönüştürülür."
    x=[]
    y=[]
    for i in range(ring.GetPointCount()):
        p=ring.GetPoint(i)
        x.append(p[0])
        y.append(p[1])
    return x,y
def ring2ring0(ring1,ring2,d=0.5):
    """ring1 değişken ring2 sabit"""
    for i in range(ring1.GetPointCount()):
        for j in range(ring2.GetPointCount()):
            ds=((ring1.GetX(i)-ring2.GetX(j))**2+(ring1.GetY(i)-ring2.GetY(j))**2)**0.5
            if ds>0 and ds<d:
                ring1.SetPoint(i,x=ring2.GetX(j),y=ring2.GetY(j))
def ring2ring(ring1,ring2,d=0.5):
    """ring1 değişken ring2 sabit iki ring birbirine d den yakınsa
    çakıştırılır."""
    chg=False
    for i in range(ring1.GetPointCount()):
        p3=ring1.GetPoint(i)
        hma=2*d
        for j in range(ring2.GetPointCount()-1):
            p1=ring2.GetPoint(j)
            p2=ring2.GetPoint(j+1)
            h,s,ia=dik(p1,p2,p3)
            #print(">>",j,j+1,s,h,ia)
            if abs(h)<hma and ia and abs(h)>0 and abs(h)<=d:
                xi,yi=ynok(p1,p2,s,0)
                ring1.SetPoint(i,x=xi,y=yi)
                chg=True
                hma=h
    return chg
def ringdraw(ring,rnk='k',yaz=True):
    plt.axis('equal')
    "ring matplotlib.pyplot ile çizdirilir."
    x,y=ring2xy(ring)
    plt.plot(x,y,color=rnk)
    if yaz:
        for i in range(len(x)):
            plt.annotate(i,(x[i],y[i]))
def listdraw(nok,rnk='k',yaz=True):
    plt.axis('equal')
    if isinstance(nok,list):
        x=[nk[0] for nk in nok]
        y=[nk[1] for nk in nok]
        plt.plot(x,y,c=rnk)
        if yaz:
            for i in range(len(x)):
                plt.annotate(i,(x[i],y[i]))
#KONTUR GENELLEŞTİRMESİ FONKSİYONLARI
def kontur(nok,da=0.05,dk=0.25):
    """Aykırı ve düz noktalar, kısa kenarlar ayıklanır"""
    #print(len(nok))
    #noktayaz(nok)
    #Kısa kenar ayıklama
    dar=abs(poly_area(nok))*0.05
    #print(dar)
    for i in range(len(nok)):
        k,a=kenar(nok[i],nok[i-1])
        if k<=dk:
            if i==len(nok)-1:
                ii=0
            else:
                ii=i+1
            k2,a2=kenar(nok[i],nok[ii])
            d=abs(a2-a)
            if abs(d-math.pi/2)<2*da or abs(d-3*math.pi/2)<2*da:
                nok[i-1]=(nok[i-1][0],nok[i-1][1],-1)
            else:
                nok[i]=(nok[i][0],nok[i][1],-1)
    nok2=[nk for nk in nok if nk[2]>-1]
    #print(nok2)
#        if k>dk:
#            nok2.append(nok[i])
    #Küçük açı ayıklama
    #noktayaz(nok2)
    for i in range(len(nok2)):
        #son nokta ile ilk nokta arasına bakmak için 
        if i<(len(nok2)-1):
            ii=i+1
        else:
            ii=0
        k1,a1=kenar(nok2[i],nok2[i-1])
        k2,a2=kenar(nok2[i],nok2[ii])
        d=abs(a2-a1) 
        #print(nok2[i],d)
        if d<da or abs(d-math.pi)<da:
            ar=0.5*k1*k2*math.sin(d)
            #print(ar,dar)
            if ar<dar:
                nok2[i]=(nok2[i][0],nok2[i][1],-1)
    return [nk for nk in nok2 if nk[2]>-1]
            
def kontur_gen(ring,da=0.05,dk=0.3,dar=0.045):
    "Bina dış çizgi genelleştirmesi"
    nok=ring.GetPoints()
    if nokesit(nok[0],nok[-1]):
        nok.pop(-1)
    if len(nok)<5:
        return ring
    nok1=self_edit(nok,dk)
    nok2=poly_clip(nok1,dk)
    nok3=kose_duzelt(nok2,dar)
    nok4=kontur(nok3,da,dk)
    ring2 = ogr.Geometry(ogr.wkbLinearRing)
    for nk in nok4:
        ring2.AddPoint(*nk)
    ring2.CloseRings()
    return ring2             

def poly_clip(nok,dk):
    "Çıkıntıları gidermek için"
#    nok=ring.GetPoints()
    if nokesit(nok[0],nok[-1]):
        nok.pop(-1)
    if len(nok)<6:
        return nok
    for i in range(len(nok)):
        if nok[i][2]<0:
            continue
        for j in range(i+1,len(nok)):
            if nok[j][2]<0:
                continue
            k,a=kenar(nok[i],nok[j])
            #print(i,j,k)
            if(k<dk):
                #print(i,j,k)
                for ii in range(i+1,j):
                    #print("---",ii)
                    nok[ii]=(nok[ii][0],nok[ii][1],-1)
    #print(*nok)
    nok2=[nk for nk in nok if nk[2]>=0]                           
    return nok2
def self_edit(nok,dk,self_only=False):
    "Kendi kendini kesme ve çıkıntılar"
#Nokta dizilimi saat ibresi mi? Değilse reverse
#    nok=ring.GetPoints()
    #listdraw(nok0)
    nok2=[]

    #İlk nokta son nokta ile aynı ise sil. 
    if nokesit(nok[0],nok[-1]):
        nok.pop(-1) 
    if len(nok)<5:
        return nok
    #
    #for i in range(len(nok)):
    #    print(i,nok[i])
    #listdraw(nok)
    f=poly_area(nok)
    if f<0:
        nok.reverse()
    #kendi kendini kesen kenarlara nokta ekleme. 
    for i in range(len(nok)):
        nok2.append(nok[i-1])
        for j in range(len(nok)):
            if i!=j:
                nkes,ii=line_intersect(nok[i-1], nok[i], nok[j-1], nok[j])
                if ii:
                    nok2.append(nkes)
    #listdraw(nok2)                #print(i,j,"varr")
    if self_only:
        return nok2
    nok3=[]    
    #İnilen dik kısa ise nokta atar.
    for i in range(len(nok2)):
        kn,a=kenar(nok2[i-1],nok2[i])
        nok3.append(nok2[i-1])
        if kn<1.e-10:
            continue
        for j in range(len(nok2)):
            if i==j:
                continue
            h,s,ii=dik(nok2[i-1],nok2[i],nok2[j])
            if ii and abs(h)<dk and abs(h)>0:
                p=ynok2(nok2[i-1],nok2[i],s,0)
                nok3.append(p)
    nok4=[]
    #listdraw(nok3)
    #birbirine çok yakın noktalar var mı?
    for i in range(len(nok3)):
        ion,isn=oncesonra(i,len(nok3))
        k,a=kenar(nok3[i],nok3[isn])
        if k>0.1*dk:
            nok4.append(nok3[i])
    #listdraw(nok4)
    return nok4 

def kose_duzelt(nok,da=0.03):
    #İlk nokta son nokta ile aynı ise sil. 
    if nokesit(nok[0],nok[-1]):
        nok.pop(-1)
    if len(nok)<6:
        return nok
    for i in range(len(nok)):
        ion=i-1
        isn=i+1
        if isn>=len(nok):
            isn-=len(nok)
        aln=poly_area([nok[ion],nok[i],nok[isn]])
        if aln<0 and abs(aln)<da:
            ionn=ion-1
            isnn=isn+1
            if isnn>=len(nok):
                isnn-=len(nok)
            if is_ortho(nok[ionn],nok[ion],nok[isn],nok[isnn]):
                nks,ara=line_intersect(nok[ionn],nok[ion],nok[isn],nok[isnn])
                nok[i]=nks
                nok[ion]=(nok[ion][0],nok[ion][1],-1)
                nok[isn]=(nok[isn][0],nok[isn][1],-1)
    return [nk for nk in nok if nk[2]>-1]
def listeyap(nok,da=0.12,dk=0.1,dar=0.05):
    #Noktalarla ilgili bilgi listesi yap.
    #aln5=abs(poly_area(nok))*0.05
    noklis=[]
    for i in range(len(nok)):
        ion,isn=oncesonra(i,len(nok))
        #print(i,ion,isn)
        k0,a0=kenar(nok[i],nok[ion])
        k1,a1=kenar(nok[i],nok[isn])
        t=a0-a1
        if t<0:
            t+=2*math.pi
        ar=k0*k1*math.sin(t)
        
        ark=int(0)
        if abs(ar)<dar:
            if ar<0:
                ark=-1
            else:
                ark=1
        t1=t if t<math.pi else t-math.pi
        #print(i,ar,math.degrees(t))
        orto=abs(t1-math.pi/2) < da
        duz=abs(t)<da or abs(t-math.pi)<da or abs(t-2*math.pi)<da
#        if abs(ar)>aln5:
#            duz=False
        #                 0     1  2 3      4   5   6   
        noklis.append([nok[i],True,t,k1<dk,ark,orto,duz])
        #print(i,da,noklis[i])
    return noklis
def listeyaz(lis):
    for i in range(len(lis)):
        print(f"{i:>3d}{lis[i][0][0]:>10.2f}{lis[i][0][1]:>12.2f}",end=" ")
        print(f"{lis[i][1]} {lis[i][2]:>6.3f} {lis[i][3]} {lis[i][4]:>3d}",end=" ")
        print(f"{lis[i][5]} {lis[i][6]}")
        
def kon_gen_nok(nok,da=0.08,dk=0.1,dar=0.05):
    #İlk nokta son nokta ile aynı ise sil. 
    if nokesit(nok[0],nok[-1]):
        nok.pop(-1)
    if len(nok)<6:
        return nok
    #Nokta listesi al
    #print("burada")
    noklis=listeyap(nok,da,dk,dar)
    #listeyaz(noklis)
    #Yay oluşturan noktalar
    for i in range(len(nok)):
        if not noklis[i][1]:
            continue
        ion,isn=oncesonra(i,len(nok))
        if noklis[i][6] and noklis[isn][6]:
            j=isn
            while True:
                jj,j=oncesonra(j,len(nok))
                if not noklis[j][6]:
                    break
            if abs(i-j)<3:
                continue
            #jj=i
            for jj in range(i,j):
                tp=dik(noklis[ion][0],noklis[j-1][0],noklis[jj][0])
                #print(i,j,jj,tp,dk)
                if abs(tp[0])<dk:
                    noklis[jj][1]=False
    #listeyaz(noklis)
    #yeniden liste yapalım...
    nok=[nlst[0] for nlst in noklis if nlst[1]]
#    listdraw(nok)
    noklis=listeyap(nok,da,dk,dar) 
    
    #listdraw(nok)                               
    #Dik girinti çıkıntı düzeltme
    for i in range(len(nok)):
        if not noklis[i][1]:
            continue
        ion,isn=oncesonra(i,len(nok))
        if abs(noklis[i][4])==1 and noklis[i][5]:
            j=isn
            noklis[i][1]=False
            while j<len(nok):
                if abs(noklis[j][4])==1 and noklis[j][5]:
                    noklis[j][1]=False
                    j+=1
                else:
                    break
            if j-ion==2 and noklis[ion][5] and noklis[j][5]:
                ionn,ii=oncesonra(ion,len(nok))
                jj,json=oncesonra(j,len(nok))
                nokt,lk=line_intersect(noklis[ionn][0],noklis[ion][0],noklis[j][0],noklis[json][0])                
                #nokt=simetri(noklis[ion][0],noklis[j][0],noklis[i][0])
                noklis[i][0]=nokt
                noklis[i][1]=True
        #Açı olarak sivri ya da dik olmayan alan olarak küçük girinti ve çıkıntılar
        if abs(noklis[i][4])==1 and not noklis[i][5]:
            noklis[i][1]=False
    #listeyaz(noklis)
    #yeniden liste yapalım...
    nok=[nlst[0] for nlst in noklis if nlst[1]]
    
    #print(len(nok))
    noklis=listeyap(nok,da,dk,dar)
    #Sivri/düz açı 
    nok=[nlst[0] for nlst in noklis if not nlst[6]]
    #Bir daha liste yapalım
    noklis=listeyap(nok,da,dk,dar)
    #Bir daha düz/sivri açılı noktaları silelim.
    nok=[nlst[0] for nlst in noklis if not nlst[6]]
    #kısa kenar var mı?
    noklis=listeyap(nok,da,dk,dar)  
    for i in range(len(noklis)):
        if not noklis[i][1]:
            continue
        ion,isn=oncesonra(i,len(nok))
        if noklis[i][3]:
            if noklis[i][5]:
                noklis[isn][1]=False
            else:
                noklis[i][1]=False
    nok=[nlst[0] for nlst in noklis if nlst[1]]               
    return nok
def kon_gen(ring,da=0.3,dk=0.1,dar=0.05):
    nok=ring.GetPoints()
    nok1=self_edit(nok,dk)
    nok2=kon_gen_nok(nok1,da,dk,dar)
    ring2 = ogr.Geometry(ogr.wkbLinearRing)
    for nk in nok2:
        ring2.AddPoint(*nk)
    ring2.CloseRings()
    return ring2                 
def oncesonra(i,n):
    ion=i-1
    if ion<0:
        ion+=n
    isn=i+1
    if isn>=n:
        isn-=n
    return ion,isn
def zig_zag(a,b,c,d): #returns true if three segments form zig-zag
    zz= (a[1]*(c[0]-b[0])+b[1]*(a[0]-c[0])+c[1]*(b[0]-a[0]))*(b[1]*(d[0]-c[0])+c[1]*(b[0]-d[0])+d[1]*(c[0]-b[0]))
    print("<<",zz)
    return zz<0
def is_ortho(i,j,k,l,da=0.09):
    k1,a1=kenar(i,j)
    k2,a2=kenar(k,l)
    d=abs(a2-a1)
    if d>math.pi:
        d-=math.pi
    return abs(d-math.pi/2)<=da
def kopyala(so,de):
    lis=os.listdir()
    for i in lis:
        if so in i:
            ii=i.replace(so,de)
            cmd="cp "+i+" "+ii
            os.system(cmd)
def list2ring(nok):
    ring=ogr.Geometry(ogr.wkbLinearRing)
    for nk in nok:
        ring.AddPoint(*nk)
    ring.CloseRings()
    return ring

def kirp(nok,dk=0.15,da=0.1,df=0.1):
    """Listeler (xy) için küçük parçaları kırpar.
    Uzunluk kriterine göre dik iner. Parçaları alan kriterine göre 
    ayırır. 
    Listelerde son nokta ilk nokta olmamalıdır. 
    dk: kenar yakınlık ölçütü 
    da: min açı
    df:min alan
    """
    noks=[]
    ilknokta(nok,dk=dk)
    nok1=dikin(nok,dk=dk)
    #dikin değişiklik yapmadı ise
    if len(nok1)==len(nok):
        nok2=kopart(nok1,dk=dk,df=df,dik=False)
    else:
        nok2=kopart(nok1,dk=dk,df=df,dik=True)
    for nk in nok2:
        #nkd=kontur(nk,da=da,dk=dk)
        nkd=duzle(nk,da=da,df=df)
        if len(nkd)>2:
            noks.append(nkd)
        # if len(nk)>3:
        #     nkd=duzle(nk,da=da,df=df)
        #     if len(nkd)>3:
        #         nkdd=duzle_uzak(nkd,dk=dk)
        #         if len(nkdd)>2:
        #             noks.append(nkdd)
    if len(noks)<=0:
        noks.append(nok)
    return noks

def cokgenKontrol(nok,da=0.1,df=0.1):
    """Listeler için kendi kendini kesme kontrolü
    kesme varsa kesen parçayı alan kriterine göre ayırır.
    ringler listesi geri döndürür.
    Listelerde son nokta ilk nokta olmamalı!
    da=min açı ölçütü df ayrılacak parçalarda alan ölçütü
    """
    noks=[]
    nok1=kendikes(nok)
    #listdraw(nok1)
    #Ring değişmedi ise
    if len(nok1)==len(nok):
        noks.append(nok)
        return noks
    nok2=kopart(nok1,dk=1.e-8,df=df,dik=False)
    for nk in nok2:
        nkd=duzle(nk,da=da,df=df)
        if len(nkd)>2:
            noks.append(nkd)
    return noks


#YENİ ÇALIŞMA (EKİM 2023 den itibaren)
def R_checkup(ring,da=0.1,df=0.1):
    """Ring objeleri için kendi kendini kesme kontrolü
    kesme varsa kesen parçayı alan kriterine göre ayırır.
    ringler listesi geri döndürür.
    Ringlerde son nokta ilk nokta olmasına göre çalışır.
    da=min açı ölçütü df ayrılacak parçalarda alan ölçütü
    """
    rng=[]
    nok=ring.GetPoints()
    nok.pop(-1)
    nok1=kendikes(nok)
    #listdraw(nok1)
    #Ring değişmedi ise
    if len(nok1)==len(nok):
        rng.append(ring)
        return rng
    nok2=kopart(nok1,dk=1.e-8,df=df,dik=False)
    for nk in nok2:
        nkd=duzle(nk,da=da,df=df)
        if len(nkd)>2:
            rng.append(list2ring(nkd))
    return rng

def R_crop(ring,dk=0.15,da=0.1,df=0.1):
    """Ring objeleri için küçük parçaları kırpar.
    Uzunluk kriterine göre dik iner. Parçaları alan kriterine göre 
    ayırır. 
    Ringlerde son nokta ilk nokta olmasına göre çalışır.
    dk: kenar yakınlık ölçütü 
    da: min açı
    df:min alan
    """
    rng=[]
    nok=ring.GetPoints()
    nok.pop(-1)
    ilknokta(nok,dk=dk)
    nok1=dikin(nok,dk=dk)
    #dikin değişiklik yapmadı ise
    if len(nok1)==len(nok):
        nok2=kopart(nok1,dk=dk,df=df,dik=False)
    else:
        nok2=kopart(nok1,dk=dk,df=df,dik=True)
    for nk in nok2:
        if len(nk)>3:
            nkd=duzle(nk,da=da,df=df)
            if len(nkd)>3:
                nkdd=duzle_uzak(nkd,dk=dk)
                if len(nkdd)>2:
                    rng.append(list2ring(nkdd))
    if len(rng)<=0:
        rng.append(ring)
    return rng
def kendikes(nok):
    "Kendi kendini kesen çokgenlere nokta atar."
    nok2=[]
    n=len(nok)
    for i in range(n):
        ion,isn=oncesonra(i,n)
        nok2.append(nok[i])
        for j in range(n):
            jon,jsn=oncesonra(j,n)
            if i==j:
            #if abs(i-j)<=1 or abs(isn-j)<=1:
                continue
            #print(f"{i}-{isn} <> {j}--{jsn}")
            nkes,ii=line_intersect(nok[i], nok[isn], nok[j], nok[jsn])                
            if ii:
                #print("Ekleniyor")
                nok2.append(nkes) 
    #listdraw(nok2)
    return nok2

def dikin(nok,dk=0.15):
    "Yakın noktalardan dik inme ..."
    nok2=[]
#    nok3=[]
    n=len(nok)
    #Bir kenara diğer noktalardan biri yakın ise dik inip nokta ekleme
    # for i in range(n):
    #     nok2.append(nok[i-1])
    #     for j in range(n):
    #         if i==j or i-1==j:
    #             continue
    #         h,s,ii=dik(nok[i-1], nok[i], nok[j])
    #         if ii and abs(h)<=dk:
    #             k,al=kenar(nok[i-1], nok[i])
    #             anok=ynok2(nok[i-1],nok[i],s,0)
    #             nok2.append(anok)
    for i in range(n):
        ion,isn=oncesonra(i,n)
        nok2.append(nok[i])
        ss=[]
        for j in range(n):
            #i,isn doğrusunun dışında ve devamı olmayan j gerekli
            if abs(i-j)<=1 or abs(isn-j)<=1:
                continue
            h,s,ii=dik(nok[i], nok[isn], nok[j])
            #print(f"{i}--{isn}<{j} {h:>5.2f} {s:>5.2f} {ii}")
            if ii and abs(h)<=dk and abs(s)>dk:
                #print("s eklendi")
                ss.append(s)
        if len(ss)>0:
            ss.sort()
            for jj in range(len(ss)):
                #print(f"{i}--{isn} {si:>5.2f}")
                if jj>0:
                    if abs(ss[jj]-ss[jj-1])<dk/10:
                        continue
                anok=ynok2(nok[i],nok[isn],ss[jj],0)
                nok2.append(anok)
    return nok2            
def ilknokta(nok,dk=0.15):
    """İlk nokta bir başka noktaya dk dan yakınsa 
    sıralamayı değiştirme algoritması...
    komşu ve komşu olmayan noktalara yakınlık ...
    """
    n=len(nok)
    i=0
    ii=0
    while True:
        ykn=False
        for j in range(1,n):
            s,a=kenar(nok[0],nok[j])
            if s<dk:
                nok.append(nok[0])
                nok.pop(0)
                ii+=1
                ykn=True
                break
        if not ykn:
            break
        #Tüm kenarlara bakıp çözüm bulunamadıysa döngüyü kesme
        i+=1
        if i>n:
            break
    i=0
    while True:
        ykn=False
        for j in range(1,n-1):
            h,s,ii=dik(nok[j+1], nok[j], nok[0])
            if ii and abs(h)<dk:
                #print(j)
                nok.append(nok[0])
                nok.pop(0)
                ii+=1
                ykn=True
                break
        if not ykn:
            break        
        #Tüm kenarlara bakıp çözüm bulunamadıysa döngüyü kesme
        i+=1
        if i>n:
            break
    #Kaç defa kaydırma yapıldı ise geri döndür
    return ii                
            
def kopart(nok2,dk=0.15,df=0.02,dik=True):
    #İlk noktada atlama varsa... Bunu çıkartmak gerek. 
    #Bunu dik inmeden önce yapmalı
    #
    n=len(nok2)
    for i in range(1,n):
        s,a=kenar(nok2[0],nok2[i])
        if s<=dk:
            nok2.append(nok2[0])
            nok2.pop(0)
            break
    pnt=[]
    noks=[]
    #Komşu olmayan yakın noktaları tespit ediyoruz
    i=0
    while i<n:
        for j in range(n-1,i+1,-1): 
            # print(i,j)
            s,a=kenar(nok2[i],nok2[j])
            #print(i,j,s)
            if s<=dk:
                pnt.append((i,j))
                i=j
                break
        i+=1
    #listdraw(nok2)
    #print(pnt)
    #Bu noktaların arasını budama
    for p in pnt:
        aln=poly_area(nok2[p[0]:p[1]+1])
        #print(aln,df)
        #Alan min alandan büyük ise kopart
        if abs(aln)>df:
            if dik:
                noks.append(nok2[p[0]:p[1]+1])
            else:
                noks.append(nok2[p[0]:p[1]])
                #print(p)
        if dik:
            for i in range(p[0]+1,p[1]):
                nok2[i]=(nok2[i][0],nok2[i][1],-1)
        else:
            for i in range(p[0]+1,p[1]+1):
                nok2[i]=(nok2[i][0],nok2[i][1],-1)
                #print("--",i)

    nok3=[]
    for nk in nok2:
        #print(*nk)
        if nk[2]>=0:
            nok3.append(nk)
    noks.append(nok3)
    # for ls in noks:
    #     listdraw(ls)
    return noks

def duzle(nok,da=0.1,df=0.1):
    nok2=[]
    for i in range(len(nok)):
        #son nokta ile ilk nokta arasına bakmak için 
        if i<(len(nok)-1):
            ii=i+1
        else:
            ii=0
        k1,a1=kenar(nok[i],nok[i-1])
        if k1<1.e-14:
            nok2.append(nok[i])
            continue
        k2,a2=kenar(nok[i],nok[ii])
        if k2<1.e-14:
            continue
        #print(i,k1,k2)
        d=abs(a2-a1)
        if d<da or abs(d-math.pi)<da:
            f=0.5*k1*k2*math.sin(d)  #;print(f"{i:>2d} {math.degrees(d):>5.2f} {abs(f):>5.2f} {k1:>5.2f} {k2:>5.2f}")
            if abs(f)<df:
                continue
        nok2.append(nok[i])
    return nok2

def duzle_uzak(nok,dk=0.1):
    if len(nok)<1:
        #print("oops",nok)
        return nok
    try:
        nok2=[]
        for i in range(len(nok)):
            k=kenar_oklid(nok[i-1],nok[i])
            if k>dk:
                nok2.append(nok[i])
            else:
                no=nokOrt(nok[i-1],nok[i])
                if len(nok2)>1:
                    nok2[-1]=no
                else:
                    nok2.append(no)
        return nok2
    except:
        #print(i,nok2)
        return nok

def nokOrt(n1,n2):
    return ((n1[0]+n2[0])/2,(n1[1]+n2[1])/2)

#PASİF KODLAR ...
def point_densify(ring,dk):
    """"Çıkıntıları gidermek için nokta sıklaştırma--
    Devre dışı self edit e aktarıldı"""
    nok=ring.GetPoints()
    nok2=[]
    #İlk nokta son nokta ile aynı ise sil. 
    if nokesit(nok[0],nok[-1]):
        nok.pop(-1)    
    for i in range(len(nok)):
        kn,a=kenar(nok[i-1],nok[i])
        nok2.append(nok[i-1])
        #print(i-1)
        if kn<1.e-5:
            continue
        for j in range(len(nok)):
            if i==j:
                continue
            h,s,ii=dik(nok[i-1],nok[i],nok[j])
            #print(i-1,i,j,kn,h)
            if ii and abs(h)<dk and abs(h)>0:
                #print("eklendi")
                p=ynok2(nok[i-1],nok[i],s,0)
                nok2.append(p)
    ring2 = ogr.Geometry(ogr.wkbLinearRing)
    for nk in nok2:
        ring2.AddPoint(*nk)
    ring2.CloseRings()
    return ring2                                  

def erozyon(nok,dk=0.15):
    "Erozyon algoritması üzerinde çalışılacak... Henüz olgunlaşmadı"
    nok2=[]
    n=len(nok)
    #Bir kenara diğer noktalardan biri yakın ise dik inip nokta ekleme
    i=0
    smin=1e6
    jj=-1
    while i<n:
        print(i)
        ion,isn=oncesonra(i,n)
        nok2.append(nok[i])
        for j in range(n-1,i,-1):
            print(i,isn,j)
            h,s,ii=dik(nok[i], nok[isn], nok[j])
            if ii and abs(h)<=dk:
                if s<smin:
                    smin=s
                    hh=h
                    jj=j
        print(">>",jj)
        if jj>-1:
            k,al=kenar(nok[i], nok[isn])
            anok=ynok2(nok[i],nok[isn],smin,0)
            nok2.append(anok)
            #print("burada",smin,hh)
            i=jj
            jj=-1
            smin=1e6
        else:
            i+=1
        
    return nok2

def geom2list(geom):
    """QGS poligon geometrisinden noktaları elde etmek için ...
    geom.vertices() tüm verteksleri veriyor. Geometrinin çoklu olması
    her birinin dış ve iç halkaları olması sözkonusu
    
    Bu nedenle değişiklik yapıldı
    -Çoklu poligonun ilki dikkate alındı.
    -Poligonun dış ring ve iç ringleri iki boyutlu list haline getirildi. 
     Birden fazla ring varsa ilki dış 
    lst=[]
    for nk in geom.vertices():
        lst.append((nk.x(),nk.y(),0))
    """
    lst=[]
    if geom.isMultipart():
        plgn = geom.asMultiPolygon()[0]  #Çoklu geometrinin ilk poligonu
    else: 
        plgn = geom.asPolygon()
    for ring in plgn:                    #Poligonun ringleri (ilki dış)
        lst.append([(p.x(),p.y(),0) for p in ring])
    return lst   


"""Bu dosya modül olarak düşünüldü aşağıda bazı testler var.
Koordinatlar gerçek değil. Varsayımsal noktalar"""
if __name__=="__main__":
    pass
