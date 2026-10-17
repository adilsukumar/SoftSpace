from pathlib import Path
import json,zipfile,hashlib
P=Path(__file__).parent;O=P/'engineering-v10-results';n=json.loads((O/'cad_native_report.json').read_text());rows=[]
for value in n['files']:
 f=Path(value)
 if f.suffix!='.f3d':continue
 with zipfile.ZipFile(f) as z:
  count=len(z.namelist());assert count>0;methods=sorted(set(v.compress_type for v in z.infolist()))
  try:bad=z.testzip();integrity='pass' if bad is None else 'fail: '+bad
  except NotImplementedError as e:integrity='unverified: '+str(e)
 rows.append({'file':str(f),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'archive_entries':count,'compression_methods':methods,'zip_integrity':integrity,'reopened_in_Fusion':False})
out={'status':'complete inventory','archives':rows,'all_archive_integrity_pass':len(rows)==6 and all(r['zip_integrity']=='pass' for r in rows),'limit':'Native export succeeded and archive directories can be read, but Python cannot decompress the Autodesk compression method. Full integrity and reopening in Fusion remain unchecked.'}
(O/'archive_integrity.json').write_text(json.dumps(out,indent=2));print(json.dumps({'archives':len(rows),'zip_integrity':out['all_archive_integrity_pass'],'reopening':'not checked'}))
