from project_paths import verified_source
from pathlib import Path
import sys,json,hashlib
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh
O=P/'engineering-v12-results'
def import_parts(row):
 source=verified_source(row)
 occ=gmsh.model.occ;occ.importShapes(str(source));occ.synchronize();solids=gmsh.model.getEntities(3);assert len(solids)==row.get('solid_count',32);parts={};used=set()
 for name,expected in row['part_bounds_mm'].items():
  # OCC STEP roundtrip changes loose BSpline bbox padding (up to 0.0052 mm observed).
  # This tolerance identifies parts, not a clearance or intersection acceptance gate.
  matches=[dt for dt in solids if dt not in used and max(abs(a-b) for a,b in zip(gmsh.model.getBoundingBox(*dt),expected))<.01 and abs(occ.getMass(*dt)-row['part_volumes_mm3'][name])<.005]
  assert len(matches)==1,(name,matches);parts[name]=matches[0];used.add(matches[0])
 return parts
def audit_pairs(parts,groups=None):
 occ=gmsh.model.occ;occ.synchronize();bounds={name:gmsh.model.getBoundingBox(*dt) for name,dt in parts.items()};names=list(parts);overlaps=[];errors=[];tested=0
 for i,a in enumerate(names):
  for b in names[i+1:]:
   if groups is not None and groups[a]==groups[b]:continue
   ba,bb=bounds[a],bounds[b]
   if any(min(ba[k+3],bb[k+3])-max(ba[k],bb[k])<1e-5 for k in range(3)):continue
   out=[]
   try:
    out,_=occ.intersect(occ.copy([parts[a]]),occ.copy([parts[b]]),removeObject=True,removeTool=True);v=sum(occ.getMass(*dt) for dt in out if dt[0]==3);tested+=1
    if v>.01:overlaps.append({'parts':[a,b],'intersection_mm3':v})
   except Exception as e:errors.append({'parts':[a,b],'error':str(e)})
   finally:
    if out:occ.remove(out,recursive=True)
 dims=[max(b[k+3] for b in bounds.values())-min(b[k] for b in bounds.values()) for k in range(3)]
 return {'overlaps':overlaps,'errors':errors,'pass':not overlaps and not errors,'boolean_count':tested,'bbox_dimensions_mm':dims}
