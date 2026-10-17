"""Check whether the source band supports the width-symmetry approximation."""
from pathlib import Path
import sys,json
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh
O=P/'engineering-v10-results';cad=json.loads((O/'cad_local_report.json').read_text());rows=[]
for s in cad['sizes']:
 source=P/('OwnPassiveDefender_V10Local_'+s['name']+'.step');gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;occ.importShapes(str(source));occ.synchronize()
 band=next(dt for dt in gmsh.model.getEntities(3) if (lambda b:b[0]<-75 and b[3]>75 and 81.99<b[2]<82.01 and b[4]-b[1]<30)(gmsh.model.getBoundingBox(*dt)))
 volume=occ.getMass(*band);mirror=occ.copy([band]);occ.mirror(mirror,0,1,0,0);common,_=occ.intersect([band],mirror);shared=sum(occ.getMass(*dt) for dt in common if dt[0]==3);gmsh.finalize()
 rows.append({'size':s['name'],'band_volume_mm3':volume,'Y_reflection_symmetric_difference_mm3':2*(volume-shared),'exact_Y_symmetry':abs(volume-shared)<.01})
j={'status':'complete','cases':rows,'interpretation':'The front-only clamp bore breaks Y symmetry. The quarter-band calculation mirrors the front half and its bore, rather than reproducing the actual rear wall. It is an explicit idealization, not a full-width band or assembled-contact result.','limit':'Small volume difference does not establish small stress error; full-width mechanical comparison remains open.'}
(O/'band_symmetry.json').write_text(json.dumps(j,indent=2));print(json.dumps(rows))
