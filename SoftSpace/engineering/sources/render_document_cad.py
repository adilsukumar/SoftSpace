"""Illustrations from saved STEP geometry, with no invented product photographs."""
import os,sys,json
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import gmsh,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
O=P/'documents'/'images';O.mkdir(parents=True,exist_ok=True)
files={
 'V1':P/'Cushion_with_frame_references_20261012_092613.step',
 'V2':P/'ContinuousCover_Adult_R5_20261012_134958.step',
 'V3':P/'OwnPassiveDefender_V3_adult_20261012_141900.step',
 'V4':P/'OwnPassiveDefender_V4_adult_20261012_160114.step',
 'V5':P/'OwnPassiveDefender_V5_adult_medium_20261013_002134.step',
 'V6':P/'OwnPassiveDefender_V6_adult_medium_20261013_012708.step',
 'V7':P/'OwnPassiveDefender_V7_adult_medium_20261013_130645.step',
 'V8':P/'OwnPassiveDefender_V8_adult_medium_20261013_133840.step',
 'V9':P/'OwnPassiveDefender_V9Local_adult_small.step',
 'V10':P/'OwnPassiveDefender_V10Local_adult_small.step',
 'pad':P/'ReplacementCushion_V8_adult_medium_20261013_133840.step'}
native=sorted(f for f in P.glob('OwnPassiveDefender_V9_adult_small_*.step') if 'Extension' not in f.name)
if native:files['V9']=native[-1]
native10=sorted(f for f in P.glob('OwnPassiveDefender_V10_adult_small_*.step') if 'Extension' not in f.name)
if native10:files['V10']=native10[-1]
manifest=[]
for name,path in files.items():
 if len(sys.argv)>1 and name not in sys.argv[1:]:
  manifest.append({'label':name,'source':str(path)});continue
 if name in ['V1','V2'] and (O/(name+'.png')).exists():
  manifest.append({'label':name,'source':str(path)});continue
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1)
 gmsh.model.occ.importShapes(str(path));gmsh.model.occ.synchronize()
 gmsh.option.setNumber('Mesh.MeshSizeMax',5);gmsh.option.setNumber('Mesh.MeshSizeMin',.5);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',10);gmsh.model.mesh.generate(2)
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.array(xyz).reshape(-1,3);lookup={int(t):i for i,t in enumerate(tags)}
 fig=plt.figure(figsize=(7.4,4.7));ax=fig.add_subplot(projection='3d')
 entities=gmsh.model.getEntities(3) or gmsh.model.getEntities(2)
 hidden={'V3':[1,2,6,11,12,16],'V4':[1,2,6,12,13,17],'pad':[1,2]}.get(name,[1,2,6,13,14,18] if name in ['V5','V6','V7','V8','V9','V10'] else [])
 for i,dt in enumerate(entities):
  if dt[0]==3 and dt[1] in hidden:continue
  faces=[t for d,t in gmsh.model.getBoundary([dt],oriented=False) if d==2] if dt[0]==3 else [dt[1]];triangles=[]
  for face in faces:
   types,_,arrays=gmsh.model.mesh.getElements(2,face)
   for kind,conn in zip(types,arrays):
    if kind==2:triangles.extend(np.array([lookup[int(v)] for v in conn]).reshape(-1,3).tolist())
  if triangles:
   color=['#86b5ac','#344653','#b5bfc8','#688e86'][i%4]
   ax.add_collection3d(Poly3DCollection(x[np.array(triangles)],facecolors=color,edgecolors=None,linewidth=0,shade=True,lightsource=matplotlib.colors.LightSource(315,35)))
 lo=x.min(axis=0);hi=x.max(axis=0);span=hi-lo;center=(hi+lo)/2;span=np.maximum(span,span.max()*.18)
 ax.set_xlim(center[0]-span[0]*.55,center[0]+span[0]*.55);ax.set_ylim(center[1]-span[1]*.55,center[1]+span[1]*.55);ax.set_zlim(center[2]-span[2]*.55,center[2]+span[2]*.55);ax.set_box_aspect(span)
 ax.view_init(25,-65 if name not in ['V1','V2','pad'] else -55);ax.set_axis_off();fig.subplots_adjust(0,0,1,1)
 fig.savefig(O/(name+'.png'),dpi=170,facecolor='white');plt.close(fig);gmsh.finalize();manifest.append({'label':name,'source':str(path)});print(name,flush=True)
(O/'CAD_sources.json').write_text(json.dumps(manifest,indent=2))
