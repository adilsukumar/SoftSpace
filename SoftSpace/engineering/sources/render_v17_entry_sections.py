import json
from audit_v14_motion import P,load,recipes,gp_Pnt
import sys
sys.path.insert(0,str(P/'solver-libraries'))
import numpy as np,matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
from OCP.gp import gp_Pln,gp_Dir
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
O=P/'engineering-v17-results';fig,axes=plt.subplots(2,2,figsize=(9,5.4))
for i,size in enumerate(['child_large','adult_small']):
 upper=size.startswith('adult');R=recipes[size]['band_halfspan_mm'];plane=R if upper else R+10;rear=-16 if upper else -8;z=77 if upper else 60
 for j,revision in enumerate([16,17]):
  variant=size+('_R16U2' if upper else '_R16') if revision==16 else size+'_Entry25';row=json.loads((P/f'engineering-v{revision}-results'/(variant+'_cad_report.json')).read_text());parts,_=load(row);ax=axes[i,j]
  for name,color in [('RightTongue','#41667b'),('RightLockPin','#d27c15')]:
   sec=BRepAlgoAPI_Section(parts[name],gp_Pln(gp_Pnt(plane,0,z),gp_Dir(1,0,0)),False);sec.Build();assert sec.IsDone();e=TopExp_Explorer(sec.Shape(),TopAbs_EDGE)
   while e.More():
    c=BRepAdaptor_Curve(TopoDS.Edge_s(e.Current()));pts=[c.Value(float(t)) for t in np.linspace(c.FirstParameter(),c.LastParameter(),30)];ax.plot([p.Y()-rear for p in pts],[p.Z()-z for p in pts],color=color,lw=1.6);e.Next()
  ax.set_xlim(-.5,3.5);ax.set_ylim(-1.9,1.9);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_title(size.replace('_',' ').title()+f' V{revision}',fontsize=11);ax.set_xlabel('Distance from plate entry in mm');ax.set_ylabel('Offset from pin axis in mm')
fig.suptitle('Actual CAD sections at the wearing index hole');fig.text(.5,.015,'Blue is the plate and orange is the pin. V17 has a larger hole and an entry cone. Friction and spring forces are not modelled.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.04,1,.95));fig.savefig(P/'documents/images/V17_entry_sections.png',dpi=160);plt.close(fig)
