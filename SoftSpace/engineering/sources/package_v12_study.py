"""Preserve V11 evidence and add current V12 CAD, results and both reports."""
from pathlib import Path
import json,zipfile,hashlib,datetime,shutil
P=Path(__file__).parent;O=P/'engineering-v12-results';tests=json.loads((O/'test_register.json').read_text());step=json.loads((O/'STEP_verification.json').read_text());assert step['all_pass'];target=P/'EarDefender_V12_CAD_and_Recorded_Checks.zip';updates={}
for f in O.rglob('*'):
 if f.is_file() and f.suffix in ['.json','.csv','.npz','.md','.step'] and 'checkpoint' not in f.name and 'partial' not in f.name:updates['evidence/engineering-v12-results/'+f.relative_to(O).as_posix()]=f
for r in step['cases']:updates['CAD/V12-local-candidates/'+Path(r['file']).name]=Path(r['file'])
for f in (P/'documents').glob('*.docx'):updates['documents/'+f.name]=f
updates['documents/document_status.json']=P/'documents'/'document_status.json'
for f in P.glob('*v12*.py'):updates['sources/'+f.name]=f
for name in ['build_documents.py','v12_study_section.py']:updates['sources/documents/'+name]=P/'documents'/name
for name in ['V12_lock_candidate.png','V12_lock_section.png','V12_folded_CAD.png']:updates['images/'+name]=P/'documents'/'images'/name
readme='''# V12 CAD and recorded checks

V12 is a local STEP engineering candidate with wider guide channels, an offset fork crossbar and captive angular-lock pins. Native Fusion archives remain V10. This package preserves the previous V10 and V11 evidence and adds18 V12 poses in six sizes, both updated Word reports, source scripts and new calculation records.

This is NOT a manufacturing release. The integral latch housing, pin collar and head still need a specified assembly and servicing route, cap/head retention and final fasteners. Spring solids are reserved annular space, not actual coils. Complete assembly contact, friction, stops, fatigue, impacts and physical product validation remain open. See evidence/engineering-v12-results/REVIEW.md and test_register.json first.

Recorded work includes216 rigid motion samples,18 independently reimported STEP checks,18 known embedded/disjoint collision controls, six ideal wider-guide band fixtures with refinement, two ideal fork fixtures with four meshes,80 conditional fork material/load calculations,36 pin cases and162 spring cases. A geometric or numerical pass does not establish sound isolation, comfort, sensory acceptance or durability.

The first compressed spring-space exports failed volume conservation and are retained as historical failures. Final exports reconstruct exact cylinders. Coincident copied/imported fork comparisons failed; no fork-family equivalence pass is claimed. The independent motion audit uses located original OCP solids, validity checks and known embedded/disjoint controls. Earlier interrupted gmsh motion work is preliminary, not the final audit.

The Sony WH-CH720N replacement pad still needs the user-deferred mount measurements and real fit, retention, response, ANC, incoming-noise and outgoing-playback tests. No universal pad fit, zero leakage, pain relief, unbreakable design, lowest cost or superiority over market headphones is demonstrated.

Both Word documents have structural and approximate preview checks. Native Word pagination remains unverified because local native control and the bundled renderer are unavailable. Approximate previews are QA only, not final Word layout proof.

Python dependencies are not vendored here. Scientific scripts use the project scientific libraries; the independent CAD audit also used cadquery-ocp7.8.1.1.post1 with vtk9.3.1. See source imports and recorded evidence. The material families are a70-family register with specific limited reference screens, not a test of every formulation.
'''
manifest={'status':'V12 engineering candidate; assembly design and product validation incomplete','tests':tests['tests'],'files':[]}
if target.exists():
 history=P/'package-history';history.mkdir(exist_ok=True);shutil.copy2(target,history/(target.stem+'_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip'))
with zipfile.ZipFile(P/'EarDefender_V11_Materials_and_Folding_Study.zip') as old,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for entry in old.infolist():
  if entry.is_dir() or entry.filename in updates or entry.filename in ['manifest.json','README.md']:continue
  data=old.read(entry.filename);z.writestr(entry.filename,data);manifest['files'].append({'path':entry.filename,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 for arc,f in updates.items():
  data=f.read_bytes();z.writestr(arc,data);manifest['files'].append({'path':arc,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 z.writestr('README.md',readme);z.writestr('manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for r in manifest['files']:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
print(json.dumps({'file':str(target),'bytes':target.stat().st_size,'files':len(manifest['files']),'CRC_and_all_file_SHA256':'pass','manufacturing_release':False}))
