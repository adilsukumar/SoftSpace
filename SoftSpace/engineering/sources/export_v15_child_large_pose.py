"""Export a newly checked pose of unchanged V14 child-large geometry."""
import os,json,math,hashlib
os.environ['OPENBLAS_NUM_THREADS']='1'
from v12_geometry import P,gmsh,import_parts
O=P/'engineering-v15-results';audit=json.loads((O/'child_large_path_audit.json').read_text());assert audit['new_complete_sampled_path_pass']
row=next(r for r in json.loads((P/'engineering-v14-results/cad_report.json').read_text())['sizes'] if r['size']=='child_large');R=next(r['band_halfspan_mm'] for r in json.loads((P/'lower-crown-recipes.json').read_text()) if r['name']=='child_large')
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;parts=import_parts(row)
for side,prefix in [(-1,'Left'),(1,'Right')]:
 occ.translate([parts[prefix+'LockPin'],parts[prefix+'PullKnob']],0,-6,0);occ.remove([parts[prefix+'SpringSpace']],recursive=True);a=(3,occ.addCylinder(side*(R+10),-30,60,0,9,0,3.175));b=(3,occ.addCylinder(side*(R+10),-31,60,0,11,0,2.825));result,_=occ.cut([a],[b]);assert len(result)==1;parts[prefix+'SpringSpace']=result[0]
for prefix,shift,x,z,angle in [('Left',15,-R,80,-30),('Right',-5,R,60,60)]:
 occ.translate([dt for k,dt in parts.items() if k.startswith(prefix) and not k.endswith('SliderKnob')],0,0,shift)
 occ.rotate([dt for k,dt in parts.items() if k.startswith(prefix) and k not in [prefix+'Tongue',prefix+'ForkPin',prefix+'ForkPinCap',prefix+'SliderKnob']],x,0,z,0,1,0,math.radians(angle))
occ.synchronize();before=sum(occ.getMass(*dt) for dt in gmsh.model.getEntities(3));f=P/'EarDefender_V14_child_large_V15FoldExperiment.step';gmsh.write(str(f));gmsh.finalize()
out={'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source':row['file'],'source_sha256':row['sha256'],'part_geometry_revision':'V14','pose_study_revision':'V15','expected_solids':44,'before_export_volume_mm3':before,'expected_volume_mm3':sum(row['part_volumes_mm3'].values())-.4*sum(row['part_volumes_mm3'][n+'SpringSpace'] for n in ['Left','Right']),'extension_mm':[0,20],'angles_deg':[30,60],'held_release_stroke_mm':6,'manufacturing_release':False};(O/'child_large_pose_export.json').write_text(json.dumps(out,indent=2));print(f)
