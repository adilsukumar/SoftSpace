from pathlib import Path
import os,sys,json,hashlib
os.environ['OPENBLAS_NUM_THREADS']='1'
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh,numpy as np,matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
O=P/'engineering-v11-results';I=P/'documents'/'images';s=json.loads((O/'folding_summary.json').read_text());row=next(r for r in s['sizes'] if r['size']=='adult_medium')
paths=[Path(row['source']),Path(row['best_reached_STEP'])];fig=plt.figure(figsize=(11,5));records=[]
for k,path in enumerate(paths):
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.occ.importShapes(str(path));gmsh.model.occ.synchronize()
 gmsh.option.setNumber('Mesh.MeshSizeMax',5);gmsh.option.setNumber('Mesh.MeshSizeMin',.5);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',8);gmsh.model.mesh.generate(2)
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.array(xyz).reshape(-1,3);lookup={int(t):i for i,t in enumerate(tags)};ax=fig.add_subplot(1,2,k+1,projection='3d')
 for dim,tag in gmsh.model.getEntities(3):
  if tag in [1,2,6,13,14,18]:continue
  triangles=[]
  for fd,face in gmsh.model.getBoundary([(dim,tag)],oriented=False):
   if fd!=2:continue
   types,_,arrays=gmsh.model.mesh.getElements(2,face)
   for typ,conn in zip(types,arrays):
    if typ==2:triangles.extend(np.array([lookup[int(v)] for v in conn]).reshape(-1,3).tolist())
  if triangles:ax.add_collection3d(Poly3DCollection(x[np.array(triangles)],facecolors='#8eb5ae' if tag in [3,15,28] else '#465b69',edgecolors=None,linewidth=0,shade=True,lightsource=matplotlib.colors.LightSource(315,35)))
 lo=x.min(axis=0);hi=x.max(axis=0);center=(lo+hi)/2;span=hi-lo;ax.set_xlim(center[0]-span[0]*.55,center[0]+span[0]*.55);ax.set_ylim(center[1]-span[1]*.55,center[1]+span[1]*.55);ax.set_zlim(center[2]-span[2]*.55,center[2]+span[2]*.55);ax.set_box_aspect(span);ax.view_init(25,-65);ax.set_axis_off()
 ax.set_title('V10 nominal' if k==0 else 'Exploratory staggered fold 75 and 60 degrees',fontsize=11)
 records.append({'source':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});gmsh.finalize()
fig.suptitle('Adult medium saved STEP geometry',fontsize=14);fig.text(.5,.015,'Folding poses only. Latch, strength and continuous motion remain unverified. Views use different fitting scales.',ha='center',fontsize=9);fig.subplots_adjust(0,.06,1,.91,wspace=0)
target=I/'V11_folding_study.png';fig.savefig(target,dpi=165,facecolor='white');plt.close(fig)
(O/'folding_image_sources.json').write_text(json.dumps({'image':str(target),'sources':records},indent=2));print(str(target))
