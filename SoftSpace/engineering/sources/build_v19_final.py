"""Assemble cosmetic thread envelopes for custom pins and jam nuts; preserve initial evidence."""
import json,hashlib,subprocess,sys,os
from v19_thread_prototype import P,cylinder,boolean,BRepAlgoAPI_Fuse,BRepAlgoAPI_Cut,BRepCheck_Analyzer,STEPControl_Writer,STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Pnt,gp_Vec
import math
from audit_v14_motion import mass,common
from v12_geometry import gmsh,import_parts
O=P/'engineering-v19-results';D=O/'final-CAD';D.mkdir(exist_ok=True);templates={}
def bolt(shoulder):return boolean(BRepAlgoAPI_Fuse,cylinder(2,0,shoulder+8),cylinder(3.5,-4,4))
def nut(y,height,shoulder):
 p=BRepBuilderAPI_MakePolygon()
 for k in range(6):p.Add(gp_Pnt(7/math.sqrt(3)*math.cos(k*math.pi/3),y,7/math.sqrt(3)*math.sin(k*math.pi/3)))
 p.Close();body=BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(p.Wire()).Face(),gp_Vec(0,height,0)).Shape();return boolean(BRepAlgoAPI_Cut,body,cylinder(2.05,y-.1,height+.2))
for family,shoulder in [('child',37),('adult',57)]:
 templates[family]={}
 shapes={'HingeBolt':bolt(shoulder),'HingeNut':nut(shoulder+.6625,3.2,shoulder),'JamNut':nut(shoulder+3.8625,2.2,shoulder)}
 for name,shape in shapes.items():
  assert BRepCheck_Analyzer(shape).IsValid(),(family,name)
  path=D/(family+'_'+name+'_envelope.step');w=STEPControl_Writer();w.Transfer(shape,STEPControl_AsIs);w.Write(str(path));templates[family][name]=str(path)
 for name in ['HingeNut','JamNut']:assert common(shapes['HingeBolt'],shapes[name])<1e-6
for source in sorted(O.glob('*_cad_report.json')):
 row=json.loads(source.read_text());size=row['size'];family='child' if size.startswith('child') else 'adult';gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);occ=gmsh.model.occ;parts=import_parts(row);R=next(r['band_halfspan_mm'] for r in json.loads((P/'lower-crown-recipes.json').read_text()) if r['name']==size);pivot=row['pivot_z_mm'];ystart=-row['fork_outer_halfspacing_mm']-.5
 for prefix,side in [('Left',-1),('Right',1)]:
  occ.remove([parts.pop(prefix+'HingeBolt'),parts.pop(prefix+'HingeNut')],recursive=True)
  for name,path in templates[family].items():
   added=occ.importShapes(path);solids=[v for v in added if v[0]==3];assert len(solids)==1;occ.translate(solids,side*R,ystart,pivot);parts[prefix+name]=solids[0]
 occ.synchronize();assert len(gmsh.model.getEntities(3))==42;target=P/('EarDefender_V19_'+size+'_AssemblyPrototype.step');gmsh.write(str(target));final=dict(row);final.update(revision='V19 parallel disc assembly prototype',file=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),source=row['file'],source_sha256=row['sha256'],solid_count=42,parts={k:list(v) for k,v in parts.items()},part_bounds_mm={k:gmsh.model.getBoundingBox(*v) for k,v in parts.items()},part_volumes_mm3={k:occ.getMass(*v) for k,v in parts.items()});final['hinge']=dict(row['hinge'],bolt_underhead_length_mm=45 if family=='child' else 65,plain_shoulder_length_mm=37 if family=='child' else 57,threaded_length_mm=8,thread_pitch_mm=.7,primary_nut_height_mm=3.2,jam_nut_height_mm=2.2,nominal_tip_protrusion_mm=1.9375)
 final['limits']=[x for x in row['limits'] if 'currently use thread envelopes' not in x]+['Fasteners use cosmetic thread envelopes with proposed M4 x 0.7 drawing callouts; thread strength and tolerance classes are not qualified','Experimental exact helical bolt failed the one connected solid check and is excluded from the final assembly','Two nuts are proposed for countertightening; vibration locking and torque retention remain untested','Final pin and nuts changed only; flexible joint mesh still refers to the initial V19 CAD with identical fork and tongue']
 (D/(size+'_cad_report.json')).write_text(json.dumps(final,indent=2));gmsh.finalize();print(size,'42 solids',flush=True)
s=(P/'audit_v19_motion.py').read_text().replace("O=P/'engineering-v19-results'","O=P/'engineering-v19-results'/'final-CAD'");(P/'audit_v19_final_motion.py').write_text(s)
jobs=[]
for source in sorted(D.glob('*_cad_report.json')):
 size=json.loads(source.read_text())['size']
 with (D/(size+'_motion.log')).open('w') as f:r=subprocess.run([sys.executable,str(P/'audit_v19_final_motion.py'),size],cwd=P,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
 jobs.append(dict(size=size,exit_code=r.returncode));(D/'run_status.json').write_text(json.dumps(dict(jobs=jobs,complete=False),indent=2));assert r.returncode==0
(D/'run_status.json').write_text(json.dumps(dict(jobs=jobs,complete=True),indent=2))
