import os,sys,subprocess,json
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v18-results';done=[]
for size in ['child_large','adult_small']:
 for h in [2.0,1.5]:
  with (O/(size+'_fork_h'+str(h)+'.log')).open('w') as log:r=subprocess.run([sys.executable,'v18_fork_fixture.py',size,str(h)],cwd=P,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),stdout=log,stderr=subprocess.STDOUT)
  done.append(dict(size=size,h=h,exit_code=r.returncode));(O/'fork_run_status.json').write_text(json.dumps(dict(jobs=done,complete=False),indent=2));assert r.returncode==0
(O/'fork_run_status.json').write_text(json.dumps(dict(jobs=done,complete=True),indent=2))
