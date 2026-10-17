import os,sys,subprocess,json
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v17-results';O.mkdir(exist_ok=True);env=dict(os.environ,OPENBLAS_NUM_THREADS='1',EAR_DEFENDER_AUDIT_RESULTS='engineering-v17-results');jobs=[]
for size in ['child_large','adult_small']:
 for script,arg in [('build_v17_entry_pilot.py',size),('audit_v16_indexed_rivet.py',size+'_Entry25')]:
  log=O/(size+'_'+script+'.log')
  with log.open('w') as f:r=subprocess.run([sys.executable,str(P/script),arg],cwd=P,env=env,stdout=f,stderr=subprocess.STDOUT)
  jobs.append({'script':script,'argument':arg,'exit_code':r.returncode,'log':str(log)});(O/'run_status.json').write_text(json.dumps({'jobs':jobs,'complete':False},indent=2));assert r.returncode==0
(O/'run_status.json').write_text(json.dumps({'jobs':jobs,'complete':True},indent=2))
