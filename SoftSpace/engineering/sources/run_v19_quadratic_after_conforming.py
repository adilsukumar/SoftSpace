import json,time,subprocess,sys,os
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v19-results';start=time.monotonic()
while not json.loads((O/'conforming-contact/status.json').read_text()).get('complete'):
 if time.monotonic()-start>1800:raise RuntimeError('Contact pilot did not finish within the queued wait limit')
 time.sleep(2)
with (O/'quadratic_contact.log').open('w') as f:r=subprocess.run([sys.executable,str(P/'v19_quadratic_joint.py')],cwd=P,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
assert r.returncode==0
