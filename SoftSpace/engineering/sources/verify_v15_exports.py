import json,hashlib
from audit_v14_motion import P,mass,bounds,STEPControl_Reader,TopExp_Explorer,TopAbs_SOLID,BRepCheck_Analyzer
O=P/'engineering-v15-results';pilot=json.loads((O/'adult_small_retention_cad.json').read_text());fold=json.loads((O/'child_large_pose_export.json').read_text());rows=[]
for row in [pilot,fold]:
 f=row['file'];assert hashlib.sha256(__import__('pathlib').Path(f).read_bytes()).hexdigest()==row['sha256'];reader=STEPControl_Reader();reader.ReadFile(f);reader.TransferRoots();shape=reader.OneShape();explorer=TopExp_Explorer(shape,TopAbs_SOLID);solids=[]
 while explorer.More():solids.append(explorer.Current());explorer.Next()
 volumes=[mass(s) for s in solids];expected=sum(row['part_volumes_mm3'].values()) if row is pilot else row['expected_volume_mm3'];difference=abs(sum(volumes)-expected);b=bounds(shape);dims=[b[k+3]-b[k] for k in range(3)];valid=all(BRepCheck_Analyzer(s).IsValid() for s in solids)
 pose_error=None
 if row is fold:
  review=json.loads((O/'packing_review.json').read_text());intended=next(r['best_recorded_box_mm'] for r in review['sizes'] if r['size']=='child_large');pose_error=max(abs(a-b) for a,b in zip(dims,intended))
 rows.append({'file':f,'sha256':row['sha256'],'solid_count':len(solids),'valid_solids':valid,'minimum_volume_mm3':min(volumes),'total_volume_difference_mm3':difference,'box_mm':dims,'intended_pose_box_max_error_mm':pose_error,'pass':len(solids)==(46 if row is pilot else 44) and valid and min(volumes)>0 and difference<.01 and (pose_error is None or pose_error<.02)})
out={'case_count':len(rows),'all_pass':all(r['pass'] for r in rows),'cases':rows,'scope':'Independent OCP reimport count validity volume conservation and intended fold box, not physical validation or real threads'};(O/'STEP_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
