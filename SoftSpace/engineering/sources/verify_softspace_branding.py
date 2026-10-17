from pathlib import Path
import hashlib,json
from PIL import Image
P=Path(__file__).parent;Q=P/'documents/qa';baseline=json.loads((Q/'before_softspace_branding.json').read_text());rows=[]
for name,old in baseline['body_hashes'].items():
 same=[];review=[]
 for f in sorted((Q/name).glob('page-*.png'),key=lambda f:int(f.stem[5:])):
  im=Image.open(f).convert('RGB');h=hashlib.sha256(im.crop((0,70,im.width,im.height-65)).tobytes()).hexdigest()
  (same if h in old.values() else review).append(f.name)
 rows.append(dict(document=name,unchanged_reviewed_bodies=len(same),pages_requiring_review=review))
r=dict(scope='Exact approximate-preview body hashes, excluding top 70 pixel header and bottom 65 pixel footer bands. Compare with the reviewed pre-branding V19 inward-extension reports. Changed headers must be inspected separately.',documents=rows);(Q/'softspace_branding_regression.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
