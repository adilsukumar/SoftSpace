"""Exact CAD section curves through one locking pin, not an image edit."""
import sys,json,os
os.environ['OPENBLAS_NUM_THREADS']='1'
from audit_v12_ocp import P,O,cad,recipes,load,moved,gp_Pnt,gp_Dir
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
row=next(r for r in cad['sizes'] if r['size']=='adult_small');parts,_=load(row);R=recipes[row['size']]['band_halfspan_mm'];fig,axes=plt.subplots(2,1,figsize=(10,5.8),sharex=True,sharey=True)
for panel,ax in enumerate(axes):
 for name,color in [('RightFork','#41667b'),('RightTongue','#218c69'),('RightLockPin','#ca770f')]:
  s=moved(parts[name],(0,-6,0)) if panel and name=='RightLockPin' else parts[name];sec=BRepAlgoAPI_Section(s,gp_Pln(gp_Pnt(R+10,0,60),gp_Dir(1,0,0)),False);sec.Build();assert sec.IsDone();e=TopExp_Explorer(sec.Shape(),TopAbs_EDGE);first=True
  while e.More():
   cv=BRepAdaptor_Curve(TopoDS.Edge_s(e.Current()));points=[cv.Value(float(t)) for t in np.linspace(cv.FirstParameter(),cv.LastParameter(),35)];ax.plot([p.Y() for p in points],[p.Z() for p in points],color=color,lw=2,label=name.replace('Right','') if first else None);first=False;e.Next()
 ax.set_xlim(-43,-3);ax.set_ylim(54,66);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_title('Pin engaged' if not panel else 'Pin released by 6 mm',loc='left',fontsize=11);ax.set_ylabel('Z mm')
axes[0].legend(loc='upper right',bbox_to_anchor=(1,1.22),ncol=3,fontsize=9,framealpha=.95);axes[1].set_xlabel('Y mm   Release moves to the left')
fig.suptitle('Section through the V12 captive pin',fontsize=15)
fig.text(.5,.015,'Actual saved CAD section. The integral housing still needs a defined assembly and servicing process.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.045,1,.94));f=P/'documents'/'images'/'V12_lock_section.png';fig.savefig(f,dpi=180,facecolor='white');plt.close(fig)
(O/'section_image_sources.json').write_text(json.dumps({'image':str(f),'source':row['file'],'source_sha256':row['sha256'],'plane_x_mm':R+10,'released_transform':'pin minus6Y','scope':'CAD section curves; no actual coil, threads or assembly cap'},indent=2));print(f)
