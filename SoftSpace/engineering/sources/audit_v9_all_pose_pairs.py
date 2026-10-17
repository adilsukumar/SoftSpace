"""Independent all-body pair overlap audit of the saved native STEP poses."""
from pathlib import Path
import sys,json,time,hashlib
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import gmsh
version=sys.argv[1] if len(sys.argv)>1 else 'V9'
O=P/('engineering-v10-results' if version.startswith('V10') else 'engineering-v9-results')
if version=='V10Local':
    v=json.loads((O/'cad_local_report.json').read_text());file_rows=[{'file':f} for f in v['files']]
elif version=='V10Native':
    v=json.loads((O/'cad_native_report.json').read_text());assert v['status']=='complete';file_rows=[{'file':f} for f in v['files'] if f.endswith('.step')]
else:
    v=json.loads((O/'native_verification.json').read_text());file_rows=v['STEP_checks']
rows=[]
for frow in file_rows:
    path=Path(frow['file']);start=time.time()
    gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1)
    occ=gmsh.model.occ;occ.importShapes(str(path));occ.synchronize()
    bodies=gmsh.model.getEntities(3);bounds={dt:gmsh.model.getBoundingBox(*dt) for dt in bodies}
    overlaps=[];errors=[];tested=0
    for i,a in enumerate(bodies):
        for b in bodies[i+1:]:
            ba,bb=bounds[a],bounds[b]
            if any(min(ba[k+3],bb[k+3])-max(ba[k],bb[k])<1e-5 for k in range(3)):continue
            copies=[];out=[]
            try:
                ca=occ.copy([a]);cb=occ.copy([b]);copies=ca+cb
                out,_=occ.intersect(ca,cb,removeObject=True,removeTool=True)
                volume=sum(occ.getMass(*dt) for dt in out if dt[0]==3);tested+=1
                if volume>.01:
                    overlaps.append({'body_tags':[a[1],b[1]],'bbox_a_mm':ba,'bbox_b_mm':bb,'intersection_mm3':volume})
            except Exception as e:errors.append({'body_tags':[a[1],b[1]],'error':str(e)})
            finally:
                if out:occ.remove(out,recursive=True)
    gmsh.finalize()
    row={'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'solid_count':len(bodies),'all_pair_count':len(bodies)*(len(bodies)-1)//2,'broad_phase_boolean_count':tested,'overlaps':overlaps,'errors':errors,'pass':not overlaps and not errors,'seconds':time.time()-start}
    rows.append(row);print(json.dumps({'file':path.name,'overlaps':len(overlaps),'errors':len(errors),'seconds':row['seconds']}),flush=True)
    (O/('native_all_pose_pairs_partial.json' if version=='V10Native' else 'all_pose_pairs_partial.json')).write_text(json.dumps(rows,indent=2))
j={'status':'complete','checked_exports':len(rows),'all_pass':all(r['pass'] for r in rows),'checks':rows,'threshold_mm3':.01,'limits':['Rigid saved poses only; not worn contact or tolerances','All exported solids tested, including pivot pins and clamp knobs','STEP body tags are import IDs, not native Fusion body names']}
(O/('native_all_pose_pairs.json' if version=='V10Native' else 'all_pose_pairs.json')).write_text(json.dumps(j,indent=2));print(json.dumps({'status':j['status'],'all_pass':j['all_pass'],'failing_exports':sum(not r['pass'] for r in rows)}))
