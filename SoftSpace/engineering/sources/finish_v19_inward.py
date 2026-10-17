import json,time,subprocess,sys,os
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v19-results';I=O/'quadratic-inward'
while not (I/'status.json').exists() or not json.loads((I/'status.json').read_text()).get('complete'):time.sleep(5)
with (I/'verification.log').open('w') as f:subprocess.run([sys.executable,str(P/'verify_v19_quadratic.py'),str(I)],cwd=P,stdout=f,stderr=subprocess.STDOUT,check=True,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'))
r=json.loads((O/'test_register.json').read_text());r['quadratic_inward_model']=dict(status=json.loads((I/'status.json').read_text()),verification=json.loads((I/'verification.json').read_text()));(O/'test_register.json').write_text(json.dumps(r,indent=2))
f=P/'documents/v19_quadratic_section.py';s=f.read_text();s=s.replace('The inward and other friction cases were not repeated with quadratic solids, so the new result does not replace every earlier load case.','The later inward extension is recorded in the next chapter. Other friction settings were not repeated with quadratic solids, so these results do not replace every earlier load case.');f.write_text(s)
f=P/'documents/build_documents.py';s=f.read_text();needle=' add_quadratic(d,P,new_page,para,table)';replacement=needle+'\n from v19_inward_section import add_inward\n add_inward(d,P,new_page,para,table)'
if ' from v19_inward_section import add_inward' not in s:s=s.replace(needle,replacement)
f.write_text(s)
review=O/'REVIEW.md';review.write_text(review.read_text()+'\nInward extension: quadratic-inward/status.json and verification.json record four inward reference cases on the same saved meshes. This adds no measured product or Sony-pad validation.\n')
with (I/'documents.log').open('w') as f:subprocess.run([sys.executable,str(P/'finalize_v19_documents.py')],cwd=P,stdout=f,stderr=subprocess.STDOUT,check=True)
print('Inward evidence audited and both reports rebuilt.',flush=True)
