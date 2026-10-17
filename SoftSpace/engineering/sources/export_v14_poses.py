"""Export exact released and final folding poses; verification is separate."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json,math,hashlib,sys
from v12_geometry import P,gmsh,import_parts
O=P/'engineering-v14-results'
cad=json.loads((O/'cad_report.json').read_text());recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())};angles={r['size']:r['best_reached_sample_angles_deg'] for r in json.loads((P/'engineering-v11-results'/'folding_summary.json').read_text())['sizes']};exports=json.loads((O/'pose_exports.json').read_text())['exports'] if (O/'pose_exports.json').exists() else []
for row in cad['sizes']:
 if len(sys.argv)>1 and row['size'] not in sys.argv[1:]:continue
 exports=[r for r in exports if r['size']!=row['size']]
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;parts=import_parts(row);R=recipes[row['size']]['band_halfspan_mm']
 for side,prefix in [(-1,'Left'),(1,'Right')]:
  occ.translate([parts[prefix+'LockPin'],parts[prefix+'PullKnob']],0,-6,0);occ.remove([parts[prefix+'SpringSpace']],recursive=True);a=(3,occ.addCylinder(side*(R+10),-30,60,0,9,0,3.175));b=(3,occ.addCylinder(side*(R+10),-31,60,0,11,0,2.825));out,_=occ.cut([a],[b]);assert len(out)==1;parts[prefix+'SpringSpace']=out[0]
 occ.synchronize()
 for phase in ['Released','Folded']:
  if phase=='Folded':
   for side,prefix in [(-1,'Left'),(1,'Right')]:occ.translate([dt for k,dt in parts.items() if k.startswith(prefix) and not k.endswith('SliderKnob')],0,0,-side*15)
   L,T=angles[row['size']]
   for prefix,x,z,degrees in [('Left',-R,80,-L),('Right',R,50,T)]:
    moving=[dt for k,dt in parts.items() if k.startswith(prefix) and k not in [prefix+'Tongue',prefix+'ForkPin',prefix+'ForkPinCap',prefix+'SliderKnob']];occ.rotate(moving,x,0,z,0,1,0,math.radians(degrees))
  occ.synchronize();f=P/('EarDefender_V14_'+row['size']+'_'+phase+'.step');volume=sum(occ.getMass(*dt) for dt in gmsh.model.getEntities(3));gmsh.write(str(f));exports.append({'size':row['size'],'phase':phase,'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'before_export_volume_mm3':volume,'source_sha256':row['sha256']})
 gmsh.finalize();print(row['size']+' poses exported',flush=True)
(O/'pose_exports.json').write_text(json.dumps({'exports':exports,'scope':'Exact annular spring spaces, rigid transforms only; full path clearance recorded separately by OCP'},indent=2))
