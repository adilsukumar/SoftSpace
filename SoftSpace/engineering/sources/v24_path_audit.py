"""Audit recorded CAD sources after relocation without rewriting provenance."""
from pathlib import Path
import json,hashlib,sys
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));from project_paths import verified_source
O=P/'engineering-v24-results';seen={};errors=[];references=0
excluded={'solver-libraries','cad-validation-libraries','tmp','__pycache__','package-history','CushionNext'}
def walk(value,file):
 global references
 if isinstance(value,dict):
  if isinstance(value.get('file'),str) and isinstance(value.get('sha256'),str) and len(value['sha256'])==64 and Path(value['file']).suffix.lower() in {'.step','.stp','.f3d'}:
   references+=1;key=(value['file'],value['sha256'])
   if key not in seen:
    try:
     resolved=verified_source(value);seen[key]=dict(recorded_path=value['file'],resolved=str(resolved.relative_to(P)),sha256=value['sha256'],pass_result=True)
    except (FileNotFoundError,ValueError) as e:errors.append(dict(report=str(file.relative_to(P)),source=value['file'],error=str(e)));seen[key]=dict(recorded_path=value['file'],sha256=value['sha256'],pass_result=False)
  for v in value.values():walk(v,file)
 elif isinstance(value,list):
  for v in value:walk(v,file)
for f in P.rglob('*.json'):
 if O in f.parents or any(part in excluded for part in f.relative_to(P).parts) or 'documents' in f.relative_to(P).parts:continue
 try:walk(json.loads(f.read_text(encoding='utf-8-sig')),f)
 except (ValueError,UnicodeDecodeError):continue
r=dict(date='2026-10-24',references=references,unique_sources=len(seen),verified=sum(x['pass_result'] for x in seen.values()),unresolved=errors,sources=list(seen.values()),scope='Recorded file plus SHA256 CAD references only. Historical JSON paths retained; primary mesh and motion loaders resolve moved sources by verified hash. This does not claim every historical script was migrated or every source geometry is valid.')
(O/'relocation_source_audit.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='sources'},indent=2))
