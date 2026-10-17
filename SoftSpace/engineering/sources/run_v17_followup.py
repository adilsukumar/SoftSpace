import os,sys,subprocess,json
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v17-results';env=dict(os.environ,OPENBLAS_NUM_THREADS='1',EAR_DEFENDER_ANALYSIS_RESULTS='engineering-v17-results');jobs=[]
commands=[['check_v17_entry_geometry.py'],['verify_v17_pilots.py'],['render_v17_entry_sections.py']]+[['v16_tongue_fixture.py',str(h),'guide82',size+'_Entry25'] for size in ['child_large','adult_small'] for h in [2.0,1.5]]
start=int(sys.argv[1]) if len(sys.argv)>1 else 0
if start:jobs=json.loads((O/'followup_status.json').read_text())['jobs'][:start]
for i,args in list(enumerate(commands))[start:]:
 with (O/('followup_'+str(i)+'.log')).open('w') as f:r=subprocess.run([sys.executable]+args,cwd=P,env=env,stdout=f,stderr=subprocess.STDOUT)
 jobs.append({'args':args,'exit_code':r.returncode});(O/'followup_status.json').write_text(json.dumps({'jobs':jobs,'complete':False},indent=2))
 if r.returncode:break
else:(O/'followup_status.json').write_text(json.dumps({'jobs':jobs,'complete':True},indent=2))
