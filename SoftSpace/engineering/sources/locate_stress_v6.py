from pathlib import Path
import sys,json
p=Path(__file__).parent;sys.path.insert(0,str(p/'solver-libraries'))
import numpy as np
rows=[]
for h in ['5','3','2.0']:
 d=np.load(p/'engineering-v6-results'/('child_small_h'+h+'_3d.npz'));vm=d['von_mises'];x=d['xyz'];t=d['tet'];indices=np.argsort(vm)[-5:][::-1]
 rows.append({'mesh':h,'peaks':[{'centroid_mm':x[t[i,:4]].mean(axis=0).tolist(),'stress_MPa':float(vm[i])} for i in indices]})
print(json.dumps(rows,indent=2))
(p/'engineering-v6-results'/'stress_location.json').write_text(json.dumps(rows,indent=2))
