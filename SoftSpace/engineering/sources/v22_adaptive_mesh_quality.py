"""Use Gmsh adaptive minimum Jacobian quality on reconstructed saved Tet10 meshes."""
from pathlib import Path
import sys,json,hashlib,time,os
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np,gmsh
O=P/'engineering-v22-results';rows=[];start=time.time();sources=[('child_large',2.3,P/'engineering-v19-results/quadratic-contact/child_large_h2.3.npz'),('adult_small',2.3,P/'engineering-v19-results/quadratic-contact/adult_small_h2.3.npz'),('child_large',1.9,P/'engineering-v21-results/refinement/child_large_h1.9_mesh.npz'),('adult_small',1.9,P/'engineering-v21-results/refinement/adult_small_h1.9_mesh.npz'),('adult_small','local0.9',O/'adult_fork_local_0.9_mesh.npz')]
for size,h,source in sources:
 z=np.load(source)
 for component,xn,tn in [('tongue','xt','tt'),('fork','xf','tf')]:
  x,t=z[xn],z[tn];gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('saved_mesh');entity=gmsh.model.addDiscreteEntity(3);gmsh.model.mesh.addNodes(3,entity,np.arange(1,len(x)+1),x.ravel());tags=np.arange(1,len(t)+1);gmsh.model.mesh.addElementsByType(entity,11,tags,(t+1).ravel());quality=np.array(gmsh.model.mesh.getElementQualities(tags,'minDetJac'));condition=np.array(gmsh.model.mesh.getElementQualities(tags,'minSICN'));gmsh.finalize();r=dict(size=size,mesh=h,component=component,elements=len(t),minimum_adaptive_Jacobian=float(quality.min()),nonpositive_adaptive_Jacobians=int(sum(quality<=0)),minimum_sampled_SICN=float(condition.min()),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest());rows.append(r);print(r,flush=True)
  (O/'adaptive_mesh_quality.json').write_text(json.dumps(dict(date='2026-10-24',complete=False,cases=rows),indent=2))
r=dict(date='2026-10-24',complete=True,cases=rows,seconds=time.time()-start,gmsh_version=gmsh.__version__,method='Saved Tet10 node coordinates and connectivity reconstructed as discrete Gmsh mesh; minDetJac adaptive Jacobian and sampled minSICN.',scope='Geometric element quality only. Positive adaptive minimum Jacobian does not establish accurate solution, stress, material or product strength.')
(O/'adaptive_mesh_quality.json').write_text(json.dumps(r,indent=2))
