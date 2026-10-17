"""Review package preserving old evidence and explicitly rejected V13 work."""
from pathlib import Path
import json,zipfile,hashlib,datetime,shutil
P=Path(__file__).parent;O=P/'engineering-v14-results';tests=json.loads((O/'test_register.json').read_text());verify=json.loads((O/'STEP_verification.json').read_text());assert verify['all_pass'] and verify['case_count']==18
updates={}
for version in [12,13,14]:
 folder=P/('engineering-v'+str(version)+'-results')
 for f in folder.rglob('*'):
  if f.is_file() and f.suffix in ['.json','.csv','.npz','.md','.step','.log']:updates['evidence/'+folder.name+'/'+f.relative_to(folder).as_posix()]=f
 for f in P.glob('EarDefender_V'+str(version)+'_*.step'):
  if version==14:assert any(Path(r['file'])==f for r in verify['cases'])
  category='V13-rejected-assembly' if version==13 else ('V14-local-candidates' if version==14 else 'V12-superseded-candidates')
  updates['CAD/'+category+'/'+f.name]=f
for f in (P/'documents').glob('*.docx'):updates['documents/'+f.name]=f
updates['documents/document_status.json']=P/'documents/document_status.json'
for f in P.glob('*.py'):
 if any(v in f.name for v in ['v12','v13','v14']):updates['sources/'+f.name]=f
for name in ['build_documents.py','v12_study_section.py','v14_study_section.py']:updates['sources/documents/'+name]=P/'documents'/name
for f in (P/'documents/images').glob('V1[234]*.png'):updates['images/'+f.name]=f
target=P/'EarDefender_V14_CAD_and_Recorded_Checks.zip'
if target.exists():
 hist=P/'package-history';hist.mkdir(exist_ok=True);shutil.copy2(target,hist/(target.stem+'_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip'))
readme='''# V14 engineering candidate and recorded checks

Read evidence/engineering-v14-results/REVIEW.md, test_register.json and release_review.json first. This is NOT a manufacturing release or a finished validated product. Native Fusion archives remain V10. Later revisions are local STEP candidates.

V14 records six sizes and18 STEP poses with44 positive-volume solids each,264 nominal solid validity checks,216 discrete slider/release/folding samples,66 assembly-path samples and18 known collision-query controls. It includes only its explicitly recorded ideal adult-small fork fixture. V12 band fixtures and fork results stay labelled V12. No coincident Boolean component-equivalence or complete assembly FE qualification is claimed.

V13 is retained as a rejected assembly route. Forty eight of60 radial assembly samples failed. Its motion work stopped incomplete and its one-mesh fork calculation is not a refinement pass. V14 uses a rear axial cap and separate pull knob; the actual retained knob connection, threads, torque, fastener grade, joint contact, stops and pinch access remain design and validation tasks. Spring solids are space envelopes, not real coils. Assembly samples assume a held15mm allocation and do not prove real spring handling or tooling.

Child portability is unresolved: two V14 child sizes become slightly larger when folded. Adult box volume reduces by about12to23percent, without a physical bag-fit or drop test. The70material-family register is not every formulation tested. There is no final material winner, supplier quote, proven low price or matched competitor performance result.

Comfort, sensory acceptance, incoming sound attenuation, outgoing playback leakage, heat, cleaning, ageing, folding cycles and drop survival are untested physically. Sony WH-CH720N original mount measurements were deferred by the user; the generic replacement pad is unchanged and not proved compatible. No universal preference, zero-leakage, pain-relief, unbreakable, absent-Indian-competition or market-superiority claim is established.

Both living Word reports are updated together and have structural and approximate preview checks. Native Word pagination remains unverified because the local renderer lacks LibreOffice and native document control is unavailable. Preview images are internal QA only.

Earlier allocation failures are retained. Only completed final records support the numerical claims. Dependencies are not vendored: scientific scripts use the recorded NumPy/SciPy/Gmsh environment and CAD checks used cadquery-ocp7.8.1.1.post1 with vtk9.3.1. Archive integrity and individual fileSHA256 checks verify storage, not engineering validity.
'''
manifest={'status':'V14 candidate; manufacturing release and product validation incomplete','updated':'2026-10-15','tests':tests['tests'],'files':[]}
with zipfile.ZipFile(P/'EarDefender_V11_Materials_and_Folding_Study.zip') as prior,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
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
