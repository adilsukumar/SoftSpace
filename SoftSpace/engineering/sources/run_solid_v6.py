from solid_band_3d import run,OUT
import json,traceback
report={'status':'running','model':'Quadratic-tetrahedron linear elastic CAD crown and guide housing only','cases':[],
 'limitations':['Assumed E=2000 MPa, nu=.35; no measured modulus or strength allowable','2 N per side transferred directly to housing bottom at z80; sliders/forks/clamps excluded','Ideal symmetry and one vertical datum, no skin/crown contact','Small-strain, small-displacement formulation; finite rotations not solved','Centroid stress maxima can depend on sharp housing corners; not failure/fatigue certification']}
try:
 report['verification']=run('verification_beam',1.5,True)
 for size in ['child_small','child_medium','child_large','adult_small','adult_medium','adult_large']:
  cases=[run(size,h) for h in [5,3]]
  change=abs(cases[1]['guide_mean_x_displacement_mm']/cases[0]['guide_mean_x_displacement_mm']-1)
  stress=abs(cases[1]['max_von_mises_centroid_MPa']/cases[0]['max_von_mises_centroid_MPa']-1)
  report['cases'].append({'size':size,'meshes':cases,'guide_deflection_mesh_change':change,'centroid_peak_stress_mesh_change':stress,'deflection_mesh_gate_5pct':change<.05,'stress_mesh_gate_5pct':stress<.05})
  json.dump(report,open(OUT/'solid_3d_summary.json','w'),indent=2)
 report['status']='complete'
except Exception:report['status']='error';report['error']=traceback.format_exc();print(report['error'])
json.dump(report,open(OUT/'solid_3d_summary.json','w'),indent=2)
