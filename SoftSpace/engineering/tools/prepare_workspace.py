"""Recreate legacy relative paths in a fresh directory without changing published evidence."""
from pathlib import Path
import argparse,shutil,json,hashlib
E=Path(__file__).resolve().parents[1];REPO=E.parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path);args=ap.parse_args();W=args.output.resolve()
if W.exists() and any(W.iterdir()):raise SystemExit('Choose an empty output directory; existing work will not be overwritten.')
W.mkdir(parents=True,exist_ok=True);written={}
allowed={r['path'] for r in json.loads((E/'publication_manifest.json').read_text())['records']}
def copy(source,dest,text_paths=True):
 if source.relative_to(REPO).as_posix() not in allowed:return
 data=source.read_bytes()
 if text_paths and source.suffix.lower() in ['.json','.py','.md','.txt','.csv','.log','.js','.toml']:
  try:data=data.decode('utf-8').replace('${WORKSPACE}',W.as_posix()).encode('utf-8')
  except UnicodeDecodeError:pass
 rel=dest.relative_to(W).as_posix();h=hashlib.sha256(data).hexdigest()
 if rel in written:
  if written[rel]!=h:raise RuntimeError('Conflicting flat CAD/source name: '+rel)
  return
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);written[rel]=h
for root,target in [(E/'sources',W),(E/'evidence',W),(E/'project-inputs',W),(E/'figures',W/'documents/images')]:
 for f in root.rglob('*'):
  if f.is_file():copy(f,target/f.relative_to(root))
for f in (E/'CAD').rglob('*'):
 if f.is_file() and f.suffix.lower() in ['.step','.stp','.f3d']:copy(f,W/f.name,False)
for f in (REPO/'SoftSpace Flex/CAD').rglob('*.step'):copy(f,W/f.name,False)
for source,dest in [('SoftSpace/reports/SoftSpace_Report.docx','Ear_Defender_Project.docx'),('SoftSpace Flex/reports/SoftSpace_Flex_Report.docx','Glasses_Friendly_Headphone_Cushions.docx')]:copy(REPO/source,W/'documents'/dest,False)
copy(E/'report-audit/document_status.json',W/'documents/document_status.json')
status=json.loads((W/'documents/document_status.json').read_text())
for d in status['documents']:d['path']=str(W/'documents'/Path(d['path']).name)
(W/'documents/document_status.json').write_text(json.dumps(status,indent=2))
(W/'WORKSPACE_PREPARATION.json').write_text(json.dumps(dict(files=len(written),source_repository=str(REPO),scope='Machine paths rebased; CAD and NPZ bytes preserved. No simulation was run by this preparation step.'),indent=2))
print('Prepared',len(written),'files at',W)
