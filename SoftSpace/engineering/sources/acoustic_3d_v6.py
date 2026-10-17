"""3D linear-tet Helmholtz proxy cavity; hypothetical uniformly compliant back.
Reconstructed straight-wall cavity from design dimensions, not the complete
ear/foam/cover/liner acoustics. Output is a model transfer, not attenuation rating.
"""
import os,sys,json,csv
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
p=Path(__file__).parent;sys.path.insert(0,str(p/'solver-libraries'))
import gmsh,numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
out=p/'engineering-v6-results';out.mkdir(exist_ok=True)
def mesh(family,h):
 c=({'pad_outer_width':51,'pad_outer_height':71,'ear_opening_width':50,'ear_opening_height':70} if family=='verification' else json.loads((p/'engineering-final.json').read_text())[family])
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('proxy_air')
 occ=gmsh.model.occ
 def cylinder(w,ht,z,depth):
  tag=occ.addCylinder(0,0,z,0,0,depth,ht/2);occ.dilate([(3,tag)],0,0,0,w/ht,1,1);return tag
 a=cylinder(c['pad_outer_width']-1,c['pad_outer_height']-1,-22,22)
 b=cylinder(c['ear_opening_width'],c['ear_opening_height'],0,20)
 occ.fuse([(3,a)],[(3,b)]);occ.synchronize()
 gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',h*.8);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',16)
 gmsh.model.mesh.generate(3)
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.array(xyz).reshape(-1,3)/1000;mp={int(t):i for i,t in enumerate(tags)}
 _,conn=gmsh.model.mesh.getElementsByType(4);tet=np.array([mp[int(t)] for t in conn]).reshape(-1,4)
 _,conn=gmsh.model.mesh.getElementsByType(2);tri=np.array([mp[int(t)] for t in conn]).reshape(-1,3)
 gmsh.finalize()
 jac=x[tet[:,1:]]-x[tet[:,0,None]];vol=abs(np.linalg.det(jac))/6
 grad=np.concatenate((-np.linalg.inv(jac).sum(axis=2)[:,:,None],np.linalg.inv(jac)),axis=2).transpose(0,2,1)
 # Gradients of affine shape functions checked by partition of unity.
 assert np.max(abs(grad.sum(axis=1)))<1e-8
 Klocal=np.einsum('eia,eja,e->eij',grad,grad,vol)
 Mlocal=vol[:,None,None]*(np.ones((4,4))+np.eye(4))/20
 rr=np.broadcast_to(tet[:,:,None],Klocal.shape).ravel();cc=np.broadcast_to(tet[:,None,:],Klocal.shape).ravel()
 K=coo_matrix((Klocal.ravel(),(rr,cc)),shape=(len(x),len(x))).tocsr();M=coo_matrix((Mlocal.ravel(),(rr,cc)),shape=K.shape).tocsr()
 faces=tri[np.all(np.isclose(x[tri,2],-.022),axis=1)]
 area=np.linalg.norm(np.cross(x[faces[:,1]]-x[faces[:,0]],x[faces[:,2]]-x[faces[:,0]]),axis=1)/2
 local=area[:,None,None]*(np.ones((3,3))+np.eye(3))/12
 B=coo_matrix((local.ravel(),(np.broadcast_to(faces[:,:,None],local.shape).ravel(),np.broadcast_to(faces[:,None,:],local.shape).ravel())),shape=K.shape).tocsr()
 drive=np.asarray(B@np.ones(len(x)));sample=np.flatnonzero(np.isclose(x[:,2],.020))
 return c,x,tet,K,M,B,drive,sample,float(vol.sum()),float(area.sum())
def solve(family,h):
 c,x,tet,K,M,B,b,sample,V,A=mesh(family,h);rows=[]
 # Sweep hypothetical shell properties; deliberately not fitted to any product.
 for E in [1500e6,2500e6]:
  for Q in [5,20]:
   radius=((c['pad_outer_width']-1)*(c['pad_outer_height']-1))**.5/2000
   t=.003;D=E*t**3/(12*(1-.35**2));stiff=192*D/radius**4;mass=1050*t;resistance=(stiff*mass)**.5/Q
   for f in np.geomspace(31.5,8000,48):
    omega=2*np.pi*f;k=omega/343*(1+.5j/20)
    dyn=stiff-mass*omega**2-1j*resistance*omega;beta=1.2*omega**2/dyn
    system=(K-k*k*M-beta*B).tocsc();rhs=-beta*b
    pressure=spsolve(system,rhs);mean=pressure[sample].mean();res=np.linalg.norm(system@pressure-rhs)/np.linalg.norm(rhs)
    rows.append({'family':family,'mesh_mm':h,'panel_E_MPa':E/1e6,'panel_Q':Q,'frequency_Hz':float(f),'model_pressure_transfer_db':float(20*np.log10(abs(mean))),'relative_residual':float(res)})
 analytic=1.2*343**2*A/(stiff*V+1.2*343**2*A)
 low=rows[144]['model_pressure_transfer_db'] # last E/Q scenario first freq
 summary={'family':family,'mesh_mm':h,'nodes':len(x),'tet4':len(tet),'volume_m3':V,'back_area_m2':A,'maximum_relative_residual':max(r['relative_residual'] for r in rows),'low_frequency_transfer_last_scenario_db':low,'static_lumped_limit_last_scenario_db':float(20*np.log10(analytic)),'rows':rows}
 (out/(family+'_acoustic3d_h'+str(h)+'.json')).write_text(json.dumps(summary,indent=2));print(family,h,len(x),len(tet),summary['maximum_relative_residual'],flush=True)
 return summary
if __name__=='__main__':
 results=[solve(f,h) for f in ['child','adult'] for h in [6,4]]
 comparison=[]
 for i in [0,2]:
  coarse,fine=results[i:i+2];diff=[abs(a['model_pressure_transfer_db']-b['model_pressure_transfer_db']) for a,b in zip(coarse['rows'],fine['rows'])]
  comparison.append({'family':coarse['family'],'max_transfer_mesh_difference_db':max(diff),'mesh_difference_below_1kHz_db':max(d for d,r in zip(diff,coarse['rows']) if r['frequency_Hz']<=1000),'mesh_gate_1db_all_frequencies':max(diff)<1})
 report={'status':'complete','mesh_comparison':comparison,'limitations':['Straight-walled proxy air cavity, dimensions derived from CAD','No ear/skin/pinna, porous foam/liner, cover seam, glasses leakage, shell modal FEM or actual material data','Uniform equivalent compliant back with hypothetical E, density and damping','Not a prediction of NRR, SNR, clinical benefit or measured product attenuation']}
 (out/'acoustic_3d_summary.json').write_text(json.dumps(report,indent=2))
