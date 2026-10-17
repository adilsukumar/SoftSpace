"""STEP-only experiment; never substitutes for the saved V8 Fusion archive."""
import subprocess,sys,json,traceback
from pathlib import Path
P=Path(__file__).parent
from solid_band_v9_local import run,OUT
j={'status':'running','revision':'V9Local STEP-only corner experiment','cases':[],'limitations':['No matching Fusion archive','Assumed E2000MPa and ideal2N/side; no material validation','No slider motion/contact verification for this fillet revision']}
try:
 for size in ['adult_small','adult_large','child_small','child_medium','child_large','adult_medium']:
  if not (P/('OwnPassiveDefender_V9Local_'+size+'.step')).exists():
   subprocess.run([sys.executable,str(P/'local_slot_fillet.py'),size],check=True)
  rows=[]
  for h in [3,2,1.5]:
   path=OUT/(size+'_h'+str(h)+'.json')
   rows.append(json.loads(path.read_text()) if path.exists() else run(size,h))
   if len(rows)>1:
    a,b=rows[-2:];du=abs(b['guide_mean_x_displacement_mm']/a['guide_mean_x_displacement_mm']-1);ds=abs(b['max_von_mises_centroid_MPa']/a['max_von_mises_centroid_MPa']-1)
    if du<.05 and ds<.05:break
  j['cases'].append({'size':size,'meshes':rows,'deflection_relative_mesh_change':du,'stress_relative_mesh_change':ds,'deflection_gate_5pct':du<.05,'stress_gate_5pct':ds<.05})
  (OUT/'summary.json').write_text(json.dumps(j,indent=2));print(size,du,ds,flush=True)
 j['status']='complete'
except Exception:j['status']='error';j['error']=traceback.format_exc();print(j['error'],flush=True)
(OUT/'summary.json').write_text(json.dumps(j,indent=2))
