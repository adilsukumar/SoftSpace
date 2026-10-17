"""Transparent assumed-root rod and assembly torque screen, not thread FE."""
import json,math
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v15-results';O.mkdir(exist_ok=True)
rows=[]
for diameter in [1.35,1.50]:
 for torque in [5,10,20]:
  for K in [.1,.2,.3]:
   for pull in [2,10,20,50]:
    preload=torque/(K*2);sigma=(preload+pull)/(math.pi*diameter**2/4);tau=16*torque/(math.pi*diameter**3);vm=math.sqrt(sigma*sigma+3*tau*tau)
    rows.append({'assumed_root_diameter_mm':diameter,'illustrative_torque_Nmm':torque,'assumed_nut_factor':K,'illustrative_external_pull_N':pull,'approximate_preload_N':preload,'conservative_combined_stress_MPa':vm,'required_yield_for_factor_two_MPa':2*vm})
out={'revision':'V15 retention concept','case_count':len(rows),'cases':rows,'formulas':{'preload':'T/(K*dnom) with dnom2mm','axial':'(preload+external pull)/(pi*droot^2/4)','torsion':'16*T/(pi*droot^3)','combined':'sqrt(axial^2+3*torsion^2)'},'limits':['All nut factors, root diameters, torques and pulls are chosen scenarios, not measured production inputs','Simple solid rod at an assumed root diameter; actual thread flank stripping contact runout stress concentration jam nut load sharing friction and loosening excluded','Adding full assembly torsion preload and external pull is a conservative illustrative combination, not a solved joint load history','No material grade chosen or passed; required yield is an input requirement for this reduced screen only','No fatigue or vibration or child-access qualification']}
(O/'retention_load_screen.json').write_text(json.dumps(out,indent=2));print(json.dumps({'cases':len(rows),'required_yield_range_MPa':[min(r['required_yield_for_factor_two_MPa'] for r in rows),max(r['required_yield_for_factor_two_MPa'] for r in rows)]}))
