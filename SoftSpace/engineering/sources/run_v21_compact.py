from pathlib import Path
import subprocess,sys,json
P=Path(__file__).resolve().parent;O=P/'engineering-v21-results';results=[]
for size in ['child_medium','child_small','child_large','adult_small','adult_medium','adult_large']:
 with (O/f'{size}_compact.log').open('w') as f:r=subprocess.run([sys.executable,str(P/'v21_compact_pose.py'),size],cwd=P,stdout=f,stderr=subprocess.STDOUT)
 results.append(dict(size=size,exit_code=r.returncode));print(size,r.returncode,flush=True)
(O/'compact_execution.json').write_text(json.dumps(results,indent=2));assert all(r['exit_code']==0 for r in results)
