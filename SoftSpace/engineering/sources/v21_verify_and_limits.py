"""Independent controls and explicit assumed mechanical limits; no product pass."""
from pathlib import Path
import sys,json,csv,math,hashlib
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'))
from scipy.integrate import quad
from scipy.optimize import brentq
O=P/'engineering-v21-results'
def dump(n,x):(O/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def width(y):return 40*math.sqrt(max(0,1-(y/50)**2))-(25*math.sqrt(max(0,1-(y/35)**2)) if abs(y)<35 else 0)
def strip(a,b):
 a=max(-50,a);b=min(50,b)
 if b<=a:return 0.
 return quad(width,a,b,points=[v for v in [-35,35] if a<v<b],epsabs=1e-8)[0]
rows=[]
with (O/'wider_position_scenarios.csv').open() as f:
 for i,r in enumerate(csv.DictReader(f)):
  if i%997:continue
  zh=float(r['zone_height_mm']);pos=float(r['arm_centre_mm']);w=float(r['arm_width_mm'])
  z=(15-zh/2,15+zh/2);g=(pos-w/2,pos+w/2);az=strip(*z);ag=strip(*g);both=strip(max(z[0],g[0]),min(z[1],g[1]));A=[math.pi*1125-az-ag+both,az-both,ag-both,both]
  F=float(r['force_per_cup_N']);E=float(r['assumed_E_MPa']);n=float(r['exponent']);kc=float(r['cover_stiffness_N_mm3']);h=float(r['protrusion_mm']);ratio=float(r['soft_ratio'])
  def pressure(d,s):return [E*v*(max(d+t,0)/30)**n+kc*max(d+t,0) for v,t in [(1,0),(s,0),(1,h),(s,h)]]
  def mean(s):
   d=brentq(lambda d:sum(a*p for a,p in zip(A,pressure(d,s)))-F,-h,30,xtol=1e-12)
   return sum(a*p for a,p in zip(A[2:],pressure(d,s)[2:]))/ag
  result=100*(mean(ratio)/mean(1)-1);err=abs(result-float(r['local_pressure_change_percent']))
  rows.append(dict(row_index=i,pressure_change_percent=result,difference_percentage_points=err,pass_chosen_000001_percentage_point=err<1e-6))
assert rows and all(r['pass_chosen_000001_percentage_point'] for r in rows)
dump('separate_scalar_controls.json',dict(method='Adaptive strip quadrature and Brent root; separate from the closed-form areas and vectorized bisection',cases=rows,all_pass=True,physical_validation=False))
t=json.loads((P/'engineering-v18-results/torque_and_mass.json').read_text());radius=t['effective_radius_mm'];moment=max(r['maximum_gravity_moment_over_orientation_Nmm'] for r in t['mass_cases'])
limits=[]
for mu in [.1,.2,.3]:
 for g in [1,2,3]:
  need=g*moment/(2*mu*radius);limits.append(dict(mu=mu,equivalent_static_g=g,required_preload_N=need,below_236N_catalogue_reference=need<=236))
# Tight allocation from handoff versus deliberately broad manufacturing errors.
fit=[]
for name,pin,bore,axis,finish in [('allocated controlled finish',.03,.03,.04,.02),('broad assumed raw errors',.2,.2,.08,.02)]:
 need=4+pin+bore+2*(axis+finish+.05)
 fit.append(dict(assumption=name,pin_oversize_mm=pin,bore_undersize_mm=bore,axis_error_mm=axis,radial_finish_mm=finish,chosen_min_radial_margin_mm=.05,minimum_nominal_bore_mm=need,margin_with_4_3mm_bore=(4.3-bore-4-pin)/2-axis-finish))
dump('mechanical_limits.json',dict(radius_mm=radius,assumed_worst_single_g_moment_Nmm=moment,preload_limits=limits,pin_fit=fit,
 decision='Specify measurable assembled torque and controlled pin/bore fit. Do not blindly raise preload or enlarge bores: the spring point is not a full allowable-load curve, and added clearance changes bearing/contact behaviour. V19 CAD and joint calculations remain unchanged.',
 source_revision='V18 moving-side assumed masses and friction model reused in V20; not a recomputed V19 measured mass or impact analysis',physical_validation=False))
print(json.dumps(dict(scalar_cases=len(rows),all_pass=True,max_difference_percentage_points=max(r['difference_percentage_points'] for r in rows),mechanical_limits=limits,pin_fit=fit),indent=2))
