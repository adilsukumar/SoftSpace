from pathlib import Path
import json,hashlib
P=Path(__file__).parent;O=P/'engineering-v16-results'
s=json.loads((O/'selected_candidates.json').read_text());e=json.loads((O/'STEP_verification.json').read_text());m=json.loads((O/'tongue_mechanics_summary.json').read_text())
def matched(path,digest):assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
for r in s['sizes']:
 matched(r['file'],r['sha256']);a=json.loads((O/(r['variant']+'_audit.json')).read_text());assert a['complete_sampled_motion_pass'] and a['index_blocking_pass'] and a['retention_blocking_pass']
assert s['motion_sample_count']==229 and s['solid_validity_checks']==276
assert e['case_count']==18 and e['all_pass']
for r in e['cases']:matched(r['file'],r['sha256'])
assert m['algebra_audits_pass'] and m['adult_upper_fixture']['algebra_audits_pass']
tests=[{'test':'Selected six size CAD','result':'276 solid validity checks and 229 discrete motion sequence samples pass','limit':'Rigid geometry only; not continuous loaded contact or manufacture'},
 {'test':'Folded pin engagement and knob capture','result':'48 index blocking and 36 retention blocking queries recorded','limit':'No measured spring return, holding force, forming process or child access qualification'},
 {'test':'STEP exports','result':'18 independent reimport checks pass','limit':'Native Fusion archives remain V10'},
 {'test':'Child lower plate component fixture','result':'Two meshes and independent algebra audits pass chosen comparisons','limit':'Ideal rigid guide at z82; assumed material and whole-bore traction; not complete joint'},
 {'test':'Adult upper plate component fixture','result':m.get('adult_upper_fixture',{}).get('status','Not completed'),'limit':'Separate support geometry; previous child and older fork results do not qualify it'},
 {'test':'Material reference screens','result':'45 plate cases, 15 stem cases and 36 foam load cases recorded','limit':'Only12 foam cases inside published strain range. No material qualification or exhaustive material testing'},
 {'test':'Physical product validation','result':'Not performed; seven blank records prepared','limit':'Comfort, autistic sensory acceptance, heat, noise reduction, outgoing sound, durability, Sony fit and actual cost remain open'}]
out={'revision':'V16 six size indexed folding candidates','native_Fusion_revision':'V10','manufacturing_release':False,'physical_validation_complete':False,'tests':tests,'selected':s,'STEP_checks':e,'mechanics':m}
if (O/'joint_tolerance_screen.json').exists():
 tolerance=json.loads((O/'joint_tolerance_screen.json').read_text());offset=json.loads((O/'offset_contact_validation.json').read_text());assert offset['case_count']==60 and offset['all_match']
 out.update(joint_tolerances=tolerance,offset_contact_validation=offset)
 tests.append({'test':'Additional bounded joint tolerance screen','result':'600 index scenarios, 100 interface scenarios and 60 source-solid offset queries recorded;57 index scenarios retain positive worst-case margin','limit':'Not manufacturing capability or yield. Nominal0.05mm index radial clearance is consumed by small combined errors; tolerance qualification remains open'})
(O/'test_register.json').write_text(json.dumps(out,indent=2))
(O/'REVIEW.md').write_text('''# V16 indexed folding candidates

Six local STEP candidates add wearing and folded index holes plus a recessed formed cross rivet for knob retention. Child lower plates and adult upper rear plates use different supports. Native editable Fusion archives remain V10. This is not a manufacturing release.

The selected source geometry passed 229 discrete sequence samples and 276 solid-validity checks. Forty-eight attempted index rotations and 36 attempted retention escapes produced the intended blocking. These are positive geometric capture queries, not force, spring return, continuous sweep, pinch or child small-part tests. Eighteen STEP pose exports passed independent reimport checks. Packing comparisons use each headset retracted and unfolded as the baseline.

Keep the rejected adult lower plates, initial obstructed upper housing, failed curved adult mesh attempts, interrupted fine top-only child solve and corrected query control in the evidence. Later passes do not erase these failures. The child top-only result predicts about11mm movement and is not a reliable small-displacement product prediction. Its guide-supported alternative is an ideal truncated clamp, not measured guide contact. Read tongue_mechanics_summary.json for each separate fixture and its mesh comparison.

Material screens use published grade references and assumptions; no final grade or process is selected. The thin foam curves cannot qualify a shaped20mm cushion. Blank physical records have no results. Sony WH-CH720N mounting measurements were deferred and its pad is unchanged. Comfort, sensory acceptance, acoustic attenuation, outgoing playback leakage, heat, cleaning, drops, fatigue, ageing, manufacturing yield, cost and market superiority remain unvalidated.

The additional bounded tolerance screen records600 index scenarios and100 interface scenarios. Only57 index scenarios retain positive worst-case clearance. These are chosen bounds, not process capability or a yield prediction. Sixty source-solid offset queries agree with the nominal0.05mm radial index clearance. Small combined diameter and centre errors consume this clearance. Reliable pin entry and return, actual tolerances and rivet formation remain unresolved. No CAD was changed for this screen.

Both Word reports share this update. Approximate ReportLab previews do not verify native Word pagination. ZIP CRC and SHA checks establish storage integrity only.
''')
f=P/'documents/document_status.json';d=json.loads(f.read_text());d['latest_study']={k:out[k] for k in ['revision','native_Fusion_revision','manufacturing_release','physical_validation_complete']};d['latest_study'].update(latest_six_size_CAD_revision='V16',motion_samples=229,STEP_checks=18);f.write_text(json.dumps(d,indent=2));print('V16 register and paired document status updated')
