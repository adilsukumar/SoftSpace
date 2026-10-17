"""V10 changed-guide structural checks on explicit STEP-only source geometry.
Reuse the verified quadratic element assembler; do not reuse V9 band results.
"""
from pathlib import Path
import os,sys,json,hashlib,time
os.environ['OPENBLAS_NUM_THREADS']='1'
import solid_band_v9 as base
np=base.np;gmsh=base.gmsh;P=Path(__file__).parent;O=P/'engineering-v10-results'

def run(size,h):
 start=time.time();source=P/('OwnPassiveDefender_V10Local_'+size+'.step')
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);occ=gmsh.model.occ
 occ.importShapes(str(source));occ.synchronize();candidates=[]
 for dt in gmsh.model.getEntities(3):
  a,b,c,e,f,g=gmsh.model.getBoundingBox(*dt)
  if a<0<e and 81.99<c<82.01 and g>125 and f-b<30:candidates.append(dt)
 if len(candidates)!=1:raise RuntimeError('Expected one changed V10 band '+str(candidates))
 occ.remove([dt for dt in gmsh.model.getEntities(3) if dt not in candidates],recursive=True);occ.synchronize()
 cutter=occ.addBox(0,0,0,180,30,220);occ.intersect(candidates,[(3,cutter)]);occ.synchronize()
 gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',h*.2);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',12)
 gmsh.model.mesh.generate(3);gmsh.model.mesh.setOrder(2)
 optimized=False
 if os.environ.get('V10_OPTIMIZE_HIGH_ORDER')=='1':
  gmsh.model.mesh.optimize('HighOrder');optimized=True
 etags,_=gmsh.model.mesh.getElementsByType(11)
 minimum_adaptive=float(np.min(gmsh.model.mesh.getElementQualities(etags,'minDetJac')))
 if minimum_adaptive<=0:raise RuntimeError('Nonpositive adaptive mesh Jacobian before solve')
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.asarray(xyz).reshape(-1,3);_,conn=gmsh.model.mesh.getElementsByType(11)
 mapping={int(tag):i for i,tag in enumerate(tags)};t=np.array([mapping[int(v)] for v in conn],dtype=np.int32).reshape(-1,10);gmsh.finalize()
 fixed=list(np.flatnonzero(np.isclose(x[:,0],0,atol=1e-5))*3)+list(np.flatnonzero(np.isclose(x[:,1],0,atol=1e-5))*3+1)
 crown=np.flatnonzero(np.isclose(x[:,0],0,atol=1e-5));datum=crown[np.argmin(x[crown,1]**2+(x[crown,2]-(x[crown,2].min()+x[crown,2].max())/2)**2)]
 fixed.append(int(datum*3+2));fixed=np.array(fixed)
 load=np.flatnonzero(np.isclose(x[:,2],82,atol=1e-5))
 if not len(load):raise RuntimeError('No nodes on changed guide load face')
 force=np.zeros(len(x)*3);force[load*3]=1/len(load)
 print(json.dumps({'stage':'assembly and solve','size':size,'mesh_mm':h,'nodes':len(x),'elements':len(t)}),flush=True)
 u,vm,r=base.mechanics(x,t,force,fixed,stream_assembly=os.environ.get('V10_STREAM_ASSEMBLY')=='1',progress=True,cg_maxiter=30000,reduced_storage=os.environ.get('V10_STREAM_ASSEMBLY')=='1')
 r.update(size=size,mesh_max_mm=h,high_order_mesh_optimized=optimized,minimum_adaptive_Jacobian_mm3=minimum_adaptive,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_kind='V10 STEP-only candidate',seconds=time.time()-start,E_MPa=2000,poisson=.35,load_per_full_side_N=2,guide_load_face_z_mm=82,max_displacement_mm=float(np.linalg.norm(u,axis=1).max()),guide_mean_x_displacement_mm=float(u[load,0].mean()))
 np.savez_compressed(O/(size+'_h'+str(h)+'_3d.npz'),xyz=x,tet=t,displacement=u,von_mises=vm)
 (O/(size+'_h'+str(h)+'.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True);return r

if __name__=='__main__':
 if len(sys.argv)>3 and sys.argv[3]=='optimize':os.environ['V10_OPTIMIZE_HIGH_ORDER']='1'
 if 'stream' in sys.argv[3:]:os.environ['V10_STREAM_ASSEMBLY']='1'
 run(sys.argv[1],float(sys.argv[2]))
