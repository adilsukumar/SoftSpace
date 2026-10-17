"""Independent local STEP candidate while Fusion is unavailable. No F3D change."""
import sys,json
from pathlib import Path
p=Path(__file__).parent;sys.path.insert(0,str(p/'solver-libraries'))
import gmsh
size=sys.argv[1] if len(sys.argv)>1 else 'adult_small'
j=json.loads((p/'cad_v8_report.json').read_text());path=next(f for f in j['files'] if 'OwnPassiveDefender' in f and '_'+size+'_' in f and f.endswith('.step') and 'Extension' not in f)
R=next(r['band_halfspan_mm'] for r in j['recipes'] if r['name']==size)
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.occ.importShapes(path);gmsh.model.occ.synchronize()
bands=[]
for d,t in gmsh.model.getEntities(3):
 a,b,c,e,f,g=gmsh.model.getBoundingBox(d,t)
 if a<0<e and 70<c<100 and g>125 and f-b<30:bands.append(t)
assert len(bands)==1,bands
curves=set()
for d,s in gmsh.model.getBoundary([(3,bands[0])],oriented=False):
 for dim,t in gmsh.model.getBoundary([(d,s)],oriented=False):
  if dim==1:curves.add(t)
selected=[]
for t in curves:
 a,b,c,d,e,f=gmsh.model.getBoundingBox(1,t)
 if abs(a-d)<1e-5 and abs(b-e)<1e-5 and f-c>10 and abs(abs(b)-8.3)<1e-5 and abs(abs(abs(a)-R)-2.3)<1e-5:selected.append(t)
assert len(selected)==8,selected
before=gmsh.model.occ.getMass(3,bands[0]);new=gmsh.model.occ.fillet(bands,selected,[.5]);gmsh.model.occ.synchronize();assert len(gmsh.model.getEntities(3))==28
after=sum(gmsh.model.occ.getMass(d,t) for d,t in new)
target=p/('OwnPassiveDefender_V9Local_'+size+'.step');gmsh.write(str(target));gmsh.finalize()
report={'source':path,'target':str(target),'corners':len(selected),'radius_mm':.5,'old_band_volume_mm3':before,'new_band_volume_mm3':after,'status':'STEP candidate only; no Fusion archive, assembly-motion or material validation'}
(p/'engineering-v9-results'/(size+'_local_fillet.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report))
