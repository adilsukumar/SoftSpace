"""Defined M2 jam-nut retention candidate; cosmetic thread envelopes only.
This does not qualify thread manufacture, torque, loosening or pullout.
"""
import json,hashlib,sys,math
from v12_geometry import P,gmsh,import_parts
O=P/'engineering-v15-results';O.mkdir(exist_ok=True)
source=json.loads((P/'engineering-v14-results/cad_report.json').read_text())
recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())}
size=sys.argv[1];row=next(r for r in source['sizes'] if r['size']==size)
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;parts=import_parts(row);R=recipes[size]['band_halfspan_mm']
def one(result):
 v=[dt for dt in result if dt[0]==3];assert len(v)==1,v;return v[0]
def cy(x,y1,y2,z,r):return (3,occ.addCylinder(x,y1,z,0,y2-y1,0,r))
def fuse(a,b):return one(occ.fuse([a],b)[0])
def cut(a,b):return one(occ.cut([a],[b])[0])
def hexy(x,y1,y2,z,af):
 rad=af/math.sqrt(3);pts=[occ.addPoint(x+rad*math.cos(k*math.pi/3),y1,z+rad*math.sin(k*math.pi/3)) for k in range(6)];edges=[occ.addLine(pts[k],pts[(k+1)%6]) for k in range(6)];face=occ.addPlaneSurface([occ.addCurveLoop(edges)]);return one(occ.extrude([(2,face)],0,y2-y1,0))
for side,prefix in [(-1,'Left'),(1,'Right')]:
 x=side*(R+10);occ.remove([parts[prefix+'LockPin'],parts[prefix+'PullKnob']],recursive=True)
 pin=fuse(cy(x,-34.8,-5,60,1.1),[cy(x,-40.8,-34.8,60,.9905),cy(x,-34.8,-34.4,60,1.5),cy(x,-15,-13,60,3.4)])
 knob=cut(cy(x,-40.8,-36.8,60,4),cy(x,-40.9,-36.7,60,1.0))
 knob=cut(knob,cy(x,-40.9,-39.8,60,1.15))
 nut=cut(hexy(x,-36.8,-35.2,60,4),cy(x,-36.9,-35.1,60,1.0))
 parts[prefix+'LockPin']=pin;parts[prefix+'PullKnob']=knob;parts[prefix+'ReleaseJamNut']=nut
occ.synchronize();assert len(gmsh.model.getEntities(3))==46
f=P/('EarDefender_V15_'+size+'_RetentionCandidate.step');gmsh.write(str(f))
out={'revision':'V15 retention candidate','size':size,'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source':row['file'],'source_sha256':row['sha256'],'solid_count':46,'part_bounds_mm':{n:gmsh.model.getBoundingBox(*dt) for n,dt in parts.items()},'part_volumes_mm3':{n:occ.getMass(*dt) for n,dt in parts.items()},'parts':{n:list(dt) for n,dt in parts.items()},'manufacturing_release':False,'retention_design':{'method':'Threaded metal knob counterlocked by separate metal hex jam nut','thread_callout':'M2 x 0.4; proposed external6g internal6H; gauge and supplier drawing required','male_major_envelope_diameter_mm':1.981,'female_major_envelope_diameter_mm':2.0,'male_thread_envelope_length_mm':5.6,'knob_engagement_envelope_mm':4.0,'jam_nut_engagement_envelope_mm':1.6,'jam_nut_across_flats_mm':4,'stem_diameter_mm':2.2,'shoulder_diameter_mm':3,'nominal_shoulder_to_cap_gap_mm':.4,'assembly':'Pin and collar from rear, real coil over bare rod, cap and cap screws, jam nut then knob. Hold metal flats and countertighten jam nut against knob. Gauge position so shoulder stays clear of cap. Use a torque process selected after strength and release tests.','limits':['Thread helices and actual flank engagement not modelled; clear cylinders are cosmetic envelopes','No specified final grade, coating, thread runout, undercut, wrench clearance under load or production tolerance qualification','Separate small parts not qualified for child access or choking risk','Jam nut is a retention method candidate, not a vibration loosening or pullout pass']}}
out['retention_design'].update(male_thread_envelope_length_mm=6.0,knob_engagement_envelope_mm=3.0,knob_rear_counterbore_length_mm=1.0,jam_nut_to_shoulder_gap_mm=.4)
out['retention_design']['reference']='Bossard Metric ISO Threads 01 2025 https://assets.eu.ctfassets.net/0vp0u5uh75zd/2tYqENAuufvdsudjM8Qbrc/b3461eaa59c2203d3a8b9509ac24dacf/096_098_Metric_ISOthreads_Fastening_EN_01_2025.pdf'
(O/(size+'_retention_cad.json')).write_text(json.dumps(out,indent=2));gmsh.finalize();print(json.dumps({'size':size,'solids':46,'file':str(f)}))
