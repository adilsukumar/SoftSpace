"""Five-degree folding paths on unchanged V10 solids with staggered extensions."""
from pathlib import Path
import json,sys,math,hashlib
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh
O=P/'engineering-v11-results';summary=json.loads((O/'folding_summary.json').read_text());recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())};rows=[];exports=[]
for recipe in summary['sizes']:
 size=recipe['size'];R=recipes[size]['band_halfspan_mm'];source=Path(recipe['source']);assert hashlib.sha256(source.read_bytes()).hexdigest()==recipe['source_sha256'];L,T=recipe['best_reached_sample_angles_deg']
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;occ.importShapes(str(source));occ.synchronize();bodies=gmsh.model.getEntities(3);assert len(bodies)==28
 left=[(3,i) for i in [1,2,3,4,5,6,7,9,10]];right=[(3,i+12) for i in [1,2,3,4,5,6,7,9,10]]
 occ.translate([(3,i) for i in range(1,13)],0,0,15);occ.translate([(3,i) for i in range(13,25)],0,0,-15);occ.synchronize();previous=[0,0];size_rows=[]
 for la,ra in [(a,0) for a in range(0,L+1,5)]+[(L,a) for a in range(5,T+1,5)]:
  occ.rotate(left,-R,0,80,0,1,0,-math.radians(la-previous[0]));occ.rotate(right,R,0,50,0,1,0,math.radians(ra-previous[1]));occ.synchronize();previous=[la,ra]
  bounds={dt:gmsh.model.getBoundingBox(*dt) for dt in bodies};overlaps=[];errors=[]
  for i,a in enumerate(bodies):
   for b in bodies[i+1:]:
    ga=0 if a in left else (1 if a in right else 2);gb=0 if b in left else (1 if b in right else 2)
    if ga==gb and (la or ra):continue
    ba,bb=bounds[a],bounds[b]
    if any(min(ba[k+3],bb[k+3])-max(ba[k],bb[k])<1e-5 for k in range(3)):continue
    out=[]
    try:
     out,_=occ.intersect(occ.copy([a]),occ.copy([b]),removeObject=True,removeTool=True);v=sum(occ.getMass(*dt) for dt in out if dt[0]==3)
     if v>.01:overlaps.append({'tags':[a[1],b[1]],'intersection_mm3':v})
    except Exception as e:errors.append(str(e))
    finally:
     if out:occ.remove(out,recursive=True)
  r={'size':size,'left_deg':la,'right_deg':ra,'overlaps':overlaps,'errors':errors,'pass':not overlaps and not errors,'source_sha256':recipe['source_sha256']};rows.append(r);size_rows.append(r)
  (O/'fine_fold_partial.json').write_text(json.dumps(rows,indent=2))
  print(json.dumps({'size':size,'left':la,'right':ra,'pass':r['pass']}),flush=True)
 if all(r['pass'] for r in size_rows):
  target=P/('FoldingCandidate_V11_'+size+'.step');gmsh.write(str(target));exports.append({'size':size,'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'angles_deg':[L,T]})
 gmsh.finalize()
result={'status':'complete sampled path refinement','case_count':len(rows),'cases':rows,'all_pass':all(r['pass'] for r in rows),'exports':exports,'threshold_mm3':.01,'angle_interval_deg':5,'limits':['Rigid five-degree samples, not continuous swept-volume clearance or contact dynamics','Baseline checks all pairs; later within-group relative transforms are invariant','Nominal intact components, without manufacturing variation','Slider staggering must be performed before folding; slider adjustment while folded not validated','Existing axes only; final latch, angular stops, anti-pinch details, torque, wear, impact and fatigue remain open','No new native Fusion F3D assembly or durability claim']}
(O/'fine_fold_paths.json').write_text(json.dumps(result,indent=2));print(json.dumps({'case_count':len(rows),'all_pass':result['all_pass'],'exported_sizes':len(exports)}),flush=True)
