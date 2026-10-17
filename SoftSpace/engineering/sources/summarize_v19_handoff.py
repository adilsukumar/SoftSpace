import os,sys,json,hashlib,csv
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=P/'engineering-v19-results';D=O/'final-CAD';I=P/'documents/images';rows=[json.loads(f.read_text()) for f in sorted(D.glob('*_cad_report.json'))];poses=json.loads((D/'STEP_verification.json').read_text());assert poses['all_pass']
cases=[];sizes=[]
for row in rows:
 a=json.loads((D/(row['size']+'_motion_audit.json')).read_text());assert a['sampled_motion_pass'] and a['wearing_stop_blocking_pass'];sizes.append(dict(size=row['size'],file=row['file'],sha256=row['sha256'],solid_count=row['solid_count'],motion_samples=len(a['cases']),stop_queries=len(a['wearing_stop_queries']),folded_box_mm=a['folded_box_mm'],retracted_box_mm=a['retracted_box_mm']))
for f in sorted(O.glob('*_joint_h*.json')):
 r=json.loads(f.read_text());cases.append(dict(file=str(f),size=r['size'],mesh_mm=r['mesh_max_mm'],preload_N=r['preload_N'],mu=r['assumed_mu'],side_force_N=r['side_force_N'],converged=r.get('converged',True),displacement_mm=r.get('cup_mean_displacement_x_mm'),residual=r.get('relative_free_residual')))
joint=json.loads((O/'joint_verification.json').read_text());s=json.loads((O/'handoff_summary.json').read_text());fig,ax=plt.subplots(figsize=(8,4.5))
for size in ['child_large','adult_small']:
 rr=sorted([c for c in cases if c['size']==size and c['preload_N']==140 and c['mu']==.2 and c['side_force_N']==2 and c['converged']],key=lambda c:-c['mesh_mm']);ax.plot([c['mesh_mm'] for c in rr],[c['displacement_mm'] for c in rr],'o-',label=size.replace('_',' '))
ax.invert_xaxis();ax.set(xlabel='Maximum tetrahedron mesh setting in mm',ylabel='Mean cup fixture X displacement in mm',title='V19 joint refinement at 140 N preload and 2 N outward load');ax.legend();fig.text(.5,.01,'Assumed PA66 reference and ideal pivot connector. A converged solve is not a converged mesh or physical test.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.04,1,1));fig.savefig(I/'V19_joint_refinement.png',dpi=160);plt.close(fig)
work=[
 ('Six size CAD and sampled folding','Completed finite checks','42 solids per size, saved poses and sampled motion only'),
 ('Nominal hardware and dimensions','Prototype proposal','Cosmetic threads; exact helix trial rejected; drive runout locking tool access and supplier drawing remain open'),
 ('Band fork and tongue component fixtures','Prior conditional results retained','V18 flexible geometry unchanged; assumed elastic materials and ideal supports'),
 ('Coupled three dimensional joint','Development calculation with failures and mesh limits','Unilateral contact and limited friction; ideal pivot and prescribed preload; not complete fastener or worn assembly'),
 ('All material families and grades','Finite reference screen only','Historical 70 families and 10 numerical reference grades plus 3 PORON points; no exhaustive testing or final winner'),
 ('Foam cover skin glasses and worn force','Measurement dependent','Reduced earlier proxy models only; actual curves friction shapes force and seam/bond data required'),
 ('Sound reduction music leakage and ANC','Measurement dependent','Existing cavity/lumped models exploratory; no validated attenuation or Sony result'),
 ('Heat moisture ageing and fatigue','Measurement dependent','Earlier thermal and material screens exploratory; actual samples and duty cycles required'),
 ('Sony WH CH720N mount','Input blocked','User deferred original pad and mounting measurements; form prepared'),
 ('Native Fusion editable V19','Tool blocked','No native desktop control or connected document session available this turn; V10 archives retained'),
 ('Two living reports','Updated together','Version history failures CAD pictures and test scope retained; approximate layout QA only'),
 ('Manufacturing and budget','Supplier input required','Production drawings tolerance capability actual materials quotations and tooling not released'),
 ('Autistic comfort sensory acceptance and individual preference','Physical feedback required','Voluntary trials and easy removal; cannot be certified by computer simulation')]
register=dict(revision='V19 parallel disc assembly prototype handoff',updated='2026-10-16',sizes=sizes,motion_sample_count=sum(r['motion_samples'] for r in sizes),stop_query_count=sum(r['stop_queries'] for r in sizes),pose_exports=poses,joint_cases=cases,joint_array_audits=len(joint['array_audits']),joint_mesh_comparisons=joint['mesh_comparisons'],retention=s,workstreams=[dict(zip(['workstream','status','scope'],w)) for w in work],physical_measurements=0,native_Fusion_revision='V10',product_complete=False,manufacturing_release=False,all_requested_computer_models_complete=False)
(O/'test_register.json').write_text(json.dumps(register,indent=2))
with (O/'workstream_status.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Workstream','Status','Scope']);w.writerows(work)
text='''# V19 current prototype and evidence

The latest local CAD is V19 with 42 solids in each of six sizes. Start with CAD/V19-assembly-prototype in the archive and prototype-handoff/READ_FIRST.md. V19 STEP is not a native editable Fusion feature tree; native archives remain V10.

This handoff contains a revised parallel-disc hinge proposal, longer pin and jam-nut envelopes, finite collision checks, saved poses, a conditional coupled 3D joint model, source and array checks, dimensions, blank measurement records and both illustrated Word reports. The exact-helix trial was rejected after a disconnected-solid check; no part from that trial is in the final assembly.

The joint is a development model with recorded failed solves and refinement limits. It uses ideal pivot constraints and prescribed preload, not resolved bolt, threads, bearing clearance, disc springs or the complete worn headset. Passing algebra is not a product strength pass. Read joint_verification.json and workstream_status.csv for the actual disposition.

Computer work has not established comfort, sensory acceptance, durability, sound reduction, no music leakage, exact Sony compatibility, cost superiority or production readiness. Earlier models and material references are bounded exploratory calculations. All requested computer models are not complete or validated; some need measurements, supplier decisions or unavailable native tools before useful continuation.

Next: measure actual materials, a bench hinge and headband force; record original Sony WH-CH720N pad and mount dimensions; build and compare uniform and soft-zone pad samples; calibrate the models; then assess a complete prototype on fixtures and with voluntary wearer feedback. Do not order production tooling from this packet.
'''
(O/'REVIEW.md').write_text(text);(O/'REPRODUCE.md').write_text('Run sources in the project root with the bundled Python runtime. Required OCP/Gmsh/NumPy/SciPy versions and local library paths are retained. Sequence: run_v19_cad.py, build_v19_final.py, finish_v19_exports.py, run_v19_contact_matrix.py, refine_v19_joint.py, verify_v19_joint.py, prepare_v19_handoff.py, validate_v19_inputs.py, summarize_v19_handoff.py. Do not rerun update_v19_document_source.py blindly: it is a one-time source migration. Build both reports after the evidence register exists. Heavy model runs are sequential. Existing solved case JSONs are retained by the matrix driver; use a new evidence directory for changed equations or inputs. No physical measurements are generated by these scripts.\n')
print(json.dumps(dict(sizes=len(sizes),motion_samples=register['motion_sample_count'],joint_cases=len(cases),joint_arrays=len(joint['array_audits']),all_requested_models_complete=False)))
