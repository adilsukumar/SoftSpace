from pathlib import Path
import sys,json,hashlib,ast
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'))
from v12_geometry import gmsh,import_parts
import numpy as np
O=P/'engineering-v27-results';O.mkdir(exist_ok=True)
source=ast.parse((P/'v26_relief_geometry.py').read_text());node=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='modify_joint');node.body=node.body[:next(i for i,n in enumerate(node.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='target' for t in n.targets))]
node.body.append(ast.Return(value=ast.Tuple(elts=[ast.Name(id='keep',ctx=ast.Load()),ast.Name(id='records',ctx=ast.Load())],ctx=ast.Load())))
class API:pass
a=API();a.gmsh=gmsh
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'joint_modification','exec'))
recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())}
for size in ['child_small','child_medium','child_large','adult_small','adult_medium','adult_large']:
 row=json.loads((P/'engineering-v19-results/final-CAD'/(size+'_cad_report.json')).read_text());R=recipes[size]['band_halfspan_mm'];gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;parts=import_parts(row);records=[]
 for prefix in ['Left','Right']:
  keep=[parts[prefix+'Tongue'],parts[prefix+'Fork']]
  if prefix=='Left':occ.mirror(keep,1,0,0,0)
  occ.translate(keep,-R,0,0);occ.synchronize();keep,changes=modify_joint(keep,row,size);occ.translate(keep,R,0,0)
  if prefix=='Left':occ.mirror(keep,1,0,0,0)
  for name,part in zip(['Tongue','Fork'],keep):parts[prefix+name]=part
  records.append(dict(side=prefix,changes=changes))
 occ.synchronize();assert len(gmsh.model.getEntities(3))==42
 f=O/('SoftSpace_V27_'+size+'.step');gmsh.write(str(f));out=dict(row,revision='V27 full assembly with V26B rounded relieved tongue and fork',file=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),source_CAD_sha256=row['sha256'],parts={k:list(v) for k,v in parts.items()},part_bounds_mm={k:list(gmsh.model.getBoundingBox(*v)) for k,v in parts.items()},part_volumes_mm3={k:occ.getMass(*v) for k,v in parts.items()},prototype_changes=records,scope='Prototype geometry candidate; motion and strength results separately required. Pads, band, cup, fastener envelopes unchanged from final V19.')
 (O/(size+'_cad_report.json')).write_text(json.dumps(out,indent=2));gmsh.finalize();print('Saved full assembly',size,flush=True)
