from pathlib import Path
import json,zipfile,hashlib,shutil,datetime
P=Path(__file__).parent;O=P/'engineering-v11-results';fine=json.loads((O/'fine_fold_paths.json').read_text());verify=json.loads((O/'export_verification.json').read_text());assert verify['all_pass']
target=P/'EarDefender_V11_Materials_and_Folding_Study.zip';files={}
for folder in ['engineering-v10-results','engineering-v11-results']:
 for f in (P/folder).iterdir():
  if f.suffix in ['.json','.csv','.npz','.md'] and 'partial' not in f.name:files['evidence/'+folder+'/'+f.name]=f
native=json.loads((P/'engineering-v10-results'/'cad_native_report.json').read_text());local=json.loads((P/'engineering-v10-results'/'cad_local_report.json').read_text())
for stem,record in [('V10-native',native),('V10-local',local)]:
 for name in record['files']:files['CAD/'+stem+'/'+Path(name).name]=Path(name)
for row in fine['exports']:files['CAD/V11-folding-candidates/'+Path(row['file']).name]=Path(row['file'])
for f in (P/'documents').glob('*.docx'):files['documents/'+f.name]=f
files['documents/document_status.json']=P/'documents'/'document_status.json'
for name in ['materials_v11.py','screen_folding_v10.py','summarize_v11.py','refine_v11_fold_paths.py','verify_v11_exports.py','render_v11_folding.py','package_v11_study.py','record_v11_status.py']:
 files['sources/'+name]=P/name
for name in ['build_documents.py','additional_v10_tests.py','v11_study_section.py']:files['sources/documents/'+name]=P/'documents'/name
files['images/V11_folding_study.png']=P/'documents'/'images'/'V11_folding_study.png'
readme='''# V11 material and folding study

Current native Fusion assemblies remain V10. V11 is an exploratory study using transformed V10 solids, manufacturer material data and linear analytical scaling. It is not a new production-ready native hinge design.

The candidate register lists 70 families, but only ten specific structural references have quantitative grade screens. There are 60 grade/size combinations, 240 linear imposed-load calculations and 14 foam datapoint calculations. These are not physical material tests. Unscreened families, full foam curves, printed anisotropy, creep, fatigue, impacts, acoustic sealing and wearer preference remain open.

Folding failures are retained. The six selected candidate paths use staggered sliders: left extension0 and right extension30 before folding. They use existing fork axes and different angle limits for different sizes. Five-degree rigid path samples and independent STEP reimports are recorded. This is not a continuous sweep, a designed latch, a load rating or a fatigue/drop pass. Adjustment while folded is not validated. Bounding-box volume is only a packing proxy.

All earlier V10 limits remain, including the insufficient guide/tongue tolerance budget for assumed0.2mm per-part error. The selected Sony WH-CH720N still needs measurements and compatible physical pad samples. No finished comfort, sound-reduction, zero-leakage, lowest-price or market-superiority claim is established.

Both updated Word reports are included. Native Word pagination is unverified; approximate preview checks are recorded separately. remaining_test_methods.md lists physical and material prerequisites. Failures have not been converted to passes.
'''
manifest={'status':'Exploratory V11 materials and folding study; product validation incomplete','folding_samples':fine['case_count'],'all_sampled_fold_paths_pass':fine['all_pass'],'independent_STEP_reimports_pass':verify['all_pass'],'files':[]}
if target.exists():
 history=P/'package-history';history.mkdir(exist_ok=True);shutil.copy2(target,history/(target.stem+'_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip'))
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for arc,f in files.items():
  data=f.read_bytes();z.writestr(arc,data);manifest['files'].append({'path':arc,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
 z.writestr('README.md',readme);z.writestr('manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for row in manifest['files']:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
print(json.dumps({'path':str(target),'bytes':target.stat().st_size,'CRC_and_SHA256':'pass','status':manifest['status']}))
