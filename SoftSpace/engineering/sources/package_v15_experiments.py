from pathlib import Path
import json,zipfile,hashlib,datetime,shutil
P=Path(__file__).parent;O=P/'engineering-v15-results';tests=json.loads((O/'test_register.json').read_text());updates={}
for f in O.rglob('*'):
 if f.is_file() and f.suffix in ['.json','.csv','.npz','.md','.log']:updates['evidence/engineering-v15-results/'+f.relative_to(O).as_posix()]=f
for f in P.glob('EarDefender_V15_*.step'):updates['CAD/V15-adult-small-retention-pilot/'+f.name]=f
fold=P/'EarDefender_V14_child_large_V15FoldExperiment.step';updates['CAD/V14-child-large-new-V15-pose/'+fold.name]=fold
for f in (P/'documents').glob('*.docx'):updates['documents/'+f.name]=f
updates['documents/document_status.json']=P/'documents/document_status.json'
for f in P.glob('*v15*.py'):updates['sources/'+f.name]=f
for name in ['build_documents.py','v15_study_section.py']:updates['sources/documents/'+name]=P/'documents'/name
for f in (P/'documents/images').glob('V15*.png'):updates['images/'+f.name]=f
target=P/'EarDefender_V15_Experiments_and_Recorded_Checks.zip'
if target.exists():
 hist=P/'package-history';hist.mkdir(exist_ok=True);shutil.copy2(target,hist/(target.stem+'_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip'))
manifest={'status':'V15 one-size retention experiment; V14 latest six-size candidate; no manufacturing release','updated':'2026-10-15','tests':tests['tests'],'files':[]}
readme='''# V15 retention and packing experiments

Read evidence/engineering-v15-results/REVIEW.md and test_register.json first. V15 is ONE adult-small local STEP retention pilot. V14 remains the latest six-size CAD candidate. Native Fusion archives remain V10. This package preserves prior V14 and rejected V13 evidence and adds V15 records; old revision results do not qualify new geometry.

The pilot adds intended M2x0.4 threads, a metal knob and separate jam nut. All46 solids passed the saved validity checks and six discrete release/slider endpoint clearance checks passed. Threads are smooth cosmetic envelopes, not real helices or solved flank engagement. Final grades, thread runout, gauges, tools, torque, pullout, loosening, complete joint contact, pinch and child small-part access remain unqualified. There is no V15 six-size or folding-path pass.

Three child packing searches use unchanged V14 parts. Bounding-box ranking is not an actual collision test. Only the saved finite shortlist endpoints were checked; the search stops at its first clear endpoint and rejects it if worse than the previous recorded V14 fold. Separately, the improved child-large endpoint passed27 discrete adjustment, release and folding sequence samples and its export matched the intended box. It is3.93percent smaller than the retracted unfolded baseline. This is neither a global optimum nor continuous loaded motion. Pins stay held6mm released; a stable folded storage latch is not established. Child small and medium have no useful recorded packing improvement.

The72 retention load scenarios are assumed solid-root rod equations. They are not thread FE, a torque approval or a material winner. Physical comfort, sensory acceptance, acoustics, outgoing music leakage, heat, cleaning, drops, folding life, ageing, manufacturing yield and final cost remain untested. Sony WH-CH720N mount measurements were deferred; its generic pad is unchanged and not proved compatible.

Both paired Word reports were updated together. Approximate preview checks do not verify native Word pagination. Storage CRC and SHA256 verification do not prove engineering validity. This is NOT a manufacturing release or validated finished product.
'''
with zipfile.ZipFile(P/'EarDefender_V14_CAD_and_Recorded_Checks.zip') as prior,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for item in prior.infolist():
  if item.is_dir() or item.filename in updates or item.filename in ['README.md','manifest.json']:continue
  data=prior.read(item.filename);z.writestr(item.filename,data);manifest['files'].append({'path':item.filename,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 for arc,f in updates.items():
  data=f.read_bytes();z.writestr(arc,data);manifest['files'].append({'path':arc,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 z.writestr('README.md',readme);z.writestr('manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for r in manifest['files']:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
print(json.dumps({'file':str(target),'bytes':target.stat().st_size,'files':len(manifest['files']),'CRC_and_all_SHA256':'pass','manufacturing_release':False}))
