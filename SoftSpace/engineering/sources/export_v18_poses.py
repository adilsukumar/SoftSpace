"""Three saved poses per size, independently reimported using OCP."""
import os,json,math,hashlib
os.environ['OPENBLAS_NUM_THREADS']='1'
from v12_geometry import P,gmsh,import_parts
from audit_v14_motion import mass,bounds,STEPControl_Reader,TopExp_Explorer,TopAbs_SOLID,BRepCheck_Analyzer
O=P/'engineering-v18-results';recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())};records=[]
for f in sorted(O.glob('*_cad_report.json')):
 row=json.loads(f.read_text());size=row['size'];R=recipes[size]['band_halfspan_mm'];audit=json.loads((O/(size+'_motion_audit.json')).read_text());assert audit['sampled_motion_pass'] and audit['wearing_stop_blocking_pass']
 for phase in ['Wear','Retracted','Folded']:
  gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;parts=import_parts(row)
  if phase!='Wear':
   for i,prefix,side in [(0,'Left',-1),(1,'Right',1)]:
    e=0 if phase=='Retracted' else row['fold_extension_mm'][i];shift=15-e
    if phase=='Folded':occ.rotate([dt for n,dt in parts.items() if n.startswith(prefix) and n.endswith(('Fork','MainFoam','SoftGlassesZone','ContinuousCover','Carrier','Cup','Liner','CupPin','CupPinCap'))],side*R,0,row['pivot_z_mm'],0,1,0,math.radians(side*row['fold_angles_deg'][i]))
    occ.translate([dt for n,dt in parts.items() if n.startswith(prefix) and not n.endswith('SliderKnob')],0,0,shift)
  occ.synchronize();target=P/('EarDefender_V18_'+size+'_'+phase+'.step');before=sum(occ.getMass(*s) for s in gmsh.model.getEntities(3));gmsh.write(str(target));gmsh.finalize()
  reader=STEPControl_Reader();reader.ReadFile(str(target));reader.TransferRoots();shape=reader.OneShape();e=TopExp_Explorer(shape,TopAbs_SOLID);solids=[]
  while e.More():solids.append(e.Current());e.Next()
  vols=[mass(s) for s in solids];b=bounds(shape);dims=[b[k+3]-b[k] for k in range(3)];expected=audit[{'Wear':'nominal_box_mm','Retracted':'retracted_box_mm','Folded':'folded_box_mm'}[phase]];error=max(abs(a-b) for a,b in zip(dims,expected));valid=all(BRepCheck_Analyzer(s).IsValid() for s in solids)
  rec=dict(size=size,phase=phase,file=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),source_sha256=row['sha256'],solid_count=len(solids),all_valid=valid,box_mm=dims,box_error_mm=error,volume_error_mm3=abs(sum(vols)-before),pass_result=len(solids)==38 and valid and min(vols)>0 and abs(sum(vols)-before)<.01 and error<.02);records.append(rec);(O/'STEP_verification_partial.json').write_text(json.dumps(records,indent=2));print(size,phase,rec['pass_result'],flush=True)
out=dict(case_count=len(records),all_pass=len(records)==18 and all(r['pass_result'] for r in records),cases=records,scope='OCP import checks count validity volume and pose bounds. No native Fusion feature tree or physical validation.');(O/'STEP_verification.json').write_text(json.dumps(out,indent=2))
