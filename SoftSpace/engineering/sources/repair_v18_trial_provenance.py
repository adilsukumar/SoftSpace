from pathlib import Path
import json,hashlib
P=Path(__file__).parent;O=P/'engineering-v18-results';H=O/'superseded-disc-and-adult-clearance';records=[]
for f in H.glob('*_stop_h*.json'):
 d=json.loads(f.read_text());source=H/Path(d['source']).name;assert hashlib.sha256(source.read_bytes()).hexdigest()==d['source_sha256'];d['source']=str(source);d['status']='Superseded39Ndisc candidate,not the final118Ndisc assembly';f.write_text(json.dumps(d,indent=2));records.append(str(f))
f=H/'torque_and_mass.json';d=json.loads(f.read_text())
for r in d['sources']:
 source=H/Path(r['file']).name;assert hashlib.sha256(source.read_bytes()).hexdigest()==r['sha256'];r['file']=str(source)
d['status']='Superseded fixed39Ndisc comparison,not final V18 torque calibration target';f.write_text(json.dumps(d,indent=2));records.append(str(f));(O/'preserved_trial_provenance.json').write_text(json.dumps(dict(repaired=records),indent=2))
