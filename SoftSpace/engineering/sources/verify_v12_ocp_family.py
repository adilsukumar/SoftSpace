import json
from audit_v12_ocp import O,cad,recipes,load,moved,mass,BRepAlgoAPI_Cut,common
rows=[]
for family in ['adult','child']:
 ref=next(r for r in cad['sizes'] if r['size']==family+'_small');p,_=load(ref);a=moved(p['RightFork'],(-recipes[ref['size']]['band_halfspan_mm'],0,0))
 for row in [r for r in cad['sizes'] if r['size'].startswith(family)]:
  q,_=load(row);b=moved(q['RightFork'],(-recipes[row['size']]['band_halfspan_mm'],0,0));vols=[]
  for x,y in [(a,b),(b,a)]:
   cut=BRepAlgoAPI_Cut(x,y);assert cut.IsDone();vols.append(mass(cut.Shape()))
  v=common(a,b);rows.append({'reference':ref['size'],'compared':row['size'],'symmetric_difference_mm3':sum(vols),'common_mm3':v,'reference_volume_mm3':mass(a),'pass':sum(vols)<.01 and abs(v-mass(a))<.01})
out={'checks':rows,'all_pass':all(r['pass'] for r in rows),'method':'OCP original solids with location transforms, no deep geometric copies','scope':'Two translated right fork geometry families only. Does not transfer a complete assembly or left-side load test.'};(O/'fork_family_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
