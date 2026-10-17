"""Local STEP engineering candidate: wider guides and captive angular-lock pins.
Spring bodies depict allocated annular space, not physical solid rings or actual coils.
"""
from pathlib import Path
import sys,json,hashlib,time
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh
O=P/'engineering-v12-results';O.mkdir(exist_ok=True)
native=json.loads((P/'engineering-v10-results'/'cad_native_report.json').read_text());recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())}
sizes=sys.argv[1:] or list(recipes)
report={'status':'building local STEP candidates','sizes':[],'files':[],'limits':['No native Fusion F3D created','Guide change invalidates direct transfer of V10 band stresses','Spring envelope is a space reservation, not a solid rubber or metal ring','Pin, spring and bearing calculations require final grade and processing validation','Final adjustment screw thread and friction validation, fatigue, drops, skin contact and acoustics remain open']}
for size in sizes:
 start=time.time();R=recipes[size]['band_halfspan_mm'];source=Path(next(f for f in native['files'] if '_'+size+'_' in f and f.endswith('.step') and 'Extension' not in f))
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;occ.importShapes(str(source));occ.synchronize();original=gmsh.model.getEntities(3);assert len(original)==28
 names=['MainFoam','SoftGlassesZone','ContinuousCover','Carrier','Cup','Liner','Fork','Tongue','CupPin','CupPinCap','ForkPin','ForkPinCap']
 parts={('Left' if i<12 else 'Right')+names[i%12]:dt for i,dt in enumerate(original[:24])}
 parts.update(LeftSliderKnob=original[24],RightSliderKnob=original[25],Band=original[26],CrownPad=original[27]);occ.synchronize()
 def box(x1,x2,y1,y2,z1,z2):return (3,occ.addBox(min(x1,x2),y1,z1,abs(x2-x1),y2-y1,z2-z1))
 def cyl(x,y1,y2,z,r):return (3,occ.addCylinder(x,y1,z,0,y2-y1,0,r))
 def cut(a,b):
  out,_=occ.cut([a],[b]);vol=[dt for dt in out if dt[0]==3];assert len(vol)==1,('cut not single',vol);return vol[0]
 def fuse(a,tools):
  out,_=occ.fuse([a],tools);vol=[dt for dt in out if dt[0]==3];assert len(vol)==1,('fuse not single',vol);return vol[0]
 for side,prefix in [(-1,'Left'),(1,'Right')]:
  def sb(a,b,y1,y2,z1,z2):return box(side*a,side*b,y1,y2,z1,z2)
  # Nominal 0.6 mm rectangular clearance around the 4 by 16 mm tongue.
  parts['Band']=cut(parts['Band'],sb(R-2.6,R+2.6,-8.6,8.6,60,145))
  tongue=fuse(parts[prefix+'Tongue'],[sb(R-2,R+14,-8,8,57,63)])
  tongue=cut(tongue,cyl(side*(R+10),-9,-5,60,1.15));parts[prefix+'Tongue']=tongue
  fork=parts[prefix+'Fork'];occ.synchronize();fy=gmsh.model.getBoundingBox(*fork)[4]
  bridges=[sb(R+25,R+31,-fy,fy,61,69),sb(R+17,R+31,-13,-9,61,65),sb(R+17,R+31,9,13,61,65),sb(R+17,R+31,-fy,-fy+4,64,69),sb(R+17,R+31,fy-4,fy,64,69)]
  fork=fuse(fork,bridges)
  fork=cut(fork,sb(R+16.9,R+23.1,-9,9,60.9,69.1))
  # Offset barrel joins the front fork while staying below the guide at short adjustment.
  fork=fuse(fork,[cyl(side*(R+10),-32,-10,60,5),sb(R+2,R+10,-28,-10,57,63)])
  fork=cut(fork,cyl(side*(R+10),-30,-13,60,3.5))
  fork=fuse(fork,[cyl(side*(R+10),-30,-21,60,2)])
  fork=cut(fork,cyl(side*(R+10),-33,-9,60,1.15));parts[prefix+'Fork']=fork
  pin=cyl(side*(R+10),-35,-5,60,1.1)
  pin=fuse(pin,[cyl(side*(R+10),-35,-32,60,4),cyl(side*(R+10),-15,-13,60,3.4)])
  parts[prefix+'LockPin']=pin
  envelope=cut(cyl(side*(R+10),-30,-15,60,3.175),cyl(side*(R+10),-31,-14,60,2.825));parts[prefix+'SpringSpace']=envelope
 occ.synchronize();assert len(gmsh.model.getEntities(3))==32
 # A first all-pair audit catches construction interference before exporting more sizes.
 bounds={name:gmsh.model.getBoundingBox(*dt) for name,dt in parts.items()};overlaps=[];errors=[];keys=list(parts)
 for i,a in enumerate(keys):
  for b in keys[i+1:]:
   ba,bb=bounds[a],bounds[b]
   if any(min(ba[k+3],bb[k+3])-max(ba[k],bb[k])<1e-5 for k in range(3)):continue
   out=[]
   try:
    out,_=occ.intersect(occ.copy([parts[a]]),occ.copy([parts[b]]),removeObject=True,removeTool=True);v=sum(occ.getMass(*dt) for dt in out if dt[0]==3)
    if v>.01:overlaps.append({'parts':[a,b],'intersection_mm3':v})
   except Exception as e:errors.append(str(e))
   finally:
    if out:occ.remove(out,recursive=True)
 gaps=[occ.getDistance(*parts['Band'],*parts[p+'Tongue'])[0] for p in ['Left','Right']]
 target=P/('EarDefender_V12_'+size+'_Latched.step');gmsh.write(str(target))
 row={'size':size,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'parts':{k:list(dt) for k,dt in parts.items()},'part_bounds_mm':bounds,'part_volumes_mm3':{k:occ.getMass(*dt) for k,dt in parts.items()},'solid_count':32,'guide_tongue_gaps_mm':gaps,'overlaps':overlaps,'errors':errors,'nominal_pair_pass':not overlaps and not errors,'seconds':time.time()-start}
 report['sizes'].append(row);report['files'].append(str(target));gmsh.finalize();(O/'cad_report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'size':size,'overlaps':overlaps,'errors':errors,'gaps_mm':gaps}),flush=True)
report['status']='complete local STEP batch';(O/'cad_report.json').write_text(json.dumps(report,indent=2))
