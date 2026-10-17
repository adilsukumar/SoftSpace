import sys,subprocess,json,os
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v19-results';jobs=[]
for script in ['recover_v19_iteration_limit.py','verify_v19_joint.py','summarize_v19_handoff.py','finalize_v19_documents.py']:
 with (O/(script+'_final.log')).open('w') as f:r=subprocess.run([sys.executable,str(P/script)],cwd=P,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
 jobs.append(dict(script=script,exit_code=r.returncode));(O/'report_completion_status.json').write_text(json.dumps(dict(jobs=jobs,complete=False),indent=2));assert r.returncode==0,script
(O/'report_completion_status.json').write_text(json.dumps(dict(jobs=jobs,complete=True),indent=2))
