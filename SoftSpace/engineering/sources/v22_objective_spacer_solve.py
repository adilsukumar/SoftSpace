"""Objective virtual-spacer reference solve with matrix-free Newton and checked GMRES.
Explicit mean-bore-rotation hypothesis, not a real washer material model.
"""
from pathlib import Path
P=Path(__file__).resolve().parent
prefix=(P/'v22_spacer_residual_check.py').read_text().split("for side in ['outward'")[0];exec(compile(prefix,str(P/'v22_spacer_residual_check.py'),'exec'))
import time,ctypes
from scipy.sparse import diags
from scipy.sparse.linalg import splu,LinearOperator,gmres
for folder in ['numpy.libs','scipy.libs']:
 for dll in (P/'solver-libraries'/folder).glob('*openblas*.dll'):
  lib=ctypes.CDLL(str(dll))
  for suffix in ['', '64_', '_64_']:
   try:fn=getattr(lib,'scipy_openblas_set_num_threads'+suffix);fn.argtypes=[ctypes.c_int];fn(4);break
   except AttributeError:continue
free=m['free'];G,T,A,C,areas=m['G'],m['T'],m['K'],m['C'],m['areas'];wa=areas[w]
def slip(u):return (T@u-L@(H@u)).reshape(-1,2)
def adj(v):return T.T@v-H.T@(L.T@v)
def evaluate(u,F):
 gap=G@u;pn=10000*np.maximum(gap,0);tt=1000*slip(u);norm=np.linalg.norm(tt,axis=1);ratio=np.minimum(1,.2*pn[w]/np.maximum(norm,1e-20));tau=tt*ratio[:,None];force=A@u+1e5*C.T@(C@u)+G.T@(pn*areas)+adj((tau*wa[:,None]).ravel());return force-F,(gap,pn,tt,norm,ratio,tau)
def jac(v,state,contact_only=False):
 gap,pn,tt,norm,ratio,tau=state;dp=10000*(gap>0)*(G@v);dt=1000*slip(v);stick=(norm<=.2*pn[w])&(pn[w]>0);direction=tt/np.maximum(norm[:,None],1e-20);dtr=.2*dp[w,None]*direction+ratio[:,None]*(dt-direction*np.einsum('ij,ij->i',direction,dt)[:,None]);dtr[stick]=dt[stick];contact=G.T@(dp*areas)+adj((dtr*wa[:,None]).ravel());return contact if contact_only else A@v+1e5*C.T@(C@v)+contact
outputs=[]
for side in ['outward','inward']:
 path=O/('objective_spacer_'+side+'.json')
 if path.exists() and json.loads(path.read_text()).get('converged'):continue
 reference=O/('adult_fork_local_0.9_'+side+'.npz');z=np.load(reference);u=z['u'].copy();F=z['force'];scale=np.linalg.norm(F[free]);res,state=evaluate(u,F);initial=float(np.linalg.norm(res[free])/scale);start=time.time();history=[];print('start',side,'residual',initial,flush=True)
 # Contact-only directional derivative, rather than a bulk-dominated check.
 rng=np.random.default_rng(20261024);v=np.zeros(nd);v[free]=rng.normal(size=len(free));v/=np.linalg.norm(v);derivatives=[]
 for eps in [1e-6,1e-7,1e-8]:
  pp,ps=evaluate(u+eps*v,F);mm,ms=evaluate(u-eps*v,F);fd=((pp-mm)/(2*eps)-A@v-1e5*C.T@(C@v));analytic=jac(v,state,True);error=float(np.linalg.norm(fd-analytic)/max(np.linalg.norm(analytic),1e-12));derivatives.append(dict(epsilon=eps,relative_contact_derivative_error=error))
 assert min(x['relative_contact_derivative_error'] for x in derivatives)<1e-3
 # Reference fixed-point tangent as preconditioner; pivot rank correction stays matrix-free.
 active=state[0]>0;ratio=state[4];contact=G.T@diags(10000*areas*active)@G+T.T@diags(np.repeat(1000*wa*ratio,2))@T;A0=(A+contact)[free][:,free].tocsc();factor=splu(A0);Cf=C[:,free].toarray();Z=factor.solve(Cf.T);small=np.eye(5)/1e5+Cf@Z
 def pre(v):
  y=factor.solve(v);return y-Z@np.linalg.solve(small,Cf@y)
 M=LinearOperator((len(free),len(free)),matvec=pre,dtype=float);accepted=False
 for it in range(8):
  res,state=evaluate(u,F);relative=float(np.linalg.norm(res[free])/scale)
  if relative<1e-7:accepted=True;break
  def matvec(v):
   du=np.zeros(nd);du[free]=v;return jac(du,state)[free]
  J=LinearOperator((len(free),len(free)),matvec=matvec,dtype=float);counts=[0]
  def tick(v):counts[0]+=1
  du,info=gmres(J,-res[free],M=M,rtol=1e-5,atol=1e-12,restart=40,maxiter=6,callback=tick,callback_type='pr_norm');linear=float(np.linalg.norm(matvec(du)+res[free])/max(np.linalg.norm(res[free]),1e-12));assert info==0 and linear<2e-5
  alpha=1.
  for ls in range(9):
   trial=u.copy();trial[free]+=alpha*du;rr,_=evaluate(trial,F)
   if np.linalg.norm(rr[free])<np.linalg.norm(res[free]):u=trial;break
   alpha*=.5
  else:raise RuntimeError('Newton line search failed; no equilibrium pass')
  history.append(dict(iteration=it,residual_before=relative,residual_after=float(np.linalg.norm(rr[free])/scale),step=alpha,gmres_iterations=counts[0],relative_linear_residual=linear));print(side,history[-1],flush=True)
 res,state=evaluate(u,F);relative=float(np.linalg.norm(res[free])/scale);accepted=relative<1e-7
 r=dict(date='2026-10-24',converged=accepted,reference_model='Objective virtual spacer using mean bore rotation',relative_free_residual=relative,initial_original_field_residual=initial,cup_mean_displacement_x_mm=float(m['Fc']@u),seconds=time.time()-start,history=history,contact_derivative_controls=derivatives,source_CAD_sha256=m['row']['sha256'],warm_reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),executed_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='A corrected mathematical reference model. It does not resolve an actual washer, thread, material history or whole headset. No strength or comfort validation.')
 if accepted:np.savez_compressed(path.with_suffix('.npz'),xt=m['xt'],tt=m['tt'],xf=m['xf'],tf=m['tf'],u=u,normal=state[1]*areas,traction=state[5],reaction=res,force=F)
 path.write_text(json.dumps(r,indent=2));outputs.append(r);print(json.dumps({k:v for k,v in r.items() if k not in ['history']}),flush=True);del factor
 if not accepted:raise SystemExit('Candidate did not converge')
