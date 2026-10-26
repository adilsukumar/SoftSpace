"""Manufacturer-data screening, not validated worn-pad or clinical performance."""
from pathlib import Path
import os,sys,json,math,csv,itertools,hashlib,re
P=Path(__file__).resolve().parent;O=P/'material-screen-2026-10-26';sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq
import pypdfium2 as pdfium
names=['CF-40M','CF-40AC','CF-42M','CF-42AC','CF-45M','CF-45AC','CF-47M','CF-47AC']
values=np.array([[1.4,1.5,2.1,2.2,3.1,3.9,3.9,4.8],[1.8,2.0,2.8,2.9,4.2,5.0,5.6,6.9],[2.,2.3,3.,3.2,4.5,5.3,5.9,7.2],[2.3,2.6,3.4,3.7,5.,5.9,6.5,7.9],[2.9,3.2,4.1,4.4,5.9,7.,7.6,9.3],[3.5,4.4,5.4,5.9,7.7,9.1,9.8,12.],[6.,7.5,8.8,9.8,12.,15.,16.,20.],[16.,20.,23.,25.,32.,36.,40.,49.]])
strain=np.arange(1,9)/10
pdf=pdfium.PdfDocument(str(O/'Trelleborg_Confor.pdf'));text=re.sub(r'\s+',' ',pdf[0].get_textpage().get_text_range());parsed=[]
for pct in range(10,81,10):
 a=text.index(f'Force @ {pct}% Compression');b=text.index(f'Force @ {pct+10}% Compression',a) if pct<80 else text.index('ASTM D 3574C',a)
 nums=[float(x) for x in re.findall(r'([0-9]+(?:\.[0-9]+)?)\s*\(',text[a:b])];assert len(nums)==8,(pct,nums);parsed.append(nums)
assert np.array_equal(values,np.array(parsed));assert np.all(np.diff(values,axis=0)>0)
curves={name:PchipInterpolator(strain,values[:,i],extrapolate=False) for i,name in enumerate(names)}
assert all(np.isnan(c(.05)) and np.isnan(c(.85)) for c in curves.values())
materials=dict(date='2026-10-26',source='Trelleborg_Confor',source_pdf_sha256=hashlib.sha256((O/'Trelleborg_Confor.pdf').read_bytes()).hexdigest(),grades={n:dict(strain_fraction=strain.tolist(),compression_stress_kPa=values[:,i].tolist(),density_kg_m3=96,thermal_conductivity_W_mK=.04) for i,n in enumerate(names)},method='ASTM D3574C modified; 12.7 mm specimen; compression rate 5.1 mm/min. CFD temperature and humidity not separately specified on the CFD row.',scope='Typical loading points only, not unloading, creep, complete viscoelastic law, cover, bonding, acoustic impedance or finished pad calibration. No extrapolation below10 or above80 percent. No equivalence to the existing 30 mm CAD assumed.')
(O/'material_curves.json').write_text(json.dumps(materials,indent=2))
# Analytic ellipse-strip areas for a declared flat annulus, matching V20 assumed face.
def ellipse_strip(a,b,lo,hi):
 lo=max(-b,min(b,lo));hi=max(-b,min(b,hi))
 def primitive(y):u=y/b;return .5*a*b*(math.asin(u)+u*math.sqrt(max(0.,1-u*u)))
 return primitive(hi)-primitive(lo)
def right_ring_strip(lo,hi):return ellipse_strip(40,50,lo,hi)-ellipse_strip(25,35,lo,hi)
total=math.pi*(40*50-25*35);zone=right_ring_strip(6,24);glass=right_ring_strip(12.5,17.5);areas=np.array([total-zone,zone-glass,0.,glass]);assert abs(areas.sum()-total)<1e-10 and min(areas)>=0
T=12.7

def solve(main,soft,F,h):
 extra=np.array([0.,0.,h,h]);lo=.1*T;hi=.8*T-h
 def pressures(d):
  e=np.clip((d+extra)/T,.1,.8)
  return np.array([curves[main](e[0]),curves[soft](e[1]),curves[main](e[2]),curves[soft](e[3])],float)
 def load(d):return float(areas@pressures(d)/1000)
 low,high=load(lo),load(hi)
 if F<low-1e-12:return dict(status='Below supported common strain window',lower_domain_force_N=low,upper_domain_force_N=high)
 if F>high+1e-12:return dict(status='Above supported common strain window',lower_domain_force_N=low,upper_domain_force_N=high)
 left,right=lo,hi
 for _ in range(65):
  mid=(left+right)/2
  if load(mid)<F:left=mid
  else:right=mid
 d=(left+right)/2;independent=brentq(lambda x:load(x)-F,lo,hi,xtol=1e-12);p=pressures(d)
 return dict(status='Solved within sourced strain window',closure_mm=d,maximum_strain_fraction=(d+h)/T,glasses_region_pressure_kPa=float(p[3]),other_region_mean_kPa=float(areas[:2]@p[:2]/areas[:2].sum()),force_error_N=abs(load(d)-F),independent_closure_error_mm=abs(d-independent),lower_domain_force_N=low,upper_domain_force_N=high)
rows=[];base={};identity=0.;uniform_pressure_error=0.
for main,soft,F,h in itertools.product(names,names,[2,4,8,12,16,24],[0.,.5,1.]):
 key=(main,F,h)
 if key not in base:base[key]=solve(main,main,F,h)
 b=base[key];r=solve(main,soft,F,h);row=dict(main_grade=main,zone_grade=soft,assumed_force_per_face_N=F,assumed_arm_protrusion_mm=h,reference_thickness_mm=T,**r,baseline_status=b['status'])
 if r['status'].startswith('Solved') and b['status'].startswith('Solved'):
  row['baseline_glasses_pressure_kPa']=b['glasses_region_pressure_kPa'];row['local_pressure_change_percent']=100*(r['glasses_region_pressure_kPa']/b['glasses_region_pressure_kPa']-1)
  if main==soft:identity=max(identity,abs(row['local_pressure_change_percent']))
 if r['status'].startswith('Solved') and main==soft and h==0:uniform_pressure_error=max(uniform_pressure_error,abs(r['glasses_region_pressure_kPa']-F/total*1000))
 rows.append(row)
with (O/'scenarios.csv').open('w',newline='',encoding='utf-8') as f:
 keys=list(dict.fromkeys(k for r in rows for k in r));w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
solved=[r for r in rows if r['status'].startswith('Solved')];paired=[r for r in rows if 'local_pressure_change_percent' in r];controls=dict(source_64_points_match_independent_PDF_text_parse=True,manual_page_visual_check=True,monotone_source_curves=True,no_extrapolation=True,exact_ellipse_area_sum_error_mm2=abs(areas.sum()-total),equal_material_identity_error_percent=identity,uniform_pressure_error_kPa=uniform_pressure_error,maximum_force_error_N=max(r['force_error_N'] for r in solved),maximum_independent_closure_error_mm=max(r['independent_closure_error_mm'] for r in solved))
assert controls['maximum_force_error_N']<1e-9 and controls['maximum_independent_closure_error_mm']<1e-8 and identity<1e-10 and uniform_pressure_error<1e-10
summary=dict(date='2026-10-26',scenario_count=len(rows),solved_within_source_domain=len(solved),outside_supported_domain=len(rows)-len(solved),paired_comparisons=len(paired),paired_local_pressure_increases=sum(r['local_pressure_change_percent']>1e-8 for r in paired),paired_local_pressure_decreases=sum(r['local_pressure_change_percent']<-1e-8 for r in paired),paired_identical=sum(abs(r['local_pressure_change_percent'])<=1e-8 for r in paired),controls=controls,geometry=dict(outer_mm=[80,100],assumed_opening_mm=[50,70],area_mm2=total,four_group_areas_mm2=areas.tolist(),zone_centre_mm=15,zone_height_mm=18,arm_centre_mm=15,arm_width_mm=5),reference_thickness_mm=T,assumed_forces_N=[2,4,8,12,16,24],assumed_arm_protrusions_mm=[0,.5,1],physical_measurements=0,full_product_validation=False,scope='Uncovered flat annulus independent-column reference with manufacturer loading points. Same 12.7 mm specimen thickness; not existing 30 mm CAD, worn head, membrane, skin, friction, glasses bending, actual headband force, leak, acoustics, comfort or Sony mounting validation.')
(O/'summary.json').write_text(json.dumps(summary,indent=2))
# Same-grade uniform force bounds are a screen, not a head-force recommendation.
bounds=[dict(grade=n,force_at_10pct_N=float(values[0,i]*total/1000),force_at_20pct_N=float(values[1,i]*total/1000),force_at_40pct_N=float(values[3,i]*total/1000),thermal_conductivity_W_mK=.04) for i,n in enumerate(names)]
(O/'uniform_bounds.json').write_text(json.dumps(bounds,indent=2))
rogers=dict(source='Rogers_4701_40_battery',grade='PORON 4701-40 battery pad formulation 240 kg/m3',published_thickness_mm=[1.4,3.0],strain_fraction=[.2,.25,.3,.4,.5,.6,.7],compression_stress_kPa=[40.6,44.5,49.1,60.8,81.5,127,264],force_at_20pct_on_same_assumed_annulus_N=40.6*total/1000,scope='Separate thin battery pad formulation and test data. Not a 12.7 or 30 mm headphone pad. Not combined with generic PORON page or ISO values.')
(O/'rogers_comparison.json').write_text(json.dumps(rogers,indent=2))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,axes=plt.subplots(1,2,figsize=(10,4.2))
for n in names:axes[0].plot(strain*100,curves[n](strain),marker='o',ms=3,label=n)
axes[0].set(xlabel='Compression percent',ylabel='Typical loading stress kPa',title='Named Confor grade inputs');axes[0].legend(fontsize=7,ncol=2)
for n in ['CF-40M','CF-42M','CF-45M','CF-47M']:
 sub=[r for r in rows if r['main_grade']==n and r['zone_grade']==n and r['assumed_arm_protrusion_mm']==0 and r['status'].startswith('Solved')];axes[1].plot([r['assumed_force_per_face_N'] for r in sub],[r['closure_mm'] for r in sub],marker='o',label=n)
axes[1].set(xlabel='Assumed uniform force N',ylabel='Calculated compression mm',title='12.7 mm uncovered ring reference');axes[1].legend(fontsize=8)
fig.text(.5,.01,'Manufacturer typical loading points with PCHIP interpolation only in the sourced range. No comfort or seal validation.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.05,1,1));fig.savefig(P/'documents/images/Material_loading_screen_20261026.png',dpi=160);plt.close(fig)
(O/'README.md').write_text('''# Named foam loading screen 26 October 2026

Eight Confor grades now have traceable tabulated loading points from the Trelleborg manufacturer sheet. The 64 entered values were visually checked and independently matched to PDF text. Density and thermal conductivity are retained as typical inputs. This supplies a loading curve input for a limited screen, not a complete calibrated viscoelastic material law.

The calculation uses a flat uncovered annulus of outside 80 by 100 mm and assumed opening 50 by 70 mm, with a 12.7 mm reference thickness matching the source specimen. The soft zone and glasses strips are declared in summary.json. All 1152 grade-pair/force/protrusion cases are retained. PCHIP interpolation is allowed only at 10 to 80 percent compression. Requests outside the common supported strain window are flagged instead of extrapolated. Only cases with both baseline and zone solutions are compared. Numerical controls include force balance, independent root solving, exact areas, equal-material identity and uniform-pressure identity.

The source is typical loading data for a modified specimen test at 5.1 mm/min, not guaranteed limits, unloading or recovery, dynamic behaviour, cover seams, friction, acoustic impedance, heat/moisture behaviour or actual pad fit. No equivalence to the existing 30 mm CAD is asserted. Forces are sensitivity inputs, not wearer recommendations. Grade-pair changes in local pressure are conditional model outputs, not comfort or pain-relief percentages.

A separate Rogers battery-pad formulation has multi-point data but is supplied at 1.4 to 3 mm thickness and much higher listed compression stresses. It must not be silently used as the generic PORON curve or a thick headphone cushion. PDFs and page renders are retained locally for source QA; publish URLs, hashes and extracted factual inputs, not the manufacturer PDFs. Full product validation and Sony mounting remain open.
''',encoding='utf-8')
print({k:summary[k] for k in ['scenario_count','solved_within_source_domain','outside_supported_domain','paired_comparisons','paired_local_pressure_increases','paired_local_pressure_decreases','paired_identical']});print(controls);print(bounds[:2]);print('Rogers reference force',rogers['force_at_20pct_on_same_assumed_annulus_N'])
