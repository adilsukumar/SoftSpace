"""Ideal pin, spring, and tolerance calculations; not joint durability validation."""
from pathlib import Path
import json,math,itertools
P=Path(__file__).parent;O=P/'engineering-v12-results';O.mkdir(exist_ok=True)
E=193000;G=78000;yield_ref=965;d=2.2;gap=2;engagement=3;L=gap+engagement/2;r=math.hypot(10,5);rows=[]
for external,lever,diam in itertools.product([2,5,10,20],[50,65,80],[2.19,2.2,2.21]):
 V=external*lever/r;A=math.pi*diam**2/4;I=math.pi*diam**4/64;bend=32*V*L/(math.pi*diam**3);shear=4*V/(3*A);vm=math.sqrt(bend*bend+3*shear*shear)
 rows.append({'external_side_load_N':external,'assumed_arm_mm':lever,'pin_diameter_mm':diam,'pin_reaction_N':V,'unsupported_effective_span_mm':L,'ideal_bending_stress_MPa':bend,'ideal_max_shear_MPa':shear,'combined_nominal_stress_envelope_MPa':vm,'reference_yield_ratio':yield_ref/vm,'ideal_tip_displacement_mm':V*L**3/(3*E*I),'nominal_projected_tongue_bearing_stress_MPa':V/(diam*engagement)})
# Free length21, installed15, released9;14 active and16 total turns, 6 mm mean diameter.
spring=[]
for wire,mean,active,free in itertools.product([.34,.35,.36],[5.9,6,6.1],[13,14,15],[20.5,21,21.5]):
 C=mean/wire;wahl=(4*C-1)/(4*C-4)+.615/C;k=G*wire**4/(8*mean**3*active)
 for length in [15,9]:
  F=k*(free-length);tau=wahl*8*F*mean/(math.pi*wire**3);solid=(active+2)*wire
  spring.append({'wire_diameter_mm':wire,'mean_coil_diameter_mm':mean,'active_turns':active,'free_length_mm':free,'installed_length_mm':length,'stiffness_N_per_mm':k,'ideal_axial_force_N':F,'corrected_nominal_shear_MPa':tau,'reference_static_shear_yield_ratio':(yield_ref/math.sqrt(3))/tau,'nominal_solid_length_mm':solid,'remaining_length_over_solid_mm':length-solid,'coil_outer_diameter_mm':mean+wire,'housing_radial_space_mm':(7-mean-wire)/2})
nominal=[s for s in spring if s['wire_diameter_mm']==.35 and s['mean_coil_diameter_mm']==6 and s['active_turns']==14 and s['free_length_mm']==21]
cad=json.loads((O/'cad_report.json').read_text());minimum_gap=min(min(r['guide_tongue_gaps_mm']) for r in cad['sizes'])
tol={'guide_minimum_nominal_gap_mm':minimum_gap,'assumed_body_surface_error_each_mm':.2,'gap_after_worst_relative_closure_mm':minimum_gap-.4,'pin_diameter_mm':[2.19,2.21],'finished_bore_diameter_mm':[2.28,2.32],'diametral_lock_clearance_mm':[2.28-2.21,2.32-2.19],'limits':'Body surface error and finished pin/bore limits are design assumptions. Factory capability, coatings, dirt, wear, thermal and alignment variation are not validated.'}
out={'status':'complete conditional component screen','pin_cases':rows,'pin_case_count':len(rows),'spring_cases':spring,'spring_case_count':len(spring),'nominal_spring_cases':nominal,'tolerance_budget':tol,'source':'https://www.ulbrich.com/uploads/data-sheets/301-Stainless-Steel-Wire-UNS-S30100-Wire.pdf','reference_properties':{'E_MPa':E,'G_MPa':G,'full_hard_wire_published_yield_reference_MPa':yield_ref},'limits':['Published wire data do not qualify the final manufactured pin or spring; selected stock, temper, forming and processing must be verified','External loads and lever arms are illustrative and are not measured head or drop loads','Pin treated as an ideal cantilever with a resultant at the engagement midpoint; bearing distributions and support flexibility omitted','Combining maximum beam bending and shear is a conservative nominal envelope, not a resolved stress field or bearing contact peak','Spring uses a Wahl-corrected elastic coil equation; no fatigue, set, buckling, friction, end-seat or rubbing calculation','Spring bodies in CAD reserve the envelope, not actual wire end geometry','Return force must exceed measured friction; it is not known that this spring reliably engages','No physical strength, lifetime, drop or wearer-safety pass']}
(O/'pin_spring_screen.json').write_text(json.dumps(out,indent=2));print(json.dumps({'pin_cases':len(rows),'spring_cases':len(spring),'nominal_spring':nominal,'tolerance':tol},indent=2))
