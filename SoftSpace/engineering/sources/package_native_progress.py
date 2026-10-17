from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).parent;O=P/'engineering-v9-results';v=json.loads((O/'native_verification.json').read_text());s=json.loads((O/'solid_v9_summary.json').read_text())
complete=v['status']=='complete' and s['status']=='complete' and s['all_available_stress_comparisons_pass'] and all(c['deflection_gate_5pct'] for c in s['cases'])
status='complete bounded digital checks' if complete else 'partial'
lines=['# Native V9 CAD and structural review','',f"Native geometry exported for {len(v['sizes'])} of 6 sizes. Digital check status: {status}. This is an experimental design package; product validation is unfinished.",'','Eight internal vertical slider corners were rounded by 0.5 mm. All available STEP imports contain 28 solids and the recorded band static/slider overlap checks passed. Each size has a nominal STEP, two slider endpoint STEP files and a matching local Fusion archive. The six sizes are synthetic width variants, not an anthropometric fit guarantee.']
for c in s['cases']:
 lines.append(f"\n{c['size']}: last stress mesh change {100*c['stress_relative_mesh_change']:.3f}%; guide displacement change {100*c['deflection_relative_mesh_change']:.3f}%. Latest centroid stress {c['meshes'][-1]['max_von_mises_centroid_MPa']:.4f}MPa under assumed E2000MPa, nu0.35, ideal2N/side. No material-strength or comfort claim.")
forcefile=O/'nominal_force_screen.json'
if forcefile.exists():
 q=json.loads(forcefile.read_text());fr=[r['force_N'] for r in q['cases']];cr=[r['max_compression_mm'] for r in q['cases']]
 lines += ['',f"Nominal hybrid force screen: {q['case_count']} cases, middle slider setting only, calculated force {min(fr):.3f} to {max(fr):.3f} N per side; maximum foam compression {min(cr):.3f} to {max(cr):.3f} mm. Native linear band compliance is coupled to the earlier scalar pad model. Materials, heads and 35 mm mount offset are assumed. No comfort threshold or full 3D worn-contact result."]
lines+=['','Archive check: six local Fusion archive container directories are readable. Their member compression is unsupported by the bundled ZIP checker, so member integrity/native reopening is unverified. Independent nominal and endpoint STEP imports and volume preservation checks passed.']
lines+=['','V9 refines the V8 standalone band. The V8 replacement cushion is unchanged. Keep the V8 package for its pad, force sensitivity and acoustic screening evidence. No real sound leakage, wearer comfort or physical strength result has been added.','',"Desktop control recovered and the remaining native builds ran. Old local STEP-only failures remain separate. Native mesh results apply only to their recorded geometry and ideal load. They do not verify scalp contact, slider locking, material yield, fatigue, drops or the whole assembly.",'','Before fabrication, choose actual foam, cover and band materials and measure their properties. Fit a complete assembly and calculate nonlinear contact using those measurements. Test slider retention and manufacturing tolerances. Acoustic attenuation needs a calibrated physical setup with and without glasses; music-out tests need a specific host headphone. Sensory acceptance requires voluntary wearer feedback. These cannot be replaced by assuming favourable inputs.','', 'No market superiority is established. Our calculated stress/displacement cannot be ranked against market products whose geometry, materials and matched measured tests are unavailable. The market review covers a selected sample, not every model.','', 'Both Word documents were updated together. Their native Word layout remains unverified; independent approximate previews and structural checks are available.']
(O/'REVIEW.md').write_text('\n'.join(lines),encoding='utf-8')
items={}
def add(f,target):items[target]=f
for name in v['files']:add(Path(name),'CAD/'+Path(name).name)
for folder in ['engineering-v9-results','engineering-v9-local-results']:
 for f in (P/folder).glob('*'):
  if f.suffix in ['.json','.npz','.md','.csv']:add(f,'evidence/'+folder+'/'+f.name)
for f in (P/'documents').glob('*.docx'):add(f,'documents/'+f.name)
for name in ['cad_v9_report.json','cad_v9_adult_small_first.json','v9-variants.json','lower-crown-recipes.json','solid_band_v9.py','verify_native_v9.py','summarize_native_v9.py','run_native_v9_remaining.py','audit_native_v9.py','audit_v9_exports.py','render_v9_results.py','v9_nominal_force_screen.py']:add(P/name,name)
add(P/'documents'/'document_status.json','documents/document_status.json')
add(P/'documents'/'build_documents.py','sources/build_documents.py')
add(P/'CushionNext'/'RefineBandV9.py','sources/RefineBandV9.py')
manifest={'status':status,'native_sizes':len(v['sizes']),'verified_STEP_files':len(v['STEP_checks']),'files':[{'path':n,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for n,f in items.items()]}
target=P/('EarDefender_V9_CAD_and_Structural_Checks.zip' if complete else 'EarDefender_V9_Native_Progress.zip')
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for n,f in items.items():z.write(f,n)
 z.writestr('manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for f in manifest['files']:assert hashlib.sha256(z.read(f['path'])).hexdigest()==f['sha256']
print(json.dumps({'file':str(target),'bytes':target.stat().st_size,'integrity':'pass','status':status}))
