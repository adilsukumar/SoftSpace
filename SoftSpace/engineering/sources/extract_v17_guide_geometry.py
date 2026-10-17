import json
from audit_v14_motion import P,load,recipes,bounds
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.GeomAbs import GeomAbs_Cylinder
O=P/'engineering-v17-results';rows=[]
for size in ['child_large','adult_small']:
 row=json.loads((O/(size+'_Entry25_cad_report.json')).read_text());parts,_=load(row);R=recipes[size]['band_halfspan_mm'];upper=row['layout'].startswith('upper');x=R if upper else R+10;z=77 if upper else 60;shift=-8 if upper else 0;guides={}
 for name in ['RightFork','RightServiceCap']:
  intervals=[];e=TopExp_Explorer(parts[name],TopAbs_FACE)
  while e.More():
   face=TopoDS.Face_s(e.Current());a=BRepAdaptor_Surface(face)
   if a.GetType()==GeomAbs_Cylinder:
    c=a.Cylinder();loc=c.Axis().Location();direction=c.Axis().Direction()
    if abs(c.Radius()-1.15)<1e-6 and abs(loc.X()-x)<1e-4 and abs(loc.Z()-z)<1e-4 and abs(abs(direction.Y())-1)<1e-5:
     b=bounds(face);intervals.append([b[1]-shift,b[4]-shift])
   e.Next()
  assert intervals,(size,name);guides[name]=intervals
 rows.append({'size':size,'source':row['file'],'source_sha256':row['sha256'],'front_intervals_relative_y_mm':guides['RightFork'],'rear_intervals_relative_y_mm':guides['RightServiceCap'],'relative_load_location_mm':-6.35,'pin_radius_mm':1.1,'guide_radius_mm':1.15,'meaning':'Cylinder intervals extracted from original saved solids. Adult translated8mm to common local coordinates.'})
(O/'pin_guide_geometry.json').write_text(json.dumps({'rows':rows},indent=2));print(json.dumps(rows,indent=2))
