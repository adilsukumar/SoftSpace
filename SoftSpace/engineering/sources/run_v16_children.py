import subprocess,sys,json
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v16-results';jobs=[]
for size in (sys.argv[1:] or ['child_large','child_small','child_medium']):
 for args in [['build_v16_indexed_rivet.py',size,'16'],['audit_v16_indexed_rivet.py',size+'_R16']]:
  log=O/('run_'+'_'.join(args).replace('.py','')+'.log')
  with log.open('w') as f:r=subprocess.run([sys.executable,str(P/args[0]),*args[1:]],cwd=P,stdout=f,stderr=subprocess.STDOUT)
  jobs.append({'args':args,'returncode':r.returncode,'log':str(log)});(O/'sequential_run_status.json').write_text(json.dumps({'jobs':jobs,'complete':False},indent=2));print(json.dumps(jobs[-1]),flush=True)
  if r.returncode:raise SystemExit(r.returncode)
(O/'sequential_run_status.json').write_text(json.dumps({'jobs':jobs,'complete':True},indent=2))
