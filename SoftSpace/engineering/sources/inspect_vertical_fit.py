import json
from pathlib import Path
p=Path(__file__).parent/'engineering-v7-results';j=json.loads((p/'vertical_fit_summary.json').read_text())
for size in sorted(set(r['size'] for r in j['rows'])):
 print(size,[(s['extension_mm'],round(s['band_inner_crown_height_mm'],1)) for s in j['shapes'] if s['size']==size])
print('Counts',{c:sum(r['classification']==c for r in j['rows']) for c in sorted(set(r['classification'] for r in j['rows']))})
