from pathlib import Path
import json,sys,hashlib
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh
O=P/'engineering-v11-results';fine=json.loads((O/'fine_fold_paths.json').read_text());summary=json.loads((O/'folding_summary.json').read_text());sources={r['size']:r for r in summary['sizes']};rows=[]
def inspect(path):
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.occ.importShapes(str(path));gmsh.model.occ.synchronize();entities=gmsh.model.getEntities(3);masses=[gmsh.model.occ.getMass(*dt) for dt in entities];gmsh.finalize();return len(entities),sum(masses),all(m>0 for m in masses)
for r in fine['exports']:
 target=Path(r['file']);source=Path(sources[r['size']]['source']);assert hashlib.sha256(target.read_bytes()).hexdigest()==r['sha256'];assert hashlib.sha256(source.read_bytes()).hexdigest()==sources[r['size']]['source_sha256']
 n,m,p=inspect(target);ns,ms,ps=inspect(source);delta=abs(m-ms)
 row={'size':r['size'],'export':str(target),'export_sha256':r['sha256'],'source':str(source),'source_sha256':sources[r['size']]['source_sha256'],'solids':n,'positive_volumes':p,'source_solids':ns,'total_solid_volume_difference_mm3':delta,'pass':n==ns==28 and p and ps and delta<.01};rows.append(row);print(r['size'],row['pass'],flush=True)
out={'status':'complete independent reimport','cases':rows,'all_pass':len(rows)==6 and all(r['pass'] for r in rows),'scope':'STEP import, positive solid volumes and conservation under rigid transforms. Separate fine_fold_paths.json covers sampled intersections. No native Fusion file or mechanical joint validation.'}
(O/'export_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({'all_pass':out['all_pass'],'exports':len(rows)}))
