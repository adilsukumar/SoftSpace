import json,subprocess,sys,os
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v19-results';Q=O/'quadratic-contact';assert json.loads((Q/'status.json').read_text())['complete']
for script in ['verify_v19_conforming_pilot.py','verify_v19_quadratic.py','summarize_v19_handoff.py']:
 with (O/(script+'_latest.log')).open('w') as f:subprocess.run([sys.executable,str(P/script)],cwd=P,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT,check=True)
r=json.loads((O/'test_register.json').read_text());qstatus=json.loads((Q/'status.json').read_text());r['quadratic_contact_model']=dict(status=qstatus,verification=json.loads((Q/'verification.json').read_text()));r['conforming_linear_contact_pilot']=dict(status=json.loads((O/'conforming-contact/status.json').read_text()),verification=json.loads((O/'conforming-contact/verification.json').read_text()));(O/'test_register.json').write_text(json.dumps(r,indent=2))
review=O/'REVIEW.md';review.write_text(review.read_text()+'\nLatest numerical variant: quadratic bulk solids with aligned washer and preload footprints, 27 positive integration points and small linear contact subtriangles. Read quadratic-contact/status.json and verification.json for the actual selected outward mesh comparison. Earlier linear mesh failures and iteration-limit trials are preserved. A selected displacement comparison does not qualify the full joint, every stress or actual performance.\n')
f=P/'documents/build_documents.py';s=f.read_text()
for flag in ['False','True']:
 old=' add_v19(d,P,new_page,para,table,picture,link,'+flag+')'
 if ' add_quadratic(d,P,new_page,para,table)' not in s[s.index(old):s.index(old)+250]:s=s.replace(old,old+'\n from v19_quadratic_section import add_quadratic\n add_quadratic(d,P,new_page,para,table)')
f.write_text(s)
with (O/'document_build_latest.log').open('w') as f:subprocess.run([sys.executable,str(P/'finalize_v19_documents.py')],cwd=P,stdout=f,stderr=subprocess.STDOUT,check=True)
with (O/'native_render_attempt.log').open('w') as f:subprocess.run([sys.executable,str(P/'check_v19_native_render.py')],cwd=P,stdout=f,stderr=subprocess.STDOUT,check=True)
print('Latest evidence and both reports rebuilt')
