import sys,subprocess,json,os
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v19-results';D=O/'final-CAD'
assert json.loads((D/'run_status.json').read_text())['complete']
for old,new in [('export_v18_poses.py','export_v19_poses.py'),('render_v18_candidates.py','render_v19_candidates.py')]:
 s=(P/old).read_text().replace('V18','V19').replace("O=P/'engineering-v18-results'","O=P/'engineering-v19-results'/'final-CAD'")
 if 'export' in old:s=s.replace('len(solids)==38','len(solids)==42')
 (P/new).write_text(s)
 with (O/(new+'.log')).open('w') as f:r=subprocess.run([sys.executable,str(P/new)],cwd=P,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,new
