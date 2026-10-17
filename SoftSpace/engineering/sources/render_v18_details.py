import os,sys,json
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
O=P/'engineering-v18-results';I=P/'documents/images';fig,axes=plt.subplots(2,2,figsize=(11,7))
colors={'Fork':'#41667b','Tongue':'#697b42','FrictionWasherRear':'#c45555','FrictionWasherFront':'#c45555','BackupWasherRear':'#777777','BackupWasherFront':'#777777','DiscSpring':'#ad50a0','HingeBolt':'#ca770f','HingeNut':'#ca770f'}
for i,size in enumerate(['child_large','adult_small']):
 row=json.loads((O/(size+'_cad_report.json')).read_text());parts,_=load(row);R=recipes[size]['band_halfspan_mm'];z=row['pivot_z_mm'];y=(row['fork_inner_halfspacing_mm']+row['fork_outer_halfspacing_mm'])/2
 for j,plane in enumerate([gp_Pln(gp_Pnt(R,0,z),gp_Dir(1,0,0)),gp_Pln(gp_Pnt(R,y,z),gp_Dir(0,1,0))]):
  ax=axes[i,j]
  for suffix,color in colors.items():
   if j and suffix not in ['Fork','Tongue']:continue
   sec=BRepAlgoAPI_Section(parts['Right'+suffix],plane,False);sec.Build();assert sec.IsDone();e=TopExp_Explorer(sec.Shape(),TopAbs_EDGE);first=True
   while e.More():
    c=BRepAdaptor_Curve(TopoDS.Edge_s(e.Current()));p=[c.Value(float(t)) for t in np.linspace(c.FirstParameter(),c.LastParameter(),45)];ax.plot([v.Y() if j==0 else v.X()-R for v in p],[v.Z()-z for v in p],color=color,lw=1.7,label=suffix if first else None);first=False;e.Next()
  ax.set_xlim((-row['fork_outer_halfspacing_mm']-6,row['fork_outer_halfspacing_mm']+6) if j==0 else (-7,24));ax.set_ylim(-8,10);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_title(size.replace('_',' ').title()+(' pivot section' if j==0 else ' wearing stop section'),fontsize=11);ax.set_xlabel('Y mm' if j==0 else 'X from pivot mm');ax.set_ylabel('Z from pivot mm')
fig.legend(*axes[0,0].get_legend_handles_labels(),fontsize=7,loc='upper center',bbox_to_anchor=(.5,.955),ncol=5,frameon=False);axes[0,1].legend(fontsize=8,loc='upper right');fig.suptitle('V18 actual hinge and stop sections',fontsize=16);fig.text(.5,.02,'Saved STEP sections. Spring shown at a catalogue reference height. Threads, locking and calibrated assembly remain unqualified.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.05,1,.89));fig.savefig(I/'V18_sections.png',dpi=160);plt.close(fig)
d=json.loads((O/'torque_and_mass.json').read_text());sizes=[r['size'] for r in d['sources']];fig,ax=plt.subplots(figsize=(10,4.7));x=np.arange(len(sizes))
for k,(level,color) in enumerate([('low','#9cb8c7'),('middle','#628ca5'),('high','#315d78')]):ax.bar(x+(k-1)*.23,[next(r['maximum_gravity_moment_over_orientation_Nmm'] for r in d['mass_cases'] if r['size']==s and r['density_scenario']==level) for s in sizes],.22,label=level+' assumed density',color=color)
ax.axhline(64,color='#ab6527',ls='--',label='Proposed minimum hinge torque 64 Nmm');ax.set_xticks(x,[s.replace('_','\n') for s in sizes]);ax.set_ylabel('Torque Nmm');ax.set_ylim(0,80);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.legend(fontsize=8,ncol=2);ax.set_title('Static gravity comparison for one moving cup and yoke');fig.text(.5,.02,'Density scenarios and the torque target are assumptions. No sample torque, shock resistance or comfort pass is recorded.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.05,1,1));fig.savefig(I/'V18_torque.png',dpi=160);plt.close(fig);print('Actual sections and static comparison chart saved')

