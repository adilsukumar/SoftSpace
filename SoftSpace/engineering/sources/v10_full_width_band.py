"""Actual full-Y band, X-half symmetry, ideal crown restraints and surface load.
This is a separate fixture study, not a rerun of the quarter-width boundary conditions.
"""
from pathlib import Path
import os,sys,json,hashlib,time
os.environ['OPENBLAS_NUM_THREADS']='1'
import solid_band_v9 as base
from quadratic_surface_load import nodal_surface_weights
np=base.np;gmsh=base.gmsh;P=Path(__file__).parent;O=P/'engineering-v10-results'
def run(size,h):
 start=time.time();report=json.loads((O/'cad_native_report.json').read_text());assert report['status']=='complete'
 source=Path(next(f for f in report['files'] if '_'+size+'_' in f and f.endswith('.step') and 'Extension' not in f))
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);occ=gmsh.model.occ;occ.importShapes(str(source));occ.synchronize()
 bands=[dt for dt in gmsh.model.getEntities(3) if (lambda b:b[0]<-75 and b[3]>75 and 81.99<b[2]<82.01 and b[4]-b[1]<30)(gmsh.model.getBoundingBox(*dt))];assert len(bands)==1
 occ.remove([dt for dt in gmsh.model.getEntities(3) if dt not in bands],recursive=True);occ.synchronize()
 cut=occ.addBox(0,-30,0,180,60,220);part,_=occ.intersect(bands,[(3,cut)]);occ.synchronize()
 gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',h*.2);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',12)
 gmsh.model.mesh.generate(3);gmsh.model.mesh.setOrder(2);etags,_=gmsh.model.mesh.getElementsByType(11)
 minimum=float(np.min(gmsh.model.mesh.getElementQualities(etags,'minDetJac')));optimized=False
 if minimum<=0:
  gmsh.model.mesh.optimize('HighOrder');optimized=True;minimum=float(np.min(gmsh.model.mesh.getElementQualities(etags,'minDetJac')))
 if minimum<=0:raise RuntimeError('Nonpositive adaptive Jacobian')
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.asarray(xyz).reshape(-1,3);mapping={int(v):i for i,v in enumerate(tags)};_,conn=gmsh.model.mesh.getElementsByType(11);t=np.asarray([mapping[int(v)] for v in conn],np.int32).reshape(-1,10)
 faces=[]
 for dim,tag in gmsh.model.getBoundary(part,oriented=False):
  if dim==2:
   b=gmsh.model.getBoundingBox(dim,tag)
   if abs(b[2]-82)<1e-5 and abs(b[5]-82)<1e-5:
    _,fc=gmsh.model.mesh.getElementsByType(9,tag);faces.extend(mapping[int(v)] for v in fc)
 tri=np.asarray(faces,np.int32).reshape(-1,6);assert len(tri);gmsh.finalize()
 crown=np.flatnonzero(np.isclose(x[:,0],0,atol=1e-5));fixed=list(crown*3)
 zmid=(x[crown,2].min()+x[crown,2].max())/2;ymax=np.max(x[crown,1]);ymin=np.min(x[crown,1])
 front=crown[np.argmin((x[crown,1]-ymax)**2+(x[crown,2]-zmid)**2)];rear=crown[np.argmin((x[crown,1]-ymin)**2+(x[crown,2]-zmid)**2)]
 fixed.extend([int(front*3+1),int(front*3+2),int(rear*3+2)])
 weights,area=nodal_surface_weights(x,tri);force=np.zeros(len(x)*3);force[0::3]=2*weights/area
 print(json.dumps({'stage':'assembly and solve','size':size,'mesh_mm':h,'nodes':len(x),'elements':len(t)}),flush=True)
 u,vm,r=base.mechanics(x,t,force,np.asarray(fixed),stream_assembly=True,progress=True,cg_maxiter=30000,reduced_storage=True,coarse_precondition=True);disp=float(weights@u[:,0]/area)
 peak_element=int(np.argmax(vm));centroid_shape=np.array([-.125]*4+[.25]*6)
 r['sampled_peak_centroid_xyz_mm']=(centroid_shape@x[t[peak_element]]).tolist()
 r['assumed_E_MPa']=2000;r['assumed_Poisson_ratio']=.35;r['ideal_load_per_full_side_N']=2
 r.update(size=size,mesh_max_mm=h,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),geometry_scope='X-half band, complete actual front and rear width, single front bore retained',load_method='2 N uniform traction integrated over full guide bottom',load_face_area_mm2=area,minimum_adaptive_Jacobian_mm3=minimum,high_order_mesh_optimized=optimized,guide_weighted_x_displacement_mm=disp,compliance_mm_per_N=disp/2,restraint_nodes_xyz_mm=x[[front,rear]].tolist(),seconds=time.time()-start,limits=['Ideal X symmetry; one front crown node restrains Y and Z, one rear crown node restrains Z to remove rigid roll','Restraints are numerical datums, not scalp contact','Different load distribution and crown restraints from quarter-width study; difference cannot be attributed solely to removed Y symmetry','Peak stress not used as physical strength or comfort result','Assumed E 2000 MPa and Poisson 0.35; no guide, locking or full assembly contact'])
 (O/(size+'_full_width_h'+str(h)+'.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
 return r
if __name__=='__main__':
 size=sys.argv[1];rows=[]
 for h in [2.0,1.5]:
  target=O/(size+'_full_width_h'+str(h)+'.json')
  try:rows.append(json.loads(target.read_text()) if target.exists() else run(size,h))
  except Exception as e:
   (O/(size+'_full_width_summary.json')).write_text(json.dumps({'status':'incomplete refinement','size':size,'meshes':rows,'failed_mesh_mm':h,'error':str(e),'compliance_gate_5pct':False,'limits':['Finer mesh did not produce an accepted solution. No mesh stability pass is claimed.']},indent=2));raise
 change=abs(rows[-1]['compliance_mm_per_N']/rows[-2]['compliance_mm_per_N']-1)
 (O/(size+'_full_width_summary.json')).write_text(json.dumps({'status':'complete','size':size,'meshes':rows,'compliance_relative_mesh_change':change,'compliance_gate_5pct':change<.05,'limits':rows[-1]['limits']},indent=2))
