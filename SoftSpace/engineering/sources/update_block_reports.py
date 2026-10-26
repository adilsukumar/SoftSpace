"""Append identical V26 chapters while preserving existing report text and images."""
from pathlib import Path
import json,hashlib,shutil,datetime,zipfile,sys
from docx import Document
P=Path(__file__).resolve().parent;D=P/'documents';sys.path.insert(0,str(D))
import build_documents as b
from joint_block_section import add_joint_block_review
status=json.loads((D/'document_status.json').read_text(encoding='utf-8-sig'));newrows=[];regressions=[]
current='Current update on 26 October 2026: The lower memory V26B joint pilot failed its second linear accuracy check. No new strength result is accepted. Both projects remain concepts with open validation requirements. Read the final lower memory joint solver review and the preceding named material screen.'
for name in ['Ear_Defender_Project.docx','Glasses_Friendly_Headphone_Cushions.docx']:
 f=D/name;oldhash=hashlib.sha256(f.read_bytes()).hexdigest();record=next(r for r in status['documents'] if Path(r['path']).name==name);assert oldhash==record['sha256'],'User changes detected; do not overwrite'
 d=Document(f);assert not any(p.text.startswith('Lower memory joint solver review') for p in d.paragraphs),'Material screen already added'
 oldpars=[p.text for p in d.paragraphs if not p.text.startswith('Current update on')];oldtables=[[c.text for row in t.rows for c in row.cells] for t in d.tables]
 with zipfile.ZipFile(f) as z:oldmedia={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')}
 backup=D/'history'/(f.stem+'_before_block_solver_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.docx');shutil.copy2(f,backup)
 for p in d.paragraphs:
  if p.text.startswith('Current update on'):p.text=current
 add_joint_block_review(d,P,b.new_page,b.para,b.table,b.picture)
 for section in d.sections:
  for hp in section.header.paragraphs:
   for run in hp.runs:
    if '25 October 2026' in run.text:run.text=run.text.replace('25 October 2026','26 October 2026')
 d.save(f);new=Document(f);newpars=[p.text for p in new.paragraphs if not p.text.startswith('Current update on')];assert newpars[:len(oldpars)]==oldpars
 assert [[c.text for row in t.rows for c in row.cells] for t in new.tables][:len(oldtables)]==oldtables
 with zipfile.ZipFile(f) as z:assert oldmedia.issubset({hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')});assert z.testzip() is None
 newrows.append(dict(path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size));regressions.append(dict(document=name,before_sha256=oldhash,all_old_paragraphs_preserved_except_current_summary=True,all_old_tables_preserved=True,all_old_images_preserved=True,backup=str(backup)))
status.update(updated='26 October 2026',design_status='Lower memory joint solver review',documents=newrows,native_Word_layout_verified=False)
(D/'document_status.json').write_text(json.dumps(status,indent=2));(D/'qa/block_semantic_regression.json').write_text(json.dumps(regressions,indent=2))
