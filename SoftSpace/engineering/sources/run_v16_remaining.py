import subprocess,sys,json
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v16-results';jobs=[]
argslist=[]
for size in ['adult_medium','adult_large']:argslist.extend([['build_v16_indexed_rivet.py',size,'16','upper2'],['audit_v16_indexed_rivet.py',size+'_R16U2']])
argslist.extend([['v16_tongue_fixture.py','2.0'],['v16_tongue_fixture.py','1.5']])
for args in argslist:
 log=O/('run_'+'_'.join(args).replace('.py','')+'.log')
 with log.open('w') as f:r=subprocess.run([sys.executable,str(P/args[0]),*args[1:]],cwd=P,stdout=f,stderr=subprocess.STDOUT)
 jobs.append({'args':args,'returncode':r.returncode,'log':str(log)});(O/'remaining_run_status.json').write_text(json.dumps({'jobs':jobs,'complete':False},indent=2));print(json.dumps(jobs[-1]),flush=True)
 if r.returncode:raise SystemExit(r.returncode)
(O/'remaining_run_status.json').write_text(json.dumps({'jobs':jobs,'complete':True},indent=2))
