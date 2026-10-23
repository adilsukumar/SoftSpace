"""Exact area integration and wider positional checks of the reduced V20 law.
All material/force values remain assumptions; this is not wearer validation.
"""
from pathlib import Path
import sys,os,json,csv,math,itertools,hashlib
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'))
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=P/'engineering-v21-results';O.mkdir(exist_ok=True)
def dump(n,x):(O/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def primitive(y,a,b):
 t=max(-1,min(1,y/b));return a*b/2*(t*math.sqrt(max(0,1-t*t))+math.asin(t))
def strip(lo,hi):
 if hi<=lo:return 0.
 return (primitive(hi,40,50)-primitive(lo,40,50))-(primitive(hi,25,35)-primitive(lo,25,35))
total=math.pi*1125
def area(pos,width,zh):
 z=(15-zh/2,15+zh/2);g=(pos-width/2,pos+width/2)
 az=strip(*z);ag=strip(*g);both=strip(max(z[0],g[0]),min(z[1],g[1]))
 return np.array([total-az-ag+both,az-both,ag-both,both])
combos=np.array(list(itertools.product([2,4,8],[.01,.03,.1],[1,2],[0,.0002,.001],[1,2,4],[.25,.5])),float)
def solve(A,c,uniform=False):
 F,E,n,k,h,ratio=c.T;ratio=np.ones(len(c)) if uniform else ratio
 mod=E[:,None]*np.column_stack((np.ones(len(c)),ratio,np.ones(len(c)),ratio))
 extra=h[:,None]*np.array([0,0,1,1]);lo=-h;hi=np.full(len(c),30.)
 def pressure(d):
  u=np.maximum(d[:,None]+extra,0);return mod*(u/30)**n[:,None]+k[:,None]*u
 # Explicit bracketing; high loads outside the chosen range must not silently saturate.
 assert np.all(pressure(lo)@A<=F) and np.all(pressure(hi)@A>=F)
 for _ in range(65):
  mid=(lo+hi)/2;over=pressure(mid)@A>F;hi=np.where(over,mid,hi);lo=np.where(over,lo,mid)
 d=(lo+hi)/2;p=pressure(d);u=np.maximum(d[:,None]+extra,0)
 return dict(pressure=p,glass=p[:,2:]@A[2:]/sum(A[2:])*1000,peak=np.max(np.where(A[None,:]>1e-8,p,0),axis=1)*1000,
  compression=np.max(u,axis=1)/30,closure=d,residual=np.abs(p@A-F),detached=(u<=1e-10)@A/total)
old=list(csv.DictReader((P/'engineering-v20-results/cushion_contact_scenarios.csv').open()))
groups={}
for r in old:groups.setdefault(tuple(float(r[k]) for k in ['arm_centre_mm','arm_width_mm','zone_height_mm']),[]).append(r)
verify=[]
for key,rr in groups.items():
 c=np.array([[float(r[k]) for k in ['force_per_cup_N','assumed_E_MPa','assumed_exponent','assumed_cover_parallel_N_mm3','arm_protrusion_mm','zone_modulus_ratio']] for r in rr])
 s=solve(area(*key),c)
 for j,r in enumerate(rr):
  err=abs(s['glass'][j]/float(r['soft_glasses_kPa'])-1)*100
  verify.append(dict(arm_centre_mm=key[0],arm_width_mm=key[1],zone_height_mm=key[2],exact_area_pressure_kPa=float(s['glass'][j]),midpoint_pressure_kPa=float(r['soft_glasses_kPa']),difference_percent=err,within_chosen_1_percent=err<1))
with (O/'all_v20_exact_area_comparison.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=verify[0]);w.writeheader();w.writerows(verify)
rows=[];summary={};maxres=0.;diagnostics=[]
with (O/'wider_position_scenarios.csv').open('w',newline='') as f:
 fields=['arm_centre_mm','arm_width_mm','zone_height_mm','force_per_cup_N','assumed_E_MPa','exponent','cover_stiffness_N_mm3','protrusion_mm','soft_ratio','local_pressure_change_percent','peak_pressure_change_percent','detached_area_fraction','max_compression_fraction','within_chosen_compression_range']
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for zh,pos,width in itertools.product([12,18,24,32,100],range(-10,41,2),[3,5,8]):
  A=area(pos,width,zh);assert min(A)>-1e-8 and abs(sum(A)-total)<1e-8
  base=solve(A,combos,True);soft=solve(A,combos);eligible=(soft['compression']<=.4)&(base['compression']<=.4)
  local=100*(soft['glass']/base['glass']-1);peak=100*(soft['peak']/base['peak']-1)
  maxres=max(maxres,max(soft['residual']),max(base['residual']))
  rec=summary.setdefault(zh,dict(scenarios=0,eligible=0,local_increases=0,peak_increases=0,detachment_cases=0,max_local_increase_percent=0.))
  rec['scenarios']+=len(combos);rec['eligible']+=int(sum(eligible));rec['local_increases']+=int(sum(eligible&(local>1e-8)));rec['peak_increases']+=int(sum(eligible&(peak>1e-8)));rec['detachment_cases']+=int(sum(eligible&(soft['detached']>1e-8)));rec['max_local_increase_percent']=max(rec['max_local_increase_percent'],float(max(local[eligible],default=0)))
  diagnostics.append(dict(zone=zh,position=pos,width=width,worst_eligible_local_increase=float(max(local[eligible],default=0))))
  for j,c in enumerate(combos):w.writerow(dict(zip(fields,[pos,width,zh,*c,local[j],peak[j],soft['detached'][j],soft['compression'][j],bool(eligible[j])])))
# Analytic and metamorphic controls in addition to force balance.
A=area(15,5,18);c=np.array([[4,.03,1,0,0,1],[4,.03,1,0,2,1],[8,.03,1,0,2,1],[4,.06,1,0,2,1]])
s=solve(A,c);assert abs(s['glass'][0]-4/total*1000)<1e-10
assert s['closure'][2]>s['closure'][1] and s['closure'][3]<s['closure'][1]
controls=dict(exact_annulus_area_mm2=total,force_residual_max_N=maxres,positive_root_brackets=True,uniform_pressure_reference=True,increasing_load_increases_closure=True,increasing_stiffness_reduces_closure=True,
 no_zone_identity_max_error_kPa=float(np.max(abs(solve(A,c)['glass']-solve(A,c,True)['glass']))))
assert controls['no_zone_identity_max_error_kPa']<1e-10 and maxres<1e-9
result=dict(date='2026-10-23',CAD_changed=False,exact_area_comparisons=len(verify),comparisons_exceeding_chosen_1_percent=sum(not r['within_chosen_1_percent'] for r in verify),max_exact_area_difference_percent=max(r['difference_percent'] for r in verify),
 wider_scenario_count=sum(v['scenarios'] for v in summary.values()),position_centres_mm=list(range(-10,41,2)),zone_results=summary,controls=controls,
 scope='Exact area quadrature replaces the V20 grid for this reduced independent-column model. Broader arm heights do not represent a population distribution. No curved head, lateral foam coupling, real cover membrane, mount, acoustic or comfort validation. Detached area in this model is a warning, not measured leakage.',
 sources={'V20_CSV_sha256':hashlib.sha256((P/'engineering-v20-results/cushion_contact_scenarios.csv').read_bytes()).hexdigest()})
dump('contact_envelope.json',result)
fig,ax=plt.subplots(figsize=(9,3.6))
for zh in [12,18,24,32,100]:
 vals=[max(r['worst_eligible_local_increase'] for r in diagnostics if r['zone']==zh and r['position']==pos) for pos in range(-10,41,2)]
 ax.plot(list(range(-10,41,2)),vals,label=f'{zh} mm zone')
ax.set(xlabel='Assumed glasses arm centre above cushion centre mm',ylabel='Worst local pressure increase %',title='Wider positional screen on the same assumed foam model');ax.legend(ncol=5,fontsize=8);ax.grid(alpha=.2)
fig.text(.5,.015,'Calculated cases within chosen 40% compression screen. No measured wearer benefit or leakage result.',ha='center',fontsize=8);fig.tight_layout(rect=[0,.045,1,1]);fig.savefig(P/'documents/images/V21_position_screen.png',dpi=170);plt.close(fig)
print(json.dumps(result,indent=2))
