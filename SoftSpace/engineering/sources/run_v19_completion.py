import subprocess,sys,json,os
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v19-results';jobs=[]
for script in ['run_v19_contact_matrix.py','refine_v19_joint.py','verify_v19_joint.py']:
 with (O/(script+'.log')).open('w') as f:r=subprocess.run([sys.executable,str(P/script)],cwd=P,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
 jobs.append(dict(script=script,exit_code=r.returncode));(O/'solver_completion_status.json').write_text(json.dumps(dict(jobs=jobs,complete=False),indent=2));assert r.returncode==0,script
(O/'solver_completion_status.json').write_text(json.dumps(dict(jobs=jobs,complete=True),indent=2))
