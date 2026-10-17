from pathlib import Path
import json,hashlib,zipfile,datetime,shutil
P=Path(__file__).parent;O=P/'engineering-v19-results';s=json.loads((O/'test_register.json').read_text());updates={};target=P/('EarDefender_V19_Inward_Extension_Handoff.zip' if 'quadratic_inward_model' in s else 'EarDefender_V19_Prototype_Handoff.zip');assert not target.exists(),'Preserve earlier V19 archive before replacement'
for f in O.rglob('*'):
 if f.is_file() and f.name not in ['package_verification.json','package.log'] and f.suffix.lower() in ['.json','.csv','.md','.npz','.log','.step','.pdf']:updates['evidence/engineering-v19-results/'+f.relative_to(O).as_posix()]=f
for f in P.glob('EarDefender_V19_*.step'):updates['CAD/'+('V19-initial-contact-source/' if 'ParallelDisc' in f.name else 'V19-assembly-prototype/')+f.name]=f
for f in P.glob('*v19*.py'):updates['sources/'+f.name]=f
for name in ['build_documents.py','v19_handoff_section.py','v19_quadratic_section.py','v19_inward_section.py','verify_documents.py','check_document_layout.py','record_preview_review.py']:updates['sources/documents/'+name]=P/'documents'/name
for f in (P/'documents/images').glob('V19*.png'):updates['images/'+f.name]=f
for f in (P/'documents').glob('*.docx'):updates['documents/'+f.name]=f
updates['documents/document_status.json']=P/'documents/document_status.json'
for name in ['checks.json','additional_tests_page_comparison.json','v19_visual_review.json','v19_body_regression.json','native_v19_attempt.json']:updates['documents/qa/'+name]=P/'documents/qa'/name
for f in (P/'documents/qa').glob('*_native_v19.log'):updates['documents/qa/'+f.name]=f
for f in (P/'documents/qa').glob('*v19_inward*.json'):updates['documents/qa/'+f.name]=f
manifest=dict(updated='2026-10-16',current_local_CAD_revision='V19 assembly prototype',native_Fusion_revision='V10',status='Prototype handoff with conditional models, failed solves, mesh limits and missing measured inputs',all_requested_computer_models_complete=False,product_complete=False,manufacturing_release=False,files=[])
with zipfile.ZipFile(P/'EarDefender_V18_Digital_Prototype_and_Recorded_Checks.zip') as old,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for item in old.infolist():
  if item.is_dir() or item.filename in updates or item.filename in ['README.md','manifest.json']:continue
  data=old.read(item.filename);z.writestr(item.filename,data);manifest['files'].append(dict(path=item.filename,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 for arc,f in updates.items():
  data=f.read_bytes();z.writestr(arc,data);manifest['files'].append(dict(path=arc,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 z.writestr('README.md',(O/'REVIEW.md').read_text());z.writestr('manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 assert len({f['path'] for f in manifest['files']})==len(manifest['files'])
 for r in manifest['files']:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
r=dict(file=str(target),bytes=target.stat().st_size,files=len(manifest['files']),CRC_and_all_SHA256='pass',zip_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),all_requested_models_complete=False,product_complete=False,manufacturing_release=False);(O/('package_inward_verification.json' if 'quadratic_inward_model' in s else 'package_verification.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r))
