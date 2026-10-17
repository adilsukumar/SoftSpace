import sys,json
from audit_v14_motion import P,load,check,moved,rotate,common,recipes,bounds
O=P/'engineering-v19-results'/'final-CAD';size=sys.argv[1];row=json.loads((O/(size+'_cad_report.json')).read_text());parts,valid=load(row);R=recipes[size]['band_halfspan_mm'];pivot=row['pivot_z_mm'];cases=[]
def pose(el=15,er=15,la=0,ra=0):
 q={}
 for name,shape in parts.items():
  if name.startswith(('Left','Right')) and not name.endswith('SliderKnob'):
   side=-1 if name.startswith('Left') else 1;e=el if side<0 else er;angle=-la if side<0 else ra
   if name.endswith(('Fork','MainFoam','SoftGlassesZone','ContinuousCover','Carrier','Cup','Liner','CupPin','CupPinCap')):shape=rotate(shape,side*R,pivot,angle)
   shape=moved(shape,(0,0,15-e))
  q[name]=shape
 return q
def sample(phase,el=15,er=15,la=0,ra=0):
 q=pose(el,er,la,ra)
 if phase=='nominal':groups=None
 elif phase=='adjustment':groups={k:1 if k.startswith('Left') and not k.endswith('SliderKnob') else 2 if k.startswith('Right') and not k.endswith('SliderKnob') else 0 for k in q}
 else:groups={k:1 if k.startswith('Left') and k.endswith(('Fork','MainFoam','SoftGlassesZone','ContinuousCover','Carrier','Cup','Liner','CupPin','CupPinCap')) else 2 if k.startswith('Right') and k.endswith(('Fork','MainFoam','SoftGlassesZone','ContinuousCover','Carrier','Cup','Liner','CupPin','CupPinCap')) else 0 for k in q}
 r=check(q,groups);r.update(phase=phase,extensions_mm=[el,er],angles_deg=[la,ra]);cases.append(r);print(json.dumps({'phase':phase,'angles':[la,ra],'pass':r['pass'],'overlaps':r['overlaps']}),flush=True);return r['pass']
ok=sample('nominal');L,T=row['fold_angles_deg'];EL,ER=row['fold_extension_mm']
if ok:
 for e in [0,5,10,20,25,30]:
  if not sample('adjustment',e,e):ok=False;break
if ok:
 for a,b in [(a,0) for a in range(0,L+1,5)]+[(L,b) for b in range(5,T+1,5)]:
  if not sample('folding',EL,ER,a,b):ok=False;break
stops=[]
for prefix,side in [('Left',-1),('Right',1)]:
 for angle in [-.1,-1]:
  v=common(rotate(parts[prefix+'Fork'],side*R,pivot,side*angle),parts[prefix+'Tongue']);stops.append({'side':prefix,'outward_attempt_deg':angle,'intersection_mm3':v,'block_detected':v>1e-5})
def dims(q):
 b=[bounds(s) for s in q.values()];return [max(x[i+3] for x in b)-min(x[i] for x in b) for i in range(3)]
out={'revision':'V19 parallel disc candidate','size':size,'source_sha256':row['sha256'],'validity':valid,'case_count':len(cases),'cases':cases,'sampled_motion_pass':ok,'wearing_stop_queries':stops,'wearing_stop_blocking_pass':all(r['block_detected'] for r in stops),'nominal_box_mm':dims(parts),'retracted_box_mm':dims(pose(0,0)),'folded_box_mm':dims(pose(EL,ER,L,T)),'limits':['Finite rigid geometry checks; no loaded stop force or friction torque proof','No slider clamp,thread preload,unwanted angle movement,pinch or actual handling qualification']};(O/(size+'_motion_audit.json')).write_text(json.dumps(out,indent=2));print(json.dumps({'samples':len(cases),'motion_pass':ok,'stop_pass':out['wearing_stop_blocking_pass']}))
