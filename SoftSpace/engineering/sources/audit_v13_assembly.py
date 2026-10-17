"""Discrete radial disassembly checks with removable fasteners absent.
Reverse of the recorded path is a proposed assembly route, not a physical trial.
"""
import json,time
from audit_v13_motion import P,O,cad,recipes,load,moved,unlocked,check
rows=[]
for row in cad['sizes']:
 parts,valid=load(row);R=recipes[row['size']]['band_halfspan_mm']
 base={k:s for k,s in parts.items() if 'CapBolt' not in k}
 # Nuts remain in their open split-face pockets. Both caps move outward.
 for offset in [0,1,2,5,10]:
  q={k:moved(s,((-1 if k.startswith('Left') else 1)*offset,0,0)) if k.endswith('ServiceCap') else s for k,s in base.items()}
  r=check(q,{k:i+1 if k.endswith('ServiceCap') else 0 for i,k in enumerate(q)})
  rows.append(dict(r,size=row['size'],phase='cap radial removal with bolts removed',offset_mm=offset))
 # Remove caps, retract pins out of blind tongue holes, then lift pin and coil radially.
 q=unlocked(parts,R,6);base={k:s for k,s in q.items() if 'CapBolt' not in k and not k.endswith('ServiceCap')}
 for offset in [0,1,2,5,10]:
  q={k:moved(s,((-1 if k.startswith('Left') else 1)*offset,0,0)) if k.endswith(('LockPin','SpringSpace')) else s for k,s in base.items()}
  r=check(q,{k:1 if k.startswith('Left') and k.endswith(('LockPin','SpringSpace')) else 2 if k.startswith('Right') and k.endswith(('LockPin','SpringSpace')) else 0 for k in q})
  rows.append(dict(r,size=row['size'],phase='released pin and spring radial removal with caps absent',offset_mm=offset))
 print(json.dumps({'size':row['size'],'assembly_samples':10,'failures':sum(not r['pass'] for r in rows if r['size']==row['size'])}),flush=True)
out={'cases':rows,'case_count':len(rows),'all_pass':all(r['pass'] for r in rows),'sources':[{'size':r['size'],'sha256':r['sha256']} for r in cad['sizes']], 'limits':['Discrete rigid samples, not continuous assembly, tool access or deformed coil path','Bolts removed before cap movement; no simulated unscrewing, thread geometry, torque or nut retention','Pins first retracted6mm with caps absent; radial motion preserves spring allocation, not actual compressed spring handling','Nominal5.3mm head fits nominal5.65mm coil inside diameter only; production tolerance and spring end geometry remain open']}
(O/'assembly_path_audit.json').write_text(json.dumps(out,indent=2))
