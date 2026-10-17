import os,sys,json
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import numpy as np,matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
O=P/'engineering-v18-results';s=json.loads((O/'fork_mechanics_summary.json').read_text());fig,axes=plt.subplots(1,2,figsize=(10,4.7));norm=matplotlib.colors.Normalize(0,max(r['meshes'][-1]['max_von_mises_centroid_MPa'] for r in s['cases']));cmap=plt.get_cmap('viridis')
az=np.deg2rad(-55);el=np.deg2rad(20);D=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)]);H=np.array([-np.sin(az),np.cos(az),0]);V=np.cross(D,H);proj=np.column_stack([H,V])
for ax,r in zip(axes,s['cases']):
 m=r['meshes'][-1];f=Path(m['array_audit']['file'])
 with np.load(f) as a:
  x=a['x'];t=a['t'];vm=a['vm'];faces=np.concatenate([t[:,p] for p in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]]);owners=np.tile(np.arange(len(t)),4);_,idx,counts=np.unique(np.sort(faces,axis=1),axis=0,return_index=True,return_counts=True);idx=idx[counts==1];tri=x[faces[idx]];values=vm[owners[idx]];order=np.argsort((tri@D).mean(axis=1));xy=tri@proj;ax.add_collection(PolyCollection(xy[order],facecolors=cmap(norm(values[order])),edgecolors='none'));pts=xy.reshape(-1,2);lo=pts.min(axis=0);hi=pts.max(axis=0);pad=(hi-lo)*.08;ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]);ax.set_ylim(lo[1]-pad[1],hi[1]+pad[1]);ax.set_aspect('equal');ax.set_axis_off();ax.set_title(r['size'].replace('_',' ').title()+'\n'+f"Cup movement {m['cup_weighted_x_displacement_mm']:.3f} mm",fontsize=11)
fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm,cmap=cmap),ax=axes.ravel().tolist(),shrink=.7,label='Adjacent element centroid von Mises MPa');fig.suptitle('V18 separate fork fixtures under assumed loads',fontsize=15);fig.text(.5,.025,'Undeformed saved FE boundaries coloured by adjacent element centroid stress. Ideal supports and assumed material; not joint strength.',ha='center',fontsize=8);fig.subplots_adjust(left=.02,right=.78,bottom=.1,top=.82,wspace=.04);fig.savefig(P/'documents/images/V18_fork_fixtures.png',dpi=160,facecolor='white');plt.close(fig)
