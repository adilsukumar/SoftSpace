"""One additional mesh trial to investigate the failed peak-stress comparison.
Preserve all prior NPZ files. Resource guard is recorded; no strength release.
"""
from pathlib import Path
import sys,os,json,time,gc,ctypes
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
a=q.a;np=q.np;O=P/'engineering-v21-results/refinement';O.mkdir(exist_ok=True)
start=time.time();size='child_large';h=1.9
row,meshes=a.mesh(size,h,conforming=2,order=2,optimize_high_order=True);nodes=sum(len(x) for x,t in meshes)
np.savez_compressed(O/'child_large_h1.9_mesh.npz',xt=meshes[0][0],tt=meshes[0][1],xf=meshes[1][0],tf=meshes[1][1])
r=dict(size=size,h=h,nodes=nodes,date='2026-10-23',source_sha256=row['sha256'],status='mesh generated',physical_validation=False)
(O/'trial.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
if nodes>60000:
 r.update(status='not solved beyond chosen 60000 node guard');(O/'trial.json').write_text(json.dumps(r,indent=2));raise SystemExit(0)
try:
 m=a.prepare(size,h,saved_meshes=meshes);print('prepared',flush=True)
 result,u,n,t,reaction,F=a.solve(m,140,2,.2,max_iterations=160)
 np.savez_compressed(O/'child_large_h1.9.npz',xt=m['xt'],tt=m['tt'],xf=m['xf'],tf=m['tf'],u=u,normal=n,traction=t,reaction=reaction,force=F)
 r.update(status='equilibrium converged',result=result,seconds=time.time()-start,scope='Same ideal-pivot PA66 reference model. Additional mesh trial, not physical strength.')
except (RuntimeError,MemoryError,AssertionError) as e:r.update(status='failed',error=type(e).__name__+': '+str(e),history=getattr(e,'history',[]),seconds=time.time()-start)
(O/'trial.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='result'}),flush=True)
