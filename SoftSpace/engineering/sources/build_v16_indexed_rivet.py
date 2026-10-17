"""Local indexing-plate and cross-riveted knob candidate, not production release."""
import json,hashlib,sys,math
from v12_geometry import P,gmsh,import_parts
O=P/'engineering-v16-results';O.mkdir(exist_ok=True)
size=sys.argv[1] if len(sys.argv)>1 else 'child_large'
radius=float(sys.argv[2]) if len(sys.argv)>2 else 14
variant=size+('_R'+str(int(radius)) if radius!=14 else '')
upper=len(sys.argv)>3 and sys.argv[3].startswith('upper')
upper2=upper and sys.argv[3]=='upper2'
if upper:variant+='U2' if upper2 else 'U'
old=json.loads((P/'engineering-v14-results/cad_report.json').read_text());row=next(r for r in old['sizes'] if r['size']==size);R=next(r['band_halfspan_mm'] for r in json.loads((P/'lower-crown-recipes.json').read_text()) if r['name']==size)
if size=='child_large':angles=[30,60];extensions=[0,20]
else:
 previous=next(r for r in json.loads((P/'engineering-v14-results/packing_summary.json').read_text())['sizes'] if r['size']==size);angles=previous['angles_deg'];extensions=[0,30]
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;parts=import_parts(row)
def one(out):
 v=[x for x in out if x[0]==3];assert len(v)==1,v;return v[0]
def cy(x,y1,y2,z,r):return (3,occ.addCylinder(x,y1,z,0,y2-y1,0,r))
def cx(x1,x2,y,z,r):return (3,occ.addCylinder(x1,y,z,x2-x1,0,0,r))
def cut(a,b):return one(occ.cut([a],[b])[0])
def fuse(a,b):return one(occ.fuse([a],b)[0])
for side,prefix,fold in [(-1,'Left',angles[0]),(1,'Right',angles[1])]:
 x=side*R;center=side*(R+10)
 plate=cy(x,-16 if upper else -8,-13 if upper else -5,65,radius)
 plate=cut(plate,(3,occ.addBox(x-radius-1,-17 if upper else -9,65-radius-1 if upper else 65,2*radius+2,5,radius+1)))
 if upper2:
  plate=cut(plate,(3,occ.addBox(x-radius-1 if side==1 else x+3,-17,64, radius-2,5,radius+2)))
 added=[plate]
 if upper:added.append((3,occ.addBox(x-5,-16,60,10,11,6.5)))
 tongue=fuse(parts[prefix+'Tongue'],added);tongue=cut(tongue,cy(x,-17 if upper else -9,-4.9,65,2.25))
 for angle in [0,fold]:
  a=math.radians(angle);hx=x+side*(12*math.sin(a) if upper else 10*math.cos(a)-5*math.sin(a));hz=65+(12*math.cos(a) if upper else -10*math.sin(a)-5*math.cos(a))
  tongue=cut(tongue,cy(hx,-17 if upper else -9,-12.9 if upper else -4.9,hz,1.15))
 parts[prefix+'Tongue']=tongue
 # Round cross-rivet heads sit below the existing8mm knob envelope.
 pin=cut(parts[prefix+'LockPin'],cx(center-4.1,center+4.1,-35.5,60,.425))
 knob=cut(parts[prefix+'PullKnob'],cy(center,-38,-33,60,1.15))
 knob=cut(knob,cx(center-4.1,center+4.1,-35.5,60,.425))
 knob=cut(knob,cx(center-4.1,center-3.5,-35.5,60,.65));knob=cut(knob,cx(center+3.5,center+4.1,-35.5,60,.65))
 rivet=fuse(cx(center-3.5,center+3.5,-35.5,60,.4),[cx(center-3.8,center-3.5,-35.5,60,.6),cx(center+3.5,center+3.8,-35.5,60,.6)])
 parts[prefix+'LockPin']=pin;parts[prefix+'PullKnob']=knob;parts[prefix+'KnobCrossRivet']=rivet
 if upper:
  def bx(a,b,y1,y2,z1,z2):return (3,occ.addBox(min(side*a,side*b),y1,z1,abs(b-a),y2-y1,z2-z1))
  fork=parts[prefix+'Fork'];housing=one(occ.intersect(occ.copy([fork]),[bx(R+4.1,R+16,-35,-9,50,70)])[0])
  fork=cut(fork,bx(R+1.9,R+16,-35,-9,50,70))
  # Rebuild only the front pivot prong removed with the obsolete support arm.
  fork=fuse(fork,[bx(R-4,R+4,-28,-24,54,69)])
  fork=cut(fork,cy(x,-30,-20,65,2.25))
  occ.translate([housing],-side*10,-8,17)
  fork=fuse(fork,[housing,bx(R,R+28,-28,-24,74,80),bx(R+24,R+31,-28,-24,64,80)])
  if upper2:
   fork=cut(fork,cy(x,-41,-20.999,77,3.5));fork=cut(fork,cy(x,-21.001,-17,77,1.15))
  parts[prefix+'Fork']=fork
  names=[prefix+n for n in ['ServiceCap','LockPin','PullKnob','KnobCrossRivet','SpringSpace','CapBolt1','CapBolt2','CapNut1','CapNut2']]
  occ.translate([parts[n] for n in names],-side*10,-8,17)
occ.synchronize();assert len(gmsh.model.getEntities(3))==46
f=P/('EarDefender_V16_'+variant+'_IndexedRivetCandidate.step');gmsh.write(str(f))
out={'revision':'V16 indexed fold and recessed cross-rivet candidate','size':size,'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source':row['file'],'source_sha256':row['sha256'],'solid_count':46,'part_bounds_mm':{n:gmsh.model.getBoundingBox(*dt) for n,dt in parts.items()},'part_volumes_mm3':{n:occ.getMass(*dt) for n,dt in parts.items()},'parts':{n:list(dt) for n,dt in parts.items()},'fold_angles_deg':[30,60],'fold_extension_mm':[0,20],'dimensions':{'index_plate_radius_mm':14,'index_plate_thickness_mm':3,'index_hole_diameter_mm':2.3,'locking_pin_diameter_mm':2.2,'pivot_clearance_diameter_mm':4.5,'knob_diameter_mm':8,'cross_rivet_shaft_diameter_mm':.8,'cross_drill_diameter_mm':.85,'cross_rivet_head_diameter_mm':1.2,'cross_rivet_head_length_mm':.3,'cross_rivet_overall_length_mm':7.6,'knob_rod_bore_mm':2.3},'assembly':'Insert bare pin and actual coil before rear cap. Attach cap hardware. Slide knob onto stem, align cross holes, insert a one-headed preform then upset the other rivet head in its recess. Final formed shape is modelled; upsetting and tool access not qualified. Pin service requires removing the rivet.','manufacturing_release':False,'limits':['One local candidate; no native Fusion reconstruction','Metal pin and rivet are intended; final grade, upsetting strain, tolerances, coatings and proof loads unqualified','Index holes define geometric storage locking only; actual spring return friction bearing strength wear and pinch access need validation','No hard travel stops outside engaged index positions','No physical or acoustic or sensory acceptance pass']}
out.update(variant=variant,fold_angles_deg=angles,fold_extension_mm=extensions);out['dimensions']['index_plate_radius_mm']=radius
out['layout']='upper rear index plate with relocated housing' if upper else 'lower index plate'
if upper:out['limits'].append('Upper adult layout changes fork support and plate root; earlier fork stresses do not qualify this geometry')
(O/(variant+'_cad_report.json')).write_text(json.dumps(out,indent=2));gmsh.finalize();print(json.dumps({'file':str(f),'solids':46}))
