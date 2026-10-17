from pathlib import Path
import json
O=Path(__file__).parent/'engineering-v10-results'
scope='Quarter X/Y symmetry mirrors the front-only clamp bore; the real rear wall is different. Full-width mechanical comparison remains open.'
for name in ['solid_v10_summary.json','adjustment_force_screen.json']:
 f=O/name;j=json.loads(f.read_text());j['symmetry_scope']=scope
 if scope not in j['limits']:j['limits'].append(scope)
 f.write_text(json.dumps(j,indent=2))
print('Quarter-symmetry scope explicitly recorded; numerical values unchanged.')
