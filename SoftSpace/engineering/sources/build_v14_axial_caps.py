"""Rear axial service cap and detachable pull-knob envelopes.
Fastener threads, torque and locking method remain qualification inputs.
"""
import json,hashlib,sys,math
from v12_geometry import P,gmsh,import_parts
O=P/'engineering-v14-results';O.mkdir(exist_ok=True)
old=json.loads((P/'engineering-v12-results/cad_report.json').read_text());recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())}
out={'status':'building','sizes':[],'limits':['Local STEP, not native Fusion','M1.6 by6 cap hardware and detachable pull knob are nominal envelopes without actual threads or torque qualification','Spring remains a space envelope','V12 band and cushion bodies have no intentional construction change; V12 component results remain labelled V12','Complete joint contact, actual fasteners, folding stops, fatigue, pinch access and physical validation remain open']}
def one(result):
 v=[dt for dt in result if dt[0]==3];assert len(v)==1,v;return v[0]
for row in old['sizes']:
 size=row['size']
 if len(sys.argv)>1 and size not in sys.argv[1:]:continue
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;parts=import_parts(row);R=recipes[size]['band_halfspan_mm']
 def bx(a,b,y1,y2,z1,z2,side):return (3,occ.addBox(min(side*a,side*b),y1,z1,abs(b-a),y2-y1,z2-z1))
 def cy(x,y1,y2,z,r):return (3,occ.addCylinder(x,y1,z,0,y2-y1,0,r))
 def cut(a,b):return one(occ.cut([a],[b])[0])
 def fuse(a,b):return one(occ.fuse([a],b)[0])
 def hexy(x,y1,y2,z,af):
  rad=af/math.sqrt(3);pts=[occ.addPoint(x+rad*math.cos(k*math.pi/3),y1,z+rad*math.sin(k*math.pi/3)) for k in range(6)];edges=[occ.addLine(pts[k],pts[(k+1)%6]) for k in range(6)];face=occ.addPlaneSurface([occ.addCurveLoop(edges)]);return one(occ.extrude([(2,face)],0,y2-y1,0))
 for side,prefix in [(-1,'Left'),(1,'Right')]:
  x=side*(R+10)
  # Open the rear wall and remove the original fixed central guide.
  fork=cut(parts[prefix+'Fork'],cy(x,-33,-12.999,60,3.5))
  fork=fuse(fork,[bx(R+7,R+13,-34,-26,z-2.5,z+2.5,side) for z in [54,66]])
  # Separate the rear four millimetres, including flanges, then restore its guide boss.
  cap=one(occ.intersect(occ.copy([fork]),[bx(R+4,R+16,-35,-30,50,70,side)])[0])
  fork=cut(fork,bx(R+4,R+16,-35,-30,50,70,side))
  cap=fuse(cap,[cy(x,-32,-30,60,5),cy(x,-30,-21,60,2)])
  cap=cut(cap,cy(x,-35,-20.9,60,1.15))
  for j,z in enumerate([54,66],1):
   fork=cut(fork,cy(x,-35,-25,z,.9));cap=cut(cap,cy(x,-35,-25,z,.9))
   cap=cut(cap,cy(x,-35.6,-33.9,z,1.7))
   fork=cut(fork,hexy(x,-30.1,-27.9,z,3.3))
   bolt=fuse(cy(x,-34,-28,z,.8),[cy(x,-35.5,-34,z,1.6)])
   nut=cut(hexy(x,-29.5,-28,z,3.2),cy(x,-30,-27,z,.8))
   parts[prefix+'CapBolt'+str(j)]=bolt;parts[prefix+'CapNut'+str(j)]=nut
  parts[prefix+'Fork']=fork;parts[prefix+'ServiceCap']=cap
  occ.remove([parts[prefix+'LockPin']],recursive=True)
  parts[prefix+'LockPin']=fuse(cy(x,-37,-5,60,1.1),[cy(x,-15,-13,60,3.4)])
  parts[prefix+'PullKnob']=cut(cy(x,-37,-34,60,4),cy(x,-38,-33,60,1.1))
 occ.synchronize();assert len(gmsh.model.getEntities(3))==44
 f=P/('EarDefender_V14_'+size+'_Latched.step');gmsh.write(str(f))
 out['sizes'].append({'size':size,'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source':row['file'],'source_sha256':row['sha256'],'solid_count':44,'part_bounds_mm':{n:gmsh.model.getBoundingBox(*dt) for n,dt in parts.items()},'part_volumes_mm3':{n:occ.getMass(*dt) for n,dt in parts.items()},'parts':{n:list(dt) for n,dt in parts.items()},'manufacturing_release':False,'assembly_route':'Bare pin and collar inserted from rear; real coil slides over bare rod; rear cap and guide slide along rod and compress spring to15mm; install two nominalM1.6by6 screws and nuts; detachable pull knob attached last using a still-unqualified retained thread or equivalent'});gmsh.finalize()
 (O/'cad_report.json').write_text(json.dumps(out,indent=2));print(size+' axial cap built',flush=True)
out['status']='complete local candidate build';(O/'cad_report.json').write_text(json.dumps(out,indent=2))
