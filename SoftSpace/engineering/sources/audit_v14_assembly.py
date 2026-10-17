"""Nominal axial disassembly with knob and cap fasteners removed."""
import json
from audit_v14_motion import P,O,cad,recipes,load,moved,check
rows=[]
for row in cad['sizes']:
 parts,_=load(row)
 base={k:s for k,s in parts.items() if 'CapBolt' not in k and not k.endswith('PullKnob')}
 for offset in [0,2,5,10,20]:
  q={k:moved(s,(0,-offset,0)) if k.endswith('ServiceCap') else s for k,s in base.items()}
  r=check(q,{k:i+1 if k.endswith('ServiceCap') else 0 for i,k in enumerate(q)})
  rows.append(dict(r,size=row['size'],phase='rear cap axial removal with bolts and knob removed',offset_mm=offset))
 base={k:s for k,s in base.items() if not k.endswith('ServiceCap')}
 for offset in [0,2,6,12,25,40]:
  q={k:moved(s,(0,-offset,0)) if k.endswith(('LockPin','SpringSpace')) else s for k,s in base.items()}
  r=check(q,{k:1 if k.startswith('Left') and k.endswith(('LockPin','SpringSpace')) else 2 if k.startswith('Right') and k.endswith(('LockPin','SpringSpace')) else 0 for k in q})
  rows.append(dict(r,size=row['size'],phase='pin and held spring envelope withdrawal with cap absent',offset_mm=offset))
 print(json.dumps({'size':row['size'],'samples':11,'failures':sum(not r['pass'] for r in rows if r['size']==row['size'])}),flush=True)
 (O/'assembly_path_partial.json').write_text(json.dumps({'cases':rows},indent=2))
out={'cases':rows,'case_count':len(rows),'all_pass':all(r['pass'] for r in rows),'sources':[{'size':r['size'],'sha256':r['sha256']} for r in cad['sizes']],'limits':['Discrete rigid samples, not continuous assembly or physical servicing','Knob and cap screws removed beforehand; threads, tooling, retained knob and nut access are not qualified','Spring allocation held at15mm by an unspecified fixture during withdrawal; actual coil free expansion and handling not simulated','Reverse path proposes assembly but does not prove manufacturability, low cost or child safety']}
(O/'assembly_path_audit.json').write_text(json.dumps(out,indent=2))
