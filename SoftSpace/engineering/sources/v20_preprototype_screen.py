"""Bounded, reproducible pre-prototype screens. No measured Sony geometry or product validation."""
from pathlib import Path
import sys, os, json, csv, hashlib, math, itertools, platform
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'solver-libraries'))
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=P/'engineering-v20-results';O.mkdir(exist_ok=True)
I=P/'documents/images';I.mkdir(exist_ok=True)
DATE='2026-10-21'
def write(name,obj): (O/name).write_text(json.dumps(obj,indent=2),encoding='utf-8')
def csvout(name,rows):
 with (O/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
sources=[
 dict(id='BW',url='https://www.brainwavzaudio.com/collections/on-sale/products/replacement-earpads-for-sony-wh-xb900n-headphones',checked=DATE,kind='Manufacturer of aftermarket compatible pads',facts={'outer_height_mm':100,'outer_width_mm':80,'thickness_mm':30,'compatibility_includes':'Sony WH-CH720N','mount':'Existing mounting groove'},limits='These are aftermarket pad dimensions and a compatibility claim. Not Sony OEM dimensions, tolerances, opening or mounting groove metrology. Manufacturer mentions a few mm size variation without a numeric tolerance.'),
 dict(id='SONY',url='https://www.sony.co.uk/electronics/support/wireless-headphones-bluetooth-headphones/articles/00295193',checked=DATE,kind='Sony replacement instructions',facts={'mount':'Tuck into groove, with top and bottom slot/arrow alignment'},limits='No dimensioned mounting drawing found here. Do not import the six-claw mounting instructions for other Sony models.'),
 dict(id='SERVICE',url='https://partstore.encompass.com/shop/model_research_docs/?file=/SON/rr/WHCH720N_L.pdf',checked=DATE,kind='Sony repair reference hosted by parts distributor',facts={'document_pages':2},limits='Exploded/repair reference is not a dimensioned pad manufacturing drawing. Not used as a scale drawing.'),
 dict(id='HELP',url='https://helpguide.sony.net/mdr/2966/v1/en/print.pdf',checked=DATE,kind='Sony user help guide',facts={'model':'WH-CH720N / YY2966'},limits='Operating instructions, not pad CAD or measured mounting geometry.')]
params=dict(revision='SoftSpace Flex V20 reference pad body',standalone_revision='SoftSpace V19 unchanged',date=DATE,units='mm N MPa',source_ids=['BW','SONY'],published_aftermarket_envelope_mm=[80,100,30],assumed_opening_mm=[50,70],assumed_cover_mm=.35,soft_zone_vertical_centre_mm=15,soft_zone_height_mm=18,attachment='Tuck-in mounting approach from Sony instructions; precise skirt and groove intentionally not released',measured_Sony_dimensions=False,manufacturing_release=False)
write('internet_sources.json',sources);write('design_parameters.json',params)

# Discrete area integration on the prescribed annular face; independent material columns.
def areas(n=500, zone_height=18, arm_centre=15, arm_width=5):
 dx=80/n;dy=100/n;x=-40+(np.arange(n)+.5)*dx;y=-50+(np.arange(n)+.5)*dy
 X,Y=np.meshgrid(x,y);ring=(X/40)**2+(Y/50)**2<=1
 ring &= (X/25)**2+(Y/35)**2>=1
 zone=(X>0)&(abs(Y-15)<=zone_height/2)
 glass=(X>0)&(abs(Y-arm_centre)<=arm_width/2)
 return np.array([np.count_nonzero(ring&~zone&~glass),np.count_nonzero(ring&zone&~glass),np.count_nonzero(ring&~zone&glass),np.count_nonzero(ring&zone&glass)])*dx*dy

def equilibrium(A,F,E,ratio,exponent,kcover,protrusion):
 # Pressure in MPa = E*(compression/thickness)^n + kcover*compression.
 # This assumed law is not fitted to a named foam. Cover term is an artificial parallel stiffness bracket.
 mod=E*np.array([1,ratio,1,ratio]);extra=np.array([0,0,protrusion,protrusion])
 def pressure(d):
  u=np.maximum(d+extra,0)
  return mod*(u/30)**exponent+kcover*u
 lo=-protrusion;hi=30
 for _ in range(65):
  mid=(lo+hi)/2
  if A@pressure(mid)>F:hi=mid
  else:lo=mid
 d=(lo+hi)/2;p=pressure(d);garea=A[2:].sum()
 return dict(closure_mm=float(d),local_glasses_mean_kPa=float(A[2:]@p[2:]/garea*1000) if garea else 0,other_mean_kPa=float(A[:2]@p[:2]/A[:2].sum()*1000),max_compression_fraction=float(max(np.maximum(d+extra,0))/30),force_residual_N=float(abs(A@p-F)))

rows=[]
geometry={(pos,width,zh):areas(500,zh,pos,width) for pos,width,zh in itertools.product([8,15,24],[3,5,8],[12,18,24,32])}
for (pos,width,zh),A in geometry.items():
 for F,E,n,kc,th,ratio in itertools.product([2,4,8],[.01,.03,.1],[1,2],[0,.0002,.001],[1,2,4],[.25,.5]):
  base=equilibrium(A,F,E,1,n,kc,th);soft=equilibrium(A,F,E,ratio,n,kc,th)
  rows.append(dict(arm_centre_mm=pos,arm_width_mm=width,zone_height_mm=zh,force_per_cup_N=F,assumed_E_MPa=E,assumed_exponent=n,assumed_cover_parallel_N_mm3=kc,arm_protrusion_mm=th,zone_modulus_ratio=ratio,baseline_glasses_kPa=base['local_glasses_mean_kPa'],soft_glasses_kPa=soft['local_glasses_mean_kPa'],local_change_percent=100*(soft['local_glasses_mean_kPa']/base['local_glasses_mean_kPa']-1),baseline_other_kPa=base['other_mean_kPa'],soft_other_kPa=soft['other_mean_kPa'],closure_mm=soft['closure_mm'],max_compression_fraction=soft['max_compression_fraction'],force_residual_N=soft['force_residual_N'],outside_small_compression_screen=soft['max_compression_fraction']>.4))
csvout('cushion_contact_scenarios.csv',rows)

# Verification controls for this reduced model, not a skin-contact validation.
A=areas(800);analytic_area=math.pi*(40*50-25*35)
ctrl=equilibrium(A,4,.03,1,1,0,0)
exact=4/A.sum()*1000
assert abs(ctrl['local_glasses_mean_kPa']-exact)<1e-10
assert abs(ctrl['closure_mm']-4*30/(A.sum()*.03))<1e-10
identity=equilibrium(A,4,.03,1,2,.0002,2)
checks=dict(uniform_pressure_error_kPa=abs(ctrl['local_glasses_mean_kPa']-exact),force_balance_max_N=max(r['force_residual_N'] for r in rows),area_error_percent=abs(A.sum()/analytic_area-1)*100,identical_material_identity='Same function and ratio 1; no invented improvement',status='pass')
assert checks['force_balance_max_N']<1e-9 and checks['area_error_percent']<.1
refine=[]
for ngrid in [160,320,640]:
 ar=areas(ngrid);s=equilibrium(ar,4,.03,.25,2,.0002,2);refine.append(dict(grid=ngrid,area_mm2=float(ar.sum()),pressure_kPa=s['local_glasses_mean_kPa']))
checks['area_integration_refinement']=refine;checks['last_pressure_change_percent']=abs(refine[-1]['pressure_kPa']/refine[-2]['pressure_kPa']-1)*100
checks['chosen_2_percent_integration_comparison_pass']=checks['last_pressure_change_percent']<2
write('contact_controls.json',checks)
eligible=[r for r in rows if not r['outside_small_compression_screen']]
summary=dict(date=DATE,paired_scenarios=len(rows),within_chosen_40_percent_compression_screen=len(eligible),outside_chosen_compression_screen=len(rows)-len(eligible),eligible_local_change_percent_range=[min(r['local_change_percent'] for r in eligible),max(r['local_change_percent'] for r in eligible)],eligible_cases_local_pressure_increased=sum(r['local_change_percent']>1e-8 for r in eligible),all_cases_local_pressure_increased=sum(r['local_change_percent']>1e-8 for r in rows),scope='Four-area, independent-column assumed-foam model at fixed per-cup force. No lateral foam coupling, curved head, real cover membrane, skin, glasses bending or actual Sony headband force. Cases above 40% compression are flagged outside the chosen small-compression screen. Percentages are conditional model changes, not probabilities or comfort improvements.',physical_measurements=0)
summary['zone_comparisons']=[dict(zone_height_mm=h,paired_scenarios=sum(r['zone_height_mm']==h for r in rows),eligible_pressure_increases=sum(r['zone_height_mm']==h and r['local_change_percent']>1e-8 for r in eligible),scope='Within listed arm positions and widths only') for h in [12,18,24,32]]
write('contact_summary.json',summary)

# Steady slit-flow sensitivity, not broadband sound isolation or ANC.
leak=[]
for gap in [.025,.05,.1,.2,.4,.8]:
 mu=1.81e-5;w=.005;L=.015;h=gap/1000
 conductance=w*h**3/(12*mu*L)
 leak.append(dict(assumed_gap_mm=gap,conductance_m3_Pa_s=conductance,relative_to_005mm=(gap/.05)**3,scope='Steady incompressible laminar rectangular slit approximation; no acoustic dB or ANC prediction'))
csvout('open_slit_flow_sensitivity.csv',leak)

# Worst-case arithmetic, no distribution or reliability percentage.
torque=json.loads((P/'engineering-v18-results/torque_and_mass.json').read_text());radius=torque['effective_radius_mm'];moment=max(r['maximum_gravity_moment_over_orientation_Nmm'] for r in torque['mass_cases'])
hinge=[]
for preload,mu,g in itertools.product([80,140,200,236],[.1,.2,.3],[1,2,3]):
 hold=2*mu*preload*radius;demand=g*moment
 hinge.append(dict(assumed_preload_N=preload,assumed_mu=mu,equivalent_static_g=g,holding_torque_Nmm=hold,demand_Nmm=demand,margin_Nmm=hold-demand,arithmetic_margin_nonnegative=hold>=demand))
csvout('hinge_uncertainty_scenarios.csv',hinge)
fits=[]
for pin_error,bore_error,axis,finish in itertools.product([.03,.1,.2],[.03,.1,.2],[.02,.04,.08],[0,.02]):
 rem=(4.3-bore_error-4-pin_error)/2-axis-finish
 fits.append(dict(pin_oversize_mm=pin_error,bore_undersize_mm=bore_error,axis_error_mm=axis,radial_finish_or_growth_mm=finish,remaining_radial_mm=rem,positive_margin=rem>0))
csvout('pivot_tolerance_scenarios.csv',fits)
write('mechanical_summary.json',dict(hinge_scenarios=len(hinge),negative_holding_margin=sum(not r['arithmetic_margin_nonnegative'] for r in hinge),fit_scenarios=len(fits),nonpositive_fit_margin=sum(not r['positive_margin'] for r in fits),scope='Assumed worst-case combinations. Not supplier capability, real spring calibration, drop dynamics, fatigue or reliability statistics. V19 geometry unchanged.'))

plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(1,2,figsize=(11,4.3))
for kc in [0,.0002,.001]:
 subset=[r for r in rows if r['arm_centre_mm']==15 and r['arm_width_mm']==5 and r['zone_height_mm']==18 and r['assumed_E_MPa']==.03 and r['assumed_exponent']==2 and r['arm_protrusion_mm']==2 and r['zone_modulus_ratio']==.25 and r['assumed_cover_parallel_N_mm3']==kc]
 ax[0].plot([r['force_per_cup_N'] for r in subset],[r['local_change_percent'] for r in subset],marker='o',label=f'Cover stiffness {kc:g}')
ax[0].axhline(0,color='#777',lw=.8);ax[0].set(xlabel='Assumed force per cup N',ylabel='Local mean pressure change %',title='Selected assumed foam cases');ax[0].legend(fontsize=8)
ax[1].plot([r['assumed_gap_mm'] for r in leak],[r['relative_to_005mm'] for r in leak],marker='o',color='#aa6441');ax[1].set(xlabel='Assumed open slit height mm',ylabel='Relative steady airflow conductance',yscale='log',title='Why an open glasses slot is risky')
fig.suptitle('V20 conditional design screens',fontsize=15);fig.text(.5,.015,'Calculated illustrations from saved CSVs. No measured comfort, sealing, sound reduction or ANC result.',ha='center',fontsize=9);fig.tight_layout(rect=[0,.06,1,.93]);fig.savefig(I/'V20_screens.png',dpi=170);plt.close(fig)
fig,ax=plt.subplots(1,2,figsize=(11,4.1))
for mu in [.1,.2,.3]:
 sub=[r for r in hinge if r['assumed_mu']==mu and r['equivalent_static_g']==2]
 ax[0].plot([r['assumed_preload_N'] for r in sub],[r['margin_Nmm'] for r in sub],marker='o',label=f'Assumed friction {mu}')
ax[0].axhline(0,color='#777');ax[0].set(xlabel='Assumed preload N',ylabel='Margin at equivalent static 2g Nmm',title='Hinge setting needs a bench measurement');ax[0].legend(fontsize=8)
ax[1].hist([r['remaining_radial_mm'] for r in fits],bins=16,color='#6c9e91');ax[1].axvline(0,color='#ab553f');ax[1].set(xlabel='Remaining radial clearance mm',ylabel='Scenario count',title='Tolerance scenarios include binding risks')
fig.text(.5,.015,'Scenario counts are not real-world probabilities. No impact, wear or manufactured-fit validation.',ha='center',fontsize=9);fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(I/'V20_mechanics.png',dpi=170);plt.close(fig)
write('environment.json',dict(date=DATE,python=sys.version,platform=platform.platform(),numpy=np.__version__,matplotlib=matplotlib.__version__,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),physical_tests=0))
print(json.dumps(dict(contact=summary,controls=checks),indent=2),flush=True)
