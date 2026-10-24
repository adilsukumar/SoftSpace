"""Close the bounded V22 checks with every remaining model/input gate explicit."""
from pathlib import Path
import sys,os,json,hashlib,csv,itertools
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
source=P/'v22_quadrature_mesh_audit.py';prefix=source.read_text().split("for size in ['child_large'")[0];exec(compile(prefix,str(source),'exec'));O=P/'engineering-v22-results';old=json.loads((O/'quadrature_mesh_audit.json').read_text());targeted=[]
for side in ['outward','inward']:
 path=O/('adult_fork_local_0.9_'+side+'.json');meta=json.loads(path.read_text());assert meta['converged'];z=np.load(path.with_suffix('.npz'));split=3*len(z['xt']);parts=[]
 for ix,(xn,tn,u) in enumerate([('xt','tt',z['u'][:split]),('xf','tf',z['u'][split:])]):
  x=z[xn];t=z[tn];ue=u.reshape(-1,3)[t];peaks={};energy={};minimum=1e99
  for order in [3,5]:
   peak=0.;en=0.
   for L,w in q.quadrature(order):
    strain,det=tensor(x,t,ue,L);assert det.min()>0;sig=strain@D.T;peak=max(peak,float(vm(sig).max()));en+=float((.5*np.einsum('ij,ij->i',strain,sig)*det*w).sum());minimum=min(minimum,float(det.min()))
   peaks[str(order**3)]=peak;energy[str(order**3)]=en
  latticepeak=0.;bad=0
  for ints in itertools.product(range(5),repeat=3):
   last=4-sum(ints)
   if last<0:continue
   L=np.array([last,*ints])/4;J=np.einsum('eia,ib->eab',x[t],q.gradients(L));det=np.linalg.det(J);bad+=int(sum(det<=0))
   if det.min()>0:latticepeak=max(latticepeak,float(vm(tensor(x,t,ue,L)[0]@D.T).max()))
  ref=next(r for r in old['cases'] if r['size']=='adult_small' and r['h']==1.9 and r['direction']==side and r['component']==['tongue','fork'][ix]);changes=dict(interior_27=abs(peaks['27']/ref['quadrature'][0]['interior_sampled_peak_MPa']-1)*100,interior_125=abs(peaks['125']/ref['quadrature'][2]['interior_sampled_peak_MPa']-1)*100,boundary_lattice=abs(latticepeak/ref['lattice_including_boundary_sampled_peak_MPa']-1)*100)
  parts.append(dict(component=['tongue','fork'][ix],peak_MPa=peaks,boundary_lattice_sampled_peak_MPa=latticepeak,peak_change_from_V21_percent=changes,chosen_5_percent_sampling_comparisons={k:v<5 for k,v in changes.items()},bulk_energy_N_mm=energy,nonpositive_35_point_lattice_Jacobians=bad,minimum_interior_Jacobian=minimum))
 baseline=json.loads((P/'engineering-v21-results/refinement'/('adult_small_'+side+'_h1.9.json')).read_text());balance=float(np.linalg.norm((z['reaction']+z['force']).reshape(-1,3).sum(axis=0)));assert balance<1e-5 and meta['relative_free_residual']<1e-7;disp=abs(meta['cup_mean_displacement_x_mm']/baseline['cup_mean_displacement_x_mm']-1)*100
 targeted.append(dict(direction=side,equilibrium_pass=True,relative_equilibrium_residual=meta['relative_free_residual'],force_balance_N=balance,displacement_change_percent=disp,fork_peak_125_change_percent=parts[1]['peak_change_from_V21_percent']['interior_125'],parts=parts,raw_solution_sha256=hashlib.sha256(path.with_suffix('.npz').read_bytes()).hexdigest(),source_CAD_sha256=meta['source_CAD_sha256']))
 print(side,parts,flush=True)
allpass=all(all(c['chosen_5_percent_sampling_comparisons'].values()) for x in targeted for c in x['parts'])
plain=('The targeted comparisons meet all the selected 5 percent sampling checks in this subset. ' if allpass else 'Some targeted sampling comparisons still exceed the chosen 5 percent check. ')+ 'This does not close the wider child and adult stress sampling problem. Stable force balance and displacement do not establish part strength. The actual edge and contact geometry, bolt detail and manufactured material remain unqualified.'
result=dict(date='2026-10-24',executed_V22_checks_complete=True,all_possible_software_testing_complete=False,physical_tests=0,CAD_changed=False,targeted_cases=targeted,targeted_all_sampling_comparisons_pass=allpass,targeted_plain_english=plain,scope='V19 isolated fixture geometry, same assumed E 3500 MPa nu .35, preload 140 N friction .2 and side load plus/minus 2 N. Local 0.9 mm target near adult fork hotspots, V21 tongue mesh. No resolved fastener or whole headset.',remaining_software_failure='Stable whole-part peak stress not demonstrated across recovery sampling and meshes. Actual contact/edge geometry and targeted model revision remain open.',input_gates=['Named manufactured material grades and compression/time-dependent curves','Cover tension, seams, friction and worn head geometry','Sony skirt and groove dimensions','Acoustic seal and pad properties','Thermal and moisture properties of assembled materials','Complete fastener geometry, process tolerances and durability acceptance criteria'],human_tests=['Comfort','Sensory acceptance','Real handling and sound performance'])
(O/'review_status.json').write_text(json.dumps(result,indent=2));(O/'targeted_joint_review.json').write_text(json.dumps(dict(date=result['date'],cases=targeted,scope=result['scope']),indent=2))
rows=list(csv.DictReader((P/'engineering-v21-results/test_scope_register.csv').open()));rows=[r for r in rows if r['test']!='Report native pagination']
for r in rows:
 if r['test']=='Peak stress refinement':r.update(status='FAILED broader recovery sampling',evidence='V22 recovery_comparisons.json and targeted_joint_review.json',limit_or_next_input='The six V21 passes applied to 27 interior points only; global stress remains unqualified')
rows.extend([dict(test='Higher integration and strain control',status='Completed numerical controls',evidence='V22 quadrature_mesh_audit.json',limit_or_next_input='16 saved component/load/mesh fields; energy sensitivity does not bound stress'),dict(test='Targeted adult fork',status='Completed with exact comparison statuses retained',evidence='V22 targeted_joint_review.json',limit_or_next_input='No whole product strength pass'),dict(test='Whole pad softer foam control',status='25272 assumed cases complete',evidence='V22 uniform_softness_summary.json',limit_or_next_input='22012 within selected compression limit; four model detachment cases; not comfort or leakage validation')])
with (O/'test_scope_register.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
text='''# V22 software review on 24 October 2026

This bounded review is complete with passes and failures retained. It does not establish all possible software testing, final product performance or manufacturing readiness. The two Word reports contain the same update.

The V21 six passing stress comparisons applied only to 27 interior points. V22 recomputed strains with a separate tensor-gradient expression and used 64 and 125 interior points, plus a finite 35-point lattice including corners, edges and faces. Energy changes between orders 4 and 5 were below 0.00004 percent; no nonpositive lattice Jacobian was found in these saved fields. These checks do not certify curved elements everywhere or bound stiffness error. Only two of eight 125-point peak comparisons and one of eight boundary-lattice comparisons met the chosen 5 percent mesh comparison. No globally stable peak or real strength pass is supported.

Two additional adult load cases use a 0.9 mm local fork mesh around the recorded hotspots, retaining the V21 tongue and unchanged V19 CAD. Read targeted_joint_review.json for all sampling comparisons, residuals and force balance. No different sampling method is substituted to erase a failed comparison. Nearest-node interpolation only warm-starts the iteration; acceptance requires actual final equilibrium. These fixtures use idealized pivot/contact and prescribed preload, not a real resolved bolt or worn headset.

A whole-annulus softer-foam control adds 25,272 assumed cases. 22,012 meet the chosen 40 percent compression limit. None of those eligible cases raises local or peak pressure in the reduced model; four have model detachment. The remaining 3,260 exceed the compression limit. A direct uniform-modulus control matches active-area pressures exactly. This makes uniformly softer foam a comparison candidate, not a selected material, comfort benefit, seal or acoustic result. The earlier 100 mm strip altered only the arm-facing half; this new control alters both halves. No cushion or headset part shapes are changed.

## Remaining work

Whole-part peak stress, detailed fastener contact and manufactured edge geometry remain a software/design problem. Material curves, cover and worn contact data, exact Sony mounting, acoustics, heat, creep/fatigue and production tolerances remain input-dependent. Comfort and sensory acceptance require people. Arbitrary extra generic material values do not supply these missing inputs. Read the complete test register before making claims or buying production tooling.

## Reproduce

Use a prepared repository workspace and the recorded numerical dependencies. Run v22_quadrature_mesh_audit.py, v22_recovery_summary.py and v22_uniform_softness.py. The targeted mesh uses v22_local_fork_mesh.py 0.9 and v22_local_fork_solve.py 0.9; these can take substantial time. Then run v22_review.py. Original V19 and V21 raw solutions are preserved. The new solve is fixed-point Anderson acceleration with direct LU and a recorded force-residual gate. It does not calibrate material properties or validate physical performance.
'''
(O/'README.md').write_text(text,encoding='utf8');print(json.dumps(dict(complete=True,targeted_all_sampling_pass=allpass),indent=2))

ctrl=json.loads((O/'contact_rigid_motion_controls.json').read_text());result['original_contact_all_rigid_motion_checks_pass']=ctrl['all_common_rigid_motion_checks_pass'];result['corrected_candidate_all_rigid_motion_checks_pass']=ctrl['corrected_candidate_all_rigid_motion_checks_pass'];result['adaptive_mesh_quality']=json.loads((O/'adaptive_mesh_quality.json').read_text())
result['objective_spacer_cases']=[]
for side in ['outward','inward']:
 path=O/('objective_spacer_'+side+'.json')
 if path.exists():result['objective_spacer_cases'].append(dict(direction=side,**json.loads(path.read_text())))
(O/'review_status.json').write_text(json.dumps(result,indent=2))
p=O/'README.md';text=p.read_text();text+='\n## Contact model correction\n\nThe original virtual separated-face tangential operator fails four common rigid-rotation checks across the two size families. Common translations and the hinge-axis rotation pass. A proposed 0.5 mm virtual-spacer mean-bore-rotation correction passes all twelve rigid-motion checks. This defines a mathematical reference, not an actual washer or a validated physical contact law. The original fields fail the corrected equilibrium residual gate, so new corrected reference fields are computed separately by v22_objective_spacer_solve.py with checked matrix-free Newton and GMRES. Read objective_spacer_outward.json and objective_spacer_inward.json for the exact converged status, residuals and derivative controls. No corrected field is accepted merely because the kinematic checks pass. The original histories and failed model checks remain preserved.\n';p.write_text(text,encoding='utf8')

audit=json.loads((O/'spacer_candidate_residual_check.json').read_text());assert audit['complete'] and audit['candidate_corrected_fields_satisfy_residual'];assert all(x['global_moment_balance_N_mm']<1e-6 for x in audit['cases'] if x['kind']=='corrected');result['independent_corrected_field_audit']=audit
(O/'review_status.json').write_text(json.dumps(result,indent=2))
with (O/'test_scope_register.csv').open() as f:rows=list(csv.DictReader(f))
rows.extend([dict(test='Contact common rigid motion',status='Original 4 failed of 12; candidate 12 passed',evidence='V22 contact_rigid_motion_controls.json',limit_or_next_input='Virtual spacer correction, not an actual washer contact law'),dict(test='Corrected reference equilibrium',status='Both load cases converged and separately rechecked',evidence='V22 objective_spacer files and spacer_candidate_residual_check.json',limit_or_next_input='Fixed model assumptions; no whole product or peak stress qualification'),dict(test='Adaptive curved element quality',status='10 component mesh checks positive',evidence='V22 adaptive_mesh_quality.json',limit_or_next_input='Geometric validity is not solution accuracy')])
with (O/'test_scope_register.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
p=O/'README.md';text=p.read_text();text+='\nBoth corrected reference load cases converged. A separate matrix-free residual implementation rechecked them at about 3e-11 relative residual. Net force balance errors are below 7e-10 N and moment balance errors below 1e-8 N mm. The original reference had about 0.06 N mm unbalanced internal moment in this test. The correction resolves this mathematical consistency issue in the defined virtual-spacer reference. It does not establish real washer mechanics, manufactured material strength or stable stress over further meshes and recovery points.\n';p.write_text(text,encoding='utf8')
