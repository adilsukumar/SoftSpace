import json,hashlib
from audit_v14_motion import P,load,mass
O=P/'engineering-v17-results';rows=[]
for size in ['child_large','adult_small']:
 r=json.loads((O/(size+'_Entry25_cad_report.json')).read_text());p,v=load(r);deltas={n:abs(mass(p[n])-r['part_volumes_mm3'][n]) for n in p};rows.append({'variant':r['variant'],'file':r['file'],'sha256':hashlib.sha256(__import__('pathlib').Path(r['file']).read_bytes()).hexdigest(),'solid_count':len(v),'all_valid':all(x['pass'] for x in v),'maximum_part_volume_roundtrip_error_mm3':max(deltas.values()),'pass':len(v)==46 and all(x['pass'] for x in v) and max(deltas.values())<.01})
out={'cases':rows,'all_pass':all(r['pass'] for r in rows),'scope':'Independent OCP import, validity and per-part volume checks on two pilot STEP files'};(O/'STEP_verification.json').write_text(json.dumps(out,indent=2));print(out);assert out['all_pass']
