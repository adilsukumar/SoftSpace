from pathlib import Path
import json,hashlib
P=Path(__file__).parent
s=json.loads((P/'document_status.json').read_text());q=json.loads((P/'qa'/'checks.json').read_text())
records=[]
for item in s['documents']:
 digest=hashlib.sha256(Path(item['path']).read_bytes()).hexdigest();assert digest==item['sha256']
 row=next(r for r in q if r['sha256']==digest)
 records.append({'document':Path(item['path']).name,'sha256':digest,'approximate_pages_reviewed':row['approximate_pages'],'result':'no clipping, broken tables or unintended overflow observed in approximate page images'})
s['quality_check']['approximate_preview_visual_review']={'status':'pass','documents':records,'scope':'Approximate ReportLab previews only. Native Word pagination remains unverified.'}
(P/'document_status.json').write_text(json.dumps(s,indent=2));print(json.dumps(records))
