"""Search existing V14 rigid parts before changing any folding hardware.
Bounding-box ranking is not a collision pass; check shortlisted original shapes.
"""
import json,sys,math,time,heapq
from audit_v14_motion import P,cad,recipes,load,bounds,moved,rotate,unlocked,check,common
O=P/'engineering-v15-results';O.mkdir(exist_ok=True)
size=sys.argv[1];row=next(r for r in cad['sizes'] if r['size']==size)
parts,controls=load(row);R=recipes[size]['band_halfspan_mm'];base=unlocked(parts,R,6)
left=[k for k in base if k.startswith('Left') and k not in ['LeftTongue','LeftForkPin','LeftForkPinCap','LeftSliderKnob']]
right=[k for k in base if k.startswith('Right') and k not in ['RightTongue','RightForkPin','RightForkPinCap','RightSliderKnob']]
lt=['LeftTongue','LeftForkPin','LeftForkPinCap'];rt=['RightTongue','RightForkPin','RightForkPinCap']
fixed=[k for k in base if k not in left+right+lt+rt]
groups={k:1 if k in left else 2 if k in right else 3 if k in lt else 4 if k in rt else 0 for k in base}
def union(boxes):return [min(b[k] for b in boxes) for k in range(3)]+[max(b[k] for b in boxes) for k in range(3,6)]
def shift(b,dz):return [b[0],b[1],b[2]+dz,b[3],b[4],b[5]+dz]
def volume(b):return math.prod(b[k+3]-b[k] for k in range(3))
def dimensions(b):return [b[k+3]-b[k] for k in range(3)]
fixedbox=union([bounds(base[k]) for k in fixed]);ltbox=union([bounds(base[k]) for k in lt]);rtbox=union([bounds(base[k]) for k in rt])
angleboxes={}
for side,keys in [(-1,left),(1,right)]:
 for a in range(0,121,5):angleboxes[side,a]=union([bounds(rotate(base[k],side*R,65,side*a)) for k in keys])
def box(el,er,al,ar):return union([fixedbox,shift(ltbox,15-el),shift(rtbox,15-er),shift(angleboxes[-1,al],15-el),shift(angleboxes[1,ar],15-er)])
nominal=union([bounds(s) for s in parts.values()]);retracted=union([bounds(moved(s,(0,0,15))) if k.startswith(('Left','Right')) and not k.endswith('SliderKnob') else bounds(s) for k,s in parts.items()])
short=[];count=0
for el in range(0,31,5):
 for er in range(0,31,5):
  for al in range(0,121,5):
   for ar in range(0,121,5):
    b=box(el,er,al,ar);count+=1
    # retain the best two extension pairs for each distinct angle pair
    short.append((volume(b),el,er,al,ar,b))
short.sort();selected=[];seen=set()
for predicate,quota in [(lambda t:abs(t[1]-t[2])>=20,24),(lambda t:max(t[3],t[4])<=75,12),(lambda t:True,12)]:
 added=0;angles=set()
 for item in short:
  key=tuple(item[1:5]);angle=(item[3],item[4])
  if key in seen or angle in angles or not predicate(item):continue
  seen.add(key);angles.add(angle);selected.append(item);added+=1
  if added>=quota:break
fallback=[]
for al,ar in [(60,45),(45,60),(60,30),(30,60),(45,45),(30,30)]:
 for el,er in [(0,30),(30,0),(0,20),(20,0)]:
  b=box(el,er,al,ar);fallback.append((volume(b),el,er,al,ar,b))
for item in sorted(fallback):
 if tuple(item[1:5]) not in seen:selected.append(item)
def pose(el,er,al,ar):
 return {k:moved(rotate(s,-R,65,-al),(0,0,15-el)) if k in left else moved(rotate(s,R,65,ar),(0,0,15-er)) if k in right else moved(s,(0,0,15-el)) if k in lt else moved(s,(0,0,15-er)) if k in rt else s for k,s in base.items()}
def endpoint(q):
 # Reject a known positive collision early, then perform the complete group check.
 for a,b in [('LeftContinuousCover','RightContinuousCover'),('LeftCup','RightCup'),('Band','LeftCup'),('Band','RightCup')]:
  if a not in q or b not in q:continue
  ba,bb=bounds(q[a]),bounds(q[b])
  if any(min(ba[k+3],bb[k+3])-max(ba[k],bb[k])<1e-5 for k in range(3)):continue
  v=common(q[a],q[b])
  if v>.01:return {'pass':False,'overlaps':[{'parts':[a,b],'intersection_mm3':v}],'errors':[],'early_collision_rejection':True}
 return check(q,groups)
previous=O/(size+'_packing_search.json')
results=[];best=None
if previous.exists():
 old=json.loads(previous.read_text());assert old['source_sha256']==row['sha256'];results=old['shortlisted_pose_checks']
done={tuple(r['extension_mm']+r['angles_deg']) for r in results}
for v,el,er,al,ar,b in selected:
 if (el,er,al,ar) in done:continue
 r=endpoint(pose(el,er,al,ar));r.update(extension_mm=[el,er],angles_deg=[al,ar],box_mm=dimensions(b),box_volume_mm3=v,reduction_from_nominal_percent=100*(1-v/volume(nominal)),reduction_from_retracted_percent=100*(1-v/volume(retracted)));results.append(r)
 (O/(size+'_packing_checkpoint.json')).write_text(json.dumps(results,indent=2))
 print(json.dumps({'size':size,'shortlist_checked':len(results),'pose_pass':r['pass'],'angles':[al,ar],'extension':[el,er]}),flush=True)
 if r['pass']:best=r;break
out={'revision':'V15 packing experiment on unchanged V14 CAD','size':size,'source':row['file'],'source_sha256':row['sha256'],'ranked_pose_count':count,'shortlisted_pose_checks':results,'best_clear_endpoint':best,'nominal_box_mm':dimensions(nominal),'retracted_unfolded_box_mm':dimensions(retracted),'source_solid_validity':controls,'limits':['Finite endpoint search only; not a continuous folding path','Original V14 geometry and mechanism unchanged','No force contact pinch access physical carrying or durability validation','Baseline nominal extension15mm; also compare fully retracted unfolded pose to avoid attributing slider shrinkage to folding']}
(O/(size+'_packing_search.json')).write_text(json.dumps(out,indent=2));print(json.dumps({'size':size,'best':best}))
