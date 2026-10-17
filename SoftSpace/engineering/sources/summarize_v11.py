from pathlib import Path
import sys,json,math,hashlib,os
os.environ['OPENBLAS_NUM_THREADS']='1'
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh
O=P/'engineering-v11-results';f=json.loads((O/'folding_fork_stagger_75_screen.json').read_text());rows=[]
adaptive=json.loads((O/'folding_fork_stagger_adaptive_screen.json').read_text()) if (O/'folding_fork_stagger_adaptive_screen.json').exists() else None
for size in sorted({r['size'] for r in f['cases']}):
 cases=[r for r in f['cases'] if r['size']==size];adapt=[r for r in adaptive['cases'] if r['size']==size] if adaptive else []
 if adapt:cases=adapt
 source=Path(cases[0]['source'])
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.occ.importShapes(str(source));gmsh.model.occ.synchronize();bounds=[gmsh.model.getBoundingBox(*dt) for dt in gmsh.model.getEntities(3)]
 dims=[max(b[k+3] for b in bounds)-min(b[k] for b in bounds) for k in range(3)];volume=math.prod(dims)/1e6;gmsh.finalize()
 prefix=[]
 for c in cases:
  if not c['nominal_pose_pass']:break
  prefix.append(c)
 best=min(prefix,key=lambda r:r['bounding_box_volume_L']);target=next(r for r in cases if r['left_fold_deg']==(60 if adapt else 75) and r['right_fold_deg']==45)
 rows.append({'size':size,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'nominal_bbox_mm':dims,'nominal_bbox_L':volume,'sampled_path_prefix_passes':len(prefix),'best_reached_sample_angles_deg':[best['left_fold_deg'],best['right_fold_deg']],'best_reached_bbox_L':best['bounding_box_volume_L'],'reduction_fraction_from_original_nominal':1-best['bounding_box_volume_L']/volume,'best_reached_STEP':best.get('candidate_STEP'),'target_pose_pass':target['nominal_pose_pass'],'target_path_samples_pass':all(r['nominal_pose_pass'] for r in cases[:cases.index(target)+1]),'first_failed_path_pose':None if len(prefix)==len(cases) else [cases[len(prefix)]['left_fold_deg'],cases[len(prefix)]['right_fold_deg']]})
 rows[-1]['target_angles_deg']=[target['left_fold_deg'],target['right_fold_deg']]
out={'status':'complete six-size exploratory screen','sizes':rows,'poses':len(f['cases']),'all_target_paths_pass':all(r['target_path_samples_pass'] for r in rows),'limits':['Strict all-solid intersection check; soft foam overlaps also fail until a compression model supports them','All recorded paths are sampled at15degree intervals, not swept volumes','A final pose after a failed intermediate sample is not counted as reached','Negative volume reduction means larger than the original nominal envelope','The bounded-box packing proxy does not establish carryability, hinge strength, latching or fatigue','V11 is a study on transformed V10 solids, not a new native Fusion hinge assembly']}
out['base_six_size_poses']=len(f['cases']);out['adaptive_poses']=len(adaptive['cases']) if adaptive else 0
out['all_adapted_target_paths_pass']=all(r['target_path_samples_pass'] for r in rows)
(O/'folding_summary.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

