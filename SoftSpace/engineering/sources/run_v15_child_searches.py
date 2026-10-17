import subprocess,sys,json
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v15-results';jobs=[]
for size in ['child_small','child_large']:
 log=O/(size+'_packing_run.log')
 with log.open('w') as f:r=subprocess.run([sys.executable,str(P/'screen_v15_child_packing.py'),size],cwd=P,stdout=f,stderr=subprocess.STDOUT)
 jobs.append({'size':size,'returncode':r.returncode,'log':str(log)});(O/'child_search_run_status.json').write_text(json.dumps({'jobs':jobs,'complete':False},indent=2));print(json.dumps(jobs[-1]),flush=True)
 if r.returncode:raise SystemExit(r.returncode)
(O/'child_search_run_status.json').write_text(json.dumps({'jobs':jobs,'complete':True},indent=2))
