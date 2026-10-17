"""Run CAD and FE jobs sequentially, one fresh process per case.
Logs survive a client disconnect. This is a foreground task, not an automation.
"""
import os,sys,json,subprocess,traceback
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v14-results';os.environ['OPENBLAS_NUM_THREADS']='1'
cad=json.loads((O/'cad_report.json').read_text());jobs=[]
motion=json.loads((O/'ocp_motion_partial.json').read_text()) if (O/'ocp_motion_partial.json').exists() else {'cases':[]}
for r in cad['sizes']:
 if not any(c['size']==r['size'] for c in motion['cases']):jobs.append(['audit_v14_motion.py',r['size']])
for r in cad['sizes']:jobs.append(['export_v14_poses.py',r['size']])
jobs.append(['verify_v14_exports.py'])
for h in ['2.0','1.5']:
 if not (O/('adult_small_fork_h'+h+'.json')).exists():jobs.append(['v14_fork_fixture.py','adult_small',h])
records=[]
for args in jobs:
 log=O/('run_'+('_'.join(args)).replace('.py','')+'.log')
 print('Running '+' '.join(args),flush=True)
 with log.open('w',encoding='utf-8') as stream:r=subprocess.run([sys.executable,*args],cwd=P,stdout=stream,stderr=subprocess.STDOUT)
 records.append({'args':args,'returncode':r.returncode,'log':str(log)})
 (O/'sequential_run_status.json').write_text(json.dumps({'jobs':records,'complete':False},indent=2))
 if r.returncode:print('Failed; inspect '+str(log),flush=True);sys.exit(r.returncode)
(O/'sequential_run_status.json').write_text(json.dumps({'jobs':records,'complete':True},indent=2));print('Sequential jobs finished',flush=True)
