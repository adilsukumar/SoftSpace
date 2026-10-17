import json,time,subprocess,sys,os
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v19-results';start=time.monotonic()
(O/'quadratic_initial_mesh_failure.json').write_text(json.dumps(dict(size='adult_small',mesh_mm=3,accepted=False,reason='Negative or zero curved tetrahedron Jacobian detected before accepted assembly result',evidence='quadratic_initial_invalid_mesh.log',retry='HighOrder mesh optimization',physical_failure=False),indent=2))
while not json.loads((O/'quadratic-contact/status.json').read_text()).get('complete'):
 if time.monotonic()-start>3600:raise RuntimeError('Quadratic model did not finish in this queued interval')
 time.sleep(2)
with (O/'final_update.log').open('w') as f:r=subprocess.run([sys.executable,str(P/'final_v19_update.py')],cwd=P,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
assert r.returncode==0
