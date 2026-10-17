from pathlib import Path
import json,sys
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh
r=json.loads((P/'engineering-v10-results'/'cad_native_report.json').read_text());f=next(f for f in r['files'] if 'adult_small_' in f and f.endswith('.step') and 'Extension' not in f)
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.occ.importShapes(f);gmsh.model.occ.synchronize()
rows=[{'tag':t,'name':gmsh.model.getEntityName(d,t),'bbox_mm':gmsh.model.getBoundingBox(d,t),'volume_mm3':gmsh.model.occ.getMass(d,t)} for d,t in gmsh.model.getEntities(3)]
gmsh.finalize();(P/'engineering-v10-results'/'adult_small_named_solids.json').write_text(json.dumps(rows,indent=2))
for row in rows:print(json.dumps(row),flush=True)
