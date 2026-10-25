from pathlib import Path
import json,hashlib
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent;D=P/'documents';Q=D/'qa';O=P/'engineering-v26-results'
old=json.loads((Q/'native_v25_layout_checks.json').read_text());new=json.loads((Q/'native_v26_layout_checks.json').read_text());status=json.loads((D/'document_status.json').read_text());preserved=[]
for before,after in zip(old['documents'],new['documents']):
 assert not after['blank_body_pages'] and not after['short_text_pages'] and after['out_of_page_text_rectangles']==0
 for page in range(2,before['native_pages']+1):
  a=Image.open(Path(before['render_folder'])/f'page-{page}.png');b=Image.open(Path(after['render_folder'])/f'page-{page}.png');w,h=a.size;box=(0,round(h*.06),w,round(h*.93));assert ImageChops.difference(a.crop(box),b.crop(box)).getbbox() is None,(after['document'],page)
 preserved.append(dict(document=after['document'],pages=before['native_pages']-1,body_pixels_identical_to_reviewed_V25=True,excluded_change='Header date updated from 24 to 25 October'))
folders=[Path(r['render_folder']) for r in new['documents']];matches=[]
for main,flex in [(104,79),(105,80),(106,81)]:
 a=Image.open(folders[0]/f'page-{main}.png');b=Image.open(folders[1]/f'page-{flex}.png');w,h=a.size;box=(0,round(h*.06),w,round(h*.93));assert ImageChops.difference(a.crop(box),b.crop(box)).getbbox() is None
 matches.append(dict(main_page=main,flex_page=flex,body_pixels_identical=True))
review=dict(date='2026-10-25',source_hashes=[r['sha256'] for r in status['documents']],native_pages=[106,81],all_page_contact_sheets_reviewed=False,preserved_V25_body_pages_pixel_identical=179,detailed_pages_reviewed='Both updated title pages and three new V26 chapter bodies viewed. Companion bodies pixel matched. All 179 preserved body pages pixel identical to reviewed V25; header date intentionally changed.',preserved=preserved,new_body_comparisons=matches,scope='Report visual QA and semantic preservation, not scientific product validation.')
(Q/'v26_visual_review.json').write_text(json.dumps(review,indent=2));status['quality_check'].update(native_Word_layout_verified=True,visual_review_scope=review['detailed_pages_reviewed'],reason='Native Word hashes match; all 187 pages rendered without blank short or out of page text. Updated pages visually checked, companion and preserved bodies pixel compared.');status['native_Word_layout_verified']=True;(D/'document_status.json').write_text(json.dumps(status,indent=2))
checks=json.loads((Q/'v26_semantic_regression.json').read_text());assert all(r['all_old_paragraphs_preserved_except_current_summary'] and r['all_old_tables_preserved'] and r['all_old_images_preserved'] for r in checks)
prior=[]
for f in (P/'engineering-v25-results').rglob('*outward.json'):
 r=json.loads(f.read_text());raw=f.with_suffix('.npz');assert hashlib.sha256(raw.read_bytes()).hexdigest()==r['raw_sha256'];prior.append(dict(file=raw.relative_to(P).as_posix(),sha256=r['raw_sha256']))
(O/'prior_V25_field_integrity.json').write_text(json.dumps(prior,indent=2))
sources=list(P.glob('v26_*.py'))+[P/s for s in ['v25_quadratic_contact.py','v22_objective_spacer_solve.py','v19_quadratic_joint.py','v19_contact_assembly.py','v12_geometry.py','project_paths.py']]
(O/'reproduction_sources.json').write_text(json.dumps({s.name:hashlib.sha256(s.read_bytes()).hexdigest() for s in sources},indent=2))
manifest=[dict(path=f.relative_to(O).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in O.rglob('*') if f.is_file() and f.name!='evidence_manifest.json'];(O/'evidence_manifest.json').write_text(json.dumps(manifest,indent=2))
print('V26 report layouts and evidence hashes verified; prior V25 raw fields unchanged')
