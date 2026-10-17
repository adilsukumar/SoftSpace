"""Find assumed vapor-transmission windows; not a selected textile specification."""
import json,csv,itertools
from pathlib import Path
from environment_acoustic_screen import thermal
OUT=Path(__file__).parent/'engineering-v5-results';OUT.mkdir(exist_ok=True)
rows=[thermal(a,r,w,s,.05) for a,r,w,s in itertools.product([28,32,36],[50,70,90],[1000,3000,5000],[20,100,300])]
assert all(x['water_balance_error_mg']<1e-5 for x in rows)
with (OUT/'moisture_candidates.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={'case_count':len(rows),'nominal_32C_70RH_100mg_h':[r for r in rows if r['ambient_C']==32 and r['ambient_RH_percent']==70 and r['water_source_mg_h']==100],
         'candidate_3000_cases':len([r for r in rows if r['assumed_cover_WVTR_g_m2_day']==3000]),
         'candidate_3000_saturation_cases':len([r for r in rows if r['assumed_cover_WVTR_g_m2_day']==3000 and r['RH_60min_percent']>=99.9]),
         'limitations':['Lumped balance; no evaporation cooling, local temperatures or sweat feedback','WVTR is a hypothesis at 2000 Pa pressure differential, not measured material performance','High ambient vapor pressure can prevent outward drying','No air vent added to CAD; actual cover permeability and acoustics need joint validation']}
(OUT/'moisture_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
