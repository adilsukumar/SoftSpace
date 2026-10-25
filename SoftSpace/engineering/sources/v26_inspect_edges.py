from pathlib import Path
import sys,json
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'))
from v12_geometry import gmsh,import_parts
row=json.loads((P/'engineering-v19-results/child_large_cad_report.json').read_text());gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);parts=import_parts(row);occ=gmsh.model.occ;R=next(r['band_halfspan_mm'] for r in json.loads((P/'lower-crown-recipes.json').read_text()) if r['name']=='child_large');keep=[parts['RightTongue'],parts['RightFork']];occ.remove([dt for dt in gmsh.model.getEntities(3) if dt not in keep],recursive=True);occ.translate(keep,-R,0,0);result,_=occ.cut([keep[0]],[(3,occ.addBox(-20,-40,row['guide_bottom_mm'],55,80,70))]);keep=[result[0],keep[1]];occ.synchronize();records=[]
for name,body in zip(['tongue','fork'],keep):
 faces=gmsh.model.getBoundary([body],oriented=False);edges=gmsh.model.getBoundary(faces,combined=True,oriented=False)
 # combined removes closed boundary edges, so collect individual surface edges instead.
 edges=set(dt for face in faces for dt in gmsh.model.getBoundary([face],oriented=False))
 for dim,tag in sorted(edges):
  b=occ.getBoundingBox(dim,tag);c=occ.getCenterOfMass(dim,tag)
  if (name=='tongue' and abs(c[0])<3 and 63<c[2]<67) or (name=='fork' and 5<c[0]<8 and 58<c[2]<64):records.append(dict(part=name,tag=tag,type=gmsh.model.getType(dim,tag),bounds=list(b),centre=list(c),length=occ.getMass(dim,tag)))
print(json.dumps(records,indent=2));gmsh.finalize()
