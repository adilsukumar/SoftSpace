from pathlib import Path
import sys,json
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import numpy as np
O=P/'engineering-v10-results';rows=[]
for h in [2.0,1.5,1.25,1.0]:
 path=O/('adult_medium_h'+str(h)+'_3d.npz')
 if not path.exists():continue
 d=np.load(path);x=d['xyz'];t=d['tet'];vm=d['von_mises'];top=np.argsort(vm)[-5:][::-1];pts=x[t[top]]
 centres=(-.125*pts[:,:4].sum(axis=1)+.25*pts[:,4:].sum(axis=1))
 rows.append({'mesh_mm':h,'peaks':[{'centroid_mm':p.tolist(),'von_mises_MPa':float(v)} for p,v in zip(centres,vm[top])]})
(O/'adult_medium_hotspots.json').write_text(json.dumps({'case':'adult_medium','status':'diagnostic only','meshes':rows,'limit':'Centroid stress locations; not a material strength or physical failure classification'},indent=2));print(json.dumps(rows))
