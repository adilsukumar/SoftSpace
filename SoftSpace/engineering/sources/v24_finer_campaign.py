"""V23 corrected-reference mesh campaign. No real-product strength qualification."""
from pathlib import Path
import os,sys,json,time,hashlib,inspect,ast,itertools,ctypes,gc
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import splu,LinearOperator,gmres
np=q.np;a=q.a;O=P/'engineering-v24-results';O.mkdir(exist_ok=True)
source=inspect.getsource(a.prepare)
assert 'baseK=(K+1e5*(C.T@C)).tocsr()' in source
exec(source.replace('baseK=(K+1e5*(C.T@C)).tocsr()','baseK=K'),a.__dict__)
libs=[]
for folder in ['numpy.libs','scipy.libs']:
 for dll in (P/'solver-libraries'/folder).glob('*openblas*.dll'):
  lib=ctypes.CDLL(str(dll));libs.append(lib)
  for suffix in ['', '64_', '_64_']:
   try:fn=getattr(lib,'scipy_openblas_set_num_threads'+suffix);fn.argtypes=[ctypes.c_int];fn(4);break
   except AttributeError:pass
# Reuse the exact V22 contact equations, loading only function definitions.
module=ast.parse((P/'v22_objective_spacer_solve.py').read_text())
exec(compile(ast.Module(body=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in ['slip','adj','evaluate','jac']],type_ignores=[]),'V22_contact_equations','exec'))

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stress_summary(z):
 E=3500.;nu=.35;mu=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu));D=np.zeros((6,6));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*mu);D[3:,3:]=np.eye(3)*mu
 split=3*len(z['xt']);out=[]
 for name,x,t,u in [('tongue',z['xt'],z['tt'],z['u'][:split]),('fork',z['xf'],z['tf'],z['u'][split:])]:
  ue=u.reshape(-1,3)[t];peaks={};energy=0.;minj=1e99
  points={'interior125':[L for L,wgt in q.quadrature(5)],'boundary35':[np.array([4-sum(v),*v])/4 for v in itertools.product(range(5),repeat=3) if sum(v)<=4]}
  for label,seq in points.items():
   peak=0.
   for Lp in seq:
    gr=q.gradients(Lp);J=np.einsum('eia,ib->eab',x[t],gr);det=np.linalg.det(J);minj=min(minj,float(det.min()));assert det.min()>0
    grad=np.einsum('ib,eba->eia',gr,np.linalg.inv(J));displacement_gradient=np.einsum('eia,eib->eab',ue,grad)
    Hs=displacement_gradient;s=np.stack([Hs[:,0,0],Hs[:,1,1],Hs[:,2,2],Hs[:,0,1]+Hs[:,1,0],Hs[:,1,2]+Hs[:,2,1],Hs[:,0,2]+Hs[:,2,0]],axis=1)@D.T
    xx,yy,zz,xy,yz,xz=s.T;vm=np.sqrt(((xx-yy)**2+(yy-zz)**2+(zz-xx)**2)/2+3*(xy*xy+yz*yz+xz*xz));peak=max(peak,float(vm.max()))
   peaks[label]=peak
  out.append(dict(component=name,sampled_peaks_MPa=peaks,minimum_sampled_Jacobian=minj))
 return out

for size in ['child_large','adult_small']:
 for mesh_size in [1.5]:
  labels=[f'{size}_h{mesh_size}_{s}' for s in ['outward','inward']]
  if all((O/(label+'.json')).exists() and json.loads((O/(label+'.json')).read_text()).get('converged') for label in labels):continue
  mesh=O/f'{size}_h{mesh_size}_mesh.npz'
  if not mesh.exists():
   cad,meshes=a.mesh(size,mesh_size,conforming=2,order=2,optimize_high_order=True)
   nodes=sum(len(x) for x,t in meshes)
   (O/f'{size}_mesh_trial.json').write_text(json.dumps(dict(nodes=nodes,mesh_size_mm=mesh_size,source_CAD_sha256=cad['sha256'],scope='New mesh on unchanged isolated V19 joint'),indent=2))
   assert nodes<85000, 'Resource guard; no equilibrium pass'
   np.savez_compressed(mesh,xt=meshes[0][0],tt=meshes[0][1],xf=meshes[1][0],tf=meshes[1][1]);print('New mesh',size,nodes,flush=True)
  zz=np.load(mesh);m=a.prepare(size,mesh_size,saved_meshes=[(zz['xt'],zz['tt']),(zz['xf'],zz['tf'])]);nd=m['K'].shape[0]
  rows=[];cols=[];vals=[]
  for xyz,offset in [(m['xt'],0),(m['xf'],3*len(m['xt']))]:
   nodes=np.flatnonzero(abs(np.hypot(xyz[:,0],xyz[:,2]-m['row']['pivot_z_mm'])-2.15)<1e-5);fit,dofs=a.fit_reference(xyz,nodes,m['row']['pivot_z_mm'])
   for index,component in enumerate([3,5]):rows.extend([index]*len(dofs));cols.extend((dofs+offset).tolist());vals.extend((.5*fit[component]).tolist())
  H=coo_matrix((vals,(rows,cols)),shape=(2,nd)).tocsr();w=m['washer'];gap=.5*np.sign(m['points'][w,1]);idx=np.arange(len(gap));L=coo_matrix((np.r_[-gap,gap],(np.r_[2*idx,2*idx+1],np.r_[np.ones(len(gap),int),np.zeros(len(gap),int)])),shape=(2*len(gap),2)).tocsr()
  free=m['free'];G,T,A,C,areas=m['G'],m['T'],m['K'],m['C'],m['areas'];wa=areas[w];coordinates=np.r_[m['xt'],m['xf']]-[0,0,m['row']['pivot_z_mm']];rigid=[]
  for kind in ['translation','rotation']:
   for axis in range(3):
    unit=np.eye(3)[axis];u0=(np.tile(unit,(len(coordinates),1)) if kind=='translation' else np.cross(unit,coordinates)).ravel();error=max(float(abs(G@u0).max()),float(abs(slip(u0)).max()),float(abs(C@u0).max()));rigid.append(dict(kind=kind,axis=axis,error=error,passed=error<1e-8))
  assert all(r['passed'] for r in rigid)
  for side in ['outward','inward']:
   label=f'{size}_h{mesh_size}_{side}';out=O/(label+'.json')
   if out.exists() and json.loads(out.read_text()).get('converged'):continue
   ref=P/'engineering-v23-results'/f'{size}_h1.9_{side}.npz'
   z=np.load(ref);from scipy.spatial import cKDTree
   oldsplit=3*len(z['xt']);u=np.r_[z['u'][:oldsplit].reshape(-1,3)[cKDTree(z['xt']).query(m['xt'])[1]].ravel(),z['u'][oldsplit:].reshape(-1,3)[cKDTree(z['xf']).query(m['xf'])[1]].ravel()];u[m['fixed']]=0;F=m['FP']*140+m['Fc']*(2 if side=='outward' else -2);assert np.allclose(F.reshape(-1,3).sum(axis=0),z['force'].reshape(-1,3).sum(axis=0),atol=1e-8);scale=np.linalg.norm(F[free]);start=time.time();history=[];res,state=evaluate(u,F);initial=float(np.linalg.norm(res[free])/scale);print('Prepared',label,initial,flush=True)
   rng=np.random.default_rng(20261024);v=np.zeros(nd);v[free]=rng.normal(size=len(free));v/=np.linalg.norm(v);checks=[]
   for eps in [1e-6,1e-7]:
    pp,_=evaluate(u+eps*v,F);mm,_=evaluate(u-eps*v,F);fd=(pp-mm)/(2*eps)-A@v-1e5*C.T@(C@v);analytic=jac(v,state,True);checks.append(float(np.linalg.norm(fd-analytic)/max(np.linalg.norm(analytic),1e-12)))
   assert min(checks)<1e-3
   contact=G.T@diags(10000*areas*(state[0]>0))@G+T.T@diags(np.repeat(1000*wa*state[4],2))@T
   factor=splu((A+contact)[free][:,free].tocsc());Cf=C[:,free].toarray();Z=factor.solve(Cf.T);small=np.eye(5)/1e5+Cf@Z
   def pre(v):
    y=factor.solve(v);return y-Z@np.linalg.solve(small,Cf@y)
   M=LinearOperator((len(free),len(free)),matvec=pre,dtype=float)
   for iteration in range(12):
    res,state=evaluate(u,F);relative=float(np.linalg.norm(res[free])/scale)
    if relative<1e-7:break
    def matvec(v):
     du=np.zeros(nd);du[free]=v;return jac(du,state)[free]
    J=LinearOperator((len(free),len(free)),matvec=matvec,dtype=float);count=[0]
    def tick(v):count[0]+=1
    du,info=gmres(J,-res[free],M=M,rtol=1e-5,atol=1e-12,restart=40,maxiter=8,callback=tick,callback_type='pr_norm');linear=float(np.linalg.norm(matvec(du)+res[free])/max(np.linalg.norm(res[free]),1e-12));assert info==0 and linear<2e-5
    alpha=1.
    for search in range(12):
     trial=u.copy();trial[free]+=alpha*du;rr,_=evaluate(trial,F)
     if np.linalg.norm(rr[free])<np.linalg.norm(res[free]):u=trial;break
     alpha*=.5
    else:raise RuntimeError('No decreasing Newton step')
    history.append(dict(iteration=iteration,relative_residual=float(np.linalg.norm(rr[free])/scale),linear_residual=linear,step=alpha,gmres_iterations=count[0]));print(label,history[-1],flush=True)
   res,state=evaluate(u,F);relative=float(np.linalg.norm(res[free])/scale);converged=relative<1e-7
   # Recheck pivot with independent per-row rank-one actions.
   pivot=np.zeros(nd)
   for ci in range(5):row=C.getrow(ci);pivot+=1e5*row.toarray().ravel()*float((row@u)[0])
   weighted=(state[5]*wa[:,None]).ravel();internal=A@u+pivot+G.T@(state[1]*areas)+T.T@weighted-H.T@(L.T@weighted);independent=float(np.linalg.norm((internal-F)[free])/scale)
   result=dict(date='2026-10-24',size=size,mesh_size_mm=mesh_size,direction=side,converged=converged,relative_residual=relative,independent_residual=independent,initial_residual=initial,force_balance_N=float(np.linalg.norm(internal.reshape(-1,3).sum(axis=0))),moment_balance_Nmm=float(np.linalg.norm(np.cross(coordinates,internal.reshape(-1,3)).sum(axis=0))),coulomb_excess_MPa=float(max(0.,np.max(np.linalg.norm(state[5],axis=1)-.2*state[1][w]))),cup_displacement_mm=float(m['Fc']@u),rigid_motion_controls=rigid,contact_derivative_errors=checks,history=history,seconds=time.time()-start,source_mesh_sha256=sha(mesh),source_CAD_sha256=m['row']['sha256'],warm_start_sha256=sha(ref),script_sha256=sha(Path(__file__)),scope='Corrected virtual 0.5 mm spacer reference. E3500 MPa nu0.35 preload140 N friction0.2 side force +/-2 N. Isolated V19 joint only; no physical strength, washer or product pass.')
   if converged:
    raw=out.with_suffix('.npz');np.savez_compressed(raw,xt=m['xt'],tt=m['tt'],xf=m['xf'],tf=m['tf'],u=u,force=F,reaction=internal-F,normal=state[1]*areas,traction=state[5]);result['raw_sha256']=sha(raw);result['stress']=stress_summary(np.load(raw))
   out.write_text(json.dumps(result,indent=2));print('Saved',label,relative,flush=True);del factor;gc.collect()
   if not converged:raise SystemExit('Equilibrium failed, retained as failed')
  del m;gc.collect()
print('All four finer corrected reference cases complete',flush=True)
