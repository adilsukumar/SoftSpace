"""Separate scalar root and exact ellipse-strip integration checks of selected V20 rows."""
from pathlib import Path
import sys,json,csv,math,hashlib
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'))
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
O=P/'engineering-v20-results'
rows=list(csv.DictReader((O/'cushion_contact_scenarios.csv').open()))
def width(y):
 return 40*math.sqrt(max(0,1-(y/50)**2))-(25*math.sqrt(max(0,1-(y/35)**2)) if abs(y)<35 else 0)
def strip(a,b):
 a=max(-50,a);b=min(50,b)
 if b<=a:return 0
 return quad(width,a,b,points=[v for v in [-35,35] if a<v<b],epsabs=1e-8)[0]
checks=[]
for zh in [12,18,24,32]:
 for pos in [8,15,24]:
  r=next(r for r in rows if float(r['zone_height_mm'])==zh and float(r['arm_centre_mm'])==pos and float(r['arm_width_mm'])==5 and float(r['force_per_cup_N'])==4 and float(r['assumed_E_MPa'])==.03 and float(r['assumed_exponent'])==2 and float(r['assumed_cover_parallel_N_mm3'])==.0002 and float(r['arm_protrusion_mm'])==2 and float(r['zone_modulus_ratio'])==.25)
  zone=strip(15-zh/2,15+zh/2);glass=strip(pos-2.5,pos+2.5);both=strip(max(15-zh/2,pos-2.5),min(15+zh/2,pos+2.5))
  total=math.pi*(40*50-25*35);A=[total-zone-glass+both,zone-both,glass-both,both]
  def pressures(d):return [.03*s*(max(d+g,0)/30)**2+.0002*max(d+g,0) for s,g in [(1,0),(.25,0),(1,2),(.25,2)]]
  d=brentq(lambda d:sum(a*p for a,p in zip(A,pressures(d)))-4,-2,30,xtol=1e-12)
  pressure=sum(a*p for a,p in zip(A[2:],pressures(d)[2:]))/glass*1000
  change=abs(pressure/float(r['soft_glasses_kPa'])-1)*100
  checks.append(dict(zone_height_mm=zh,arm_centre_mm=pos,independent_pressure_kPa=pressure,CSV_pressure_kPa=float(r['soft_glasses_kPa']),difference_percent=change,chosen_1_percent_gate_pass=change<1))
cad=json.loads((O/'CAD_verification.json').read_text());assert len(cad['cases'])==3
for c in cad['cases']:assert hashlib.sha256(Path(c['path']).read_bytes()).hexdigest()==c['sha256'] and c['reimport_pass']
aud=json.loads((O/'saved_audit_rerun.json').read_text());assert aud['complete'] and aud['all_pass'] and sum(len(r['verification']['array_audits']) for r in aud['runs'])==8
result=dict(date='2026-10-21',method='Independent scalar Brent root and quadrature of exact ellipse strips; same reduced physical assumptions',selected_contact_checks=checks,selected_contact_checks_pass=all(c['chosen_1_percent_gate_pass'] for c in checks),saved_joint_audits=8,STEP_files_hash_and_reimport_pass=3,physical_validation=False)
(O/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2));assert result['selected_contact_checks_pass']
