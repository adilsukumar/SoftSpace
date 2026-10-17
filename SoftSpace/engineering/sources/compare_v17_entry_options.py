from pathlib import Path
import json,math
P=Path(__file__).parent;O=P/'engineering-v17-results';O.mkdir(exist_ok=True);rows=[]
for layout,radius in [('Child lower',math.sqrt(125)),('Adult upper',12)]:
 for hole in [2.3,2.4,2.5,2.6]:
  radial=(hole-2.2)/2;drift=2*radius*math.sin(math.radians(.1)/2);margin=radial-.025-.1-drift
  rows.append({'layout':layout,'hole_diameter_mm':hole,'nominal_radial_clearance_mm':radial,'nominal_one_sided_index_rotation_deg':math.degrees(2*math.asin(radial/(2*radius))),'illustrative_remaining_margin_mm':margin,'positive_margin_in_chosen_scenario':margin>0})
out={'cases':rows,'comparison_scenario':{'each_diameter_error_bound_mm':.025,'relative_center_error_bound_mm':.1,'angular_error_bound_deg':.1,'meaning':'Chosen comparison inputs, not actual process capability or an approved requirement'},'pilot_choice':'2.5mm straight hole,3.1mm entry mouth,0.3mm entry depth','reason':'Smallest of four tested diameters with positive margin in both layouts under the chosen illustrative bounds. This does not optimize all product requirements.','limits':['Wider hole increases rigid angular play','Entry chamfer cannot overcome insufficient straight-land clearance','Pin housing and cap guides remain unchanged','Chamfer force and spring return need measured friction and actual coil properties','No final dimension or tolerance selected']};(O/'entry_option_comparison.json').write_text(json.dumps(out,indent=2));print(json.dumps(rows,indent=2))
