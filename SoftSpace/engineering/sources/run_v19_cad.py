import sys,subprocess,os,json
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v19-results';O.mkdir(exist_ok=True);done=[]
# V18 motion logic is generic in the unchanged pivot and moving-part names.
s=(P/'audit_v18_motion.py').read_text().replace("engineering-v18-results","engineering-v19-results").replace('V18 friction stop candidate','V19 parallel disc candidate');(P/'audit_v19_motion.py').write_text(s)
for size in ['child_large','adult_small','child_small','child_medium','adult_medium','adult_large']:
 for script in ['build_v19_candidate.py','audit_v19_motion.py']:
  with (O/(size+'_'+script+'.log')).open('w') as f:r=subprocess.run([sys.executable,script,size],cwd=P,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
  done.append(dict(size=size,script=script,exit_code=r.returncode));(O/'CAD_run_status.json').write_text(json.dumps(dict(jobs=done,complete=False),indent=2));assert r.returncode==0
 a=json.loads((O/(size+'_motion_audit.json')).read_text());assert a['sampled_motion_pass'] and a['wearing_stop_blocking_pass']
(O/'CAD_run_status.json').write_text(json.dumps(dict(jobs=done,complete=True),indent=2))
