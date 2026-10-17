"""Separate fork fixture with ideal fixed pivot bores and statically balanced cup/stop loads."""
import os,sys,json,time
os.environ['OPENBLAS_NUM_THREADS']='1'
from v12_geometry import P,gmsh,import_parts
import solid_band_v9 as base
from quadratic_surface_load import nodal_surface_weights
np=base.np;O=P/'engineering-v18-results'
def run(size,h):
 start=time.time();row=json.loads((O/(size+'_cad_report.json')).read_text());R=next(r['band_halfspan_mm'] for r in json.loads((P/'lower-crown-recipes.json').read_text()) if r['name']==size);inner=row['fork_inner_halfspacing_mm'];outer=row['fork_outer_halfspacing_mm'];pivot=row['pivot_z_mm']
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);parts=import_parts(row);occ=gmsh.model.occ;body=parts['RightFork'];occ.remove([dt for dt in gmsh.model.getEntities(3) if dt!=body],recursive=True);occ.translate([body],-R,0,0);before=occ.getMass(*body)
 patches=[(2,occ.addRectangle(8,a,pivot,4,b-a)) for a,b in [(-outer,-inner),(inner,outer)]];res,_=occ.fragment([body],patches);vol=[dt for dt in res if dt[0]==3];assert len(vol)==1;body=vol[0];assert abs(occ.getMass(*body)-before)<.01;occ.synchronize();fixed_faces=[];cup_faces=[];stop_faces=[]
 for dim,tag in gmsh.model.getBoundary([body],oriented=False):
  if dim!=2:continue
  b=gmsh.model.getBoundingBox(dim,tag);c=occ.getCenterOfMass(dim,tag);typ=gmsh.model.getType(dim,tag)
  if typ=='Cylinder' and abs(c[0])<.01 and abs(c[2]-pivot)<.01:fixed_faces.append(tag)
  if typ=='Cylinder' and abs(c[0]-20)<.01 and abs(c[2]-35)<.01:cup_faces.append(tag)
  if abs(b[2]-pivot)<1e-4 and abs(b[5]-pivot)<1e-4 and abs(c[0]-10)<1e-4 and abs(abs(c[1])-(inner+outer)/2)<1e-4:stop_faces.append(tag)
 assert len(fixed_faces)==2 and len(cup_faces)==2 and len(stop_faces)==2,dict(fixed=fixed_faces,cup=cup_faces,stop=stop_faces)
 gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',h*.25);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',12);gmsh.option.setNumber('Mesh.SecondOrderLinear',1);gmsh.model.mesh.generate(3);gmsh.model.mesh.setOrder(2);etags,_=gmsh.model.mesh.getElementsByType(11);minimum=float(np.min(gmsh.model.mesh.getElementQualities(etags,'minDetJac')));assert minimum>0
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.asarray(xyz).reshape(-1,3);mapping={int(tag):i for i,tag in enumerate(tags)};_,conn=gmsh.model.mesh.getElementsByType(11);t=np.array([mapping[int(i)] for i in conn],np.int32).reshape(-1,10);fn=set()
 for face in fixed_faces:
  tags,_,_=gmsh.model.mesh.getNodes(2,face,includeBoundary=True);fn.update(mapping[int(tag)] for tag in tags)
 def weights(faces):
  tri=[]
  for face in faces:
   _,nodes=gmsh.model.mesh.getElementsByType(9,face);tri.extend(mapping[int(i)] for i in nodes)
  return nodal_surface_weights(x,np.array(tri,np.int32).reshape(-1,6))
 wc,ac=weights(cup_faces);ws,astop=weights(stop_faces);assert abs(astop-32)<.01;assert abs(ac-2*2*np.pi*2.1*6)/(2*2*np.pi*2.1*6)<.02;zc=float(wc@x[:,2]/ac);xs=float(ws@x[:,0]/astop);sf=2*(pivot-zc)/xs;force=np.zeros((len(x),3));force[:,0]=2*wc/ac;force[:,2]=-sf*ws/astop;moment=np.cross(x-np.array([0,0,pivot]),force).sum(axis=0);assert abs(moment[1])<1e-7;fixed=(np.array(sorted(fn))[:,None]*3+np.arange(3)).ravel();gmsh.finalize();print(json.dumps(dict(stage='fork solve',size=size,h=h,nodes=len(x),elements=len(t))),flush=True)
 u,vm,r=base.mechanics(x,t,force.ravel(),fixed,E=2000,nu=.35,stream_assembly=True,reduced_storage=True,coarse_precondition=True,progress=True,cg_maxiter=30000)
 r.update(size=size,source=row['file'],source_sha256=row['sha256'],mesh_max_mm=h,minimum_adaptive_Jacobian_mm3=minimum,cup_force_N=2,stop_force_N=sf,cup_loaded_area_mm2=ac,stop_loaded_area_mm2=astop,cup_weighted_x_displacement_mm=float(wc@u[:,0]/ac),stop_weighted_z_displacement_mm=float(ws@u[:,2]/astop),external_moment_about_pivot_Nmm=moment.tolist(),assumed_E_MPa=2000,assumed_nu=.35,seconds=time.time()-start,limits=['Separate linear elastic fork fixture; two full pivot bore surfaces fixed in all directions','Uniform 2N total X traction on cup pin bores; downward stop load chosen to balance moment about pivot','Not a full assembly contact solution; actual pin bearing pressure friction preload stop load sharing and support compliance are omitted','E2000MPa nu0.35 are assumed; no actual material strength creep drop fatigue child handling or comfort qualification'])
 f=O/(size+'_fork_h'+str(h))
 __import__('pathlib').Path(str(f)+'.json').write_text(json.dumps(r,indent=2));np.savez_compressed(str(f)+'.npz',x=x,t=t,u=u,vm=vm,force=force.ravel(),fixed=fixed,cup_weights=wc,stop_weights=ws);print(json.dumps(r),flush=True)
if __name__=='__main__':run(sys.argv[1],float(sys.argv[2]))
