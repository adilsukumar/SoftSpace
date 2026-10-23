from pathlib import Path
import sys,subprocess,concurrent.futures,json
P=Path(__file__).resolve().parent;O=P/'engineering-v21-results';O.mkdir(exist_ok=True)
def run(size):
 with (O/f'{size}_motion.log').open('w',encoding='utf-8') as f:
  r=subprocess.run([sys.executable,str(P/'v21_motion_audit.py'),size],cwd=P,stdout=f,stderr=subprocess.STDOUT)
 return dict(size=size,exit_code=r.returncode)
sizes=['adult_small','adult_medium','adult_large','child_small','child_medium','child_large']
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 results=list(ex.map(run,sizes))
(O/'motion_execution.json').write_text(json.dumps(results,indent=2));print(json.dumps(results),flush=True)
assert all(r['exit_code']==0 for r in results)
