"""Ideal top-fixed index plate fixture; actual pin bearing contact is excluded."""
import os,sys,json,time,hashlib,math
os.environ['OPENBLAS_NUM_THREADS']='1'
from v12_geometry import P,gmsh,import_parts
O=P/os.environ.get('EAR_DEFENDER_ANALYSIS_RESULTS','engineering-v16-results')
import solid_band_v9 as base
from quadratic_surface_load import nodal_surface_weights
np=base.np
def run(h,support='top134',variant='child_large_R16'):
 start=time.time();row=json.loads((O/(variant+'_cad_report.json')).read_text());R=next(r['band_halfspan_mm'] for r in json.loads((P/'lower-crown-recipes.json').read_text()) if r['name']==row['size']);a=math.radians(row['fold_angles_deg'][1]);upper=row.get('layout','lower index plate').startswith('upper');cx=12*math.sin(a) if upper else 10*math.cos(a)-5*math.sin(a);cz=65+(12*math.cos(a) if upper else -10*math.sin(a)-5*math.cos(a));locking_radius=12 if upper else math.sqrt(125)
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);parts=import_parts(row);occ=gmsh.model.occ;body=parts['RightTongue'];occ.remove([dt for dt in gmsh.model.getEntities(3) if dt!=body],recursive=True);occ.translate([body],-R,0,0)
 clamp_z=134
 if support=='guide82':
  result,_=occ.cut([body],[(3,occ.addBox(-30,-20,82,60,40,60))]);volumes=[dt for dt in result if dt[0]==3];assert len(volumes)==1;body=volumes[0];clamp_z=82
 occ.synchronize();clamp=[];load=[];diagnostic=[]
 for dim,tag in gmsh.model.getBoundary([body],oriented=False):
  if dim!=2:continue
  b=gmsh.model.getBoundingBox(dim,tag);typ=gmsh.model.getType(dim,tag);center=occ.getCenterOfMass(dim,tag)
  if abs(b[2]-clamp_z)<1e-4 and abs(b[5]-clamp_z)<1e-4:clamp.append(tag)
  if typ=='Cylinder':
   diagnostic.append({'tag':tag,'bbox':b,'center':center})
   entry_depth=row['dimensions'].get('index_entry_depth_mm',0)
   if abs(center[0]-cx)<1e-4 and abs(center[2]-cz)<1e-4 and abs(b[1]+(16 if upper else 8)-entry_depth)<1e-4 and abs(b[4]+(13 if upper else 5))<1e-4:load.append(tag)
 if not clamp or not load:
  (O/'tongue_face_diagnostic.json').write_text(json.dumps({'clamp':clamp,'load':load,'cylinders':diagnostic},indent=2));raise RuntimeError('Expected tongue top and folded index cylinder')
 gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',h*.25);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',12)
 faceted=upper or 'index_entry_depth_mm' in row['dimensions']
 if faceted:gmsh.option.setNumber('Mesh.SecondOrderLinear',1)
 gmsh.model.mesh.generate(3);gmsh.model.mesh.setOrder(2);etags,_=gmsh.model.mesh.getElementsByType(11);minimum=float(np.min(gmsh.model.mesh.getElementQualities(etags,'minDetJac')))
 if minimum<=0:gmsh.model.mesh.optimize('HighOrderElastic' if upper else 'HighOrder');minimum=float(np.min(gmsh.model.mesh.getElementQualities(etags,'minDetJac')))
 if minimum<=0:raise RuntimeError('Invalid high-order tongue mesh')
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.asarray(xyz).reshape(-1,3);mapping={int(tag):i for i,tag in enumerate(tags)};_,conn=gmsh.model.mesh.getElementsByType(11);t=np.asarray([mapping[int(i)] for i in conn],np.int32).reshape(-1,10);fn=set();triangles=[]
 for face in clamp:
  tags,_,_=gmsh.model.mesh.getNodes(2,face,includeBoundary=True);fn.update(mapping[int(tag)] for tag in tags)
 for face in load:
  _,fc=gmsh.model.mesh.getElementsByType(9,face);triangles.extend(mapping[int(i)] for i in fc)
 tri=np.asarray(triangles,np.int32).reshape(-1,6);gmsh.finalize();weights,area=nodal_surface_weights(x,tri);direction=np.array([65-cz,0,cx])/locking_radius;pin_load=2*65/locking_radius;force=(weights[:,None]/area*pin_load*direction).ravel();fixed=np.asarray(sorted(fn),np.int32);fixed=(fixed[:,None]*3+np.arange(3)).ravel();print(json.dumps({'stage':'index plate fixture solve','variant':variant,'h':h,'nodes':len(x),'elements':len(t)}),flush=True)
 u,vm,result=base.mechanics(x,t,force,fixed,E=2000,nu=.35,stream_assembly=True,reduced_storage=True,coarse_precondition=True,progress=True,cg_maxiter=30000)
 result.update(mesh_max_mm=h,source=row['file'],source_sha256=row['sha256'],part='RightTongue lower index plate and stem',load_on_folded_index_hole_N=pin_load,load_direction=direction.tolist(),loaded_area_mm2=area,load_face_ids=load,clamped_top_face_ids=clamp,minimum_adaptive_Jacobian_mm3=minimum,assumed_E_MPa=2000,assumed_nu=.35,weighted_load_direction_displacement_mm=float(weights@(u@direction)/area),seconds=time.time()-start,limits=['Top stem face fully fixed instead of slider, screw and bearing contact','Uniform whole-bore tangential traction, not actual unilateral pin pressure','Illustrative2N side load times65mm divided bysqrt125mm locking radius','Homogeneous E2000MPa nu0.35, not an actual selected grade','No complete joint contact, spring force, fatigue, drop, creep or comfort qualification'])
 result.update(support_definition=support,clamp_plane_z_mm=clamp_z)
 result.update(variant=variant,locking_radius_mm=locking_radius,part='RightTongue '+('upper rear index plate and neck' if upper else 'lower index plate and stem'))
 if upper:
  result['limits'][2]='Illustrative2N side load times65mm divided by12mm locking radius'
 if faceted:
  result['limits'].append('Straight-sided quadratic tetrahedra approximate curved boundaries with facets; no exact curved-boundary stress claim')
  result['mesh_geometry']='straight-sided quadratic tetrahedra'
 if 'index_entry_depth_mm' in row['dimensions']:result['limits'].append('Load is distributed only on the remaining straight folded-hole land; no load or centering action is assigned to the entry cone')
 if support=='guide82':result['limits'][0]='Stem truncated at z82 and section fully fixed as an ideal rigid guide support assumption; not actual gap contact or a measured support stiffness'
 f=O/(variant+'_tongue_'+('guide82_' if support=='guide82' else '')+'h'+str(h));__import__('pathlib').Path(str(f)+'.json').write_text(json.dumps(result,indent=2));np.savez_compressed(str(f)+'.npz',x=x,t=t,u=u,vm=vm,force=force,fixed=fixed);print(json.dumps(result),flush=True)
if __name__=='__main__':run(float(sys.argv[1]),sys.argv[2] if len(sys.argv)>2 else 'top134',sys.argv[3] if len(sys.argv)>3 else 'child_large_R16')
