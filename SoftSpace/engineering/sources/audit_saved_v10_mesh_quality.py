"""Adaptive Jacobian quality check on the saved quadratic element coordinates."""
from pathlib import Path
import sys,json,time
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh,numpy as np
O=P/'engineering-v10-results';files=[O/(sys.argv[1]+'_3d.npz')] if len(sys.argv)>1 else sorted(O.glob('*_3d.npz'));rows=[]
for path in files:
 start=time.time();data=np.load(path);x=data['xyz'];t=data['tet'];gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.add('savedmesh');tag=gmsh.model.addDiscreteEntity(3)
 gmsh.model.mesh.addNodes(3,tag,np.arange(1,len(x)+1,dtype=np.uint64),x.ravel())
 etags=np.arange(1,len(t)+1,dtype=np.uint64);gmsh.model.mesh.addElementsByType(tag,11,etags,(t+1).ravel())
 q=np.asarray(gmsh.model.mesh.getElementQualities(etags,'minDetJac'));gmsh.finalize()
 row={'file':str(path),'elements':len(t),'adaptive_minimum_Jacobian_mm3':float(q.min()),'nonpositive_elements':int(np.count_nonzero(q<=0)),'pass':bool(np.all(q>0)),'seconds':time.time()-start,'method':'Gmsh adaptive minDetJac on saved10-node tetrahedra'}
 (O/('mesh_quality_'+path.stem+'.json')).write_text(json.dumps(row,indent=2));rows.append(row);print(json.dumps(row),flush=True)
(O/'saved_mesh_quality_last_run.json').write_text(json.dumps(rows,indent=2))
