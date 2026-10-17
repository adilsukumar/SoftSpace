"""Actual section of the pilot plus explicitly dimensioned thread allocation."""
import sys,json,os
os.environ['OPENBLAS_NUM_THREADS']='1'
from audit_v14_motion import P,recipes,load,gp_Pnt,gp_Dir
O=P/'engineering-v15-results';sys.path.insert(0,str(P/'solver-libraries'))
import numpy as np,matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
from OCP.gp import gp_Pln
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
row=json.loads((O/'adult_small_retention_cad.json').read_text());parts,_=load(row);R=recipes['adult_small']['band_halfspan_mm'];fig,ax=plt.subplots(figsize=(11,5.5))
for name,color in [('RightFork','#41667b'),('RightServiceCap','#218c69'),('RightLockPin','#ca770f'),('RightPullKnob','#a369b4'),('RightReleaseJamNut','#c45555')]:
 sec=BRepAlgoAPI_Section(parts[name],gp_Pln(gp_Pnt(R+10,0,60),gp_Dir(1,0,0)),False);sec.Build();assert sec.IsDone();e=TopExp_Explorer(sec.Shape(),TopAbs_EDGE);first=True
 while e.More():
  cv=BRepAdaptor_Curve(TopoDS.Edge_s(e.Current()));points=[cv.Value(float(t)) for t in np.linspace(cv.FirstParameter(),cv.LastParameter(),35)];ax.plot([p.Y() for p in points],[p.Z() for p in points],color=color,lw=2,label=name.replace('Right','') if first else None);first=False;e.Next()
ax.set_xlim(-43,-9);ax.set_ylim(52,69);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('Y mm');ax.set_ylabel('Z mm')
ax.annotate('Metal knob with 3 mm thread allocation',xy=(-38.3,64),xytext=(-42,67),fontsize=10,arrowprops={'arrowstyle':'->'},bbox={'facecolor':'white','edgecolor':'none','alpha':.95,'pad':2})
ax.annotate('Separate M2 jam nut',xy=(-36,62),xytext=(-31,66),fontsize=10,arrowprops={'arrowstyle':'->'},bbox={'facecolor':'white','edgecolor':'none','alpha':.95,'pad':2})
ax.annotate('0.4 mm nominal gap to cap',xy=(-34.2,61.5),xytext=(-29,56),fontsize=10,arrowprops={'arrowstyle':'->'},bbox={'facecolor':'white','edgecolor':'none','alpha':.95,'pad':2})
fig.suptitle('V15 threaded knob and jam nut candidate',fontsize=16);fig.legend(*ax.get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.91),ncol=5,frameon=False,fontsize=9)
fig.text(.5,.025,'Actual CAD section. M2 x 0.4 callout defines intended threads; helices, flank contact and manufacturing tolerances are not modelled.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.07,1,.84));f=P/'documents/images/V15_retention_section.png';fig.savefig(f,dpi=160,facecolor='white');plt.close(fig)
(O/'section_image_sources.json').write_text(json.dumps({'image':str(f),'source':row['file'],'source_sha256':row['sha256'],'scope':'Exact section of adult-small pilot; cosmetic thread envelopes only'},indent=2));print(f)
