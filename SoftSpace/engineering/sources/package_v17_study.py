from pathlib import Path
import json,zipfile,hashlib,datetime,shutil
P=Path(__file__).parent;O=P/'engineering-v17-results';tests=json.loads((O/'test_register.json').read_text());updates={}
for f in O.rglob('*'):
 if f.is_file() and f.suffix in ['.json','.csv','.npz','.md','.log']:updates['evidence/engineering-v17-results/'+f.relative_to(O).as_posix()]=f
for f in P.glob('EarDefender_V17_*.step'):updates['CAD/V17-two-size-entry-pilots/'+f.name]=f
for f in (P/'documents').glob('*.docx'):updates['documents/'+f.name]=f
updates['documents/document_status.json']=P/'documents/document_status.json'
for f in P.glob('*v17*.py'):updates['sources/'+f.name]=f
for name in ['audit_v16_indexed_rivet.py','v16_tongue_fixture.py']:updates['sources/'+name]=P/name
for name in ['build_documents.py','v17_study_section.py']:updates['sources/documents/'+name]=P/'documents'/name
for f in (P/'documents/images').glob('V17*.png'):updates['images/'+f.name]=f
for name in ['checks.json','additional_tests_page_comparison.json']:updates['documents/qa/'+name]=P/'documents/qa'/name
target=P/('EarDefender_V17_Loaded_Pin_Assessment.zip' if (O/'digital_closeout.json').exists() else 'EarDefender_V17_Entry_Pilots_and_Recorded_Checks.zip')
if target.exists():
 hist=P/'package-history';hist.mkdir(exist_ok=True);shutil.copy2(target,hist/(target.stem+'_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip'))
manifest={'status':'V17 two entry pilots and loaded-pin assessment; V16 latest six-size candidate; native Fusion V10; production hold and no manufacturing release','updated':'2026-10-15','tests':tests['tests'],'product_complete':False,'files':[]}
with zipfile.ZipFile(P/'EarDefender_V16_Indexed_CAD_and_Recorded_Checks.zip') as prior,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for item in prior.infolist():
  if item.is_dir() or item.filename in updates or item.filename in ['README.md','manifest.json']:continue
  data=prior.read(item.filename);z.writestr(item.filename,data);manifest['files'].append({'path':item.filename,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 for arc,f in updates.items():
  data=f.read_bytes();z.writestr(arc,data);manifest['files'].append({'path':arc,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 z.writestr('README.md',(O/'REVIEW.md').read_text());z.writestr('manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for r in manifest['files']:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
result={'file':str(target),'bytes':target.stat().st_size,'files':len(manifest['files']),'CRC_and_all_SHA256':'pass','manufacturing_release':False};(O/'package_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
