"""Attempt native DOCX rendering and retain exact diagnostics; no false layout pass."""
import os,sys,subprocess,json
from pathlib import Path
P=Path(__file__).parent;Q=P/'documents/qa';T=P/'tmp/native-v19';T.mkdir(parents=True,exist_ok=True);renderer=Path('${USER_HOME}/.codex/plugins/cache/openai-primary-runtime/documents/26.1013.11914/skills/documents/render_docx.py');records=[]
for name in ['Ear_Defender_Project','Glasses_Friendly_Headphone_Cushions']:
 with (Q/(name+'_native_v19.log')).open('w') as f:r=subprocess.run([sys.executable,str(renderer),str(P/'documents'/(name+'.docx')),'--output_dir',str(Q/(name+'_native_v19')),'--emit_pdf'],cwd=P,env=dict(os.environ,TEMP=str(T),TMP=str(T)),stdout=f,stderr=subprocess.STDOUT)
 records.append(dict(document=name+'.docx',return_code=r.returncode,native_render_pass=r.returncode==0,log=str(Q/(name+'_native_v19.log'))))
(Q/'native_v19_attempt.json').write_text(json.dumps(dict(attempts=records,scope='Native renderer attempted. Failed attempts do not establish Word pagination. Approximate ReportLab previews remain a separate fallback.'),indent=2));print(json.dumps(records))
