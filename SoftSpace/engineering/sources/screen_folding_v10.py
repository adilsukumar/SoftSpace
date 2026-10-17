"""Explore existing fork pivots as folding axes; retain failed poses."""
from pathlib import Path
import sys,json,math,hashlib
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh
O=P/'engineering-v11-results';O.mkdir(exist_ok=True)
n=json.loads((P/'engineering-v10-results'/'cad_native_report.json').read_text());recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())}
mode='cup' if 'cup' in sys.argv else 'fork'
stagger='stagger' in sys.argv;max_fold=75 if 'partial' in sys.argv else 90;label=mode+('_stagger' if stagger else '')+('_75' if max_fold==75 else '')
adaptive='adaptive' in sys.argv
if adaptive:label='fork_stagger_adaptive'
rows=[]
for size in (list(recipes) if 'all' in sys.argv else ['adult_small','child_small']):
 if adaptive:
  failed=[r['size'] for r in json.loads((O/'folding_summary.json').read_text())['sizes'] if not r['target_path_samples_pass']]
  if size not in failed:continue
  max_fold=60
 source=Path(next(f for f in n['files'] if '_'+size+'_' in f and f.endswith('.step') and 'Extension' not in f));R=recipes[size]['band_halfspan_mm']
 for la,ra in ([(a,0) for a in range(0,max_fold+1,15)]+[(max_fold,a) for a in range(15,max_fold+1,15)] if stagger else [(0,0),(15,15),(30,30),(45,45),(60,60),(75,75),(90,90),(90,0),(0,90)]):
  gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;occ.importShapes(str(source));occ.synchronize();bodies=gmsh.model.getEntities(3);assert len(bodies)==28
  original_bounds=[gmsh.model.getBoundingBox(*dt) for dt in bodies]
  nominal_dims=[max(b[k+3] for b in original_bounds)-min(b[k] for b in original_bounds) for k in range(3)]
  # Native STEP ordering verified against the recorded per-body bounds and V8 builder order.
  left=[(3,i) for i in [1,2,3,4,5,6,7,9,10]];right=[(3,i+12) for i in [1,2,3,4,5,6,7,9,10]]
  if mode=='cup':left=[(3,i) for i in range(1,7)];right=[(3,i) for i in range(13,19)]
  if stagger:
   occ.translate([(3,i) for i in range(1,13)],0,0,15)
   occ.translate([(3,i) for i in range(13,25)],0,0,-15);occ.synchronize()
  for group,side,angle in [(left,-1,la),(right,1,ra)]:
   assert all((lambda b:(b[0]+b[3])*side>0)(gmsh.model.getBoundingBox(*dt)) for dt in group)
   occ.rotate(group,side*(R+20 if mode=='cup' else R),0,(35 if mode=='cup' else 65)+(-side*15 if stagger else 0),0,1,0,side*math.radians(angle))
  occ.synchronize();bounds={dt:gmsh.model.getBoundingBox(*dt) for dt in bodies};errors=[];overlaps=[]
  for i,a in enumerate(bodies):
   for b in bodies[i+1:]:
    ga=0 if a in left else (1 if a in right else 2);gb=0 if b in left else (1 if b in right else 2)
    if ga==gb and (la or ra):continue
    ba,bb=bounds[a],bounds[b]
    if any(min(ba[k+3],bb[k+3])-max(ba[k],bb[k])<1e-5 for k in range(3)):continue
    out=[]
    try:
     out,_=occ.intersect(occ.copy([a]),occ.copy([b]),removeObject=True,removeTool=True);volume=sum(occ.getMass(*dt) for dt in out if dt[0]==3)
     if volume>.01:overlaps.append({'tags':[a[1],b[1]],'intersection_mm3':volume})
    except Exception as e:errors.append(str(e))
    finally:
     if out:occ.remove(out,recursive=True)
  lo=[min(b[k] for b in bounds.values()) for k in range(3)];hi=[max(b[k+3] for b in bounds.values()) for k in range(3)];dims=[b-a for a,b in zip(lo,hi)]
  row={'size':size,'left_fold_deg':la,'right_fold_deg':ra,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'bounding_box_dimensions_mm':dims,'bounding_box_volume_L':math.prod(dims)/1e6,'overlaps':overlaps,'errors':errors,'nominal_pose_pass':not overlaps and not errors}
  row['original_nominal_bbox_mm']=nominal_dims;row['original_nominal_bbox_L']=math.prod(nominal_dims)/1e6
  if not overlaps and not errors and (la or ra):
   target=P/('FoldingStudy_V11_'+label+'_'+size+'_L'+str(la)+'_R'+str(ra)+'.step');gmsh.write(str(target));row['candidate_STEP']=str(target)
  rows.append(row);gmsh.finalize();(O/('folding_'+label+'_partial.json')).write_text(json.dumps(rows,indent=2));print(json.dumps({'size':size,'L':la,'R':ra,'clashes':len(overlaps),'pose_pass':row['nominal_pose_pass'],'bbox_L':row['bounding_box_volume_L']}),flush=True)
out={'status':'complete exploratory screen','cases':rows,'limits':['Two sizes only; existing fork pivots explored without a new hinge','Sampled rigid poses, not continuous folding paths or loaded motion','Pinch protection, latch, play, hinge friction, fatigue, drop and folded bag-compression resistance untested','Bounding box volume is a packing proxy, not measured carrying comfort','No material or strength conclusions transfer from the V10 intact-band fixture to a redesigned hinge']}
out['pivot_mode']=mode
out['limits'][0]=str(len({r['size'] for r in rows}))+' sizes; existing pivots explored without a new latch or hinge design'
out['staggered_extensions']=stagger
if stagger:out['stagger_definition']='Left complete lower assembly shifted up15mm, right down15mm relative to nominal band: intended left extension0 right30; folding around shifted pivots. First pose checks all pairs, later poses reuse within-group invariance.'
(O/('folding_'+label+'_screen.json')).write_text(json.dumps(out,indent=2))

