"""Close only the defined available-data study, preserving unresolved model gates."""
from pathlib import Path
import json,hashlib,sys
from PIL import Image
P=Path(__file__).resolve().parent;O=P/'engineering-v20-results';D=P/'documents';Q=D/'qa'
s=json.loads((D/'document_status.json').read_text());before=json.loads((Q/'before_v20_body_hashes.json').read_text());changed=[];same=[];added=[]
for f in Q.glob('*/page-*.png'):
 im=Image.open(f);h=hashlib.sha256(im.crop((0,70,im.width,im.height-65)).tobytes()).hexdigest();key=f.relative_to(Q).as_posix()
 old=before.get(key,before.get(key.replace('/','\\')))
 (added if old is None else same if old==h else changed).append(key)
reg=dict(unchanged_prior_bodies=len(same),changed_prior_bodies=changed,added_pages=added,scope='Approximate rendered body hashes excluding header and footer. Native Word pagination unverified.')
(Q/'v20_body_comparison.json').write_text(json.dumps(reg,indent=2),encoding='utf-8')
duplicate=[]
for a,b in zip(range(78,83),range(54,59)):
 def body(stem,n):
  im=Image.open(Q/stem/f'page-{n}.png');return hashlib.sha256(im.crop((0,70,im.width,im.height-65)).tobytes()).hexdigest()
 duplicate.append(dict(main_page=a,flex_page=b,identical_body=body('Ear_Defender_Project',a)==body('Glasses_Friendly_Headphone_Cushions',b)))
# The same shared chapter is used in both reports, but page footer numbers differ.
assert all(r['identical_body'] for r in duplicate)
s['latest_update']=dict(date='2026-10-21',pack_review_date='2026-10-22',standalone_CAD='V19 unchanged',replacement_CAD='V20 reference pad bodies',source='engineering-v20-results',physical_measurements=0,all_requested_computer_models_complete=False,manufacturing_release=False,finite_preprototype_screens_complete=True)
s['publication_branding']=dict(main='SoftSpace',replacement_cushion='SoftSpace Flex',trademark_clearance='Incomplete',legacy_local_report_filenames_preserved=True)
s['quality_check']['approximate_preview_visual_review']=dict(status='pass for changed pages and regression-matched prior bodies',review_date='2026-10-22',changed_pages_reviewed=changed,new_main_pages_reviewed=list(range(78,83)),new_flex_pages=duplicate,unchanged_prior_bodies=len(same),scope='Approximate preview review only. New Flex bodies match the reviewed shared chapter exactly. Native Word pagination remains unverified.')
(D/'document_status.json').write_text(json.dumps(s,indent=2),encoding='utf-8');(Q/'v20_visual_review.json').write_text(json.dumps(s['quality_check']['approximate_preview_visual_review'],indent=2),encoding='utf-8')
contact=json.loads((O/'contact_summary.json').read_text());mechanics=json.loads((O/'mechanical_summary.json').read_text());v=json.loads((O/'verification.json').read_text())
params=json.loads((O/'design_parameters.json').read_text());params['CAD_variant_zone_heights_mm']=[0,18,32];params['screened_zone_heights_mm']=[12,18,24,32];(O/'design_parameters.json').write_text(json.dumps(params,indent=2),encoding='utf-8')
status=dict(results_date='2026-10-21',pack_review_date='2026-10-22',finite_preprototype_study_complete=True,all_possible_software_work_complete=False,full_calibrated_product_simulation_complete=False,physical_validation=False,manufacturing_release=False,prototype_purchase_decision='Small material, pad and bench-hinge samples are justified; production tooling and complete batches are not released',Sony_exact_mount_verified=False,missing_inputs=['Exact Sony groove and skirt dimensions from supplier/reference part','Traceable foam and cover material data','Headband force versus width and hinge torque versus setting','Physical acoustic, thermal and durability measurements'],new_checks=v,contact=contact,mechanical=mechanics,reports=s['documents'],native_Word_layout_verified=False)
(O/'phase_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
for name in ['v20_preprototype_screen.py','verify_v20_screen.py','build_v20_flex_reference.py','run_v20_saved_audits.py','close_v20_preprototype.py']:
 assert (P/name).exists()
inventory=[]
for f in sorted(O.rglob('*')):
 if f.is_file() and f.name!='evidence_manifest.json':inventory.append(dict(path=f.relative_to(O).as_posix(),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size))
inventory += [dict(path='../'+name,sha256=hashlib.sha256((P/name).read_bytes()).hexdigest(),bytes=(P/name).stat().st_size) for name in ['v20_preprototype_screen.py','verify_v20_screen.py','build_v20_flex_reference.py','run_v20_saved_audits.py','close_v20_preprototype.py']]
(O/'evidence_manifest.json').write_text(json.dumps(dict(date='2026-10-22',files=inventory,scope='Integrity list, not scientific validation. The review date does not replace the recorded calculation/source dates.'),indent=2),encoding='utf-8')
print(json.dumps(dict(changed=changed,unchanged=len(same),identical_shared_pages=duplicate,files=len(inventory)),indent=2))
