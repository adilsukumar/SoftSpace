"""Rigid open-clamp overtravel checks; not a pull-out force or continuous sweep."""
from pathlib import Path
import sys,json,hashlib,time
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh
O=P/'engineering-v10-results';native=json.loads((O/'cad_native_report.json').read_text());rows=[]
for size in native['sizes']:
 name=size['name'];source=Path(next(f for f in native['files'] if '_'+name+'_' in f and f.endswith('.step') and 'Extension' not in f));digest=hashlib.sha256(source.read_bytes()).hexdigest()
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1)
 occ=gmsh.model.occ;occ.importShapes(str(source));occ.synchronize();bodies=gmsh.model.getEntities(3);bounds={dt:gmsh.model.getBoundingBox(*dt) for dt in bodies}
 band=[dt for dt,b in bounds.items() if b[0]<-75 and b[3]>75 and abs(b[2]-82)<1e-5 and b[4]-b[1]<30]
 knobs=[dt for dt,b in bounds.items() if abs(b[1]-8)<1e-5 and abs(b[4]-16)<1e-5 and abs((b[2]+b[5])/2-99)<1e-5]
 crown=[dt for dt,b in bounds.items() if dt not in band and b[0]<-10 and b[3]>10 and b[2]>110 and b[4]-b[1]<36]
 tongues=[dt for dt,b in bounds.items() if abs(b[2]-61)<1e-5 and abs(b[5]-134)<1e-5 and abs(b[1]+8)<1e-5 and abs(b[4]-8)<1e-5]
 assert len(bodies)==28 and len(band)==1 and len(knobs)==2 and len(crown)==1 and len(tongues)==2
 moving=band+crown;stationary=[dt for dt in bodies if dt not in moving+knobs];previous=15
 # Clamp knobs are removed for this unlocked scenario. No retractable screw joint exists in the CAD.
 occ.remove(knobs,recursive=True);occ.synchronize()
 for ext in [30,40,50,60,70,75]:
  start=time.time();occ.translate(moving,0,0,ext-previous);occ.synchronize();previous=ext
  bounds={dt:gmsh.model.getBoundingBox(*dt) for dt in moving+stationary};overlaps=[];errors=[];tested=0
  for a in moving:
   for b in stationary:
    ba,bb=bounds[a],bounds[b]
    if any(min(ba[k+3],bb[k+3])-max(ba[k],bb[k])<1e-5 for k in range(3)):continue
    out=[]
    try:
     out,_=occ.intersect(occ.copy([a]),occ.copy([b]),removeObject=True,removeTool=True)
     volume=sum(occ.getMass(*dt) for dt in out if dt[0]==3);tested+=1
     if volume>.01:overlaps.append({'tags':[a[1],b[1]],'volume_mm3':volume})
    except Exception as e:errors.append(str(e))
    finally:
     if out:occ.remove(out,recursive=True)
  gaps=[occ.getDistance(*band[0],*tongue)[0] for tongue in tongues]
  guide_lower=bounds[band[0]][2];tongue_upper=max(bounds[t][5] for t in tongues)
  row={'size':name,'extension_mm':ext,'source':str(source),'source_sha256':digest,'moving_solids':2,'stationary_solids':24,'removed_clamp_knobs':2,'cross_group_pairs':len(moving)*len(stationary),'boolean_count':tested,'overlaps':overlaps,'errors':errors,'sample_has_no_blocking_overlap':not overlaps and not errors,'band_to_tongues_distance_mm':gaps,'guide_lower_z_mm':guide_lower,'tongue_upper_z_mm':tongue_upper,'separated_axially':guide_lower>tongue_upper,'seconds':time.time()-start}
  rows.append(row);(O/'overtravel_partial.json').write_text(json.dumps(rows,indent=2));print(json.dumps({'size':name,'extension':ext,'overlaps':len(overlaps),'separated_axially':row['separated_axially']}),flush=True)
 gmsh.finalize()
out={'status':'complete','cases':rows,'case_count':len(rows),'all_samples_no_overlap':all(r['sample_has_no_blocking_overlap'] for r in rows),'sizes_with_separation_at_75mm':[r['size'] for r in rows if r['extension_mm']==75 and r['separated_axially']],'retention_validation':'Geometric obstruction is present at sampled 40 to 60 mm extensions; loaded end-stop strength remains untested','method':'Native STEP band and crown translated together; both clamp knobs removed to represent an open clamp. Only moving versus stationary pairs can change under this translation. Prior all-body nominal audit covers unchanged within-group pairs.','limits':['Outside intended operating range; diagnostic only','Separated shapes at 70 and 75 mm are imposed poses beyond the intervening collisions, not evidence of a reachable extraction path','No physical pull-out load friction end-stop strength or real screw retraction model','No deformation or misalignment; no native CAD edit made','The clamp knobs in the saved CAD are placeholders, so locked retention still cannot be established']}
(O/'overtravel_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'status':'complete','cases':len(rows),'all_samples_no_overlap':out['all_samples_no_overlap'],'separated_sizes':len(out['sizes_with_separation_at_75mm'])}),flush=True)
