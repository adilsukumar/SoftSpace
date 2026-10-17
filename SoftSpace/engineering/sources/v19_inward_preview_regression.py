import json,hashlib,sys
from pathlib import Path
from PIL import Image
P=Path(__file__).parent;Q=P/'documents/qa';baseline=Q/'before_v19_inward_bodies.json'
def hashes():
 rows={}
 for name in ['Ear_Defender_Project','Glasses_Friendly_Headphone_Cushions']:
  rows[name]={}
  for f in (Q/name).glob('page-*.png'):
   im=Image.open(f).convert('RGB');rows[name][f.name]=hashlib.sha256(im.crop((0,0,im.width,im.height-65)).tobytes()).hexdigest()
 return rows
if sys.argv[1]=='before':
 assert not baseline.exists();baseline.write_text(json.dumps(hashes(),indent=2));print('Reviewed pre-inward page body hashes saved.')
else:
 before=json.loads(baseline.read_text());after=hashes();rows=[]
 for name in after:
  unchanged=[p for p,h in after[name].items() if h in before[name].values()];review=[p for p in after[name] if p not in unchanged]
  rows.append(dict(document=name,unchanged_reviewed_bodies=len(unchanged),pages_requiring_review=sorted(review,key=lambda s:int(s[5:-4]))))
 result=dict(scope='Exact RGB body hashes excluding bottom footer band, compared against the visually reviewed V19 reports before the inward extension. Approximate ReportLab previews only.',documents=rows);(Q/'v19_inward_body_regression.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
