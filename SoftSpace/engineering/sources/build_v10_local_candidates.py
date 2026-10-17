"""STEP-only prototype fixing guide/pin and child knob/fork interference.
Does not create or claim a native Fusion archive.
"""
from pathlib import Path
import json,sys,time,hashlib
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import gmsh
O=P/'engineering-v10-results';O.mkdir(exist_ok=True)
v=json.loads((P/'engineering-v9-results'/'native_verification.json').read_text())
recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())}
report={'status':'started','route':'local STEP candidates only','sizes':[],'files':[],'changes':['Guide lower end trimmed by2mm','Clamp bore and knob raised4mm','V9 crown, cushion, fork, pivot and30mm adjustment retained'],'limitations':['No native Fusion archive yet','Locking threads and retention still placeholders','Structural results must be recalculated for changed guide']}
for size in v['sizes']:
 name=size['name'];R=recipes[name]['band_halfspan_mm'];src=next(Path(f) for f in v['files'] if '_'+name+'_' in Path(f).name and Path(f).suffix=='.step' and 'Extension' not in f)
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;occ.importShapes(str(src));occ.synchronize();original=gmsh.model.getEntities(3)
 bboxes={dt:gmsh.model.getBoundingBox(*dt) for dt in original}
 bands=[dt for dt,b in bboxes.items() if b[0]<-75 and b[3]>75 and 79.99<b[2]<80.01 and b[4]-b[1]<30]
 if len(bands)!=1:raise RuntimeError('Ambiguous band '+name)
 band=bands[0];oldvol=occ.getMass(*band)
 knobs=[dt for dt,b in bboxes.items() if abs(b[1]-8)<.001 and abs(b[4]-16)<.001 and abs((b[2]+b[5])/2-95)<.001]
 if len(knobs)!=2:raise RuntimeError('Expected2 clamp knobs')
 for side in [-1,1]:
  x=side*R
  fill=occ.addCylinder(x,8.3,95,0,2.7,0,1.5)
  result,_=occ.fuse([band],[(3,fill)]);band=next(dt for dt in result if dt[0]==3)
  bore=occ.addCylinder(x,7,99,0,6,0,1.5)
  result,_=occ.cut([band],[(3,bore)]);band=next(dt for dt in result if dt[0]==3)
  cut=occ.addBox(x-4.1,-11.1,79.9,8.2,22.2,2.1)
  result,_=occ.cut([band],[(3,cut)]);band=next(dt for dt in result if dt[0]==3)
 occ.translate(knobs,0,0,4);occ.synchronize()
 bodies=gmsh.model.getEntities(3)
 if len(bodies)!=28:raise RuntimeError('Expected28 solids after modification')
 nominal=P/('OwnPassiveDefender_V10Local_'+name+'.step');gmsh.write(str(nominal));report['files'].append(str(nominal))
 newvol=occ.getMass(*band);bandbbox=gmsh.model.getBoundingBox(*band)
 # Crown pad shares the broad-span band shape; shift it together with band/knobs.
 crown=[dt for dt in bodies if dt!=band and (lambda b:b[0]<-10 and b[3]>10 and b[2]>110 and b[4]-b[1]<36)(gmsh.model.getBoundingBox(*dt))]
 if len(crown)!=1:raise RuntimeError('Expected one crown pad '+str(crown))
 moving=[band]+knobs+crown
 for ext in [0,30]:
  occ.translate(moving,0,0,ext-15);occ.synchronize()
  target=P/('OwnPassiveDefender_V10Local_'+name+'_Extension_'+str(ext)+'.step');gmsh.write(str(target));report['files'].append(str(target))
  occ.translate(moving,0,0,15-ext);occ.synchronize()
 gmsh.finalize()
 report['sizes'].append({'name':name,'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'body_count':len(bodies),'band_volume_before_mm3':oldvol,'band_volume_after_mm3':newvol,'nominal_band_bbox_mm':bandbbox,'guide_bottom_mm':82,'clamp_axis_z_mm':99,'travel_mm':[0,30],'nominal_guide_engagement_mm':32})
 (O/'cad_local_report.json').write_text(json.dumps(report,indent=2));print(name,'local candidate exported',flush=True)
report['status']='complete STEP-only candidates';(O/'cad_local_report.json').write_text(json.dumps(report,indent=2))
