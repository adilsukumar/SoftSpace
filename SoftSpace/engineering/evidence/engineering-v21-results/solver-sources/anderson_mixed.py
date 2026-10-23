"""Accelerated fixed-point contact iteration, with the original force residual gate.
No change to physical equations. Projection keeps friction weights in [0,1].
"""
from pathlib import Path
import sys,os,json,time,hashlib,gc,ctypes
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
from scipy.sparse import diags
from scipy.sparse.linalg import splu
a=q.a;np=q.np;O=P/'engineering-v21-results/refinement';handles=[]
for folder in ['numpy.libs','scipy.libs']:
 for dll in (P/'solver-libraries'/folder).glob('*openblas*.dll'):
  lib=ctypes.CDLL(str(dll));handles.append(lib)
  for suffix in ['', '64_', '_64_']:
   try:fn=getattr(lib,'scipy_openblas_set_num_threads'+suffix);fn.argtypes=[ctypes.c_int];fn(4);break
   except AttributeError:continue
def solve(m,side,name):
 G,T,w,area,free=m['G'],m['T'],m['washer'],m['areas'],m['free'];F=m['FP']*140+m['Fc']*side;u=np.zeros(len(F));active=np.ones(len(area),bool);fric=np.ones(len(w));C=m['C'][:,free].toarray();history=[];xs=[];rs=[];lastres=1e99
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
   if max(abs(weights))<10:nextfric=.2*fric+.8*np.clip(np.column_stack(xs)@weights,0,1)
  fric=np.clip(nextfric,0,1);active=newactive;lastres=res
 raise RuntimeError('Accelerated iteration limit reached; no equilibrium pass')
for size,side in [('child_large',2),('child_large',-2),('adult_small',2),('adult_small',-2)]:
 name=size+('_outward' if side>0 else '_inward');path=O/(name+'_h1.9.json')
 if path.exists() and json.loads(path.read_text()).get('converged') and 'Anderson' in json.loads(path.read_text()).get('linear_solver',''):continue
 start=time.time();mesh=O/(size+'_h1.9_mesh.npz')
 if mesh.exists():z=np.load(mesh);meshes=[(z['xt'],z['tt']),(z['xf'],z['tf'])]
 else:
  row,meshes=a.mesh(size,1.9,conforming=2,order=2,optimize_high_order=True);np.savez_compressed(mesh,xt=meshes[0][0],tt=meshes[0][1],xf=meshes[1][0],tf=meshes[1][1])
 nodes=sum(len(x) for x,t in meshes);assert nodes<60000;m=a.prepare(size,1.9,saved_meshes=meshes);print('prepared',name,nodes,flush=True)
 try:
  u,n,t,reaction,F,history=solve(m,side,name);out=dict(converged=True,size=size,side_force_N=side,h=1.9,nodes=nodes,seconds=time.time()-start,linear_solver='Anderson accelerated original fixed-point contact equations with direct LU',relative_free_residual=history[-1]['residual'],cup_mean_displacement_x_mm=float(m['Fc']@u),history=history,inner_max_residual=None,factorizations=len(history),linear_system_calls=len(history),source_mesh_sha256=hashlib.sha256(mesh.read_bytes()).hexdigest(),source_CAD=m['row']['file'],source_CAD_sha256=m['row']['sha256'])
  if size=='child_large' and side==2:
   ref=np.load(O/'child_large_h1.9.npz');err=float(np.linalg.norm(u-ref['u'])/max(np.linalg.norm(ref['u']),1e-12));out['direct_LU_control_relative_u_error']=err;out['direct_LU_control_pass']=err<1e-5;assert out['direct_LU_control_pass']
  np.savez_compressed(path.with_suffix('.npz'),xt=m['xt'],tt=m['tt'],xf=m['xf'],tf=m['tf'],u=u,normal=n,traction=t,reaction=reaction,force=F)
 except (RuntimeError,AssertionError,MemoryError) as e:out=dict(converged=False,size=size,side_force_N=side,error=type(e).__name__+': '+str(e),seconds=time.time()-start)
 path.write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='history'}),flush=True);del m;gc.collect()
 if not out['converged']:raise SystemExit('Stopped after recorded acceleration failure')
