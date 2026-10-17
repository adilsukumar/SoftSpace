import os,sys,json
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
p=Path(__file__).parent;sys.path.insert(0,str(p/'solver-libraries'))
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from collections import Counter
o=p/'engineering-v6-results'
fig=plt.figure(figsize=(12,5.5))
for index,size in enumerate(['adult_medium','child_medium']):
 data=np.load(o/(size+'_h3_3d.npz'));x=data['xyz'];u=data['displacement'];t=data['tet'][:,:4]
 faces=np.concatenate([t[:,[0,1,2]],t[:,[0,1,3]],t[:,[0,2,3]],t[:,[1,2,3]]]);keys=np.sort(faces,axis=1)
 _,idx,counts=np.unique(keys,axis=0,return_index=True,return_counts=True);f=faces[idx[counts==1]]
 keep=~(np.all(np.isclose(x[f,0],0,atol=1e-5),axis=1)|np.all(np.isclose(x[f,1],0,atol=1e-5),axis=1));f=f[keep]
 ax=fig.add_subplot(1,2,index+1,projection='3d');m=np.linalg.norm(u,axis=1);norm=plt.Normalize(0,m.max())
 for sx in [-1,1]:
  for sy in [-1,1]:
   sign=np.array([sx,sy,1]);deformed=(x+u)*sign
   col=Poly3DCollection(deformed[f],facecolors=plt.cm.viridis(norm(m[f].mean(axis=1))),linewidth=0,alpha=.95);ax.add_collection3d(col)
 ax.set_xlim(-130,130);ax.set_ylim(-35,35);ax.set_zlim(70,185);ax.set_box_aspect((2.6,.7,1.15));ax.view_init(20,-65)
 ax.set_yticks([-20,0,20]);ax.set_zticks([80,120,160,180]);ax.tick_params(labelsize=9)
 ax.set_xlabel('X / mm');ax.set_ylabel('Y / mm');ax.set_zlabel('Z / mm');ax.set_title(size.replace('_',' ')+'\nCAD crown and guides only')
 fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap='viridis'),ax=ax,location='bottom',shrink=.6,pad=.04,label='Displacement / mm')
fig.suptitle('3D linear elastic FEM • E = 2000 MPa • ideal 2 N per side • deformation scale 1×',fontsize=13)
fig.text(.5,.025,'No slider/contact/locking model. These shapes are not measured worn-head fit or comfort.',ha='center',fontsize=10)
fig.subplots_adjust(top=.80,bottom=.22,wspace=.2)
fig.savefig(o/'band_3d.png',dpi=170,bbox_inches='tight');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(12,4.8))
for ax,family in zip(axs,['adult','child']):
 for h,style in [(6,'--'),(4,'-')]:
  j=json.loads((o/(family+'_acoustic3d_h'+str(h)+'.json')).read_text());r=j['rows'][144:]
  ax.semilogx([v['frequency_Hz'] for v in r],[v['model_pressure_transfer_db'] for v in r],style,label=str(h)+'mm mesh')
 ax.axvspan(1000,8000,color='#f7bd62',alpha=.25,label='Mesh sensitivity unresolved');ax.set_title(family+' proxy cavity');ax.set_xlabel('Frequency / Hz');ax.set_ylabel('Model pressure transfer / dB');ax.grid(alpha=.3);ax.legend(fontsize=8)
fig.suptitle('Hypothetical compliant wall • E = 2500 MPa, Q = 20 • not product attenuation',fontsize=12)
fig.tight_layout();fig.savefig(o/'acoustic_proxy.png',dpi=170);plt.close(fig)
print('Saved 3D band and acoustic proxy plots')
