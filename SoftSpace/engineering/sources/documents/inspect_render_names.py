import sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'solver-libraries'))
import gmsh
for name in ['ReplacementCushion_V8_adult_medium_20261013_133840.step','OwnPassiveDefender_V3_adult_20261012_141900.step']:
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.occ.importShapes(str(P/name));gmsh.model.occ.synchronize()
 print(name)
 for dt in gmsh.model.getEntities(3):print(dt,gmsh.model.getEntityName(*dt),round(gmsh.model.occ.getMass(*dt)))
 gmsh.finalize()
