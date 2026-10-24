from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;from project_paths import verified_source
O=P/'engineering-v24-results';controls=[]
for size in ['child_large','adult_small']:
 row=json.loads((P/'engineering-v19-results'/f'{size}_cad_report.json').read_text());f=verified_source(row);controls.append(dict(case='moved_current_'+size,passed=hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256']))
recovered=json.loads((O/'historical_source_recovery.json').read_text());unique={r['sha256']:r for r in recovered['exact_recoveries']}
for h,r in unique.items():
 row=dict(file='C:/Users/adils/Downloads/EarDefenderProject/'+r['file'],sha256=h);f=verified_source(row);controls.append(dict(case='exact_archived_'+r['file'],passed=f.relative_to(P).parts[0]=='source-archive' and hashlib.sha256(f.read_bytes()).hexdigest()==h))
row=json.loads((P/'engineering-v19-results/child_large_cad_report.json').read_text());row['sha256']='0'*64
try:verified_source(row);negative=False
except FileNotFoundError:negative=True
controls.append(dict(case='wrong_hash_rejected',passed=negative));assert len(controls)==7 and all(c['passed'] for c in controls)
(O/'path_loader_controls.json').write_text(json.dumps(dict(controls=controls,all_pass=True),indent=2));print('Seven verified path loader controls passed')
