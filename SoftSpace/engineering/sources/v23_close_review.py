"""Close V23 evidence and native report checks without changing report content."""
from pathlib import Path
import json,hashlib,sys
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent;D=P/'documents';O=P/'engineering-v23-results';Q=D/'qa'
status=json.loads((D/'document_status.json').read_text());layout=json.loads((Q/'native_v23_layout_checks.json').read_text());native=json.loads((Q/'native_word_status.json').read_text(encoding='utf-8-sig'))
assert len(layout['documents'])==2
for row in layout['documents']:
 assert not row['blank_body_pages'] and not row['short_text_pages'] and row['out_of_page_text_rectangles']==0
 assert hashlib.sha256((D/(row['document']+'.docx')).read_bytes()).hexdigest()==row['source_sha256']
folders=[Path(r['render_folder']) for r in layout['documents']];matches=[]
for main,flex in [(95,70),(96,71),(97,72)]:
 a=Image.open(folders[0]/f'page-{main}.png');b=Image.open(folders[1]/f'page-{flex}.png');w,h=a.size;box=(0,round(h*.06),w,round(h*.88));equal=ImageChops.difference(a.crop(box),b.crop(box)).getbbox() is None;assert equal;matches.append(dict(main_page=main,flex_page=flex,body_pixels_identical=True))
review=dict(date='2026-10-24',source_hashes=[r['sha256'] for r in status['documents']],native_pages=[97,72],all_page_contact_sheets_reviewed=True,detailed_pages_reviewed='Both title pages and all three shared new V23 chapters. New chapter bodies pixel compared between reports.',new_body_comparisons=matches,scope='Visual layout and semantic preservation review, not independent scientific validation.')
(Q/'v23_visual_review.json').write_text(json.dumps(review,indent=2));status['quality_check'].update(native_Word_layout_verified=True,visual_review_scope=review['detailed_pages_reviewed'],reason='Native Word exports match current report hashes; all pages rendered, page bounds and blank/short page checks passed, all contact sheets reviewed, new chapters and title pages reviewed in detail.')
status['native_Word_layout_verified']=True;(D/'document_status.json').write_text(json.dumps(status,indent=2))
checks=json.loads((Q/'v23_semantic_regression.json').read_text());assert all(r['all_old_paragraphs_preserved_except_current_summary'] and r['all_old_tables_preserved'] and r['all_old_images_preserved'] for r in checks)
sources=['v23_corrected_mesh_campaign.py','v23_review.py','v22_objective_spacer_solve.py','v19_quadratic_joint.py','v19_contact_assembly.py','v12_geometry.py']
(O/'reproduction_sources.json').write_text(json.dumps({s:hashlib.sha256((P/s).read_bytes()).hexdigest() for s in sources},indent=2))
manifest=[dict(path=f.relative_to(O).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in O.rglob('*') if f.is_file() and f.name!='evidence_manifest.json'];(O/'evidence_manifest.json').write_text(json.dumps(manifest,indent=2))
print('V23 evidence hashes and both native Word layouts verified')
