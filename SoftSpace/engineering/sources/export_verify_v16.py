"""Export and independently reimport the six selected wear, release and folded poses."""
import os,json,math,hashlib,sys
os.environ['OPENBLAS_NUM_THREADS']='1'
from v12_geometry import P,gmsh,import_parts
from audit_v14_motion import mass,bounds,STEPControl_Reader,TopExp_Explorer,TopAbs_SOLID,BRepCheck_Analyzer
O=P/'engineering-v16-results';selected=json.loads((O/'selected_candidates.json').read_text());recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())};exports=[]
for row in selected['sizes']:
 size=row['size'];variant=row['variant'];R=recipes[size]['band_halfspan_mm'];upper=row.get('layout','lower index plate').startswith('upper')
 for phase in ['Wear','Released','FoldedEngaged']:
  gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;parts=import_parts(row)
  if phase=='Released':
   for side,prefix in [(-1,'Left'),(1,'Right')]:
    occ.translate([parts[prefix+n] for n in ['LockPin','PullKnob','KnobCrossRivet']],0,-6,0);occ.remove([parts[prefix+'SpringSpace']],recursive=True);a=(3,occ.addCylinder(side*(R+10),-30,60,0,9,0,3.175));b=(3,occ.addCylinder(side*(R+10),-31,60,0,11,0,2.825));result,_=occ.cut([a],[b]);assert len(result)==1;parts[prefix+'SpringSpace']=result[0]
    if upper:occ.translate([parts[prefix+'SpringSpace']],-side*10,-8,17)
  if phase=='FoldedEngaged':
   for side,prefix,e,angle in [(-1,'Left',row['fold_extension_mm'][0],-row['fold_angles_deg'][0]),(1,'Right',row['fold_extension_mm'][1],row['fold_angles_deg'][1])]:
    shift=15-e;occ.translate([dt for k,dt in parts.items() if k.startswith(prefix) and not k.endswith('SliderKnob')],0,0,shift);occ.rotate([dt for k,dt in parts.items() if k.startswith(prefix) and k not in [prefix+'Tongue',prefix+'ForkPin',prefix+'ForkPinCap',prefix+'SliderKnob']],side*R,0,65+shift,0,1,0,math.radians(angle))
  occ.synchronize();f=P/('EarDefender_V16_'+variant+'_'+phase+'.step');before=sum(occ.getMass(*dt) for dt in gmsh.model.getEntities(3));gmsh.write(str(f));gmsh.finalize()
  expected=sum(row['part_volumes_mm3'].values())-(.4*sum(row['part_volumes_mm3'][p+'SpringSpace'] for p in ['Left','Right']) if phase=='Released' else 0);digest=hashlib.sha256(f.read_bytes()).hexdigest();reader=STEPControl_Reader();reader.ReadFile(str(f));reader.TransferRoots();shape=reader.OneShape();e=TopExp_Explorer(shape,TopAbs_SOLID);solids=[]
  while e.More():solids.append(e.Current());e.Next()
  volumes=[mass(s) for s in solids];valid=all(BRepCheck_Analyzer(s).IsValid() for s in solids);b=bounds(shape);dims=[b[k+3]-b[k] for k in range(3)];error=None
  if phase=='FoldedEngaged':intended=next(r for r in selected['packing'] if r['size']==size)['folded_pins_engaged_box_mm'];error=max(abs(a-b) for a,b in zip(dims,intended))
  r={'size':size,'variant':variant,'phase':phase,'file':str(f),'sha256':digest,'source_sha256':row['sha256'],'solid_count':len(solids),'all_valid':valid,'minimum_volume_mm3':min(volumes),'volume_difference_from_analytic_mm3':abs(sum(volumes)-expected),'roundtrip_volume_error_mm3':abs(sum(volumes)-before),'box_mm':dims,'intended_pose_box_error_mm':error,'pass':len(solids)==46 and valid and min(volumes)>0 and abs(sum(volumes)-expected)<.01 and abs(sum(volumes)-before)<.01 and (error is None or error<.02)};exports.append(r);(O/'STEP_verification_partial.json').write_text(json.dumps(exports,indent=2));print(json.dumps({'variant':variant,'phase':phase,'pass':r['pass']}),flush=True)
out={'case_count':len(exports),'all_pass':len(exports)==18 and all(r['pass'] for r in exports),'cases':exports,'scope':'Independent OCP reimport counts validity volumes and folded box only; not native Fusion archives or physical validation'};(O/'STEP_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({'case_count':len(exports),'all_pass':out['all_pass']}))
