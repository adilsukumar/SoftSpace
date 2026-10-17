"""Tie current CAD bytes to the recorded geometry and native reopening checks."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;O=P/'engineering-v10-results'
def audit():
 records={}
 def add(path,digest,evidence):
  path=Path(path).resolve();assert path.is_relative_to(P)
  assert path.suffix.lower() in ['.step','.f3d']
  key=str(path).casefold()
  if key in records:
   assert records[key]['recorded_sha256']==digest,'Recorded file hashes disagree'
   records[key]['evidence'].append(evidence)
  else:records[key]={'file':str(path),'recorded_sha256':digest,'evidence':[evidence]}
 for name,key in [('native_all_pose_pairs.json','checks'),('all_pose_pairs.json','checks'),('native_archive_reopen.json','archives')]:
  for r in json.loads((O/name).read_text())[key]:add(r['file'],r['sha256'],name)
 for r in json.loads((O/'native_local_band_comparison.json').read_text())['cases']:
  for kind in ['native','local']:add(r[kind],r[kind+'_sha256'],'native_local_band_comparison.json')
 for r in records.values():
  with Path(r['file']).open('rb') as f:r['current_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
  r['match']=r['current_sha256']==r['recorded_sha256']
 out={'status':'complete','date':'2026-10-14','unique_CAD_files':len(records),'all_match':all(r['match'] for r in records.values()),'checks':list(records.values()),'scope':'Current file identity only. The geometry, overlap and native reopening outcomes remain the separately recorded tests; no new physical pass is added.'}
 (O/'source_identity_audit.json').write_text(json.dumps(out,indent=2));assert out['all_match'],'Current CAD differs from tested CAD'
 return out
if __name__=='__main__':
 r=audit();print(json.dumps({k:v for k,v in r.items() if k!='checks'}))
