import json,math
from audit_v14_motion import P,load,common,moved
O=P/'engineering-v17-results';cases=[];sources=[]
for size in ['child_large','adult_small']:
 row=json.loads((O/(size+'_Entry25_cad_report.json')).read_text());parts,_=load(row);upper=row['layout'].startswith('upper');direction=(1,0,0) if upper else (5/math.sqrt(125),0,10/math.sqrt(125));sources.append({'file':row['file'],'sha256':row['sha256']})
 for prefix in ['Left','Right']:
  for offset,stroke,expected in [(.0,0,False),(.14,0,False),(.16,0,True),(.3,2.9,False),(.3,2.8,True),(.3,0,True)]:
   v=common(moved(parts[prefix+'LockPin'],tuple(offset*d-(stroke if i==1 else 0) for i,d in enumerate(direction))),parts[prefix+'Tongue']);cases.append({'variant':row['variant'],'side':prefix,'offset_mm':offset,'release_stroke_mm':stroke,'interference_mm3':v,'expected_interference':expected,'matches_expectation':v>1e-5 if expected else v<1e-5})
out={'sources':sources,'case_count':len(cases),'all_match':all(c['matches_expectation'] for c in cases),'cases':cases,'limits':['Wear position pin versus tongue only','Entry may admit an offset tip but cannot force the rest of an offset pin through the straight land','No friction force or spring centering behavior solved']};(O/'entry_geometry_validation.json').write_text(json.dumps(out,indent=2));print(json.dumps({'cases':len(cases),'all_match':out['all_match']}));assert out['all_match']
