"""Sample native V10 rigid travel at 5 mm intervals; no contact mechanics claim."""
from pathlib import Path
import sys,json,hashlib,time
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import gmsh
O=P/'engineering-v10-results'
native=json.loads((O/'cad_native_report.json').read_text());assert native['status']=='complete'
rows=[]
for size in native['sizes']:
 name=size['name'];source=Path(next(f for f in native['files'] if '_'+name+'_' in f and f.endswith('.step') and 'Extension' not in f))
 digest=hashlib.sha256(source.read_bytes()).hexdigest()
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1)
 occ=gmsh.model.occ;occ.importShapes(str(source));occ.synchronize();bodies=gmsh.model.getEntities(3)
 bounds={dt:gmsh.model.getBoundingBox(*dt) for dt in bodies}
 band=[dt for dt,b in bounds.items() if b[0]<-75 and b[3]>75 and abs(b[2]-82)<1e-5 and b[4]-b[1]<30]
 knobs=[dt for dt,b in bounds.items() if abs(b[1]-8)<1e-5 and abs(b[4]-16)<1e-5 and abs((b[2]+b[5])/2-99)<1e-5]
 crown=[dt for dt,b in bounds.items() if dt not in band and b[0]<-10 and b[3]>10 and b[2]>110 and b[4]-b[1]<36]
 assert len(bodies)==28 and len(band)==1 and len(knobs)==2 and len(crown)==1,(name,band,knobs,crown)
 moving=band+knobs+crown;previous=15;invariant=[]
 for extension in range(0,31,5):
  start=time.time();occ.translate(moving,0,0,extension-previous);occ.synchronize();previous=extension
  bounds={dt:gmsh.model.getBoundingBox(*dt) for dt in bodies};overlaps=[];errors=[];tested=0
  for i,a in enumerate(bodies):
   for b in bodies[i+1:]:
    # Pairs translated by the same rigid transform keep the first-pose result.
    if extension and ((a in moving)==(b in moving)):continue
    ba,bb=bounds[a],bounds[b]
    if any(min(ba[k+3],bb[k+3])-max(ba[k],bb[k])<1e-5 for k in range(3)):continue
    out=[]
    try:
     out,_=occ.intersect(occ.copy([a]),occ.copy([b]),removeObject=True,removeTool=True)
     volume=sum(occ.getMass(*dt) for dt in out if dt[0]==3);tested+=1
     if volume>.01:overlaps.append({'body_tags':[a[1],b[1]],'intersection_mm3':volume,'bbox_a_mm':ba,'bbox_b_mm':bb})
    except Exception as e:errors.append({'body_tags':[a[1],b[1]],'error':str(e)})
    finally:
     if out:occ.remove(out,recursive=True)
  if extension==0:invariant=[o for o in overlaps if ((3,o['body_tags'][0]) in moving)==((3,o['body_tags'][1]) in moving)]
  else:overlaps+=invariant
  row={'size':name,'extension_mm':extension,'source':str(source),'source_sha256':digest,'solid_count':len(bodies),'all_pair_count':378,'boolean_count':tested,'overlaps':overlaps,'errors':errors,'pass':not overlaps and not errors,'seconds':time.time()-start}
  rows.append(row);(O/'intermediate_travel_partial.json').write_text(json.dumps(rows,indent=2))
  print(json.dumps({'size':name,'extension_mm':extension,'pass':row['pass'],'overlaps':len(overlaps),'seconds':row['seconds']}),flush=True)
 gmsh.finalize()
result={'status':'complete','pose_count':len(rows),'pair_candidates':378*len(rows),'all_pass':all(r['pass'] for r in rows),'overlap_threshold_mm3':.01,'cases':rows,'method':'Native nominal STEP imported per size; band, crown pad and clamp knobs translated together in Z by extension minus 15 mm; all 28 solids covered by bounding-box broad phase and OCC exact intersections. Pairs within one rigid moving or stationary group are tested at the first pose and reused because their relative transform is unchanged. Any first-pose Boolean error invalidates the overall check.','limits':['Seven sampled rigid poses per size, not continuous swept-volume clearance','Nominal unstrained CAD only; no dimensional variation, friction, deformation or loads','No locking, end-stop retention, wear or manufacturing acceptance','Cushion and Sony compatibility results unchanged']}
(O/'intermediate_travel_audit.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'status':'complete','pose_count':len(rows),'all_pass':result['all_pass']}),flush=True)
