"""Motion and positive locking-query controls using original located solids."""
import json,sys,math,os
from audit_v14_motion import P,load,check,unlocked,moved,rotate,common,mass,recipes,gp_Pnt
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
O=P/os.environ.get('EAR_DEFENDER_AUDIT_RESULTS','engineering-v16-results');variant=sys.argv[1] if len(sys.argv)>1 else 'child_large';row=json.loads((O/(variant+'_cad_report.json')).read_text());size=row['size'];L,T=row['fold_angles_deg'];EL,ER=row['fold_extension_mm'];parts,validity=load(row);R=recipes[size]['band_halfspan_mm'];left=[k for k in parts if k.startswith('Left') and k not in ['LeftTongue','LeftForkPin','LeftForkPinCap','LeftSliderKnob']];right=[k for k in parts if k.startswith('Right') and k not in ['RightTongue','RightForkPin','RightForkPinCap','RightSliderKnob']];lt=['LeftTongue','LeftForkPin','LeftForkPinCap'];rt=['RightTongue','RightForkPin','RightForkPinCap']
out={'revision':row.get('revision','V16 indexed fold and cross-rivet pilot'),'size':size,'source':row['file'],'source_sha256':row['sha256'],'solid_validity':validity,'cases':[],'limits':['Discrete motion and geometric blocking only; no stress, fatigue, friction, spring return or physical handling qualification','Space allocations for springs are not actual coils','One pilot; no six-size qualification','Index pin does not establish hard travel stops outside the indexed positions']}
out['limits'][2]='One '+size+' '+variant+' pilot; this record alone does not establish a six-size pass'
def persist(): (O/(variant+'_audit_checkpoint.json')).write_text(json.dumps(out,indent=2))
upper=row.get('layout','').startswith('upper')
cube=BRepPrimAPI_MakeBox(gp_Pnt(R+3 if upper else R+8,-15.75 if upper else -7.75,71 if upper else 56),1,1,1).Shape();v=common(parts['RightTongue'],cube);d=common(parts['RightTongue'],moved(cube,(0,100,0)));rv=common(rotate(parts['RightTongue'],R,65,60),rotate(cube,R,65,60));out['new_plate_query_controls']={'embedded_cube_mm3':v,'disjoint_cube_mm3':d,'rotated_embedded_cube_mm3':rv,'pass':abs(v-1)<1e-5 and d<1e-5 and abs(rv-1)<1e-5};persist();assert out['new_plate_query_controls']['pass']
def pose(el,er,stroke=0,la=0,ra=0):
 q=unlocked(parts,R,stroke)
 for side,prefix in [(-1,'Left'),(1,'Right')]:
  q[prefix+'KnobCrossRivet']=moved(parts[prefix+'KnobCrossRivet'],(0,-stroke,0))
  if upper:q[prefix+'SpringSpace']=moved(q[prefix+'SpringSpace'],(-side*10,-8,17))
 return {k:moved(rotate(s,-R,65,-la),(0,0,15-el)) if k in left else moved(rotate(s,R,65,ra),(0,0,15-er)) if k in right else moved(s,(0,0,15-el)) if k in lt else moved(s,(0,0,15-er)) if k in rt else s for k,s in q.items()}
def sample(phase,el=15,er=15,stroke=0,la=0,ra=0):
 q=pose(el,er,stroke,la,ra)
 if phase=='nominal':groups=None
 elif phase=='adjustment':groups={k:1 if k.startswith('Left') and not k.endswith('SliderKnob') else 2 if k.startswith('Right') and not k.endswith('SliderKnob') else 0 for k in q}
 elif phase=='release' or phase=='folded return':groups={k:i+1 if k.endswith(('LockPin','PullKnob','KnobCrossRivet','SpringSpace')) else 0 for i,k in enumerate(q)}
 else:groups={k:1 if k in left else 2 if k in right else 3 if k in lt else 4 if k in rt else 0 for k in q}
 r=check(q,groups);r.update(phase=phase,extension_mm=[el,er],stroke_mm=stroke,angles_deg=[la,ra]);out['cases'].append(r);persist();print(json.dumps({'phase':phase,'angles':[la,ra],'stroke':stroke,'pass':r['pass'],'overlaps':r['overlaps']}),flush=True);return r['pass']
ok=sample('nominal')
if ok:
 for el in [10,5,0]:
  if not sample('adjustment',el,15):ok=False;break
if ok:
 for er in range(20,ER+1,5):
  if not sample('adjustment',EL,er):ok=False;break
if ok:
 for stroke in [0,2,4,6]:
  if not sample('release',EL,ER,stroke):ok=False;break
if ok:
 for la,ra in [(a,0) for a in range(0,L+1,5)]+[(L,a) for a in range(5,T+1,5)]:
  if not sample('folding',EL,ER,6,la,ra):ok=False;break
if ok:
 for stroke in [4,2,0]:
  if not sample('folded return',EL,ER,stroke,L,T):ok=False;break
blocking=[]
if ok:
 for state,el,er,la,ra in [('wear',15,15,0,0),('folded',EL,ER,L,T)]:
  for prefix in ['Left','Right']:
   for delta in [-1,1]:
    q=pose(el,er,0,la+delta if prefix=='Left' else la,ra+delta if prefix=='Right' else ra);v=common(q[prefix+'LockPin'],q[prefix+'Tongue']);blocking.append({'state':state,'side':prefix,'angular_attempt_deg':delta,'pin_plate_interference_mm3':v,'geometric_block_detected':v>.01})
 # Capture is tested by attempting motion, expecting a positive blocked volume.
 retention=[]
 for prefix in ['Left','Right']:
  for delta in [-.2,.2]:
   v=common(moved(parts[prefix+'KnobCrossRivet'],(delta,0,0)),parts[prefix+'PullKnob']);retention.append({'side':prefix,'attempt':'cross rivet sideways','delta_mm':delta,'interference_mm3':v,'geometric_block_detected':v>.001})
  v=common(moved(parts[prefix+'KnobCrossRivet'],(0,-.2,0)),parts[prefix+'LockPin']);retention.append({'side':prefix,'attempt':'knob and rivet outward along release stem','delta_mm':-.2,'interference_mm3':v,'geometric_block_detected':v>.001})
 out['retention_blocking']=retention
out.update(case_count=len(out['cases']),complete_sampled_motion_pass=ok,index_blocking=blocking,index_blocking_pass=bool(blocking) and all(r['geometric_block_detected'] for r in blocking),retention_blocking_pass=bool(out.get('retention_blocking')) and all(r['geometric_block_detected'] for r in out.get('retention_blocking',[])))
if ok:
 from audit_v14_motion import bounds
 def dimensions(q):
  b=[bounds(s) for s in q.values()];return [max(x[k+3] for x in b)-min(x[k] for x in b) for k in range(3)]
 n=dimensions(parts);r=dimensions(pose(0,0));f=dimensions(pose(EL,ER,0,L,T));out['packing']={'nominal_box_mm':n,'retracted_box_mm':r,'folded_pins_engaged_box_mm':f,'reduction_from_retracted_percent':100*(1-math.prod(f)/math.prod(r)),'reduction_from_nominal_percent':100*(1-math.prod(f)/math.prod(n))}
out['variant']=variant
(O/(variant+'_audit.json')).write_text(json.dumps(out,indent=2));print(json.dumps({k:out[k] for k in ['case_count','complete_sampled_motion_pass','index_blocking_pass','retention_blocking_pass']}))
