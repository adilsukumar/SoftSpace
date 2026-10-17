import ctypes,json,platform,sys,hashlib,shutil
from ctypes import wintypes
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v19-results'
class M(ctypes.Structure):
 _fields_=[('length',wintypes.DWORD),('load',wintypes.DWORD)]+[(n,ctypes.c_ulonglong) for n in ['total','available','page_total','page_available','virtual_total','virtual_available','extended']]
m=M();m.length=ctypes.sizeof(m);ok=ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m));r=dict(python=sys.version,platform=platform.platform(),runtime=sys.executable,total_memory_bytes=int(m.total) if ok else None,available_memory_bytes=int(m.available) if ok else None,chosen_joint_node_limit=30000,scope='Snapshot while local tasks run; 30000 nodes is a chosen bounded study limit, not a demonstrated hardware maximum')
(O/'environment.json').write_text(json.dumps(r,indent=2));path=O/'thread_trial_status.json';old=json.loads(path.read_text());backup=O/'rejected-thread-trials/original_trial_status.json'
if not backup.exists():shutil.copy2(path,backup)
old.update(expected_one_connected_bolt_solid=False,actual_bolt_solids=2,accepted_for_final_assembly=False,superseded_by='helical_thread_rejection.json');path.write_text(json.dumps(old,indent=2));print(json.dumps(r))
