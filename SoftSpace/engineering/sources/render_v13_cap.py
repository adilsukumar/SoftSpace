"""Exact CAD section curves through one locking pin, not an image edit."""
import sys,json,os
os.environ['OPENBLAS_NUM_THREADS']='1'
from audit_v13_motion import P,O,cad,recipes,load,moved,gp_Pnt,gp_Dir
sys.path.insert(0,str(P/'solver-libraries'))
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from OCP.gp import gp_Pln
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
row=next(r for r in cad['sizes'] if r['size']=='adult_small');parts,_=load(row);R=recipes[row['size']]['band_halfspan_mm'];fig,axes=plt.subplots(1,2,figsize=(11,6),sharex=False,sharey=True)
for panel,ax in enumerate(axes):
 for name,color in [('RightFork','#41667b'),('RightServiceCap','#218c69'),('RightCapBolt1','#ca770f'),('RightCapBolt2','#ca770f'),('RightCapNut1','#a369b4'),('RightCapNut2','#a369b4')]:
  s=moved(parts[name],(8,0,0)) if panel and name=='RightServiceCap' else moved(parts[name],(14,0,0)) if panel and 'CapBolt' in name else parts[name];sec=BRepAlgoAPI_Section(s,gp_Pln(gp_Pnt(0,-26,60),gp_Dir(0,1,0)),False);sec.Build();assert sec.IsDone();e=TopExp_Explorer(sec.Shape(),TopAbs_EDGE);first=True
  while e.More():
   cv=BRepAdaptor_Curve(TopoDS.Edge_s(e.Current()));points=[cv.Value(float(t)) for t in np.linspace(cv.FirstParameter(),cv.LastParameter(),35)];ax.plot([p.X()-R for p in points],[p.Z() for p in points],color=color,lw=2,label=name.replace('Right','') if first else None);first=False;e.Next()
 ax.set_xlim(4,32);ax.set_ylim(50,70);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_title('Assembled section at the cap screws' if not panel else 'Exploded cap and screws',loc='left',fontsize=11);ax.set_ylabel('Z mm')
axes[0].legend(loc='upper left',bbox_to_anchor=(0,-.15),ncol=2,fontsize=8,framealpha=.95)
for ax in axes:ax.set_xlabel('X relative to band half span mm')
fig.suptitle('V13 removable cap and nominal screw envelopes',fontsize=15)
fig.text(.5,.015,'Actual CAD sections at Y minus26mm. Exploded offsets are for display. Threads and an actual coil are not modelled.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.12,1,.94));f=P/'documents'/'images'/'V13_cap_section.png';fig.savefig(f,dpi=180,facecolor='white');plt.close(fig)
(O/'section_image_sources.json').write_text(json.dumps({'image':str(f),'source':row['file'],'source_sha256':row['sha256'],'section_y_mm':-26,'display_offsets_mm':{'cap':8,'bolts':14},'scope':'Actual CAD section, nominal hardware, no threads or real assembly trial'},indent=2));print(f)
