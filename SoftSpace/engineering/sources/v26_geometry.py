"""V26 isolated joint candidate. Adds land beside preload footprint and rounds transitions."""
from pathlib import Path
import os,sys,json,hashlib,inspect
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
np=q.np;a=q.a;O=P/'engineering-v26-results';O.mkdir(exist_ok=True);LOCAL_TARGET=None

def modify_joint(keep,row,size):
 gmsh=a.gmsh;occ=gmsh.model.occ;pivot=row['pivot_z_mm'];inner=row['fork_inner_halfspacing_mm'];outer=row['fork_outer_halfspacing_mm'];before=[occ.getMass(*v) for v in keep]
 # Backfill the original 6.001 mm notch up to x=7, giving finite land beyond radius-6 preload.
 boxes=[]
 for sign in [-1,1]:
  lo,hi=sorted([sign*inner,sign*outer]);boxes.append((3,occ.addBox(6.,lo,pivot,1.,hi-lo,4.)))
 result,_=occ.fuse([keep[1]],boxes);vol=[dt for dt in result if dt[0]==3];assert len(vol)==1;keep[1]=vol[0];occ.synchronize();records=[]
 for i,name in enumerate(['tongue','fork']):
  faces=gmsh.model.getBoundary([keep[i]],oriented=False);edges=set(dt for face in faces for dt in gmsh.model.getBoundary([face],oriented=False));selected=[]
  for dim,tag in edges:
   b=occ.getBoundingBox(dim,tag);c=occ.getCenterOfMass(dim,tag)
   along_y=abs(b[3]-b[0])<1e-5 and abs(b[5]-b[2])<1e-5 and b[4]-b[1]>1
   target=(name=='tongue' and abs(abs(c[0])-2)<1e-5 and abs(c[2]-(pivot+np.sqrt(32)))<1e-5) or (name=='fork' and min(abs(c[0]-7),abs(c[0]-13.001))<1e-5 and abs(c[2]-pivot)<1e-5)
   if along_y and target:selected.append(tag)
  assert len(selected)==(2 if name=='tongue' else 4),(name,selected)
  result=occ.fillet([keep[i][1]],selected,[.6],removeVolume=True);vol=[dt for dt in result if dt[0]==3];assert len(vol)==1;keep[i]=vol[0];occ.synchronize();records.append(dict(part=name,fillet_radius_mm=.6,edges=len(selected)))
 target=O/f'{size}_RoundedJoint.step'
 if not target.exists():a.gmsh.write(str(target))
 r=dict(row,file=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),revision='V26 isolated rounded joint candidate',source_CAD_sha256=row['sha256'],source_CAD_file=row['file'],parts={'RightTongue':list(keep[0]),'RightFork':list(keep[1])},part_bounds_mm={name:list(occ.getBoundingBox(*body)) for name,body in zip(['RightTongue','RightFork'],keep)},part_volumes_mm3={name:occ.getMass(*body) for name,body in zip(['RightTongue','RightFork'],keep)},solid_count=2,old_component_volumes_mm3=before,new_component_volumes_mm3=[occ.getMass(*v) for v in keep],changes=records,scope='Isolated cropped joint only. Not integrated in full headset or manufacturing released. Added fork notch land from x6.001 to x7 and radius0.6 transitions.')
 (O/f'{size}_candidate_cad.json').write_text(json.dumps(r,indent=2));return keep,r

def install_mesh():
 source=inspect.getsource(a.mesh)
 needle=' # Partition both actual stop faces into the same nominal rectangle.'
 assert needle in source
 source=source.replace(needle,' keep,row=modify_joint(keep,row,size)\n'+needle)
 a.modify_joint=modify_joint
 if LOCAL_TARGET is not None:
  token='gmsh.model.mesh.generate(3)'
  injection="gmsh.option.setNumber('Mesh.MeshSizeMin',.15);fields=[];"
  for left,right in [(1.75,2.85),(-2.85,-1.75)]:
   injection+="field=gmsh.model.mesh.field.add('Box');"+''.join("gmsh.model.mesh.field.setNumber(field,"+repr(k)+","+repr(v)+");" for k,v in dict(VIn=LOCAL_TARGET,VOut=2.,XMin=left,XMax=right,YMin=-8.1,YMax=8.1,ZMin=64.,ZMax=65.75,Thickness=.5).items())+"fields.append(field);"
  injection+="combined=gmsh.model.mesh.field.add('Min');gmsh.model.mesh.field.setNumbers(combined,'FieldsList',fields);gmsh.model.mesh.field.setAsBackgroundMesh(combined);"+token
  source=source.replace(token,injection)
 exec(source,a.__dict__)

if __name__=='__main__':
 LOCAL_TARGET=float(sys.argv[2]) if len(sys.argv)>2 else None;install_mesh();h=float(sys.argv[1]) if len(sys.argv)>1 else 1.9;row,meshes=a.mesh('child_large',h,conforming=2,order=2,optimize_high_order=True);nodes=sum(len(x) for x,t in meshes);print('Generated nodes',nodes,flush=True);assert nodes<85000
 label=f'child_large_h{h}'+(f'_local{LOCAL_TARGET}' if LOCAL_TARGET else '');f=O/f'{label}_mesh.npz';np.savez_compressed(f,xt=meshes[0][0],tt=meshes[0][1],xf=meshes[1][0],tf=meshes[1][1]);(O/f'{label}_mesh.json').write_text(json.dumps(dict(nodes=nodes,source_CAD_sha256=row['sha256'],raw_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),mesh_target_mm=h,local_target_mm=LOCAL_TARGET),indent=2));print('V26 mesh saved',h,nodes,flush=True)
