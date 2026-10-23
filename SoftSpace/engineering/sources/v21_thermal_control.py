"""Analytic temperature control of an older uncalibrated one-node proxy.
Not a current V19 thermal model or measured sweating/comfort experiment.
"""
from pathlib import Path
import csv,json,math,hashlib
P=Path(__file__).resolve().parent;O=P/'engineering-v21-results'
source=P/'engineering-final-results/thermal_vapor_cases.csv';rows=list(csv.DictReader(source.open()));checks=[]
for r in rows:
 ambient=float(r['ambient_C']);k=float(r['foam_k_W_mK']);area=.0044
 ga=1/(.020/(k*area)+.0002/(.15*area)+1/(8*area));gs=5*area;Tinf=(gs*34+ga*ambient)/(gs+ga);tau=30/(gs+ga)
 analytic=Tinf+(ambient-Tinf)*math.exp(-3600/tau);recorded=float(r['temperature_60min_C'])
 checks.append(dict(ambient_C=ambient,foam_k_W_mK=k,analytic_C=analytic,recorded_C=recorded,error_C=abs(analytic-recorded),pass_chosen_001_C=abs(analytic-recorded)<.01))
assert all(c['pass_chosen_001_C'] for c in checks)
result=dict(date='2026-10-23',rows=len(rows),max_temperature_difference_C=max(c['error_C'] for c in checks),analytic_temperature_control_pass=True,
 saturation_cases=sum(float(r['RH_60min_percent'])>=99.999 for r in rows),max_saved_water_balance_error_mg=max(float(r['water_balance_error_mg']) for r in rows),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
 scope='Closed-form temperature ODE compared with old Euler integration at one hour. It checks implementation of that older one-node geometry/property proxy only. No full V19 worn heat transfer, sweating feedback, measured permeability, sensory acceptance or thermal comfort validation.',cases=checks)
(O/'thermal_proxy_control.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
