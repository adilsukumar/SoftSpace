from pathlib import Path
import json,shutil,hashlib
P=Path(__file__).parent; Q=P/'documents/qa'; O=P/'engineering-v19-results'
r=json.loads((Q/'v19_body_regression.json').read_text())
records=[]
for d in r['documents']:
 records.append(dict(document=d['document'],visually_inspected_pages=[int(Path(f).stem.split('-')[-1]) for f in d['pages_requiring_visual_review']],unchanged_previously_reviewed_page_bodies=len(d['previously_reviewed_bodies_unchanged'])))
(Q/'v19_visual_review.json').write_text(json.dumps(dict(date='2026-10-16',result='pass for approximate previews',documents=records,observation='No clipping, unreadable figures or broken tables observed. Glasses report page 12 carries the continuation paragraph from the preceding change table. Reviewed footer numbers align with page files, ending at 76 and 52.',scope='Approximate ReportLab previews. Exact body regression excludes only footer band. Native Word pagination could not be verified; renderer unavailable.'),indent=2))
old=O/'report_completion_status.json'; hist=O/'document-build-history';hist.mkdir(exist_ok=True)
if old.exists() and not (hist/'initial_draft_completion_status.json').exists():shutil.copy2(old,hist/'initial_draft_completion_status.json')
s=json.loads((P/'documents/document_status.json').read_text())
for d in s['documents']:assert hashlib.sha256(Path(d['path']).read_bytes()).hexdigest()==d['sha256']
old.write_text(json.dumps(dict(date='2026-10-16',prototype_report_update_complete=True,saved_result_audits_complete=True,approximate_preview_review='pass',native_Word_pagination_verified=False,current_STEP_revision='V19',native_Fusion_revision='V10',all_requested_computer_models_complete=False,product_complete=False,manufacturing_release=False,remaining=['Measured material curves and hinge/headband behaviour','Calibrated full worn contact, acoustic and thermal models','Sony WH-CH720N mount measurements and compatible carrier','Hardware locking, tolerances and manufacturing review','Physical acoustic, durability and voluntary sensory acceptance tests']),indent=2))
print('Review records saved; document hashes match.')
