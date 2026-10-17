import os,sys,json,hashlib
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1'
P=Path(__file__).parent;O=P/'engineering-v14-results';sys.path.insert(0,str(P/'solver-libraries'));import numpy as np
meshes=[]
for h in [2.0,1.5]:
 f=O/('adult_small_fork_h'+str(h)+'.json');r=json.loads(f.read_text());assert hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['source_sha256']
 with np.load(f.with_suffix('.npz')) as a:
  u=a['u'];force=a['force'];work=float(force@u.ravel());energy=abs(2*r['strain_energy_Nmm']-work)/abs(work);balance=float(np.linalg.norm(np.asarray(r['reaction_sum_N'])+force.reshape(-1,3).sum(axis=0)));fixed=float(np.max(np.abs(u.ravel()[a['fixed']])));finite=bool(np.isfinite(u).all() and np.isfinite(a['vm']).all())
 r['independent_algebra_audit']={'work_energy_relative_error':energy,'force_balance_error_N':balance,'maximum_fixed_displacement_mm':fixed,'pass':energy<1e-6 and balance<1e-6 and fixed<1e-12 and finite and r['relative_free_residual']<1e-6 and r['minimum_adaptive_Jacobian_mm3']>0};meshes.append(r)
a,b=meshes;dc=abs(b['weighted_load_direction_displacement_mm']/a['weighted_load_direction_displacement_mm']-1);sc=abs(b['max_von_mises_centroid_MPa']/a['max_von_mises_centroid_MPa']-1)
row={'size':'adult_small','meshes':meshes,'displacement_mesh_change_fraction':dc,'sampled_peak_stress_mesh_change_fraction':sc,'mesh_comparison_pass':dc<.05 and sc<.05,'algebra_audits_pass':all(r['independent_algebra_audit']['pass'] for r in meshes)}
out={'cases':[row],'limits':['One ideal adult-small main fork fixture, not all six joints','Full illustrative pin bore load with fixed pivot bores; cap knob threads screws preload contact friction and worn fit excluded','Homogeneous E2000MPa nu0.35, not a final grade or a manufactured strength rating','No fatigue drop sensory comfort or acoustic pass']};(O/'fork_mechanics_summary.json').write_text(json.dumps(out,indent=2));print({k:row[k] for k in ['mesh_comparison_pass','algebra_audits_pass','displacement_mesh_change_fraction','sampled_peak_stress_mesh_change_fraction']})
