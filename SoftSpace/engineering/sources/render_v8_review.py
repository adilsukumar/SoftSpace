import os,sys,json
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
p=Path(__file__).parent;sys.path.insert(0,str(p/'solver-libraries'))
import numpy as np,gmsh,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
o=p/'engineering-v8-results';report=json.loads((p/'cad_v8_report.json').read_text())
for size in ['adult_medium','child_small']:
 path=next(f for f in report['files'] if 'OwnPassiveDefender' in f and f.endswith('.step') and '_'+size+'_' in f and 'Extension' not in f)
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.occ.importShapes(path);gmsh.model.occ.synchronize()
 gmsh.option.setNumber('Mesh.MeshSizeMax',4);gmsh.option.setNumber('Mesh.MeshSizeMin',.3);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',12);gmsh.model.mesh.generate(2)
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.array(xyz).reshape(-1,3);lookup={int(t):i for i,t in enumerate(tags)}
 fig=plt.figure(figsize=(8,7));ax=fig.add_subplot(projection='3d')
 visible=[3,5,7,8,9,10,11,12,15,17,19,20,21,22,23,24,25,26,27,28]
 for tag in visible:
  faces=[t for d,t in gmsh.model.getBoundary([(3,tag)],oriented=False) if d==2];triangles=[]
  for face in faces:
   types,_,arrays=gmsh.model.mesh.getElements(2,face)
   for kind,conn in zip(types,arrays):
    if kind==2:triangles.extend(np.array([lookup[int(v)] for v in conn]).reshape(-1,3).tolist())
  if not triangles:continue
  tris=np.array(triangles);color='#344653' if tag in [5,17,27] else '#adb9c0'
  if tag in [3,15,28]:color='#709e96'
  ax.add_collection3d(Poly3DCollection(x[tris],facecolors=color,edgecolors=None,linewidth=0,shade=True,lightsource=matplotlib.colors.LightSource(azdeg=315,altdeg=35)))
 ax.set_xlim(-145,145);ax.set_ylim(-90,90);ax.set_zlim(-65,190);ax.set_box_aspect((2.9,1.8,2.55));ax.view_init(20,-65);ax.set_axis_off();ax.set_title(size.replace('_',' ')+' • V8 lower-crown digital concept',fontsize=17)
 fig.text(.5,.05,'Colours illustrate parts; materials, comfort and sound reduction are not validated.',ha='center',fontsize=10)
 fig.tight_layout();fig.savefig(o/(size+'_CAD.png'),dpi=170,bbox_inches='tight');plt.close(fig);gmsh.finalize();print('Rendered',size,flush=True)
