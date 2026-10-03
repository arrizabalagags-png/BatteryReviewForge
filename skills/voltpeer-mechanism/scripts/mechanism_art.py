# -*- coding: utf-8 -*-
"""Original native SVG scenes rebuilt from VoltPeer's own imagegen composition.

All materials, domains, ligand counts and paths are schematic. No publication
pixels, image elements, copied geometries or chemical ball-and-stick models.
"""
from __future__ import annotations
import json
import math
import random
from html import escape

WIDTH, HEIGHT = 1600, 1050
ART_VERSION = "1.1.1"

class Scene:
    def __init__(self, record, colors, background, cation="Li+"):
        self.record, self.colors, self.cation = record, colors, cation
        self.parts=[]
        self.defs=[]
        self.serial=0
        if background=="white": self.parts.append('<rect id="background" width="1600" height="1050" fill="#FFFFFF"/>')
        for key, color in [("ion",colors[0]),("electron",colors[1]),("domain",colors[2]),("matrix",colors[3])]:
            self.defs.append(f'<radialGradient id="{key}-sphere" cx="30%" cy="24%" r="78%"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".24" stop-color="{color}" stop-opacity=".62"/><stop offset=".65" stop-color="{color}"/><stop offset="1" stop-color="#263A43"/></radialGradient>')
            self.defs.append(f'<linearGradient id="{key}-material" x1="0" y1="0" x2=".3" y2="1"><stop offset="0" stop-color="{color}" stop-opacity=".15"/><stop offset=".56" stop-color="{color}" stop-opacity=".3"/><stop offset="1" stop-color="{color}" stop-opacity=".52"/></linearGradient>')
            # Fixed-size open tips stay subordinate to ions and material layers.
            # The tip point is anchored at the scientific path endpoint.
            self.defs.append(f'<marker id="{key}-arrow" markerUnits="userSpaceOnUse" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="10" markerHeight="10" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker>')
        self.defs.extend([
            '<radialGradient id="metal-sphere" cx="30%" cy="24%" r="78%"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".28" stop-color="#D6DDE1"/><stop offset=".68" stop-color="#A5AFB6"/><stop offset="1" stop-color="#636F79"/></radialGradient>',
            '<linearGradient id="metal-front" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#E4E9EC"/><stop offset=".6" stop-color="#BFC9CF"/><stop offset="1" stop-color="#A5B0B8"/></linearGradient>',
            '<linearGradient id="metal-side" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#C2CCD2"/><stop offset="1" stop-color="#84939E"/></linearGradient>',
            '<linearGradient id="metal-top" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#EBF0F2"/><stop offset="1" stop-color="#B8C4CC"/></linearGradient>',
        ])
    def group(self,name,transform=None):
        self.parts.append(f'<g id="{escape(name)}"'+(f' transform="{transform}"' if transform else '')+'>')
    def end(self): self.parts.append('</g>')
    def path(self,d,fill="none",stroke=None,width=2,opacity=1,dash=None,marker=None):
        if marker: width = min(width, 2.5)
        attrs=f'fill="{fill}" opacity="{opacity:g}"'
        if stroke: attrs+=f' stroke="{stroke}" stroke-width="{width:g}" stroke-linecap="round" stroke-linejoin="round"'
        if dash: attrs+=f' stroke-dasharray="{dash}"'
        if marker: attrs+=f' marker-end="url(#{marker}-arrow)"'
        self.parts.append(f'<path d="{d}" {attrs}/>')
    def polygon(self,points,fill,stroke=None,opacity=1):
        self.path('M'+' L'.join(f'{x:g},{y:g}' for x,y in points)+' Z',fill,stroke,1.5,opacity)
    def sphere(self,x,y,r=25,kind="ion",opacity=1):
        self.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="url(#{kind}-sphere)" opacity="{opacity:g}" stroke="#FFFFFF" stroke-opacity=".68" stroke-width="1.5"/>')
    def text(self,x,y,label,size=34,anchor="start",color="#243543",weight=400):
        self.parts.append(f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{escape(label)}</text>')
    def charge(self,x,y,positive=True,r=26,kind=None):
        self.sphere(x,y,r,kind or ("ion" if positive else "domain"))
        # Charges remain separate editable ASCII glyphs in all render engines.
        self.text(x,y+r*.32,"+" if positive else "−",r*.9,"middle","#FFFFFF",500)
    def arrow(self,d,kind="ion",width=2.5,dashed=False,opacity=1):
        self.path(d,stroke=self.colors[{'ion':0,'electron':1,'domain':2}[kind]],width=min(width,2.5),marker=kind,dash="7 7" if dashed else None,opacity=opacity)
    def ligand(self,x,y,angle=0,scale=1,opacity=1):
        """Explicit generic donor glyph: no apparent atom bonds or molecule."""
        self.serial+=1
        self.group(f'generic-donor-{self.serial}',f'translate({x:g} {y:g}) rotate({angle:g}) scale({scale:g})')
        self.path('M-13 -22 Q-33 -40 -47 -18 Q-63 5 -45 25 Q-28 43 -12 25',fill='url(#matrix-material)',stroke=self.colors[3],width=2,opacity=opacity)
        self.parts.append(f'<circle cx="0" cy="0" r="15" fill="#FFFFFF" stroke="{self.colors[3]}" stroke-width="2" opacity="{opacity}"/>')
        self.parts.append(f'<g transform="rotate({-angle:g})">')
        self.text(0,8,'D',24,'middle','#243543',500)
        self.end()
        self.end()
    def shell(self,x,y,n=4,radius=88,rotation=0,ion_r=28):
        self.group(f'coordination-{self.serial}')
        for i in range(n):
            a=math.radians(rotation+360*i/n)
            xx,yy=x+radius*math.cos(a),y+radius*math.sin(a)
            self.path(f'M{x+ion_r*math.cos(a):g} {y+ion_r*math.sin(a):g} L{xx-17*math.cos(a):g} {yy-17*math.sin(a):g}',stroke=self.colors[0],width=2,opacity=.55,dash='7 7')
            self.ligand(xx,yy,math.degrees(a)+180)
        self.charge(x,y,r=ion_r)
        self.end()
    def leader(self,x,y,x2,y2,label,anchor='start'):
        self.path(f'M{x:g} {y:g} L{x2:g} {y2:g}',stroke='#52626E',width=1.7)
        self.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="3" fill="#52626E"/>')
        self.text(x2+(12 if anchor=='start' else -12),y2+10,label,32,anchor)
    def metal(self,transform=None,atoms=True):
        self.group('metal-'+str(self.serial),transform)
        front=[(85,670),(1235,800),(1235,990),(85,860)]
        side=[(1235,800),(1435,595),(1435,780),(1235,990)]
        top=[(85,670),(280,475),(1435,595),(1235,800)]
        self.polygon(front,'url(#metal-front)','#8E9FA9')
        self.polygon(side,'url(#metal-side)','#8E9FA9')
        self.polygon(top,'url(#metal-top)','#97A7B0')
        if atoms:
            for row in range(3):
                for i in range(34):
                    x=110+i*33+(row%2)*16
                    y=664+(x-85)*130/1150+row*24
                    if x<1225:self.sphere(x,y,17,'metal')
            for row in range(3):
                for i in range(6):
                    x=1251+i*29;y=795-i*30+row*26
                    self.sphere(x,y,17,'metal')
        self.end()
    def interphase(self,solid=False,crack=False,transform=None):
        self.serial+=1
        suffix=str(self.serial)
        top='M85 530 Q185 538 280 340 L1435 460 Q1442 520 1235 660 L85 530 Z'
        front='M85 530 Q185 515 310 552 T570 581 T830 610 T1090 642 L1235 660 L1235 790 Q1130 784 1020 763 T780 738 T530 706 T300 681 L85 665 Z'
        side='M1235 660 Q1380 553 1435 460 L1435 590 L1235 790 Z'
        self.defs.append(f'<clipPath id="interphase-front-{suffix}"><path d="{front}"/></clipPath>')
        self.defs.append(f'<clipPath id="interphase-top-{suffix}"><path d="{top}"/></clipPath>')
        self.group(('solid-electrolyte-' if solid else 'interphase-')+suffix,transform)
        self.path(top,fill='url(#matrix-material)',stroke='#A7C6CB',width=2)
        self.path(front,fill='url(#matrix-material)',stroke='#91B7BD',width=2)
        self.path(side,fill='url(#matrix-material)',stroke='#8EADB4',width=2)
        rng=random.Random(9021)
        if not solid:
            for face,count in [('front',23),('top',32)]:
                self.parts.append(f'<g clip-path="url(#interphase-{face}-{suffix})">')
                for i in range(count):
                    x=rng.uniform(80,1450); y=rng.uniform(545,805) if face=='front' else rng.uniform(340,662)
                    rx=rng.uniform(24,68); ry=rng.uniform(23,47) if face=='front' else rng.uniform(12,29)
                    pts=[(x+rx*math.cos(j*math.pi/3)*rng.uniform(.75,1.1),y+ry*math.sin(j*math.pi/3)*rng.uniform(.75,1.1)) for j in range(6)]
                    self.polygon(pts,'url(#domain-material)',self.colors[2],.54)
                    self.path(f'M{x-rx*.4:g} {y-ry*.45:g} L{x:g} {y:g} L{x+rx*.65:g} {y-ry*.25:g}',stroke='#FFFFFF',width=1,opacity=.4)
                self.end()
            # A few continuous matrix contours provide restrained material depth.
            for i in range(4):
                y=563+i*25
                self.path(f'M110 {y} Q270 {y-16} 445 {y+36} T810 {y+76} T1190 {y+115}',stroke='#FFFFFF',width=1.3,opacity=.45)
        else:
            for x,y in [(400,430),(695,470),(970,535),(1140,580)]:
                self.path(f'M{x} {y} l50 -20 l60 40 l-20 30',stroke=self.colors[2],width=2,opacity=.28)
        if crack:self.path('M720 588L699 611L734 638L709 663L739 737',stroke='#FFFFFF',width=23)
        self.end()
    def footer(self,label='D = generic donor ligand; geometry and counts are illustrative'):
        self.text(82,1024,label,24,color='#5E6E78')
    def finish(self):
        description=self.record[5]+' '+self.record[7]+' Generic D ligands are abstract symbols, not molecular structures. Repeated ions may show successive snapshots of one transport event; arrows and material dimensions are not measurements.'
        meta={'license':'MIT','version':ART_VERSION,'template':self.record[0],'native_geometry':True,'raster_embedded':False,'source_figures_reused':False,'composition_reference':'VoltPeer original imagegen draft 2026-10-03','evidence':'conceptual artwork; literature supports listed relations only','arrow_style':'fixed 10px open chevron; process stroke <=2.5px; endpoints preserve scientific relations'}
        return '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1050" viewBox="0 0 1600 1050" role="img" aria-labelledby="figure-title figure-description"><title id="figure-title">'+escape(self.record[2])+'</title><desc id="figure-description">'+escape(description)+'</desc><metadata>'+escape(json.dumps(meta))+'</metadata><defs>'+''.join(self.defs)+'</defs><g font-family="Arial, Helvetica, sans-serif">'+''.join(self.parts)+'</g></svg>\n'

def illustrate(record,colors,background='white',cation='Li+'):
    s=Scene(record,colors,background,cation)
    key=record[0]
    if key in {'solvation-shell','ion-pairing','ligand-exchange'}:
        if key=='solvation-shell':
            s.shell(690,460,4,215,32,55)
            for x,y,a in [(300,300,20),(1110,360,-30),(1030,755,80),(310,770,20)]:s.ligand(x,y,a,1.35,.5)
            s.charge(1285,620,False,45)
            s.leader(735,424,935,195,cation.replace('+','')+' ion')
            s.leader(872,574,1120,780,'Generic donor ligand')
            s.text(695,916,'Illustrative coordination environment',36,'middle')
        elif key=='ion-pairing':
            for x,title in [(290,'SSIP'),(790,'CIP'),(1300,'AGG')]:s.text(x,185,title,40,'middle',weight=500)
            s.shell(240,460,4,125,35,36);s.charge(451,474,False,35)
            s.shell(725,460,3,125,50,36);s.charge(800,487,False,36)
            for x,y,pos in [(1210,424,True),(1280,460,False),(1350,425,True),(1296,533,True),(1390,522,False)]:s.charge(x,y,pos,31)
            for x,y,a in [(1153,380,10),(1360,337,100),(1430,590,160),(1220,600,-90)]:s.ligand(x,y,a)
            s.path('M1235 436L1257 450M1309 449L1324 436M1300 505L1300 485M1322 534L1361 526',stroke=colors[0],width=2,opacity=.45,dash='6 7')
            for x,label in [(290,'Solvent-separated'),(790,'Direct ion association'),(1300,'Connected ionic motif')]:s.text(x,735,label,31,'middle')
            s.text(800,862,'Motifs shown separately; no population fraction is assumed',26,'middle',color='#5E6E78')
        else:
            for x,n,title in [(270,4,'Initial environment'),(790,3,'Ligand departure'),(1315,4,'New coordination')]:
                s.shell(x,505,n,130,35,38);s.text(x,772,title,31,'middle')
            s.arrow('M410 505C495 485 535 485 627 505',width=2.5)
            s.arrow('M925 505C1010 485 1060 485 1155 505',width=2.5)
            s.ligand(785,255,270);s.arrow('M795 340Q815 307 807 282',width=2.5,dashed=True)
            s.ligand(1315,255,90);s.arrow('M1315 282Q1297 328 1305 367',width=2.5,dashed=True)
            s.text(800,880,'Exchange sequence is conceptual; rates are not assigned',26,'middle',color='#5E6E78')
        s.footer()
    elif key=='migration-diffusion':
        for x,title in [(45,'Electric-field-driven migration'),(850,'Concentration-driven diffusion')]:
            s.group('electrolyte-volume-'+str(x))
            s.polygon([(x+20,370),(x+530,422),(x+690,277),(x+180,230)],'url(#matrix-material)','#B4CFD2')
            s.polygon([(x+20,370),(x+530,422),(x+530,740),(x+20,688)],'url(#matrix-material)','#B4CFD2')
            s.polygon([(x+530,422),(x+690,277),(x+690,596),(x+530,740)],'url(#matrix-material)','#B4CFD2')
            s.text(x+340,160,title,31,'middle',weight=500)
            s.end()
        s.path('M162 276L527 313',stroke='#536579',width=3,marker='domain');s.text(358,242,'E',30,'middle')
        s.charge(165,475,r=36);s.arrow('M215 483L555 516',width=2.5)
        s.charge(555,625,False,36);s.arrow('M500 620L167 585',kind='domain',width=2.5)
        for x,y in [(910,444),(985,473),(924,538),(1006,580),(916,639),(1402,533),(1400,645)]:s.charge(x,y,r=26)
        s.arrow('M1100 555L1321 579',width=2.5)
        s.text(1130,835,'higher → lower concentration',29,'middle')
        s.text(370,835,'Cation and anion drift oppose each other',27,'middle')
        s.footer('Directions are schematic; arrow lengths do not specify flux')
    elif key in {'plating-stripping','film-reformation'}:
        for i,title in enumerate(['Plating','Stripping'] if key=='plating-stripping' else ['Fresh surface exposed','Further interphase formation']):
            x=40+i*800
            transform=f'translate({x} 220) scale(.48 .65)'
            s.metal(transform);s.interphase(crack=key=='film-reformation',transform=transform)
            s.text(x+360,150,title,34,'middle',weight=500)
            if key=='plating-stripping':
                s.shell(x+370,333,2,64,25,25)
                if i==0:
                    s.arrow(f'M{x+370} 371Q{x+389} 570 {x+470} 700',dashed=True)
                    s.arrow(f'M{x+337} 818Q{x+428} 805 {x+470} 719',kind='electron')
                    s.text(x+360,960,'Li+ + e− → Li⁰',31,'middle')
                else:
                    s.arrow(f'M{x+470} 704Q{x+384} 610 {x+370} 378',dashed=True)
                    s.arrow(f'M{x+466} 730Q{x+417} 814 {x+325} 823',kind='electron')
                    s.text(x+360,960,'Li⁰ → Li+ + e−',31,'middle')
            else:
                s.ligand(x+370,337,270)
                s.arrow(f'M{x+370} 380Q{x+380} 513 {x+387} 638',dashed=True)
                if i:
                    s.path(f'M{x+374} 632q34 -17 30 39l-21 30l-20 -28Z',fill='url(#domain-material)',stroke=colors[2],width=2)
        s.footer('Schematic snapshots; reversibility, repair and reaction rates require evidence')
    elif key=='dual-pathways':
        s.polygon([(95,705),(1240,850),(1450,500),(312,363)],'url(#matrix-material)','#B5D1D4')
        s.polygon([(95,705),(1240,850),(1240,970),(95,825)],'url(#matrix-material)','#B5D1D4')
        s.group('electronic-network')
        s.path('M155 750L397 597L706 685L970 482L1320 600',stroke=colors[1],width=22,opacity=.32)
        s.path('M155 750L397 597L706 685L970 482L1320 600',stroke=colors[1],width=9)
        s.end()
        for x,y,r in [(390,545,100),(715,634,105),(995,441,97),(1285,573,80)]:s.sphere(x,y,r,'metal')
        for x,y in [(325,250),(705,304),(1050,240)]:s.charge(x,y,r=26)
        s.arrow('M325 281Q265 390 326 472',dashed=True)
        s.arrow('M705 336Q780 430 750 531',dashed=True)
        s.arrow('M1050 273Q1120 333 1070 383',dashed=True)
        s.arrow('M182 734L285 668',kind='electron')
        s.leader(731,690,660,904,'Electronic network','end')
        s.leader(778,461,1005,187,'Ion access through electrolyte')
        s.leader(389,530,234,272,'Active particle','end')
        s.footer('Conceptual network; separate ionic and electronic conductivity need measurement')
    elif key=='solid-contact-loss':
        # Independently generated solid-contact composition; a thick solid, no SEI.
        s.polygon([(130,330),(1438,240),(1270,112),(42,215)],'url(#matrix-material)','#A7C2CB')
        s.polygon([(42,215),(130,330),(130,665),(42,541)],'url(#matrix-material)','#A7C2CB')
        solid='M130 330L1438 240L1438 541Q1362 524 1290 554T1160 568Q1124 574 1100 578Q1065 580 1005 577T735 601Q620 617 562 615Q547 608 526 618Q483 650 404 632Q271 613 130 665Z'
        s.path(solid,fill='url(#matrix-material)',stroke='#A7C2CB',width=2)
        metal='M130 665Q282 671 402 674Q470 675 526 625Q549 608 566 624Q620 667 731 644T1006 626Q1065 621 1100 580Q1121 571 1153 602Q1220 640 1300 603Q1372 575 1438 566L1438 844L130 952Z'
        s.path(metal,fill='url(#metal-front)',stroke='#8E9FA9',width=2)
        s.polygon([(42,541),(130,665),(130,952),(42,819)],'url(#metal-side)','#8E9FA9')
        for row in range(2):
            for i in range(9):s.sphere(61+row*24,564+i*28+row*24,16,'metal')
        for x,y in [(550,616),(1100,580)]:
            s.arrow(f'M{x} {y-18}Q{x+17} {y-85} {x+19} {y-180}',width=2.5)
            for dy in (209,256,301):s.charge(x+19+(8 if dy==256 else 0),y-dy,r=18)
        s.arrow('M540 642Q532 739 279 771',kind='electron',width=2.5)
        s.arrow('M1110 606Q1129 688 1332 713',kind='electron',width=2.5)
        s.leader(815,626,830,710,'Void')
        s.leader(1100,580,1260,473,'Remaining contact')
        s.text(186,419,'Solid electrolyte',34)
        s.text(188,901,'Li metal',34)
        s.text(495,255,'Li+',31)
        s.text(1060,221,'Li+',31)
        s.text(369,816,'e−',31,color=colors[1])
        s.text(1215,764,'e−',31,color=colors[1])
        s.footer('Stripping snapshots; Li/Li6PS5Cl evidence is condition-specific; dimensions are schematic')
    else:
        s.metal(atoms=key!='cei-formation')
        if key not in {'nucleation-growth','double-layer'}:s.interphase()
        if key=='double-layer':
            # A fluid volume, without SEI domains; ions describe an EDL here.
            s.polygon([(85,430),(280,235),(1435,355),(1235,660)],'url(#matrix-material)',opacity=.35)
            s.polygon([(85,430),(1235,660),(1235,790),(85,665)],'url(#matrix-material)',opacity=.35)
        if key=='desolvation':
            s.shell(330,230,4,105,33,31);s.shell(743,305,2,79,20,28)
            s.arrow('M377 261C448 245 487 322 613 325',width=2.5)
            s.ligand(823,145,115);s.ligand(955,273,145)
            s.arrow('M790 246Q811 206 816 174',width=2.5,dashed=True,opacity=.6)
            s.arrow('M806 310Q861 294 915 281',width=2.5,dashed=True,opacity=.6)
            s.arrow('M756 343Q783 394 835 447',width=2.5)
            s.charge(851,469,r=25)
            s.arrow('M862 503Q900 563 946 587T1020 748',dashed=True,width=2.5)
            s.charge(963,645,r=24)
            s.arrow('M883 902Q981 889 1017 799',kind='electron',width=2.5)
            s.sphere(1030,776,25,'metal')
            s.text(1016,755,'0',18,'middle',color='#324854')
            s.charge(168,416,False,37);s.charge(1273,287,False,37)
            s.leader(304,220,281,120,'Li+','end')
            s.leader(879,910,808,943,'e−','end')
        elif key=='double-layer':
            for x,y in [(210,613),(426,641),(647,666),(860,692),(1072,717)]:
                s.charge(x,y,r=32);s.text(x,y+77,'−',29,'middle',color='#50616D')
            for x,y in [(250,252),(730,212),(1240,286)]:s.charge(x,y,False,34)
            for x,y,a in [(310,398,35),(610,424,80),(985,510,140)]:s.ligand(x,y,a)
            s.text(520,175,'Counterion enrichment',35,'middle')
            s.footer('Illustrative EDL; positions, charge density and distances are not quantitative')
        elif key in {'selective-passivation','heterogeneous-sei'}:
            for i,(x,y) in enumerate([(330,283),(710,344),(1080,395)]):
                s.shell(x,y,2,59,30,26)
                s.arrow(f'M{x+12} {y+50}Q{x+35} {y+170} {x+97} {y+248}T{x+121} {690+i*46}',dashed=True,width=2.5)
            s.arrow('M955 906Q1010 875 1016 795',kind='electron',width=2.5)
            if key=='selective-passivation':
                s.path('M991 785L1038 817M1035 785L990 817',stroke=colors[1],width=5)
                s.leader(1017,801,1175,882,'Electron restriction')
            else:s.text(824,180,'Possible local ion routes',34,'middle')
            s.footer('Dashed paths are proposed routes; domain identity and conductivity need evidence')
        elif key in {'sei-formation','cei-formation'}:
            for x,y in [(335,250),(737,313),(1100,341)]:s.ligand(x,y,90,1.1)
            for i,(x,y) in enumerate([(360,712),(738,758),(1100,799)]):
                if key=='sei-formation':s.arrow(f'M{x-72} {y+101}Q{x-22} {y+80} {x} {y+6}',kind='electron',width=2.5)
                else:s.arrow(f'M{x} {y+3}Q{x+10} {y+65} {x+87} {y+100}',kind='electron',width=2.5)
                s.path(f'M{x-35} {y-19}q35 -32 67 2l-9 31l-57 -6Z',fill='url(#domain-material)',stroke=colors[2],width=2)
            s.text(770,166,'Electrolyte reduction' if key=='sei-formation' else 'Electrolyte oxidation',36,'middle')
            if key=='cei-formation':s.text(715,941,'Positive electrode',34,'middle')
            s.footer('Interphase products are generic; no specific composition or protective effect is assigned')
        elif key=='nucleation-growth':
            for x,y,r in [(290,608,23),(560,641,42),(870,678,68),(1150,711,92)]:
                # Hemisphere in contact with its substrate, not a floating ball.
                s.path(f'M{x-r} {y}C{x-r} {y-r*1.3} {x+r} {y-r*1.3} {x+r} {y}Q{x} {y+r*.28} {x-r} {y}Z',fill='url(#metal-sphere)',stroke='#FFFFFF',width=1.5)
                s.path(f'M{x-r} {y}Q{x} {y-r*.15} {x+r} {y}',stroke='#8799A4',width=1,opacity=.5)
                s.shell(x,y-270,2,66,10,26)
                s.arrow(f'M{x} {y-226}L{x} {y-r-13}',width=2.5)
            s.text(770,174,'Illustrative nucleation and growth',36,'middle')
            s.path('M257 891L1175 994',stroke='#52626E',width=2,marker='domain')
            s.footer('Sizes and shapes are conceptual; no nucleation barrier or growth rate is specified')
        elif key=='inactive-lithium':
            # The Li0 island is disconnected from the metal by the interphase.
            s.sphere(497,618,48,'metal');s.text(497,629,'Li⁰',31,'middle')
            s.path('M490 671L496 723',stroke=colors[1],width=3,dash='8 10')
            s.path('M478 683L516 708M512 680L482 712',stroke=colors[1],width=4)
            s.leader(458,602,250,312,'Isolated metal','end')
            for x,y in [(845,541),(928,573),(1100,586)]:s.text(x,y,'Li+',27,'middle',color=colors[2])
            s.leader(1028,574,1165,339,'Li bound in SEI')
            s.footer('Inventory classes require chemical quantification; morphology alone cannot separate them')
        elif key=='solid-contact-loss':
            for x,y,r in [(270,676,60),(603,714,82),(1077,766,69)]:
                s.path(f'M{x-r} {y}Q{x-r*.5} {y-40} {x} {y-33}Q{x+r*.8} {y-25} {x+r} {y+6}Q{x} {y+31} {x-r} {y}Z',fill='#FFFFFF',stroke='#7D909B',width=2)
            for x,y in [(448,700),(850,744)]:s.arrow(f'M{x} {y+91}L{x} {y-29}',width=2.5)
            s.leader(274,680,149,819,'Void','end')
            s.leader(850,742,1100,866,'Remaining contact')
            s.text(890,225,'Stripping at a solid interface',34,'middle')
            s.footer('Li/Li6PS5Cl evidence is condition-specific; pressure and protocol affect contact loss')
        if key not in {'double-layer','cei-formation','nucleation-growth'}:
            s.leader(1348,610,1490,378,'Solid electrolyte' if key=='solid-contact-loss' else 'SEI','end')
            s.leader(1373,792,1490,992,'Li metal','end')
        if key=='nucleation-growth':s.leader(1373,792,1490,992,'Metal substrate','end')
        if key=='desolvation':
            s.leader(1160,163,1305,93,'Electrolyte')
            s.footer('D = generic donor ligand; repeated ions are snapshots; sizes and paths are schematic')
        elif key not in {'double-layer','selective-passivation','heterogeneous-sei','sei-formation','cei-formation','nucleation-growth','inactive-lithium','solid-contact-loss'}:s.footer()
    return s.finish()
