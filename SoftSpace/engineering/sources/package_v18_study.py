from pathlib import Path
import json,hashlib,zipfile,datetime,shutil
P=Path(__file__).parent;O=P/'engineering-v18-results';s=json.loads((O/'test_register.json').read_text());updates={}
for f in O.rglob('*'):
 if f.is_file() and f.name not in ['package_verification.json','package.log'] and f.suffix.lower() in ['.json','.csv','.md','.npz','.log','.step']:updates['evidence/engineering-v18-results/'+f.relative_to(O).as_posix()]=f
for f in P.glob('EarDefender_V18_*.step'):updates['CAD/V18-friction-stop/'+f.name]=f
for f in P.glob('*v18*.py'):updates['sources/'+f.name]=f
for name in ['build_documents.py','v18_study_section.py','v18_completion_section.py','v18_final_screen_section.py','verify_documents.py','check_document_layout.py','record_preview_review.py']:updates['sources/documents/'+name]=P/'documents'/name
for f in (P/'documents/images').glob('V18*.png'):updates['images/'+f.name]=f
for f in (P/'documents').glob('*.docx'):updates['documents/'+f.name]=f
updates['documents/document_status.json']=P/'documents/document_status.json'
for name in ['checks.json','additional_tests_page_comparison.json']:updates['documents/qa/'+name]=P/'documents/qa'/name
target=P/'EarDefender_V18_Digital_Prototype_and_Recorded_Checks.zip'
if target.exists():
 h=P/'package-history';h.mkdir(exist_ok=True);shutil.copy2(target,h/(target.stem+'_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip'))
manifest=dict(updated='2026-10-16',current_local_CAD_revision='V18',native_Fusion_revision='V10',status='Digital prototype candidate with conditional numerical checks and unperformed physical validation',product_complete=False,manufacturing_release=False,files=[])
with zipfile.ZipFile(P/'EarDefender_V17_Loaded_Pin_Assessment.zip') as old,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for item in old.infolist():
  if item.is_dir() or item.filename in updates or item.filename in ['README.md','manifest.json']:continue
  data=old.read(item.filename);z.writestr(item.filename,data);manifest['files'].append(dict(path=item.filename,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 for arc,f in updates.items():
  data=f.read_bytes();z.writestr(arc,data);manifest['files'].append(dict(path=arc,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 z.writestr('README.md',(O/'REVIEW.md').read_text());z.writestr('manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for r in manifest['files']:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
r=dict(file=str(target),bytes=target.stat().st_size,files=len(manifest['files']),CRC_and_all_SHA256='pass',product_complete=False,manufacturing_release=False);(O/'package_verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
