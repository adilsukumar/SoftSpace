"""Recover the previously reviewed V18 reports for pagination-independent visual regression."""
import zipfile,hashlib,json,subprocess,sys
from pathlib import Path
P=Path(__file__).parent;D=P/'documents/qa/v18-baseline';D.mkdir(exist_ok=True);records=[]
expected={'Ear_Defender_Project.docx':'669e507082f9b03ce0cfdb6b083a63c3e6b09bece79fb033495d714109eccac5','Glasses_Friendly_Headphone_Cushions.docx':'7036ce736fb6c3114567eb0d9b82c916d506939f1adb095db4965ae04fd810fd'}
with zipfile.ZipFile(P/'EarDefender_V18_Digital_Prototype_and_Recorded_Checks.zip') as z:
 (D/'document_status.json').write_bytes(z.read('documents/document_status.json'))
 for name,digest in expected.items():
  data=z.read('documents/'+name);assert hashlib.sha256(data).hexdigest()==digest;(D/name).write_bytes(data);records.append(dict(name=name,sha256=digest))
(D/'check_document_layout.py').write_text((P/'documents/check_document_layout.py').read_text());(D/'source_identity.json').write_text(json.dumps(records,indent=2))
with (D/'render.log').open('w') as f:subprocess.run([sys.executable,str(D/'check_document_layout.py')],cwd=P,stdout=f,stderr=subprocess.STDOUT,check=True)
