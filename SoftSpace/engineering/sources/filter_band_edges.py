import json
from pathlib import Path
p=Path(__file__).parent/'engineering-v7-results'/'band_edges.json'
for r in json.loads(p.read_text()):
 x,y,z=r['point_mm']
 if x>70 and 105<z<140:print(r)
