from pathlib import Path
import json
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent;Q=P/'documents/qa';new=json.loads((Q/'native_v24_layout_checks.json').read_text());old=json.loads((Q/'native_v23_layout_checks.json').read_text());out=[]
for a,b in zip(new['documents'],old['documents']):
 same=[];different=[]
 for page in range(2,b['native_pages']+1):
  x=Image.open(Path(a['render_folder'])/f'page-{page}.png');y=Image.open(Path(b['render_folder'])/f'page-{page}.png')
  (same if x.size==y.size and ImageChops.difference(x,y).getbbox() is None else different).append(page)
 out.append(dict(document=a['document'],unchanged_pages=same,different_pages=different,scope='Exact full page pixel comparison against previously reviewed V23 native renders; title page intentionally updated and excluded.'))
(Q/'v24_preserved_page_pixels.json').write_text(json.dumps(out,indent=2));print(json.dumps([dict(document=r['document'],identical=len(r['unchanged_pages']),different=r['different_pages']) for r in out],indent=2));assert not any(r['different_pages'] for r in out)
s=(P/'v23_close_review.py').read_text(encoding='utf-8-sig').replace('V23','V24').replace('v23','v24').replace('[(95,70),(96,71),(97,72)]','[(98,73),(99,74),(100,75)]').replace('native_pages=[97,72]','native_pages=[100,75]').replace('all_page_contact_sheets_reviewed=True',"all_page_contact_sheets_reviewed=False,preserved_V23_pages_pixel_identical=167")
s=s.replace('Both title pages and all three shared new V24 chapters. New chapter bodies pixel compared between reports.','Both updated title pages and three new V24 chapter bodies reviewed; matching companion bodies pixel compared. The other 167 previously reviewed pages are exactly pixel identical to V23.')
s=s.replace('all contact sheets reviewed, new chapters and title pages reviewed in detail','167 preserved pages pixel matched to reviewed V23, new chapters and title pages reviewed in detail')
s=s.replace("sources=['v24_corrected_mesh_campaign.py','v24_review.py'","sources=['project_paths.py','audit_v14_motion.py','v24_finer_campaign.py','v24_review.py'")
(P/'v24_close_review.py').write_text(s,encoding='utf8',newline='\n')
