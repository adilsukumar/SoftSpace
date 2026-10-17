"""Quadratic tetrahedral small-strain CAD band FEM, explicit ideal guide loads.
No slider friction, foam, worn-head geometry or strength allowable is implied.
Units mm, N, MPa. Quarter model: symmetric x/y planes, one vertical datum.
"""
import os,sys,json,time
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
p=Path(__file__).parent;sys.path.insert(0,str(p/'solver-libraries'))
import numpy as np,gmsh
from scipy.sparse import coo_matrix,diags,csr_matrix
from scipy.sparse.linalg import cg,LinearOperator
OUT=p/'engineering-v9-results';OUT.mkdir(exist_ok=True)
grads=np.array([[-1,-1,-1],[1,0,0],[0,1,0],[0,0,1]],float)
edges=[(0,1),(1,2),(2,0),(0,3),(2,3),(1,3)] # Gmsh type11 order
aa=.585410196624969;bb=.138196601125011
quadrature=[np.array([aa if i==j else bb for i in range(4)]) for j in range(4)]
def dshape(l):
 g=np.empty((10,3));g[:4]=(4*l[:,None]-1)*grads
 for k,(i,j) in enumerate(edges):g[4+k]=4*(l[i]*grads[j]+l[j]*grads[i])
 return g
def mechanics(x,t,force,fixed,E=2000,nu=.35,stream_assembly=False,progress=False,cg_maxiter=15000,reduced_storage=False,coarse_precondition=False):
 n=len(x);nd=n*3;lam=E*nu/((1+nu)*(1-2*nu));mu=E/(2*(1+nu))
 D=np.zeros((6,6));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*mu);D[3:,3:]=np.eye(3)*mu
 index_dtype=np.int32 if nd<2**31 else np.int64
 dofs=(t.astype(index_dtype,copy=False)[:,:,None]*3+np.arange(3,dtype=index_dtype)).reshape(-1,30)
 fixed=np.unique(fixed);free=np.setdiff1d(np.arange(nd),fixed);direct_reduced=stream_assembly and reduced_storage
 if direct_reduced:
  free_map=np.full(nd,-1,dtype=index_dtype);free_map[free]=np.arange(len(free),dtype=index_dtype)
  fixed_map=np.full(nd,-1,dtype=index_dtype);fixed_map[fixed]=np.arange(len(fixed),dtype=index_dtype)
  constrained_rows=csr_matrix((len(fixed),len(free)))
 vals=[];rows=[];cols=[];minjac=1e30;assembled=csr_matrix((len(free),len(free)) if direct_reduced else (nd,nd)) if stream_assembly else None
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
  if stream_assembly and (start%2048==1792 or start+256>=len(t)):
   vv=np.concatenate(vals);rr=np.concatenate(rows);cc=np.concatenate(cols);vals.clear();rows.clear();cols.clear()
   if direct_reduced:
    ri=free_map[rr];ci=free_map[cc];active=(ri>=0)&(ci>=0)
    chunk=coo_matrix((vv[active],(ri[active],ci[active])),shape=(len(free),len(free))).tocsr()
    rfix=fixed_map[rr];reaction_entries=(rfix>=0)&(ci>=0)
    constrained_rows=constrained_rows+coo_matrix((vv[reaction_entries],(rfix[reaction_entries],ci[reaction_entries])),shape=constrained_rows.shape).tocsr()
    del ri,ci,active,rfix,reaction_entries
   else:chunk=coo_matrix((vv,(rr,cc)),shape=(nd,nd)).tocsr()
   del vv,rr,cc
   assembled=assembled+chunk;vals.clear();rows.clear();cols.clear();del chunk
 if direct_reduced:A=assembled;del K,assembled
 else:K=assembled if stream_assembly else coo_matrix((np.concatenate(vals),(np.concatenate(rows),np.concatenate(cols))),shape=(nd,nd)).tocsr()
 del vals,rows,cols
 if not direct_reduced:
  if reduced_storage:
   constrained_rows=K[fixed][:,free];A=K[free];del K,assembled;A=A[:,free]
  else:A=K[free][:,free]
 rhs=force[free];counter=[0]
 inverse_diagonal=1/A.diagonal();preconditioner=diags(inverse_diagonal);coarse_rank=0
 if coarse_precondition:
  xn=x[:,0]/max(abs(x[:,0]).max(),1);yn=x[:,1]/max(abs(x[:,1]).max(),1);zn=(x[:,2]-x[:,2].mean())/max(np.ptp(x[:,2]),1)
  fields=[(0,xn),(0,xn**3),(0,xn*zn),(0,xn*xn*zn),(0,xn*zn*zn),(1,xn*yn),(1,xn**3*yn),(1,xn*yn*zn),(2,xn*xn),(2,xn**3),(2,xn*xn*zn),(2,xn*xn*yn*yn)]
  basis=np.zeros((nd,len(fields)))
  for j,(axis,v) in enumerate(fields):basis[axis::3,j]=v
  basis=basis[free];coarse=basis.T@(A@basis);coarse=(coarse+coarse.T)/2
  values,vectors=np.linalg.eigh(coarse);keep=values>max(values.max(),1e-30)*1e-12;coarse_rank=int(keep.sum())
  if not coarse_rank:raise RuntimeError('Coarse preconditioner has no positive modes')
  inv_coarse=(vectors[:,keep]/values[keep])@vectors[:,keep].T
  def apply_preconditioner(r):return inverse_diagonal*r+basis@(inv_coarse@(basis.T@r))
  preconditioner=LinearOperator(A.shape,matvec=apply_preconditioner,dtype=float)
 def cb(u):
  counter[0]+=1
  if progress and counter[0]%2000==0:print(json.dumps({'stage':'linear solve','cg_iteration':counter[0],'nodes':n}),flush=True)
 ufree,info=cg(A,rhs,M=preconditioner,rtol=1e-9,atol=1e-12,maxiter=cg_maxiter,callback=cb)
 if info:raise RuntimeError('CG did not converge '+str(info))
 u=np.zeros(nd);u[free]=ufree
 if reduced_storage:
  reaction=np.zeros(nd);reaction[free]=A@ufree-rhs;reaction[fixed]=constrained_rows@ufree-force[fixed];energy=float(ufree@(A@ufree)/2)
 else:reaction=K@u-force;energy=float(u@(K@u)/2)
 residual=np.linalg.norm(reaction[free])/max(np.linalg.norm(rhs),1e-20)
 peak=0;vms=[]
 for start in range(0,len(t),256):
  sl=slice(start,start+256);B,det=Bmatrix(t[sl],np.ones(4)/4)
  stress=np.einsum('ab,ebi,ei->ea',D,B,u[dofs[sl]],optimize=True)
  a,b,c,d,e,f=stress.T;vm=np.sqrt(((a-b)**2+(b-c)**2+(c-a)**2)/2+3*(d*d+e*e+f*f));vms.extend(vm.tolist());peak=max(peak,float(vm.max()))
 return u.reshape(-1,3),np.array(vms),{'nodes':n,'tet10_elements':len(t),'assembly_method':'CSR batches of up to2048 elements' if stream_assembly else 'single COO assembly','reduced_matrix_storage':reduced_storage,'coarse_preconditioner_modes':coarse_rank,'cg_iterations':counter[0],'relative_free_residual':float(residual),'minimum_quadrature_jacobian_mm3':minjac,'max_von_mises_centroid_MPa':peak,'strain_energy_Nmm':energy,'reaction_sum_N':reaction.reshape(-1,3).sum(axis=0).tolist()}
def mesh_geometry(size,h,test=False):
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('band')
 occ=gmsh.model.occ
 if test:occ.addBox(0,0,0,20,4,2);occ.synchronize()
 else:
  paths=[f for f in p.glob('OwnPassiveDefender_V9_'+size+'_*.step') if 'Extension' not in f.name]
  occ.importShapes(str(sorted(paths)[-1]));occ.synchronize()
  candidates=[]
  for d,t in gmsh.model.getEntities(3):
   a,b,c,e,f,g=gmsh.model.getBoundingBox(d,t)
   if a<0<e and 70<c<100 and g>125 and f-b<30:candidates.append((d,t))
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
