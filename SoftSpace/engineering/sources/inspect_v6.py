import json,ctypes
from pathlib import Path
p=Path(__file__).parent
for name in ['cad_v6_report.json','cad_v6_audit.json']:
 f=p/name
 if not f.exists():continue
 j=json.loads(f.read_text());print(name,j.get('status'),j.get('error'),len(j.get('files',[])),len(j.get('sizes',[])),j.get('stages',[])[-2:])
 if 'sizes' in j:
  for s in j['sizes']:print(s['name'],len(s['positive_solid_overlaps']),s['mass_range_g'])
class M(ctypes.Structure):
 _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in ['total','available','total_page','available_page','total_virtual','available_virtual','extra']]
m=M();m.length=ctypes.sizeof(m);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m));print('Available GiB',round(m.available/2**30,2))
