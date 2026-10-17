"""Higher-order Helmholtz refinement with area-integrated receiver pressure.
Uses 10-node volume / 6-node surface elements and degree4 quadrature.
All material/wall assumptions remain hypothetical, as in V6.
"""
import os,sys,json,time,itertools
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import numpy as np,gmsh
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
O=P/'engineering-v7-results';O.mkdir(exist_ok=True)
g4=np.array([[-1,-1,-1],[1,0,0],[0,1,0],[0,0,1]])
e4=[(0,1),(1,2),(2,0),(0,3),(2,3),(1,3)]
g3=np.array([[-1,-1],[1,0],[0,1]]);e3=[(0,1),(1,2),(2,0)]
quad=[(np.ones(4)/4,-.0131555555555556)]
for i in range(4):
 l=np.ones(4)/14;l[i]=11/14;quad.append((l,.00762222222222222))
for ij in itertools.combinations(range(4),2):
 l=np.ones(4)*.1005964238332008;l[list(ij)]=.3994035761667992;quad.append((l,.0248888888888889))
tri_quad=[]
for a,b,w in [(.445948490915965,.10810301816807,.111690794839005),(.091576213509771,.816847572980458,.054975871827661)]:
 for i in range(3):
  l=np.ones(3)*a;l[i]=b;tri_quad.append((l,w))
def shape(l,g,edges):
 N=list(l*(2*l-1));d=list((4*l[:,None]-1)*g)
 for i,j in edges:N.append(4*l[i]*l[j]);d.append(4*(l[i]*g[j]+l[j]*g[i]))
 return np.array(N),np.array(d)
assert abs(sum(w for _,w in quad)-1/6)<1e-12
assert abs(sum(w for _,w in tri_quad)-.5)<1e-12
def mesh(family,h):
 c=({'pad_outer_width':51,'pad_outer_height':71,'ear_opening_width':50,'ear_opening_height':70} if family=='verification' else json.loads((P/'engineering-final.json').read_text())[family])
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('P2_cavity');occ=gmsh.model.occ
 def ellipse(w,ht,z,depth):
  t=occ.addCylinder(0,0,z,0,0,depth,ht/2);occ.dilate([(3,t)],0,0,0,w/ht,1,1);return t
 a=ellipse(c['pad_outer_width']-1,c['pad_outer_height']-1,-22,22);b=ellipse(c['ear_opening_width'],c['ear_opening_height'],0,20)
 volumes,_=occ.fuse([(3,a)],[(3,b)]);cutter=occ.addBox(0,0,-25,100,100,50);occ.intersect(volumes,[(3,cutter)]);occ.synchronize()
 gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',h*.8);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',16);gmsh.model.mesh.generate(3);gmsh.model.mesh.setOrder(2)
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.array(xyz).reshape(-1,3)/1000;mp={int(t):i for i,t in enumerate(tags)}
 _,conn=gmsh.model.mesh.getElementsByType(11);t=np.array([mp[int(v)] for v in conn]).reshape(-1,10)
 _,conn=gmsh.model.mesh.getElementsByType(9);faces=np.array([mp[int(v)] for v in conn]).reshape(-1,6);gmsh.finalize()
 Klocal=np.zeros((len(t),10,10));Mlocal=Klocal.copy();V=0
 for l,w in quad:
  N,d=shape(l,g4,e4);J=np.einsum('eia,ib->eab',x[t],d);det=np.linalg.det(J)
  if np.any(det<=0):raise RuntimeError('Nonpositive Jacobian')
  grad=np.einsum('ib,eba->eia',d,np.linalg.inv(J))
  Klocal+=np.einsum('eia,eja,e->eij',grad,grad,det*w);Mlocal+=np.einsum('i,j,e->eij',N,N,det*w);V+=float((det*w).sum())
 def sparse(local,conn):
  return coo_matrix((local.ravel(),(np.broadcast_to(conn[:,:,None],local.shape).ravel(),np.broadcast_to(conn[:,None,:],local.shape).ravel())),shape=(len(x),len(x))).tocsr()
 K=sparse(Klocal,t);M=sparse(Mlocal,t)
 def boundary(z):
  f=faces[np.all(np.isclose(x[faces,2],z),axis=1)];local=np.zeros((len(f),6,6));area=0
  for l,w in tri_quad:
   N,d=shape(l,g3,e3);J=np.einsum('eia,ib->eab',x[f],d);jac=np.linalg.norm(np.cross(J[:,:,0],J[:,:,1]),axis=1)
   local+=np.einsum('i,j,e->eij',N,N,jac*w);area+=float((jac*w).sum())
  return sparse(local,f),area
 B,A=boundary(-.022);C,Af=boundary(.020);b=B@np.ones(len(x));receiver=(C@np.ones(len(x)))/Af
 assert np.linalg.norm(K@np.ones(len(x)))<1e-8
 return c,K,M,B,b,receiver,V,A,len(x),len(t)
def solve(family,h):
 start=time.time();c,K,M,B,b,receiver,V,A,n,nt=mesh(family,h);rows=[]
 for E in [1500e6,2500e6]:
  for Q in [5,20]:
   radius=((c['pad_outer_width']-1)*(c['pad_outer_height']-1))**.5/2000;D=E*.003**3/(12*(1-.35**2));stiff=192*D/radius**4;mass=1050*.003;R=(stiff*mass)**.5/Q
   for f in np.geomspace(31.5,8000,48):
    omega=2*np.pi*f;k=omega/343*(1+.5j/20);beta=1.2*omega**2/(stiff-mass*omega**2-1j*R*omega)
    system=(K-k*k*M-beta*B).tocsc();rhs=-beta*b;pressure=spsolve(system,rhs);mean=receiver@pressure
    row={'family':family,'mesh_mm':h,'panel_E_MPa':E/1e6,'panel_Q':Q,'frequency_Hz':float(f),'model_pressure_transfer_db':float(20*np.log10(abs(mean))),'relative_residual':float(np.linalg.norm(system@pressure-rhs)/np.linalg.norm(rhs))}
    if family=='verification':
     exact=beta/(k*np.sin(k*.042)+beta*np.cos(k*.042));row['relative_complex_error']=float(abs(mean/exact-1))
    rows.append(row)
 j={'family':family,'order':2,'symmetry':'quarter cavity, rigid symmetry planes and symmetric excitation','receiver':'area-integrated front pressure','mesh_mm':h,'nodes':n,'tet10':nt,'volume_m3':V,'back_area_m2':A,'elapsed_seconds':time.time()-start,'rows':rows,'maximum_relative_residual':max(r['relative_residual'] for r in rows)}
 (O/(family+'_P2_h'+str(h)+'.json')).write_text(json.dumps(j,indent=2));print(family,h,n,nt,'seconds',round(time.time()-start,1),flush=True);return j
if __name__=='__main__':
 family=sys.argv[1] if len(sys.argv)>1 else 'verification';h=float(sys.argv[2]) if len(sys.argv)>2 else 6
 solve(family,h)
