import os,sys,subprocess,json
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v18-results';done=[]
jobs=[('v18_stop_fixture.py',s,h) for s in ['child_large','adult_small'] for h in [2.0,1.5]]
jobs += [('v18_band_fixture.py',s,h) for s in ['adult_small','adult_medium','adult_large'] for h in [2.5,2.0]]
for script,size,h in jobs:
 with (O/(size+'_'+script+'_'+str(h)+'.log')).open('w') as f:
  r=subprocess.run([sys.executable,script,size,str(h)],cwd=P,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
 done.append(dict(script=script,size=size,h=h,exit_code=r.returncode));(O/'fixture_run_status.json').write_text(json.dumps(dict(jobs=done,complete=False),indent=2));assert r.returncode==0
(O/'fixture_run_status.json').write_text(json.dumps(dict(jobs=done,complete=True),indent=2))
