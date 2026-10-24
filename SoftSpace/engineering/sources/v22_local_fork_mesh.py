"""Generate a targeted adult fork mesh around the two recorded V21 hotspots.
Unchanged CAD and old tongue mesh. Finite quality checks before any solve.
"""
from pathlib import Path
import sys,os,json,hashlib,time
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
np=q.np;a=q.a;O=P/'engineering-v22-results';O.mkdir(exist_ok=True);local=float(sys.argv[1]) if len(sys.argv)>1 else .9;name='adult_fork_local_'+str(local);row=json.loads((P/'engineering-v19-results/adult_small_cad_report.json').read_text());pivot=row['pivot_z_mm'];inner=row['fork_inner_halfspacing_mm'];outer=row['fork_outer_halfspacing_mm'];old=a.gmsh.model.mesh.generate

def generate(dim):
 def size(dim,tag,x,y,z,lc):
  if abs(y)<inner-.1:return lc
  distance=min(((x-6)**2+(abs(y)-inner)**2+(z-pivot)**2)**.5,((x-13)**2+(abs(y)-(inner+outer)/2)**2+(z-pivot)**2)**.5)
  target=local+(1.9-local)*min(max((distance-2)/4,0),1)
  return min(lc,target)
 a.gmsh.option.setNumber('Mesh.MeshSizeMin',.25);a.gmsh.model.mesh.setSizeCallback(size)
 try:return old(dim)
 finally:a.gmsh.model.mesh.removeSizeCallback()
a.gmsh.model.mesh.generate=generate
start=time.time();cad,meshes=a.mesh('adult_small',1.9,conforming=2,order=2,optimize_high_order=True);ref=np.load(P/'engineering-v21-results/refinement/adult_small_h1.9_mesh.npz');xt,tt=ref['xt'],ref['tt'];xf,tf=meshes[1];nodes=len(xt)+len(xf);minimum=1e99
for L,w in q.quadrature(3):
 gr=q.gradients(L);det=np.linalg.det(np.einsum('eia,ib->eab',xf[tf],gr));minimum=min(minimum,float(det.min()))
path=O/(name+'_mesh.npz');np.savez_compressed(path,xt=xt,tt=tt,xf=xf,tf=tf)
r=dict(date='2026-10-24',size='adult_small',local_size_mm=local,global_size_mm=1.9,nodes=nodes,tongue_nodes=len(xt),fork_nodes=len(xf),source_CAD_sha256=cad['sha256'],mesh_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),minimum_27_point_fork_Jacobian=minimum,seconds=time.time()-start,scope='Unchanged V19 isolated joint geometry; adaptive fork mesh, V21 tongue unchanged. Finite positive Jacobian checks do not prove global curved-element validity. No equilibrium solve in this step.')
(O/(name+'_mesh.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True);assert minimum>0
