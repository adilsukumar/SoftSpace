"""Images from actual saved STEP surfaces; colours only identify parts."""
import os,sys,json,hashlib
os.environ['OPENBLAS_NUM_THREADS']='1'
from v12_geometry import P,O,gmsh,import_parts
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
cad=json.loads((O/'cad_report.json').read_text());row=next(r for r in cad['sizes'] if r['size']=='adult_small')
R=next(r['band_halfspan_mm'] for r in json.loads((P/'lower-crown-recipes.json').read_text()) if r['name']=='adult_small')
fig=plt.figure(figsize=(11,6));sources=[]
for panel in range(2):
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);parts=import_parts(row);occ=gmsh.model.occ
 if panel:occ.translate([parts['RightLockPin']],0,-6,0);occ.dilate([parts['RightSpringSpace']],0,-30,0,1,.6,1)
 keep=['RightFork','RightTongue','RightLockPin','RightSpringSpace'];occ.remove([v for k,v in parts.items() if k not in keep],recursive=True);occ.synchronize()
 gmsh.option.setNumber('Mesh.MeshSizeMax',2);gmsh.option.setNumber('Mesh.MeshSizeMin',.3);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',12);gmsh.model.mesh.generate(2)
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.asarray(xyz).reshape(-1,3);lookup={int(t):i for i,t in enumerate(tags)};ax=fig.add_subplot(1,2,panel+1,projection='3d')
 colors=['#6f8c9c','#72baa5','#df983b','#ce6964']
 for name,color in zip(keep,colors):
  triangles=[]
  for dim,face in gmsh.model.getBoundary([parts[name]],oriented=False):
   if dim!=2:continue
   _,conn=gmsh.model.mesh.getElementsByType(2,face)
   if len(conn):triangles.extend(np.asarray([lookup[int(i)] for i in conn]).reshape(-1,3).tolist())
  if triangles:ax.add_collection3d(Poly3DCollection(x[np.asarray(triangles)],facecolors=color,alpha=.35 if name.endswith('SpringSpace') else (.52 if name.endswith('Fork') else 1),linewidth=0,edgecolors=None))
 ax.set_xlim(R-7,R+35);ax.set_ylim(-43,22);ax.set_zlim(45,78);ax.set_box_aspect((42,65,33));ax.view_init(24,-58);ax.set_axis_off();ax.set_title('Pin engaged in fixed tongue' if not panel else 'Pin pulled back by 6 mm',fontsize=12)
 gmsh.finalize()
fig.suptitle('V12 folding lock candidate from saved CAD',fontsize=15)
fig.text(.5,.1,'Blue transparent fork and housing   Green fixed tongue   Orange captive pin   Red spring space',ha='center',fontsize=10)
fig.text(.5,.055,'Close views crop the larger assembly. Transparency reveals the mechanism; the red region is not a real coil.',ha='center',fontsize=9)
fig.subplots_adjust(left=0,right=1,bottom=.13,top=.9,wspace=0)
target=P/'documents'/'images'/'V12_lock_candidate.png';fig.savefig(target,dpi=180,facecolor='white');plt.close(fig)
(O/'image_sources.json').write_text(json.dumps({'image':str(target),'source':row['file'],'source_sha256':row['sha256'],'released_transform':'RightLockPin translated minus6Y; spring envelope shortened15to9','scope':'Display surface tessellation only; not FEA or a physical prototype'},indent=2));print(target)
