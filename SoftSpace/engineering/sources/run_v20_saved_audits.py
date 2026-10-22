from pathlib import Path
import subprocess,sys,time,json,hashlib,shutil,os
P=Path(r'${WORKSPACE}');O=P/'engineering-v20-results';O.mkdir(exist_ok=True)
W=P.parent/'SoftSpace/.workspaces/published-v19'
assert W.exists()
shutil.copy2(P/'verify_v19_quadratic.py',W/'verify_v19_quadratic.py')
# Libraries stay outside the published repository.
runner=O/'run_saved_audits.py'
runner.write_text("import sys,runpy,os\nsys.path.insert(0,"+repr(str(P/'solver-libraries'))+")\nsys.path.insert(0,"+repr(str(W))+")\nos.environ['OPENBLAS_NUM_THREADS']='1'\nrunpy.run_path("+repr(str(W/'verify_v19_quadratic.py'))+",run_name='__main__')\n",encoding='utf-8')
rows=[]
for folder in ['quadratic-contact','quadratic-inward']:
 start=time.time()
 with (O/(folder+'_audit.log')).open('w') as f:
  r=subprocess.run([sys.executable,str(runner),str(W/'engineering-v19-results'/folder)],cwd=W,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'))
 row={'study':folder,'exit_code':r.returncode,'seconds':time.time()-start,'method':'Same-equation reassembly of saved solutions, not an independent solver or physical test'}
 if r.returncode==0:
  q=json.loads((W/'engineering-v19-results'/folder/'verification.json').read_text());row['verification']=q
 rows.append(row);(O/'saved_audit_rerun.json').write_text(json.dumps({'date':'2026-10-21','runs':rows,'complete':len(rows)==2,'all_pass':len(rows)==2 and all(x['exit_code']==0 for x in rows)},indent=2));print(folder,row['exit_code'],round(row['seconds']),flush=True)
 if r.returncode:break
