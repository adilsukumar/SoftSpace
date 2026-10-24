from pathlib import Path
import json,zipfile,hashlib
P=Path(__file__).resolve().parent;O=P/'engineering-v24-results';r=json.loads((O/'relocation_source_audit.json').read_text());targets={s['recorded_path'].replace('\\','/').split('/')[-1]:s for s in r['sources'] if not s['pass_result']};found=[];trials=[]
archives=list(P.glob('*.zip'))+list((P/'package-history').glob('*.zip'))+list(P.parent.glob('*.zip'))
for archive in archives:
 try:
  with zipfile.ZipFile(archive) as z:
   for item in z.infolist():
    name=Path(item.filename).name
    if name not in targets:continue
    data=z.read(item);actual=hashlib.sha256(data).hexdigest();expected=targets[name]['sha256'];trials.append(dict(archive=str(archive.relative_to(P.parent)),member=item.filename,hash_matches=actual==expected,sha256=actual))
    if actual==expected:
     dest=P/'source-archive'/expected/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);found.append(dict(file=name,sha256=actual,recovered=str(dest.relative_to(P)),archive=str(archive.relative_to(P.parent)),member=item.filename))
 except zipfile.BadZipFile:continue
(O/'historical_source_recovery.json').write_text(json.dumps(dict(archives_scanned=len(archives),exact_recoveries=found,candidate_trials=trials,scope='Exact hash recovery only; no approximation or overwritten source accepted'),indent=2));print(json.dumps(dict(archives=len(archives),candidate_trials=len(trials),recoveries=len(found))))
