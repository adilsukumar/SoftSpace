"""Source-specific reference calculations; no purchased material qualification."""
import json,csv,math,sys,os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v16-results';O.mkdir(exist_ok=True)
basf='https://download.basf.com/p1/8a8081c57fd4b609017fd636717a3e69/en/ULTRAMID%253Csup%253E%25C2%25AE%253Csup%253E_B3S_Product_Data_Sheet_Asia_PacificEurope_English.pdf%3Fview'
foam_source='https://www.rogerscorp.com/-/media/project/rogerscorp/documents/elastomeric-material-solutions/poron/english/data-sheets/17-388-ideal-cfd-curves-for-battery-pad-applications-poron-4701-30-very-soft.pdf'
reference=json.loads((P/'engineering-v11-results/materials_screen.json').read_text());pom=next(r for r in reference['numeric_grades'] if r['grade']=='TECAFORM AH natural POM C')
grades=[{'grade':'Ultramid B3S dry reference','E_MPa':3500,'typical_yield_MPa':90,'source':basf},{'grade':'Ultramid B3S conditioned reference','E_MPa':1200,'typical_yield_MPa':45,'source':basf},{'grade':pom['grade'],'E_MPa':pom['modulus_MPa'],'typical_yield_MPa':pom['typical_yield_MPa'],'source':'V11 saved Ensinger source; not remeasured or certified material'}]
r=math.sqrt(125);edge=16-r-1.15;plate=[]
for grade in grades:
 for force in [.5,2,5,10,20]:
  reaction=force*65/r;bearing=reaction/(2.2*3);ligament=reaction/(3*edge)
  for concentration in [1,2,3]:
   proxy=max(bearing,ligament)*concentration;plate.append({'grade':grade['grade'],'illustrative_side_force_N':force,'assumed_force_arm_mm':65,'pin_force_N':reaction,'nominal_bearing_MPa':bearing,'single_minimum_ligament_nominal_MPa':ligament,'assumed_peak_multiplier':concentration,'peak_proxy_MPa':proxy,'reference_yield_over_two_times_proxy':grade['typical_yield_MPa']/(2*proxy)})
pull=[]
R=1.1;a=.425;net=math.pi*R*R-2*(a*math.sqrt(R*R-a*a)+R*R*math.asin(a/R))
for force in [2,10,20,50,100]:
 for concentration in [1,2,3]:pull.append({'external_pull_N':force,'exact_central_net_area_mm2':net,'assumed_peak_multiplier':concentration,'required_pin_yield_for_factor_two_MPa':2*force/net*concentration,'nominal_rivet_double_shear_MPa':force/(2*math.pi*.8**2/4),'nominal_pin_hole_bearing_MPa':force/(.8*2.2),'limits':'Net area is exact at central cut only. Stress factor assumed; no three-dimensional hole bending, contact, forming or fatigue solve.'})
curves=[{'density_kg_m3':240,'strain':[.2,.25,.3,.4,.5,.6,.7],'stress_kPa':[19.4,21.6,24.1,30.7,42.1,68.3,149.0],'published_sheet_thickness_mm':[1.3,3.0]},{'density_kg_m3':320,'strain':[.2,.25,.3,.4,.5,.6,.7],'stress_kPa':[34.1,38.3,42.9,55.2,77.6,136,345],'published_sheet_thickness_mm':[.85,3.0]}]
foam=[]
for c in curves:
 for area in [50,100,3000]:
  for force in [.5,1,2,5,10,20]:
   stress=force/area*1000;strain=None
   if c['stress_kPa'][0]<=stress<=c['stress_kPa'][-1]:
    for i in range(6):
     if c['stress_kPa'][i]<=stress<=c['stress_kPa'][i+1]:
      fraction=(stress-c['stress_kPa'][i])/(c['stress_kPa'][i+1]-c['stress_kPa'][i]);strain=c['strain'][i]+fraction*(c['strain'][i+1]-c['strain'][i]);break
   foam.append({'density_kg_m3':c['density_kg_m3'],'assumed_flat_loaded_area_mm2':area,'force_N':force,'stress_kPa':stress,'interpolated_strain':strain,'within_published_20_to_70percent_range':strain is not None})
out={'updated':'2026-10-15','revision':'V16 reference material calculations','grade_references':grades,'PA6_conditioned_to_dry_modulus_ratio':1200/3500,'plate_cases':plate,'plate_case_count':len(plate),'minimum_radial_hole_edge_ligament_mm':edge,'pin_pull_cases':pull,'pin_pull_case_count':len(pull),'foam_source':foam_source,'foam_published_curves':curves,'foam_flat_cases':foam,'foam_case_count':len(foam),'foam_interpolated_case_count':sum(x['within_published_20_to_70percent_range'] for x in foam),'limits':['Plate screen is a nominal bearing/minimum-ligament proxy with chosen multipliers, not resolved FE or validated strength','Typical datasheet yields are references, not production allowables. No grade is qualified or selected','Pin cross-hole net area and rivet shear do not solve actual combined hinge loading, contact, fatigue or rivet forming','Published thin battery-pad PORON grades differ from a20mm shaped ear cushion. No thickness layering or low-pressure extrapolation','Flat foam points omit cover tension, head geometry, glasses, friction, acoustic leakage and perceived comfort','No physical test or all-material pass']}
(O/'materials_reference_screen.json').write_text(json.dumps(out,indent=2))
sys.path.insert(0,str(P/'solver-libraries'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(9,4.5))
for c in curves:ax.plot([100*x for x in c['strain']],c['stress_kPa'],'o-',label=str(c['density_kg_m3'])+' kg per cubic metre')
ax.set_xlabel('Compression percent');ax.set_ylabel('Published compressive stress kPa');ax.grid(alpha=.25);ax.legend();ax.set_title('Published thin PORON battery pad reference curves');fig.text(.5,.025,'Rogers Publication 17-388. Data cover 20 to 70 percent compression of 0.85 to 3 mm sheets; not measured headphone cushions.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.07,1,1));fig.savefig(P/'documents/images/V16_foam_reference.png',dpi=160,facecolor='white');plt.close(fig)
print(json.dumps({'plate_cases':len(plate),'pull_cases':len(pull),'foam_cases':len(foam),'within_foam_data_range':out['foam_interpolated_case_count'],'no_material_qualified':True}))
