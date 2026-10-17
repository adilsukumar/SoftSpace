import hashlib,json
from pathlib import Path
from PIL import Image
P=Path(__file__).parent;D=P/'documents/qa';records=[]
def bodyhash(f):
 im=Image.open(f).convert('RGB');return hashlib.sha256(im.crop((0,0,im.width,im.height-65)).tobytes()).hexdigest()
for folder in ['Ear_Defender_Project','Glasses_Friendly_Headphone_Cushions']:
 old={bodyhash(f):str(f) for f in (D/'v18-baseline/qa'/folder).glob('page-*.png')};same=[];new=[]
 for f in sorted((D/folder).glob('page-*.png'),key=lambda f:int(f.stem.split('-')[-1])):
  h=bodyhash(f)
  if h in old:same.append(dict(current=str(f),reviewed_V18_body=old[h],body_sha256=h))
  else:new.append(str(f))
 records.append(dict(document=folder,previously_reviewed_bodies_unchanged=same,pages_requiring_visual_review=new))
(D/'v19_body_regression.json').write_text(json.dumps(dict(documents=records,scope='Exact RGB body hash comparison to the byte-verified previously reviewed V18 reports. Only the bottom 65 pixel footer band is excluded; it lies below the ReportLab body frame. Page numbers and final counts must be checked separately. Approximate previews only.'),indent=2));print(json.dumps([dict(document=r['document'],matched=len(r['previously_reviewed_bodies_unchanged']),review_pages=[Path(f).name for f in r['pages_requiring_visual_review']]) for r in records],indent=2))
