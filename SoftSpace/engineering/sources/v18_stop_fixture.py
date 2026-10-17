"""Actual V18 tongue stop patches, ideal guide support, assumed elastic material."""
import os,sys,json,time,math
os.environ['OPENBLAS_NUM_THREADS']='1'
from v12_geometry import P,gmsh,import_parts
import solid_band_v9 as base
from quadratic_surface_load import nodal_surface_weights
np=base.np;O=P/'engineering-v18-results'
def run(size,h):
 start=time.time();row=json.loads((O/(size+'_cad_report.json')).read_text());R=next(r['band_halfspan_mm'] for r in json.loads((P/'lower-crown-recipes.json').read_text()) if r['name']==size);inner=row['fork_inner_halfspacing_mm'];outer=row['fork_outer_halfspacing_mm'];pivot=row['pivot_z_mm'];guide=row['guide_bottom_mm'];gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);parts=import_parts(row);occ=gmsh.model.occ;body=parts['RightTongue'];occ.remove([dt for dt in gmsh.model.getEntities(3) if dt!=body],recursive=True);occ.translate([body],-R,0,0);before=occ.getMass(*body)
 patches=[(2,occ.addRectangle(8,a,pivot,4,b-a)) for a,b in [(-outer,-inner),(inner,outer)]];result,_=occ.fragment([body],patches);vol=[dt for dt in result if dt[0]==3];assert len(vol)==1;body=vol[0];assert abs(occ.getMass(*body)-before)<.01
 result,_=occ.cut([body],[(3,occ.addBox(-20,-outer-1,guide,45,2*outer+2,60))]);vol=[dt for dt in result if dt[0]==3];assert len(vol)==1;body=vol[0];occ.synchronize();clamp=[];load=[]
 for dim,tag in gmsh.model.getBoundary([body],oriented=False):
  if dim!=2:continue
  b=gmsh.model.getBoundingBox(dim,tag);center=occ.getCenterOfMass(dim,tag)
  if abs(b[2]-guide)<1e-4 and abs(b[5]-guide)<1e-4:clamp.append(tag)
  if abs(b[2]-pivot)<1e-4 and abs(b[5]-pivot)<1e-4 and abs(center[0]-10)<1e-4 and abs(abs(center[1])-(inner+outer)/2)<1e-4:load.append(tag)
 if not clamp or len(load)!=2:
  raise RuntimeError(str({'clamp':clamp,'loads':load,'surfaces':[(d,t,occ.getCenterOfMass(d,t)) for d,t in gmsh.model.getBoundary([body],oriented=False)]}))
 gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',h*.25);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',12);gmsh.option.setNumber('Mesh.SecondOrderLinear',1);gmsh.model.mesh.generate(3);gmsh.model.mesh.setOrder(2);etags,_=gmsh.model.mesh.getElementsByType(11);minimum=float(np.min(gmsh.model.mesh.getElementQualities(etags,'minDetJac')));assert minimum>0
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.asarray(xyz).reshape(-1,3);mapping={int(tag):i for i,tag in enumerate(tags)};_,conn=gmsh.model.mesh.getElementsByType(11);t=np.array([mapping[int(i)] for i in conn],np.int32).reshape(-1,10);fn=set();tri=[]
 for face in clamp:
  tags,_,_=gmsh.model.mesh.getNodes(2,face,includeBoundary=True);fn.update(mapping[int(tag)] for tag in tags)
 for face in load:
  _,nodes=gmsh.model.mesh.getElementsByType(9,face);tri.extend(mapping[int(i)] for i in nodes)
 gmsh.finalize();weights,area=nodal_surface_weights(x,np.array(tri,np.int32).reshape(-1,6));assert abs(area-32)<.01;direction=np.array([0.,0,1.]);stop_force=2*65/10;force=(weights[:,None]*direction*stop_force/area).ravel();fixed=(np.array(sorted(fn))[:,None]*3+np.arange(3)).ravel();print(json.dumps({'stage':'stop fixture solve','size':size,'nodes':len(x),'elements':len(t)}),flush=True);u,vm,r=base.mechanics(x,t,force,fixed,E=2000,nu=.35,stream_assembly=True,reduced_storage=True,coarse_precondition=True,progress=True,cg_maxiter=30000)
 r.update(size=size,source=row['file'],source_sha256=row['sha256'],mesh_max_mm=h,minimum_adaptive_Jacobian_mm3=minimum,weighted_load_direction_displacement_mm=float(weights@(u@direction)/area),loaded_area_mm2=area,total_stop_force_N=stop_force,assumed_E_MPa=2000,assumed_nu=.35,seconds=time.time()-start,limits=['Ideal rigid stem support at guide bottom instead of actual guide contact','Uniform13N total on both wearing-stop patches;illustrative2N side load at65mm lever','Pivot bearing is not constrained here,so this is a separate load-path fixture,not solved joint load sharing','Homogeneous isotropic assumed material,faceted quadratic mesh and small displacements','No plasticity,creep,impact,actual fasteners,complete3D contact or physical strength qualification']);f=O/(size+'_stop_h'+str(h));__import__('pathlib').Path(str(f)+'.json').write_text(json.dumps(r,indent=2));np.savez_compressed(str(f)+'.npz',x=x,t=t,u=u,vm=vm,force=force,fixed=fixed);print(json.dumps(r),flush=True)
if __name__=='__main__':run(sys.argv[1],float(sys.argv[2]))

