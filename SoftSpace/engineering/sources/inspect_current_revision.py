from pathlib import Path
import json,sys
p=Path(__file__).parent;version=sys.argv[1] if len(sys.argv)>1 else 'v8'
for name in ['cad_'+version+'_report.json','cad_'+version+'_audit.json']:
 f=p/name
 if not f.exists():continue
 j=json.loads(f.read_text());print(name,j.get('status'),'files',len(j.get('files',[])),'sizes',len(j.get('sizes',[])),'failed_gates',j.get('failed_gates'),j.get('error'))
 if 'sizes' in j:
  for r in j['sizes']:print(r['name'],len(r['positive_solid_overlaps']),[round(v,2) for v in r['mass_range_g']])
