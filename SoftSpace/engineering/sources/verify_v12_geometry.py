"""Independent STEP roundtrip and exact translated fork family checks."""
import json,hashlib
from v12_geometry import P,O,gmsh,import_parts
cad=json.loads((O/'cad_report.json').read_text());recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())};exports=[];families=[]
for row in cad['sizes']:
 for phase in ['Latched','Released','Folded']:
  f=P/('EarDefender_V12_'+row['size']+'_'+phase+'.step')
  if not f.exists():continue
  gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;occ.importShapes(str(f));occ.synchronize();solids=gmsh.model.getEntities(3);volumes=[occ.getMass(*dt) for dt in solids];expect=sum(row['part_volumes_mm3'].values())
  if phase!='Latched':expect-=.4*sum(row['part_volumes_mm3'][p+'SpringSpace'] for p in ['Left','Right'])
  diff=abs(sum(volumes)-expect);exports.append({'size':row['size'],'phase':phase,'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'solid_count':len(solids),'minimum_volume_mm3':min(volumes),'total_volume_mm3':sum(volumes),'expected_total_volume_mm3':expect,'volume_difference_mm3':diff,'pass':len(solids)==32 and min(volumes)>0 and diff<.01});gmsh.finalize()
# Keep only fork solids, move them to the same datum, then compare differences.
for family in ['adult','child']:
 reference=next(r for r in cad['sizes'] if r['size']==family+'_small')
 for row in [r for r in cad['sizes'] if r['size'].startswith(family)]:
  gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;parts=import_parts(reference);ref=parts['RightFork'];occ.remove([v for k,v in parts.items() if k!='RightFork'],recursive=True);occ.translate([ref],-recipes[reference['size']]['band_halfspan_mm'],0,0);occ.synchronize()
  # A second model avoids stale names and tags from the first import.
  old=set(gmsh.model.getEntities(3));occ.importShapes(row['file']);occ.synchronize();new=[dt for dt in gmsh.model.getEntities(3) if dt not in old];e=row['part_bounds_mm']['RightFork'];matches=[dt for dt in new if max(abs(a-b) for a,b in zip(gmsh.model.getBoundingBox(*dt),e))<.01 and abs(occ.getMass(*dt)-row['part_volumes_mm3']['RightFork'])<.005];assert len(matches)==1;other=matches[0];occ.remove([dt for dt in new if dt!=other],recursive=True);occ.translate([other],-recipes[row['size']]['band_halfspan_mm'],0,0);occ.synchronize()
  diffs=[]
  for a,b in [(ref,other),(other,ref)]:
   out,_=occ.cut(occ.copy([a]),occ.copy([b]));diffs.append(sum(occ.getMass(*dt) for dt in out if dt[0]==3))
   if out:occ.remove(out,recursive=True)
  families.append({'family':family,'reference_size':reference['size'],'compared_size':row['size'],'symmetric_difference_mm3':sum(diffs),'pass':sum(diffs)<.01});gmsh.finalize()
out={'status':'complete for exported files present at execution','exports':exports,'export_count':len(exports),'all_exports_pass':all(r['pass'] for r in exports),'fork_family_checks':families,'all_fork_family_checks_pass':all(r['pass'] for r in families),'scope':'Positive volume, count and volume conservation on independently imported STEP files; translated right-fork equivalence only. Does not validate mechanism strength or physical manufacture.'}
(O/'export_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({'exports':len(exports),'all_exports_pass':out['all_exports_pass'],'fork_family_checks':families}))
