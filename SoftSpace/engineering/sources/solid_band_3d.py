"""Quadratic tetrahedral small-strain CAD band FEM, explicit ideal guide loads.
No slider friction, foam, worn-head geometry or strength allowable is implied.
Units mm, N, MPa. Quarter model: symmetric x/y planes, one vertical datum.
"""
import os,sys,json,time
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
p=Path(__file__).parent;sys.path.insert(0,str(p/'solver-libraries'))
import numpy as np,gmsh
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import cg
OUT=p/'engineering-v6-results';OUT.mkdir(exist_ok=True)
grads=np.array([[-1,-1,-1],[1,0,0],[0,1,0],[0,0,1]],float)
edges=[(0,1),(1,2),(2,0),(0,3),(2,3),(1,3)] # Gmsh type11 order
aa=.585410196624969;bb=.138196601125011
quadrature=[np.array([aa if i==j else bb for i in range(4)]) for j in range(4)]
def dshape(l):
 g=np.empty((10,3));g[:4]=(4*l[:,None]-1)*grads
 for k,(i,j) in enumerate(edges):g[4+k]=4*(l[i]*grads[j]+l[j]*grads[i])
 return g
def mechanics(x,t,force,fixed,E=2000,nu=.35):
 n=len(x);nd=n*3;lam=E*nu/((1+nu)*(1-2*nu));mu=E/(2*(1+nu))
 D=np.zeros((6,6));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*mu);D[3:,3:]=np.eye(3)*mu
 dofs=(t[:,:,None]*3+np.arange(3)).reshape(-1,30)
 vals=[];rows=[];cols=[];minjac=1e30
 def Bmatrix(conn,l):
  ds=dshape(l);J=np.einsum('eia,ib->eab',x[conn],ds);det=np.linalg.det(J)
  if np.any(det<=0):raise RuntimeError('Nonpositive quadratic mesh Jacobian')
  g=np.einsum('ib,eba->eia',ds,np.linalg.inv(J));B=np.zeros((len(conn),6,30))
  B[:,0,0::3]=g[:,:,0];B[:,1,1::3]=g[:,:,1];B[:,2,2::3]=g[:,:,2]
  B[:,3,0::3]=g[:,:,1];B[:,3,1::3]=g[:,:,0]
  B[:,4,1::3]=g[:,:,2];B[:,4,2::3]=g[:,:,1]
  B[:,5,0::3]=g[:,:,2];B[:,5,2::3]=g[:,:,0]
  return B,det
 for start in range(0,len(t),256):
  sl=slice(start,start+256);conn=t[sl];K=np.zeros((len(conn),30,30))
  for l in quadrature:
   B,det=Bmatrix(conn,l);minjac=min(minjac,float(det.min()));K+=np.einsum('eai,ab,ebj,e->eij',B,D,B,det/24,optimize=True)
  vals.append(K.ravel());rows.append(np.broadcast_to(dofs[sl,:,None],K.shape).ravel().copy());cols.append(np.broadcast_to(dofs[sl,None,:],K.shape).ravel().copy())
 K=coo_matrix((np.concatenate(vals),(np.concatenate(rows),np.concatenate(cols))),shape=(nd,nd)).tocsr()
 del vals,rows,cols
 free=np.setdiff1d(np.arange(nd),fixed);A=K[free][:,free];rhs=force[free];counter=[0]
 def cb(u):counter[0]+=1
 ufree,info=cg(A,rhs,M=diags(1/A.diagonal()),rtol=1e-9,atol=1e-12,maxiter=15000,callback=cb)
 if info:raise RuntimeError('CG did not converge '+str(info))
 u=np.zeros(nd);u[free]=ufree;reaction=K@u-force
 residual=np.linalg.norm(reaction[free])/max(np.linalg.norm(rhs),1e-20)
 peak=0;vms=[]
 for start in range(0,len(t),256):
  sl=slice(start,start+256);B,det=Bmatrix(t[sl],np.ones(4)/4)
  stress=np.einsum('ab,ebi,ei->ea',D,B,u[dofs[sl]],optimize=True)
  a,b,c,d,e,f=stress.T;vm=np.sqrt(((a-b)**2+(b-c)**2+(c-a)**2)/2+3*(d*d+e*e+f*f));vms.extend(vm.tolist());peak=max(peak,float(vm.max()))
 return u.reshape(-1,3),np.array(vms),{'nodes':n,'tet10_elements':len(t),'cg_iterations':counter[0],'relative_free_residual':float(residual),'minimum_quadrature_jacobian_mm3':minjac,'max_von_mises_centroid_MPa':peak,'strain_energy_Nmm':float(u@(K@u)/2),'reaction_sum_N':reaction.reshape(-1,3).sum(axis=0).tolist()}
def mesh_geometry(size,h,test=False):
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('band')
 occ=gmsh.model.occ
 if test:occ.addBox(0,0,0,20,4,2);occ.synchronize()
 else:
  paths=[f for f in p.glob('OwnPassiveDefender_V6_'+size+'_*.step') if 'Extension' not in f.name]
  occ.importShapes(str(sorted(paths)[-1]));occ.synchronize()
  candidates=[]
  for d,t in gmsh.model.getEntities(3):
   a,b,c,e,f,g=gmsh.model.getBoundingBox(d,t)
   if a<0<e and 70<c<100 and g>165 and f-b<30:candidates.append((d,t))
  if len(candidates)!=1:raise RuntimeError('Expected one CAD band '+str(candidates))
  occ.remove([dt for dt in gmsh.model.getEntities(3) if dt not in candidates],recursive=True);occ.synchronize()
  cutter=occ.addBox(0,0,0,180,30,220);occ.intersect(candidates,[(3,cutter)]);occ.synchronize()
 gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',h*.2)
 gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',12);gmsh.model.mesh.generate(3);gmsh.model.mesh.setOrder(2)
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.asarray(xyz).reshape(-1,3);_,conn=gmsh.model.mesh.getElementsByType(11)
 mapping={int(tag):i for i,tag in enumerate(tags)};t=np.array([mapping[int(v)] for v in conn],dtype=np.int32).reshape(-1,10)
 gmsh.finalize();return x,t
def run(size,h,test=False):
 start=time.time();x,t=mesh_geometry(size,h,test);F=np.zeros(len(x)*3)
 if test:
  fixed=(np.flatnonzero(np.isclose(x[:,0],0))[:,None]*3+np.arange(3)).ravel()
  end=np.flatnonzero(np.isclose(x[:,0],20));F[end*3+2]=-1/len(end)
 else:
  fixed=list(np.flatnonzero(np.isclose(x[:,0],0,atol=1e-5))*3)+list(np.flatnonzero(np.isclose(x[:,1],0,atol=1e-5))*3+1)
  crown=np.flatnonzero(np.isclose(x[:,0],0,atol=1e-5));datum=crown[np.argmin(x[crown,1]**2+(x[crown,2]-(x[crown,2].min()+x[crown,2].max())/2)**2)]
  fixed.append(int(datum*3+2));fixed=np.array(fixed)
  load=np.flatnonzero(np.isclose(x[:,2],80,atol=1e-5));F[load*3]=1/len(load) # half-width model, full side 2N
 u,vm,r=mechanics(x,t,F,fixed);r.update({'size':size,'mesh_max_mm':h,'seconds':time.time()-start,'E_MPa':2000,'poisson':.35,'load_per_full_side_N':2 if not test else 1,'max_displacement_mm':float(np.linalg.norm(u,axis=1).max())})
 if test:
  displacement=-float(u[end,2].mean());analytic=.5+20/(2000/(2*(1+.35))*4*2*(5/6))
  r.update(tip_deflection_mm=displacement,beam_with_shear_mm=analytic,relative_beam_difference=abs(displacement/analytic-1))
 else:r['guide_mean_x_displacement_mm']=float(u[load,0].mean());np.savez_compressed(OUT/(size+'_h'+str(h)+'_3d.npz'),xyz=x,tet=t,displacement=u,von_mises=vm)
 json.dump(r,open(OUT/(size+'_h'+str(h)+'.json'),'w'),indent=2);print(json.dumps(r),flush=True)
 return r
if __name__=='__main__':
 size=sys.argv[1] if len(sys.argv)>1 else 'adult_medium';h=float(sys.argv[2]) if len(sys.argv)>2 else 5
 run(size,h,size=='verification_beam')
