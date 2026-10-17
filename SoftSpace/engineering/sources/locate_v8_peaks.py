import sys,json
from pathlib import Path
p=Path(__file__).parent;sys.path.insert(0,str(p/'solver-libraries'))
import numpy as np
for size in ['adult_small','adult_medium','adult_large','child_medium']:
 files=sorted((p/'engineering-v8-results').glob(size+'_h*_3d.npz'))
 for f in files:
  d=np.load(f);i=int(np.argmax(d['von_mises']));print(f.name,round(float(d['von_mises'][i]),4),[round(float(v),3) for v in d['xyz'][d['tet'][i,:4]].mean(axis=0)])
