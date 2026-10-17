"""Known embedded and disjoint volumes test the actual collision query."""
import json
from audit_v14_motion import cad,recipes,O,load,mass,common,moved,rotate,gp_Pnt
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
rows=[]
for row in cad['sizes']:
 p,_=load(row);R=recipes[row['size']]['band_halfspan_mm'];fy=28 if row['size'].startswith('adult') else 20
 cube=BRepPrimAPI_MakeBox(gp_Pnt(R+19.5,fy-2.5,64.5),1,1,1).Shape();fork=p['RightFork'];tests=[('one cubic mm embedded in known prong',fork,cube,1),('known disjoint box',fork,moved(cube,(0,10,0)),0),('embedded pair rotated by sixty degrees',rotate(fork,R,65,60),rotate(cube,R,65,60),1)]
 for label,a,b,expect in tests:
  v=common(a,b);rows.append({'size':row['size'],'test':label,'expected_mm3':expect,'common_mm3':v,'pass':abs(v-expect)<1e-5})
out={'cases':rows,'case_count':len(rows),'all_pass':all(r['pass'] for r in rows),'scope':'Known embedded and disjoint rigid geometry controls; not a proof that every tangential or coincident CAD query is reliable. Coincident independently copied fork comparison still fails and is recorded separately.'};(O/'kernel_controls.json').write_text(json.dumps(out,indent=2));print(json.dumps({'case_count':len(rows),'all_pass':out['all_pass']}))
