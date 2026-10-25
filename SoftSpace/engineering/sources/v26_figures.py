from pathlib import Path
import os,sys,json
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
O=P/'engineering-v26-results';np=q.np
fig=plt.figure(figsize=(10,5.5))
for k,(folder,title) in enumerate([(O,'Candidate A\nFolding obstruction found'),(O/'relieved','Candidate B\nTop corner relieved')]):
 z=np.load(folder/'child_large_h1.9_mesh.npz');ax=fig.add_subplot(1,2,k+1,projection='3d')
 for key,color in [('t','#55a6a0'),('f','#526776')]:
  x=z['x'+key];t=z['t'+key];faces=q.boundary(t);pc=Poly3DCollection(x[faces],facecolor=color,edgecolor='none',alpha=1);ax.add_collection3d(pc)
 ax.set(xlim=(-9,26),ylim=(-20,20),zlim=(29,84),xlabel='x mm',ylabel='y mm',zlabel='z mm',title=title);ax.set_box_aspect((35,40,55));ax.view_init(elev=22,azim=-55);ax.set_axis_off()
fig.suptitle('V26 isolated child joint candidates',fontsize=15);fig.text(.5,.025,'Saved meshes of two local parts only. Colours identify parts, not materials or stress. Full headset CAD is unchanged.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.05,1,.95));fig.savefig(P/'documents/images/V26_local_joint_candidates.png',dpi=160);plt.close(fig)
print('Saved actual candidate mesh figure')
