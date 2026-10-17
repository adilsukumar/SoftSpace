from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).parent;O=P/'engineering-v10-results';cad=json.loads((O/'cad_local_report.json').read_text());pairs=json.loads((O/'all_pose_pairs.json').read_text());s=json.loads((O/'solid_v10_summary.json').read_text())
lines=['# V10 guide and clamp clearance candidates','', 'The later all-body audit found V9 clashes at its shortest setting in all six sizes: both pivot pins intersected their guides; child thumb knobs also intersected the forks. The earlier selected-body motion check omitted those parts. The old V9 package is a historical snapshot and is superseded on this clearance question.','', 'V10 trims2mm from the guide bottoms and raises clamp bores and knobs4mm. Crown, cushions, forks, pins and intended30mm adjustment are retained. All18 local nominal/endpoint STEP exports pass the all-body intersection check at the0.01mm3 threshold. These are STEP-only candidates; no native V10 Fusion archive is claimed until separately rebuilt.','', 'Exact-shape minimum distances: guide/tongue0.217157mm; guide/pivot pin1.0mm; knob/fork0.5mm. Nominal overlap clearance is not a manufacturing tolerance pass. The example±0.2mm-per-part closing budget could consume0.4mm, exceeding the smallest gap. No factory capability is assumed.','', 'Changed-guide quadratic structural results use E2000MPa, nu0.35 and an ideal2N/full-side load at the shortened guide face.']
for c in s['cases']:lines.append(f"\n{c['size']}: final stress change {100*c['stress_relative_mesh_change']:.3f}%; guide displacement change {100*c['deflection_relative_mesh_change']:.3f}%; chosen5% stress {'PASS' if c['stress_gate_5pct'] else 'FAIL'}, displacement {'PASS' if c['deflection_gate_5pct'] else 'FAIL'}. Exact STEP source hash is recorded. These are mesh comparisons, not physical-strength tests.")
sl=O/'slider_compliance.json'
if sl.exists():
 q=json.loads(sl.read_text());lines+=['','Exposed-slider segment calculations cover0/15/30mm settings under ideal clamping and end-face loads. They omit guide contact, pin bearing, actual locking and rotational coupling. Only compliance convergence is used; clamped-edge stress is not a strength result.']
force=O/'adjustment_force_screen.json'
if force.exists():
 q=json.loads(force.read_text());f=[r['force_N'] for r in q['cases']];d=[r['max_compression_mm'] for r in q['cases']]
 lines+=['',f"Reduced adjustment force screen: {q['case_count']} synthetic cases; force {min(f):.3f}–{max(f):.3f}N/side, maximum pad compression {min(d):.3f}–{max(d):.3f}mm. This combines linear band and slider compliances in series with a scalar pad model. It does not solve full contact, guide moments or vertical worn fit. Materials, heads, cover tension and35mm mounting offsets are assumed. No comfort or seal threshold is used."]
lines+=['','Band-model scope: quarter X/Y symmetry reflects the front-only clamp bore onto the rear wall. The actual band is not exactly Y-symmetric, as band_symmetry.json confirms. A full-width mechanical comparison is still open. Neither mesh convergence nor the small reflected volume difference establishes the error from this idealization.','', 'Native Fusion rebuilding is prepared in CushionNext/GuideClearanceV10.py. Desktop activation timed out, then failed to activate the captured window. App input stopped pending the requested foreground/ready step. No native V10 completion is asserted.','', 'Next unresolved work: locking threads/retention, manufacturing tolerances and chosen materials, full worn-head/joint contact, durability and calibrated acoustic measurements with and without glasses. Sensory acceptance needs voluntary feedback. No market superiority, pain reduction, universal fit or clinical benefit is established.','', 'The V8 replacement cushion is unchanged. Host-specific compatibility and incoming noise/outgoing music tests require an exact target headphone and measurements.','', 'Both Word reports were updated together. Native Word pagination is unverified because the renderer is unavailable; structural/hash checks and approximate previews were checked.']
(O/'REVIEW.md').write_text('\n'.join(lines),encoding='utf-8');items={}
def add(f,n):items[n]=f
for n in cad['files']:add(Path(n),'CAD/'+Path(n).name)
for f in O.glob('*'):
 if f.suffix in ['.json','.csv','.npz','.md'] and '_partial' not in f.name:add(f,'evidence/'+f.name)
add(P/'engineering-v9-results'/'all_pose_pairs.json','prior-V9/all_pose_pairs.json');add(P/'engineering-v9-results'/'REVIEW.md','prior-V9/REVIEW.md')
for f in (P/'documents').glob('*.docx'):add(f,'documents/'+f.name)
add(P/'documents'/'document_status.json','documents/document_status.json')
for n in ['build_v10_local_candidates.py','audit_v9_all_pose_pairs.py','solid_band_v10.py','solid_band_v9.py','run_v10_structure.py','audit_v10_numerics.py','audit_saved_v10_mesh_quality.py','v10_hotspot_diagnostic.py','v10_clearance_distances.py','audit_v10_band_symmetry.py','annotate_v10_scope.py','render_v10_clearance_fix.py','v10_slider_segment.py','quadratic_surface_load.py','v10_adjustment_force_screen.py','v10-variants.json']:add(P/n,'sources/'+n)
add(P/'CushionNext'/'GuideClearanceV10.py','sources/GuideClearanceV10.py')
manifest={'status':'STEP-only candidate progress; native build pending','CAD_files':len(cad['files']),'all_pose_pairs_pass':pairs['all_pass'],'structural_cases':len(s['cases']),'all_stress_comparisons_pass':s['all_stress_comparisons_pass'],'files':[{'path':n,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for n,f in items.items()]}
target=P/'EarDefender_V10_Clearance_Candidates_and_Checks.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for n,f in items.items():z.write(f,n)
 z.writestr('manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for r in manifest['files']:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
print(json.dumps({'file':str(target),'bytes':target.stat().st_size,'integrity':'pass','status':manifest['status']}))
