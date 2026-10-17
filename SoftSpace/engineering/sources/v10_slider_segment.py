"""Ideal clamped exposed slider segment cut from actual V10 STEP geometry.
Bearing/contact and guide rotations are not solved. Compliance screen only.
"""
import os,sys,json,hashlib,time
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import solid_band_v9 as base
from quadratic_surface_load import nodal_surface_weights
np=base.np;gmsh=base.gmsh;P=Path(__file__).parent;O=P/'engineering-v10-results'
source=P/'OwnPassiveDefender_V10Local_adult_small.step';R=next(r['band_halfspan_mm'] for r in json.loads((P/'lower-crown-recipes.json').read_text()) if r['name']=='adult_small')

def run(ext,h):
 start=time.time();length=ext+2
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);occ=gmsh.model.occ
 occ.importShapes(str(source));occ.synchronize()
 candidates=[]
 for dt in gmsh.model.getEntities(3):
  a,b,c,e,f,g=gmsh.model.getBoundingBox(*dt)
  if a>0 and abs(c-61)<.01 and abs(g-134)<.01 and abs(b+8)<.01 and abs(f-8)<.01:candidates.append(dt)
 if len(candidates)!=1:raise RuntimeError('Expected right slider tongue')
 occ.remove([dt for dt in gmsh.model.getEntities(3) if dt not in candidates],recursive=True)
 clip=occ.addBox(R-10,-10,65,20,20,length);seg,_=occ.intersect(candidates,[(3,clip)]);occ.translate(seg,-R,0,-65);occ.synchronize()
 gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',h*.25);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',12);gmsh.model.mesh.generate(3);gmsh.model.mesh.setOrder(2)
 etags,_=gmsh.model.mesh.getElementsByType(11);minimum_adaptive=float(np.min(gmsh.model.mesh.getElementQualities(etags,'minDetJac')));optimized=False
 if minimum_adaptive<=0:
  gmsh.model.mesh.optimize('HighOrder');optimized=True;minimum_adaptive=float(np.min(gmsh.model.mesh.getElementQualities(etags,'minDetJac')))
 if minimum_adaptive<=0:raise RuntimeError('Invalid adaptive slider mesh Jacobian')
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.asarray(xyz).reshape(-1,3);_,conn=gmsh.model.mesh.getElementsByType(11);mapping={int(tag):i for i,tag in enumerate(tags)};t=np.array([mapping[int(i)] for i in conn],dtype=np.int32).reshape(-1,10)
 faces=[]
 for dim,tag in gmsh.model.getBoundary(seg,oriented=False):
  if dim!=2:continue
  bbox=gmsh.model.getBoundingBox(dim,tag)
  if abs(bbox[2])<1e-5 and abs(bbox[5])<1e-5:
   _,fc=gmsh.model.mesh.getElementsByType(9,tag)
   faces.extend([mapping[int(i)] for i in fc])
 load_tri=np.asarray(faces,dtype=np.int32).reshape(-1,6)
 if not len(load_tri):raise RuntimeError('No quadratic end load faces')
 gmsh.finalize()
 clamped=np.flatnonzero(np.isclose(x[:,2],length,atol=1e-5));fixed=(clamped[:,None]*3+np.arange(3)).ravel();end=np.flatnonzero(np.isclose(x[:,2],0,atol=1e-5))
 weights,area=nodal_surface_weights(x,load_tri);force=np.zeros(len(x)*3);force[0::3]=2*weights/area;u,vm,r=base.mechanics(x,t,force,fixed)
 displacement=float(weights@u[:,0]/area)
 r.update(extension_mm=ext,exposed_length_mm=length,mesh_max_mm=h,load_method='Consistent uniform traction with quadratic Tri6 surface integration',load_face_area_mm2=area,minimum_adaptive_Jacobian_mm3=minimum_adaptive,high_order_mesh_optimized=optimized,tip_mean_x_displacement_mm=displacement,tip_compliance_mm_per_N=displacement/2,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),E_MPa=2000,poisson=.35,ideal_load_N=2,seconds=time.time()-start)
 (O/('slider_traction_ext'+str(ext)+'_h'+str(h)+'.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True);return r

if __name__=='__main__':
 cases=[]
 for ext in [0,15,30]:
  meshes=[]
  for h in ([1.0,.75,.5,.35] if ext==0 else [1.5,1.25,1.0]):
   f=O/('slider_traction_ext'+str(ext)+'_h'+str(h)+'.json');r=json.loads(f.read_text()) if f.exists() else run(ext,h);meshes.append(r)
   if len(meshes)>1:
    change=abs(meshes[-1]['tip_compliance_mm_per_N']/meshes[-2]['tip_compliance_mm_per_N']-1)
    if change<.05:break
  cases.append({'extension_mm':ext,'meshes':meshes,'compliance_relative_mesh_change':change,'compliance_gate_5pct':change<.05})
 summary={'status':'complete','load_method':'Consistent uniform traction','cases':cases,'all_compliance_comparisons_pass':all(c['compliance_gate_5pct'] for c in cases),'limits':['One actual CAD tongue used for the common 4x16mm section','Guide-facing cut fully clamped; ideal end-face load at pivot-centre cut','Earlier equal-node-load trials are retained separately and not used in force screen','No pin bearing, guide contact, clamp friction or rotational coupling','Corner stress not used as a strength result']}
 (O/'slider_compliance.json').write_text(json.dumps(summary,indent=2));print(json.dumps({'cases':3,'all_compliance_pass':summary['all_compliance_comparisons_pass']}))
