from pathlib import Path
import os,sys,json
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from v12_geometry import gmsh,import_parts
O=P/'engineering-v27-results';fig=plt.figure(figsize=(11,5.5))
for i,(path,title) in enumerate([(O/'adult_small_cad_report.json','SoftSpace V27 adult small\nFull 42 part prototype assembly'),(O/'flex_zone32_cad_report.json','SoftSpace Flex V27 wide zone\n12.7 mm foam reference and continuous cover')]):
 row=json.loads(path.read_text());gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);parts=import_parts(row);gmsh.option.setNumber('Mesh.MeshSizeMax',6);gmsh.option.setNumber('Mesh.MeshSizeMin',1);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',10);gmsh.model.mesh.generate(2);tags,xyz,_=gmsh.model.mesh.getNodes();xyz=np.array(xyz).reshape(-1,3);lookup={int(t):j for j,t in enumerate(tags)};ax=fig.add_subplot(1,2,i+1,projection='3d')
 for name,body in parts.items():
  faces=gmsh.model.getBoundary([body],oriented=False);tri=[]
  for dim,tag in faces:
   _,conn=gmsh.model.mesh.getElementsByType(2,abs(tag));tri.extend(np.array([lookup[int(n)] for n in conn]).reshape(-1,3).tolist())
  if not tri:continue
  color='#e5a04b' if 'Zone' in name or 'CF40' in name else '#62aaa3' if 'Foam' in name or 'CF42' in name else '#465d70';alpha=.18 if 'Cover' in name or 'cover' in name else 1
  ax.add_collection3d(Poly3DCollection(xyz[np.array(tri)],facecolor=color,edgecolor='none',alpha=alpha))
 lo=xyz.min(axis=0);hi=xyz.max(axis=0);centre=(lo+hi)/2;span=max(hi-lo);ax.set(xlim=(centre[0]-span/2,centre[0]+span/2),ylim=(centre[1]-span/2,centre[1]+span/2),zlim=(centre[2]-span/2,centre[2]+span/2),title=title);ax.set_box_aspect((1,1,1));ax.view_init(elev=22,azim=-60);ax.set_axis_off();gmsh.finalize()
fig.text(.5,.025,'Rendered from the saved STEP geometry. Colours identify parts, not measured performance. Flex donor mounting skirt is not modelled.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.05,1,.91));fig.savefig(P/'documents/images/V27_prototype_CAD.png',dpi=160);plt.close(fig)
rows=json.loads((O/'flex_alignment_cases.json').read_text());fig,ax=plt.subplots(figsize=(9,4))
for zh in [18,32]:
 r=[r for r in rows if r['zone_height_mm']==zh and r['arm_width_mm']==5 and r['arm_protrusion_mm']==1 and r['force_per_face_N']==12 and 'glass_mean_change_percent' in r];ax.plot([x['arm_centre_y_mm'] for x in r],[x['glass_mean_change_percent'] for x in r],marker='o',label=f'{zh} mm soft zone')
ax.axhline(0,color='black',lw=.8);ax.set(xlabel='Assumed glasses arm centre above pad centre mm',ylabel='Mean arm pressure change percent',title='Glasses alignment sensitivity at assumed 12 N and 1 mm protrusion');ax.legend();fig.text(.5,.015,'CF 42M main with CF 40M zone; 12.7 mm uncovered loading model. Negative values mean lower calculated pressure, not pain relief.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.06,1,1));fig.savefig(P/'documents/images/V27_alignment_sensitivity.png',dpi=160);plt.close(fig)
print('Saved STEP geometry render and pressure sensitivity figure')
