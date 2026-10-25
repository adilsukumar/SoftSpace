"""Review V26 geometry trials with explicit failures and unchanged product gates."""
from pathlib import Path
import json,csv,hashlib,sys,os
P=Path(__file__).resolve().parent;O=P/'engineering-v26-results';sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
cases=[];rows=[];groups={}
for variant,folder in [('A',O),('B',O/'relieved')]:
 group=[]
 for h in [1.9,1.5]:
  f=folder/f'child_large_h{h}_outward.json'
  if not f.exists():continue
  r=json.loads(f.read_text());assert r['converged'] and hashlib.sha256(f.with_suffix('.npz').read_bytes()).hexdigest()==r['raw_sha256'];assert r['independent_residual']<1e-7 and r['force_balance_N']<1e-6 and r['moment_balance_Nmm']<1e-5 and r['coulomb_excess_MPa']<1e-10 and min(r['contact_derivative_errors'])<1e-3 and all(x['passed'] for x in r['rigid_motion_controls']);r['variant']=variant;cases.append(r);group.append(r)
 groups[variant]=group
 if len(group)==2:
  assert group[0]['source_CAD_sha256']==group[1]['source_CAD_sha256']
  for a,b in zip(group[0]['stress'],group[1]['stress']):
   for method in ['interior125','boundary35']:
    u=a['sampled_peaks_MPa'][method];v=b['sampled_peaks_MPa'][method];delta=abs(v/u-1)*100;rows.append(dict(variant=variant,component=a['component'],sampling=method,coarse_MPa=u,fine_MPa=v,change_percent=delta,chosen_5_percent_pass=delta<5))
ma=json.loads((O/'local_motion_audit.json').read_text());mb=json.loads((O/'relieved/local_motion_audit.json').read_text());baseline=json.loads((O/'baseline_local_motion_control.json').read_text());assert all(x['intersection_mm3']<.01 for x in baseline['samples'])
summary=dict(date='2026-10-25',revision='V26',scope='Two local cropped child joint variants only. No full headset integration, adult or inward validation. Fixed assumed reference material and loads remain unchanged.',cases=cases,comparisons=rows,variant_A=dict(accepted_fields=len(groups['A']),mesh_passes=sum(x['chosen_5_percent_pass'] for x in rows if x['variant']=='A'),folding_failures=[x for x in ma['folding_samples'] if not x['passed']],promoted=False),variant_B=dict(accepted_fields=len(groups['B']),mesh_comparisons_available=len(groups['B'])==2,mesh_passes=sum(x['chosen_5_percent_pass'] for x in rows if x['variant']=='B'),sampled_local_motion_pass=mb['sampled_local_motion_pass'],wearing_stop_pass=mb['stop_blocking_pass'],promoted=False),all_product_software_testing_complete=False,whole_part_strength_demonstrated=False,physical_tests=0,main_headset_CAD_changed=False,Sony_pad_CAD_changed=False)
(O/'review_status.json').write_text(json.dumps(summary,indent=2))
with (O/'stress_comparisons.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
register=list(csv.DictReader((P/'engineering-v25-results/remaining_test_register.csv').open()))
register[0].update(Status='Two local candidate studies; read exact accepted fields',Evidence=str(len(cases))+' accepted equilibrium fields',Limit='No full assembly adult or inward result for these candidates')
register[1].update(Status='Not closed',Evidence='A fork comparisons pass; A tongue comparisons fail; see B status separately',Limit='No globally reliable peak or strength claim')
register[4].update(Status='Main assembly unchanged; local regression detected and corrected',Evidence='A obstructs two samples; B passes 25 local positions and two stop queries',Limit='No continuous loaded full headset tolerance or pinch qualification')
register.append(dict(Area='V26 candidate promotion',Status='Not promoted',Evidence='Geometry and solver histories retained separately',Limit='Local part results cannot replace full assembly regression and qualified inputs'))
with (O/'remaining_test_register.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(register[0]));w.writeheader();w.writerows(register)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(9,3.9));labels=['tongue\n125 interior','tongue\n35 boundary','fork\n125 interior','fork\n35 boundary'];x=np.arange(4)
for offset,variant,color in [(-.18,'A','#486d84'),(.18,'B','#4d9c91')]:
 vals=[r['change_percent'] for r in rows if r['variant']==variant]
 if len(vals)==4:ax.bar(x+offset,vals,.36,label='Candidate '+variant,color=color)
ax.axhline(5,color='firebrick',ls='--',label='Chosen 5 percent check');ax.set_xticks(x,labels);ax.set_ylabel('Peak change between meshes percent');ax.set_title('Local joint mesh comparisons retain failures');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(P/'documents/images/V26_stress_comparisons.png',dpi=160);plt.close(fig)
(O/'README.md').write_text('''# V26 rounded joint trials

Full product software validation remains open. These are reversible local child-joint candidates, not new full headset releases. The original V19 full headset and V20 Sony pad CAD remain unchanged.

V25 peak locations pointed to the fork notch beside a radius-6 preload footprint and the tongue transition. Candidate A widens the notch land from x6.001 to x7 and adds 0.6 mm rounds. Two equilibrium fields pass numerical controls. Its fork mesh comparisons pass the chosen 5 percent check; tongue comparisons fail. Independent OCP checks found added folding interference at 25 and 27.5 degrees. Original V19 control queries at those angles did not interfere. A is rejected for promotion.

Candidate B adds a 0.6 mm convex relief at the exact top corner identified by collision bounds. Both STEP solids pass validity and a fork self-intersection positive control. All 25 sampled local folding positions from 0 to 60 degrees pass the 0.01 mm3 overlap check; two outward attempts produce wearing-stop interference. This is not continuous collision or full assembly folding proof. Its accepted equilibrium fields, if any, are listed in review_status.json, never inferred from a solver starting.

The full LU preconditioner was stopped under memory pressure. The first low-memory solve and refreshed fill5 solve failed their linear-solver gates; these are not accepted fields. Broad local refinement exceeded the node guard. Narrower meshes were saved, but A's optional refinement worker was stopped after its folding failure. Logs and resource_events.json retain these outcomes. A stronger refreshed ILU run was stopped at a five-minute operational cap without an accepted field. Its observed process commitment was about 8.7 GB. This operational stop does not prove divergence or physical failure; it leaves strength validation unavailable. Read stronger_resource_stop.json and the exact accepted-field count.

Reproduce with v26_peak_diagnostic.py and v26_geometry.py for A; v26_geometry_audit.py, v26_baseline_motion.py and v26_collision_locations.py check the failure. Use v26_relief_geometry.py and v26_relief_audit.py for B. Equilibrium sources identify their assumptions and raw SHA256 hashes. The 125 interior and 35 boundary stress sets are finite samples and do not bound a global maximum. Geometry, contact, material and physical validity remain distinct gates. Review remaining_test_register.csv before using this package for any prototype or grant claim.
''',encoding='utf-8')
print({k:summary[k] for k in ['variant_A','variant_B','all_product_software_testing_complete']})
