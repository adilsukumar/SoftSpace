import os,sys,json,subprocess
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v18-results';env=dict(os.environ,OPENBLAS_NUM_THREADS='1');jobs=[]
for size in ['child_large','adult_small','child_small','child_medium','adult_medium','adult_large']:
 for script in ['build_v18_friction_stop.py','audit_v18_motion.py']:
  with (O/(size+'_'+script+'.log')).open('w') as f:r=subprocess.run([sys.executable,script,size],cwd=P,env=env,stdout=f,stderr=subprocess.STDOUT)
  jobs.append({'size':size,'script':script,'exit_code':r.returncode});(O/'size_run_status.json').write_text(json.dumps({'jobs':jobs,'complete':False},indent=2));assert r.returncode==0
 a=json.loads((O/(size+'_motion_audit.json')).read_text())
 if not a['sampled_motion_pass'] or not a['wearing_stop_blocking_pass']:raise RuntimeError(size+' did not pass its sampled geometry gates')
(O/'size_run_status.json').write_text(json.dumps({'jobs':jobs,'complete':True},indent=2))
