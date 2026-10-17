import os,json,sys
os.environ['OPENBLAS_NUM_THREADS']='1'
from audit_v14_motion import P,load,recipes,gp_Pnt,gp_Dir
sys.path.insert(0,str(P/'solver-libraries'));import numpy as np,matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
from OCP.gp import gp_Pln
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
O=P/'engineering-v16-results';selected=json.loads((O/'selected_candidates.json').read_text());fig,axes=plt.subplots(2,1,figsize=(10,6.2))
for ax,size in zip(axes,['child_large','adult_small']):
 row=next(r for r in selected['sizes'] if r['size']==size);parts,_=load(row);R=recipes[size]['band_halfspan_mm'];upper=row.get('layout','lower index plate').startswith('upper');plane=R if upper else R+10
 for name,color in [('RightFork','#41667b'),('RightTongue','#697b42'),('RightServiceCap','#218c69'),('RightLockPin','#ca770f'),('RightPullKnob','#a369b4'),('RightKnobCrossRivet','#c45555')]:
  sec=BRepAlgoAPI_Section(parts[name],gp_Pln(gp_Pnt(plane,0,60),gp_Dir(1,0,0)),False);sec.Build();assert sec.IsDone();e=TopExp_Explorer(sec.Shape(),TopAbs_EDGE);first=True
  while e.More():
   c=BRepAdaptor_Curve(TopoDS.Edge_s(e.Current()));points=[c.Value(float(t)) for t in np.linspace(c.FirstParameter(),c.LastParameter(),35)];ax.plot([p.Y() for p in points],[p.Z() for p in points],color=color,lw=1.8,label=name.replace('Right','') if first else None);first=False;e.Next()
 ax.set_xlim(-50,10);ax.set_ylim(50 if not upper else 60,85 if not upper else 95);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_title(size.replace('_',' ').title()+(' lower plate' if not upper else ' upper rear plate'),loc='left',fontsize=11);ax.set_ylabel('Z mm')
axes[1].set_xlabel('Y mm');fig.legend(*axes[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.93),ncol=6,frameon=False,fontsize=8);fig.suptitle('V16 pin and rivet section details',fontsize=16);fig.text(.5,.02,'Sections through the wear-position pin axes. The rivet is shown in its final formed shape. Actual coil wire, forming and force are not modelled.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.05,1,.86));fig.savefig(P/'documents/images/V16_sections.png',dpi=160,facecolor='white');plt.close(fig);print('Actual V16 section details rendered')
