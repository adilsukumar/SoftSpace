from pathlib import Path
import json,hashlib,shutil,subprocess,sys
P=Path(__file__).parent;D=P/'documents';H=D/'history';T=H/'v17_body_comparison';T.mkdir(exist_ok=True)
expected={'Ear_Defender_Project':'65c5d342c4a89b1ca366156338475014263172a41233b5fcbb444f3c9a412232','Glasses_Friendly_Headphone_Cushions':'ea8b06f2fa460078c2b5ab04207c07d4d97282464e016ef0f3dbee8ce7d88905'}
for name,digest in expected.items():
 matches=[f for f in H.glob(name+'_*.docx') if hashlib.sha256(f.read_bytes()).hexdigest()==digest];assert matches,name;shutil.copy2(matches[0],T/(name+'.docx'))
(T/'document_status.json').write_text(json.dumps({'updated':'16 October 2026'}));shutil.copy2(D/'check_document_layout.py',T/'check_document_layout.py');subprocess.run([sys.executable,str(T/'check_document_layout.py')],check=True,stdout=subprocess.DEVNULL)
checks=[];unchanged=0;changed=[];added=[]
for name in expected:
 old=T/'qa'/name;new=D/'qa'/name
 for f in sorted(new.glob('page-*.png')):
  prev=old/f.name;path=str(f.relative_to(D/'qa'))
  if not prev.exists():added.append(path)
  elif f.read_bytes()==prev.read_bytes():unchanged+=1
  else:changed.append(path)
out=dict(unchanged_prior_body_page_images=unchanged,changed_prior_page_images=changed,added_page_images=added,scope='V17 DOCX copies re-rendered with current preview header date to isolate body changes. Unchanged pages retain the prior visual review. Native Word layout remains unverified.');(D/'qa/additional_tests_page_comparison.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
