"""Accelerated fixed-point contact iteration, with the original force residual gate.
No change to physical equations. Projection keeps friction weights in [0,1].
"""
from pathlib import Path
import sys,os,json,time,hashlib,gc,ctypes
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
from scipy.sparse import diags
from scipy.sparse.linalg import splu
a=q.a;np=q.np;O=P/'engineering-v22-results';handles=[]
for folder in ['numpy.libs','scipy.libs']:
 for dll in (P/'solver-libraries'/folder).glob('*openblas*.dll'):
  lib=ctypes.CDLL(str(dll));handles.append(lib)
  for suffix in ['', '64_', '_64_']:
   try:fn=getattr(lib,'scipy_openblas_set_num_threads'+suffix);fn.argtypes=[ctypes.c_int];fn(4);break
   except AttributeError:continue
def solve(m,side,name,warm):
 G,T,w,area,free=m['G'],m['T'],m['washer'],m['areas'],m['free'];F=m['FP']*140+m['Fc']*side;u=warm.copy();active=G@u>0;pres=10000*np.maximum(G@u,0);tau=1000*(T@u).reshape(-1,2);fric=np.minimum(1,.2*pres[w]/np.maximum(np.linalg.norm(tau,axis=1),1e-20));C=m['C'][:,free].toarray();history=[];xs=[];rs=[];lastres=1e99
 for it in range(100):
  contact=G.T@diags(10000*area*active)@G+T.T@diags(np.repeat(1000*area[w]*fric,2))@T;A0=(m['K']+contact)[free][:,free].tocsc();fac=splu(A0);Y=fac.solve(np.column_stack([F[free],C.T]));b,Z=Y[:,0],Y[:,1:];trial=np.zeros(len(F));trial[free]=b-Z@np.linalg.solve(np.eye(5)/1e5+C@Z,C@b);del fac
  gap=G@trial;pressure=10000*np.maximum(gap,0);t=1000*(T@trial).reshape(-1,2);norm=np.linalg.norm(t,axis=1);target=np.minimum(1,.2*pressure[w]/np.maximum(norm,1e-20));traction=t*target[:,None];newactive=gap>0
  internal=m['A']@trial+G.T@(pressure*area)+T.T@(traction*area[w,None]).ravel();res=float(np.linalg.norm((internal-F)[free])/max(np.linalg.norm(F[free]),1e-12));du=float(np.linalg.norm(trial-u)/max(np.linalg.norm(trial),1e-12));stable=np.array_equal(newactive,active)
  history.append(dict(iteration=it,residual=res,relative_displacement_change=du,active=int(newactive.sum())));print(name,it,res,du,flush=True);u=trial
  (O/(name+'_iteration_progress.json')).write_text(json.dumps(dict(iteration=it,residual=res,history=history),indent=2))
  if stable and res<1e-7 and du<1e-5:return u,pressure*area,traction,internal-F,F,history
  if not stable or res>2*lastres:xs=[];rs=[]
  xs.append(target.copy());rs.append(target-fric);xs=xs[-5:];rs=rs[-5:]
  nextfric=.5*fric+.5*target
  if stable and len(rs)>=2:
   B=np.column_stack(rs);M=B.T@B;M+=np.eye(len(rs))*max(float(np.trace(M))*1e-12,1e-20);K=np.block([[M,np.ones((len(rs),1))],[np.ones((1,len(rs))),np.zeros((1,1))]])
   weights=np.linalg.solve(K,np.r_[np.zeros(len(rs)),1])[:-1]
   if max(abs(weights))<10:nextfric=np.clip(np.column_stack(xs)@weights,0,1)
  fric=np.clip(nextfric,0,1);active=newactive;lastres=res
 raise RuntimeError('Accelerated iteration limit reached; no equilibrium pass')

from scipy.spatial import cKDTree
local=float(sys.argv[1]) if len(sys.argv)>1 else .9
name='adult_fork_local_'+str(local);mesh=O/(name+'_mesh.npz');zz=np.load(mesh);meshes=[(zz['xt'],zz['tt']),(zz['xf'],zz['tf'])];m=a.prepare('adult_small',1.9,saved_meshes=meshes)
assert len(m['xt'])+len(m['xf'])<70000
for side in [2,-2]:
 label=name+('_outward' if side>0 else '_inward');path=O/(label+'.json')
 if path.exists() and json.loads(path.read_text()).get('converged'):continue
 reference=P/'engineering-v21-results/refinement'/('adult_small_'+('outward' if side>0 else 'inward')+'_h1.9.npz');ref=np.load(reference);oldsplit=3*len(ref['xt']);nearest=cKDTree(ref['xf']).query(m['xf'])[1];warm=np.r_[ref['u'][:oldsplit],ref['u'][oldsplit:].reshape(-1,3)[nearest].ravel()];start=time.time();print('prepared',label,len(warm)//3,flush=True)
 try:
  u,n,t,reaction,F,history=solve(m,side,label,warm)
  np.savez_compressed(path.with_suffix('.npz'),xt=m['xt'],tt=m['tt'],xf=m['xf'],tf=m['tf'],u=u,normal=n,traction=t,reaction=reaction,force=F)
  r=dict(converged=True,date='2026-10-24',size='adult_small',side_force_N=side,local_size_mm=local,nodes=len(u)//3,seconds=time.time()-start,relative_free_residual=history[-1]['residual'],cup_mean_displacement_x_mm=float(m['Fc']@u),history=history,source_mesh_sha256=hashlib.sha256(mesh.read_bytes()).hexdigest(),source_CAD_sha256=m['row']['sha256'],executed_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),warm_start_reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),scope='Targeted mesh refinement only; same idealized fixture physics. Warm displacement and friction initialize iteration, not acceptance. Exact final equilibrium gate below 1e-7; no strength or real material pass.')
 except (RuntimeError,AssertionError,MemoryError) as e:r=dict(converged=False,date='2026-10-24',error=type(e).__name__+': '+str(e),seconds=time.time()-start)
 path.write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='history'}),flush=True)
 if not r['converged']:raise SystemExit('Recorded solve did not converge')
