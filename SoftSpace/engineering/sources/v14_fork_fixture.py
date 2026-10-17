"""Ideal fixed-pivot-bore fork fixture on actual V12 CAD, not bearing contact FEA."""
import os,sys,json,time,hashlib,math
os.environ['OPENBLAS_NUM_THREADS']='1'
from v12_geometry import P,gmsh,import_parts
O=P/'engineering-v14-results'
import solid_band_v9 as base
from quadratic_surface_load import nodal_surface_weights
np=base.np
def run(size,h):
 start=time.time();cad=json.loads((O/'cad_report.json').read_text());row=next(r for r in cad['sizes'] if r['size']==size);recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())};R=recipes[size]['band_halfspan_mm']
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);parts=import_parts(row);occ=gmsh.model.occ;fork=parts['RightFork'];occ.remove([dt for dt in gmsh.model.getEntities(3) if dt!=fork],recursive=True);occ.translate([fork],-R,0,0);occ.synchronize()
 clamp_faces=[];load_faces=[];diagnostics=[]
 for dim,tag in gmsh.model.getBoundary([fork],oriented=False):
  if dim!=2:continue
  b=gmsh.model.getBoundingBox(dim,tag);typ=gmsh.model.getType(dim,tag)
  if typ!='Cylinder':continue
  diagnostics.append({'tag':tag,'bbox':b})
  if abs((b[0]+b[3])/2)<1e-5 and abs((b[2]+b[5])/2-65)<1e-5 and abs(b[3]-b[0]-2.2)<1e-4:clamp_faces.append(tag)
  if abs((b[0]+b[3])/2-10)<1e-5 and abs((b[2]+b[5])/2-60)<1e-5 and abs(b[1]+12.999)<1e-5 and abs(b[4]+10)<1e-5:load_faces.append(tag)
 if not clamp_faces or not load_faces:
  (O/'fork_face_diagnostic.json').write_text(json.dumps({'clamp_faces':clamp_faces,'load_faces':load_faces,'cylinders':diagnostics},indent=2));raise RuntimeError('Expected pivot clamp and rear rod guide surfaces')
 gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',h*.25);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',12);gmsh.model.mesh.generate(3);gmsh.model.mesh.setOrder(2)
 etags,_=gmsh.model.mesh.getElementsByType(11);minimum=float(np.min(gmsh.model.mesh.getElementQualities(etags,'minDetJac')));optimized=False
 if minimum<=0:gmsh.model.mesh.optimize('HighOrder');optimized=True;minimum=float(np.min(gmsh.model.mesh.getElementQualities(etags,'minDetJac')))
 if minimum<=0:raise RuntimeError('Invalid high-order fork mesh')
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.asarray(xyz).reshape(-1,3);mapping={int(tag):i for i,tag in enumerate(tags)};_,conn=gmsh.model.mesh.getElementsByType(11);t=np.asarray([mapping[int(i)] for i in conn],np.int32).reshape(-1,10)
 fixed_nodes=set()
 for face in clamp_faces:
  ft,_,_=gmsh.model.mesh.getNodes(2,face,includeBoundary=True);fixed_nodes.update(mapping[int(tag)] for tag in ft)
 triangles=[]
 for face in load_faces:
  _,fc=gmsh.model.mesh.getElementsByType(9,face);triangles.extend(mapping[int(i)] for i in fc)
 tri=np.asarray(triangles,np.int32).reshape(-1,6);gmsh.finalize();weights,area=nodal_surface_weights(x,tri);direction=np.array([5.,0,10])/math.sqrt(125);pin_load=2*65/math.sqrt(125);force=(weights[:,None]/area*pin_load*direction).ravel();fixed=np.asarray(sorted(fixed_nodes),np.int32);fixed=(fixed[:,None]*3+np.arange(3)).ravel()
 print(json.dumps({'stage':'solve fork fixture','size':size,'h':h,'nodes':len(x),'elements':len(t),'load_N':pin_load}),flush=True)
 u,vm,result=base.mechanics(x,t,force,fixed,E=2000,nu=.35,stream_assembly=True,reduced_storage=True,coarse_precondition=True,progress=True,cg_maxiter=30000)
 result.update(size=size,mesh_max_mm=h,source=row['file'],source_sha256=row['sha256'],part='RightFork with rear cap removed; cap and hardware excluded',load_per_side_reference_N=2,assumed_cup_force_arm_mm=65,load_on_lock_bore_N=pin_load,load_direction=direction.tolist(),loaded_area_mm2=area,load_face_ids=load_faces,clamped_pivot_face_ids=clamp_faces,minimum_adaptive_Jacobian_mm3=minimum,optimized=optimized,assumed_E_MPa=2000,assumed_nu=.35,weighted_load_direction_displacement_mm=float(weights@(u@direction)/area),seconds=time.time()-start,limits=['Fixed full pivot bore surfaces, not free bearing contact','Uniform tangent-direction traction on rear rod-guide cylinder, not solved pin contact or load sharing','Main fork receives full illustrative pin load; rear cap screws knob and all contact excluded','Assumed homogeneous isotropic material; not a final manufactured grade','Peak centroid stresses and ideal stiffness cannot certify joint strength, fatigue or drop survival'])
 (O/(size+'_fork_h'+str(h)+'.json')).write_text(json.dumps(result,indent=2));np.savez_compressed(O/(size+'_fork_h'+str(h)+'.npz'),x=x,t=t,u=u,vm=vm,force=force,fixed=fixed);print(json.dumps(result),flush=True);return result
if __name__=='__main__':run(sys.argv[1],float(sys.argv[2]))
