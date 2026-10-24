from pathlib import Path
import json,hashlib
from PIL import Image,ImageChops
P=Path(r'${WORKSPACE}');D=P/'documents';Q=D/'qa';O=P/'engineering-v25-results'
old=json.loads((Q/'native_v24_layout_checks.json').read_text());new=json.loads((Q/'native_v25_layout_checks.json').read_text());status=json.loads((D/'document_status.json').read_text());preserved=[]
for before,after in zip(old['documents'],new['documents']):
 assert not after['blank_body_pages'] and not after['short_text_pages'] and after['out_of_page_text_rectangles']==0
 for page in range(2,before['native_pages']+1):
  a=Image.open(Path(before['render_folder'])/f'page-{page}.png');b=Image.open(Path(after['render_folder'])/f'page-{page}.png');assert ImageChops.difference(a,b).getbbox() is None
 preserved.append(dict(document=after['document'],pages=before['native_pages']-1,pixel_identical_to_reviewed_V24=True))
folders=[Path(r['render_folder']) for r in new['documents']];matches=[]
for main,flex in [(101,76),(102,77),(103,78)]:
 a=Image.open(folders[0]/f'page-{main}.png');b=Image.open(folders[1]/f'page-{flex}.png');w,h=a.size;box=(0,round(h*.06),w,round(h*.88));assert ImageChops.difference(a.crop(box),b.crop(box)).getbbox() is None
 matches.append(dict(main_page=main,flex_page=flex,body_pixels_identical=True))
review=dict(date='2026-10-24',source_hashes=[r['sha256'] for r in status['documents']],native_pages=[103,78],all_page_contact_sheets_reviewed=False,preserved_V24_pages_pixel_identical=173,detailed_pages_reviewed='Both updated title pages and all three new V25 chapter bodies viewed; companion chapter bodies pixel matched. All 173 remaining pages are pixel identical to previously reviewed V24.',preserved=preserved,new_body_comparisons=matches,scope='Visual and semantic preservation checks, not independent scientific validation.')
(Q/'v25_visual_review.json').write_text(json.dumps(review,indent=2));status['quality_check'].update(native_Word_layout_verified=True,visual_review_scope=review['detailed_pages_reviewed'],reason='Native Word hashes match; all 181 pages rendered with no blank short or out of page text. Title pages and new chapters visually checked; preserved pages pixel identical.');status['native_Word_layout_verified']=True;(D/'document_status.json').write_text(json.dumps(status,indent=2))
sources=['v25_quadratic_contact.py','v25_contact_campaign.py','v25_quadrature_campaign.py','v25_review.py','v22_objective_spacer_solve.py','v19_quadratic_joint.py','v19_contact_assembly.py','v12_geometry.py','project_paths.py']
(O/'reproduction_sources.json').write_text(json.dumps({s:hashlib.sha256((P/s).read_bytes()).hexdigest() for s in sources},indent=2))
manifest=[dict(path=f.relative_to(O).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in O.rglob('*') if f.is_file() and f.name!='evidence_manifest.json'];(O/'evidence_manifest.json').write_text(json.dumps(manifest,indent=2))
print('V25 all page checks passed, 173 preserved pages identical and three new companion bodies identical')
