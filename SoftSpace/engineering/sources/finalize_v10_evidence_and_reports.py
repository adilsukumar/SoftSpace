"""Run after the current refinement job, then visually review before packaging."""
from pathlib import Path
import sys,json,subprocess
P=Path(__file__).parent;O=P/'engineering-v10-results'
s=json.loads((O/'full_width_sizes_summary.json').read_text())
assert s['status']=='complete' and len(s['cases'])==6
assert s.get('stress_refinement_status')=='complete','Finish recording all stress refinements first'
jobs=[('runtime version record',['record_v10_environment.py']),
      ('actual-width reduced force screen',['v10_adjustment_force_screen.py','full']),
      ('conditional material screen',['v10_conditional_strength_screen.py']),
      ('accepted solution audit',['audit_v10_numerics.py']),
      ('source-bound numerical figures',['render_v10_numerical_summary.py']),
      ('both living Word reports',['documents/build_documents.py']),
      ('approximate preview rendering',['documents/check_document_layout.py']),
      ('report structure and source hashes',['documents/verify_documents.py'])]
with (O/'finalization_log.txt').open('w',encoding='utf-8') as log:
 for label,args in jobs:
  print('START '+label,flush=True);log.write('START '+label+'\n');log.flush()
  child=subprocess.Popen([sys.executable,*args],cwd=P,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
  for line in child.stdout:
   print(line,end='',flush=True);log.write(line);log.flush()
  code=child.wait();log.write('EXIT '+str(code)+'\n');log.flush()
  if code:raise RuntimeError(label+' failed with exit '+str(code))
print('Evidence and reports updated. Visual inspection and package integrity checks remain.',flush=True)
