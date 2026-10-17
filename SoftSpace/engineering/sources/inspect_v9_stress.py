from pathlib import Path
import sys,json
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import numpy as np
for f in sorted((P/'engineering-v9-results').glob('adult_small_h*_3d.npz')):
 d=np.load(f);i=int(np.argmax(d['von_mises']));print(f.name,'peak',float(d['von_mises'][i]),'centroid_mm',d['xyz'][d['tet'][i,:4]].mean(axis=0).tolist())
