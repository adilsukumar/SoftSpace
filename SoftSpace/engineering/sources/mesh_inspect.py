import sys,json
from pathlib import Path
p=Path(__file__).parent;sys.path.insert(0,str(p/'solver-libraries'))
import gmsh
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0)
f=sorted(f for f in p.glob('OwnPassiveDefender_V6_child_small_*.step') if 'Extension' not in f.name)[-1]
print('Inspecting',f.name)
gmsh.model.occ.importShapes(str(f));gmsh.model.occ.synchronize()
for d,t in gmsh.model.getEntities(3):
 print(t,gmsh.model.getEntityName(d,t),[round(v,2) for v in gmsh.model.getBoundingBox(d,t)],round(gmsh.model.occ.getMass(d,t),2))
gmsh.finalize()
