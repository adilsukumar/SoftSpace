"""Serviceable split barrel candidate; nominal fastener envelopes, not threads.
The coil can pass over the smaller one-piece pin head before radial assembly.
"""
import json,hashlib,sys
from v12_geometry import P,gmsh,import_parts
O=P/'engineering-v13-results';O.mkdir(exist_ok=True);old=json.loads((P/'engineering-v12-results'/'cad_report.json').read_text());recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())};out={'status':'building','sizes':[],'limits':['Local STEP, not native Fusion archives','Nominal M1.6 by6 screw and hex nut envelopes; actual catalogue geometry, grade, thread engagement and torque still need qualification','Split caps and fasteners need new contact and structural checks','Same wider band and cushions inherited from V12 without intentional changes; component evidence must be linked explicitly','Spring remains a space envelope; real spring forming, ends and seats require samples','Child portability remains an open design issue']}
def one(result):
 v=[dt for dt in result if dt[0]==3];assert len(v)==1,('expected one solid',v);return v[0]
for row in old['sizes']:
 size=row['size']
 if len(sys.argv)>1 and size not in sys.argv[1:]:continue
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;parts=import_parts(row);R=recipes[size]['band_halfspan_mm']
 def bx(a,b,y1,y2,z1,z2,side=1):return (3,occ.addBox(min(side*a,side*b),y1,z1,abs(b-a),y2-y1,z2-z1))
 def cy(x,y1,y2,z,r):return (3,occ.addCylinder(x,y1,z,0,y2-y1,0,r))
 def cx(x1,x2,y,z,r):return (3,occ.addCylinder(x1,y,z,x2-x1,0,0,r))
 def cut(a,b):return one(occ.cut([a],[b])[0])
 def fuse(a,tools):return one(occ.fuse([a],tools)[0])
 def hex_prism(x1,x2,y,z,af):
  import math
  radius=af/math.sqrt(3);pts=[occ.addPoint(x1,y+radius*math.cos(k*math.pi/3),z+radius*math.sin(k*math.pi/3)) for k in range(6)];edges=[occ.addLine(pts[k],pts[(k+1)%6]) for k in range(6)];wire=occ.addCurveLoop(edges);face=occ.addPlaneSurface([wire]);return one(occ.extrude([(2,face)],x2-x1,0,0))
 for side,prefix in [(-1,'Left'),(1,'Right')]:
  fork=parts[prefix+'Fork'];flanges=[bx(R+7,R+13,-30,-22,z-2.5,z+2.5,side) for z in [54,66]];fork=fuse(fork,flanges)
  # The plane through the barrel axis opens the housing radially.
  cap_box=bx(R+10,R+17,-33,-9,50,70,side);cap=one(occ.intersect(occ.copy([fork]),[cap_box])[0]);fork=cut(fork,bx(R+10,R+17,-33,-9,50,70,side))
  for j,z in enumerate([54,66],1):
   # Hole clearances, a nut pocket opening at the split face, and removable hardware.
   fork=cut(fork,cx(side*(R+6),side*(R+14),-26,z,.9));cap=cut(cap,cx(side*(R+6),side*(R+14),-26,z,.9))
   cap=cut(cap,cx(side*(R+13),side*(R+17.1),-26,z,1.7))
   pocket=hex_prism(side*(R+8),side*(R+10.1),-26,z,3.3);fork=cut(fork,pocket)
   shaft=cx(side*(R+7),side*(R+13),-26,z,.8);head=cx(side*(R+13),side*(R+14.5),-26,z,1.6);bolt=fuse(shaft,[head]);parts[prefix+'CapBolt'+str(j)]=bolt
   nut=hex_prism(side*(R+8),side*(R+9.5),-26,z,3.2);nut=cut(nut,cx(side*(R+7.5),side*(R+10),-26,z,.8));parts[prefix+'CapNut'+str(j)]=nut
  parts[prefix+'Fork']=fork;parts[prefix+'ServiceCap']=cap
  occ.remove([parts[prefix+'LockPin']],recursive=True)
  pin=cy(side*(R+10),-35,-5,60,1.1);pin=fuse(pin,[cy(side*(R+10),-35,-32,60,2.65),cy(side*(R+10),-15,-13,60,3.4)]);parts[prefix+'LockPin']=pin
 occ.synchronize();assert len(gmsh.model.getEntities(3))==42;f=P/('EarDefender_V13_'+size+'_Latched.step');gmsh.write(str(f));bounds={n:gmsh.model.getBoundingBox(*dt) for n,dt in parts.items()};volumes={n:occ.getMass(*dt) for n,dt in parts.items()};out['sizes'].append({'size':size,'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source':row['file'],'source_sha256':row['sha256'],'solid_count':42,'part_bounds_mm':bounds,'part_volumes_mm3':volumes,'parts':{n:list(dt) for n,dt in parts.items()},'coil_nominal_inner_diameter_mm':5.65,'pin_head_nominal_diameter_mm':5.3,'assembly_route':'Place captive nuts in open split-face pockets; slide real coil over5.3mm head onto rod; compress to allocated15mm length; lay pin and coil radially into open barrel; fit cap radially and install two M1.6 by6 screws per side','manufacturing_release':False});gmsh.finalize();(O/'cad_report.json').write_text(json.dumps(out,indent=2));print(size+' split cap candidate built',flush=True)
out['status']='complete local candidate build';(O/'cad_report.json').write_text(json.dumps(out,indent=2))
