"""Run only after visually inspecting the inward report pages identified by regression."""
import json,hashlib,shutil,csv
from pathlib import Path
P=Path(__file__).parent;Q=P/'documents/qa';O=P/'engineering-v19-results';I=O/'quadratic-inward'
s=json.loads((P/'documents/document_status.json').read_text());reg=json.loads((Q/'v19_inward_body_regression.json').read_text());records=[]
for d in s['documents']:
 assert hashlib.sha256(Path(d['path']).read_bytes()).hexdigest()==d['sha256']
 row=next(r for r in reg['documents'] if r['document']==Path(d['path']).stem)
 records.append(dict(document=Path(d['path']).name,sha256=d['sha256'],visually_reviewed_pages=row['pages_requiring_review'],unchanged_reviewed_bodies=row['unchanged_reviewed_bodies']))
(Q/'v19_inward_visual_review.json').write_text(json.dumps(dict(date='2026-10-16',result='Approximate preview pass',documents=records,scope='New or changed page bodies inspected; unchanged bodies matched to the previously reviewed V19 pages. Native Word pagination remains unverified.'),indent=2))
hist=O/'document-build-history';hist.mkdir(exist_ok=True);old=O/'report_completion_status.json'
if not (hist/'before_inward_completion_status.json').exists():shutil.copy2(old,hist/'before_inward_completion_status.json')
r=json.loads(old.read_text());r['quadratic_inward_extension']=dict(status=json.loads((I/'status.json').read_text()),verification=json.loads((I/'verification.json').read_text()));r['current_review']='documents/qa/v19_inward_visual_review.json';old.write_text(json.dumps(r,indent=2))
status=r['quadratic_inward_extension']['status'];checks=[c for c in status['cases'] if c['change_percent'] is not None]
with (O/'workstream_status.csv').open(newline='') as f:rows=list(csv.DictReader(f))
rows=[row for row in rows if row['Workstream']!='Quadratic inward reference fixture']
rows.append(dict(Workstream='Quadratic inward reference fixture',Status=str(sum(c['gate'] is True for c in checks))+' of '+str(len(checks))+' recorded mesh comparisons pass',Scope='Four prescribed-preload ideal-pivot reference cases; current saved-array audit in quadratic-inward/verification.json. No physical or complete joint qualification.'))
with (O/'workstream_status.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=['Workstream','Status','Scope']);writer.writeheader();writer.writerows(rows)
provenance={name:hashlib.sha256((P/name).read_bytes()).hexdigest() for name in ['v19_contact_assembly.py','v19_quadratic_joint.py','v19_quadratic_inward.py','verify_v19_quadratic.py']};(I/'source_snapshot.json').write_text(json.dumps(dict(scope='Current source snapshot at inward-study closure. STEP and saved mesh hashes are recorded per case.',sha256=provenance),indent=2));print('Inward report review and closure saved.')
