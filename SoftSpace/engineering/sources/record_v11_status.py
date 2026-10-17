from pathlib import Path
import json,hashlib
P=Path(__file__).parent;O=P/'engineering-v11-results';m=json.loads((O/'materials_screen.json').read_text());fine=json.loads((O/'fine_fold_paths.json').read_text());v=json.loads((O/'export_verification.json').read_text())
assert fine['all_pass'] and v['all_pass'] and len(fine['exports'])==6
for r in fine['exports']:assert hashlib.sha256(Path(r['file']).read_bytes()).hexdigest()==r['sha256']
bands=json.loads((P/'engineering-v10-results'/'full_width_sizes_summary.json').read_text())
band_sources={c['size']:Path(c['meshes'][-1]['source']) for c in bands['cases']}
for r in m['band_cases']:assert hashlib.sha256(band_sources[r['size']].read_bytes()).hexdigest()==r['band_source_sha256']
tests=[
 {'test':'Material breadth','status':'Register only for unscreened families','result':str(m['families_count'])+' candidate families; not a finite claim to every formulation'},
 {'test':'Specific structural references','status':'Limited linear analytical screen complete','result':str(m['band_case_count'])+' grade/size combinations and '+str(m['prescribed_load_case_count'])+' imposed-load calculations; not nonlinear, fatigue, creep or drop tests'},
 {'test':'Foam references','status':'Individual datapoint calculations complete','result':str(m['foam_case_count'])+' flat ring proxy cases; no complete material law or comfort result'},
 {'test':'Cover candidates','status':'Manufacturer data and hypotheses only','result':'Film and spacer textiles require physical friction, stretch, seam, vapour and acoustic checks'},
 {'test':'Folding geometry','status':'Chosen sampled sequences pass','result':str(fine['case_count'])+' samples at5degree intervals, six exported STEP files; no continuous or loaded-motion pass'},
 {'test':'Folded STEP exports','status':'Independent import and volume checks pass','result':'28 positive-volume solids in each of six candidates'},
 {'test':'Latch and angular stops','status':'Unfinished design','result':'Final rigidity, retention, play, pinch clearance and release force not established'},
 {'test':'Manufacturing tolerances','status':'Unresolved','result':'Earlier0.217mm guide/tongue gap does not guarantee clearance for assumed0.2mm per part error'},
 {'test':'Durability','status':'Not physically tested','result':'Repeated folding, fatigue, drops, packed compression, cleaning and ageing need final hardware and samples'},
 {'test':'Comfort and sound','status':'Not validated','result':'Material samples, calibrated acoustics and voluntary wearer feedback still needed'},
 {'test':'Sony WH CH720N fit','status':'Awaiting deferred measurements','result':'Generic replacement pad remains unchanged; mount, force, ANC and sound tests open'}]
out={'updated':'2026-10-14','native_CAD':'V10','new_study':'V11 materials and folding','overall_status':'Product and physical validation incomplete','tests':tests,'evidence_SHA256':{name:hashlib.sha256((O/name).read_bytes()).hexdigest() for name in ['materials_screen.json','fine_fold_paths.json','export_verification.json','folding_summary.json']}}
(O/'test_register.json').write_text(json.dumps(out,indent=2))
d=P/'documents'/'document_status.json';status=json.loads(d.read_text());status['additional_study']={'revision':'V11','material_families_registered':70,'quantitatively_screened_structural_references':10,'linear_load_cases':240,'foam_datapoint_cases':14,'folding_samples':fine['case_count'],'folding_exports':6,'physical_validation_complete':False};d.write_text(json.dumps(status,indent=2));print(json.dumps({'folding_samples':fine['case_count'],'material_references':10,'product_validation':'incomplete'}))
