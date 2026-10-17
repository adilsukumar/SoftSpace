import json
from pathlib import Path
p=Path(__file__).parent;j=json.loads((p/'engineering-v7-results'/'verification_P2_h6.0.json').read_text())
rows=sorted(j['rows'],key=lambda r:r['relative_complex_error'],reverse=True)
print('Maximum exact-solution difference',rows[0]['relative_complex_error'],'at',rows[0]['frequency_Hz'],'Hz; lowfrequency',max(r['relative_complex_error'] for r in rows if r['frequency_Hz']<=1000))
for family in ['child','adult']:
 a=json.loads((p/'engineering-v6-results'/(family+'_acoustic3d_h6.json')).read_text())['rows'];b=json.loads((p/'engineering-v6-results'/(family+'_acoustic3d_h4.json')).read_text())['rows']
 differences=sorted([(abs(u['model_pressure_transfer_db']-v['model_pressure_transfer_db']),u) for u,v in zip(a,b)],key=lambda v:v[0],reverse=True)
 print(family,'worst P1 mesh',differences[0])
