"""Plot actual calculated fork fields; assign interior sampled peaks to boundary faces."""
from pathlib import Path
import sys,os,json,hashlib
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
src=P/'v22_quadrature_mesh_audit.py';exec(compile(src.read_text().split("for size in ['child_large'")[0],str(src),'exec'));O=P/'engineering-v22-results';data=[]
for side in ['outward','inward']:
 path=O/('adult_fork_local_0.9_'+side+'.npz')
 if not path.exists():continue
 cache=O/('fork_field_'+side+'.npz')
 if cache.exists():z=np.load(cache);x,t,peak=z['x'],z['t'],z['peak']
 else:
  z=np.load(path);x,t=z['xf'],z['tf'];u=z['u'][3*len(z['xt']):].reshape(-1,3)[t];peak=np.zeros(len(t))
  for L,w in q.quadrature(5):peak=np.maximum(peak,vm(tensor(x,t,u,L)[0]@D.T))
  np.savez_compressed(cache,x=x,t=t,peak=peak)
 faces=np.concatenate([t[:,v+[q.edge_index[tuple(sorted((v[i],v[j])))] for i,j in [(0,1),(1,2),(2,0)]]] for v in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]]);_,idx,count=np.unique(np.sort(faces,axis=1),axis=0,return_index=True,return_counts=True);idx=idx[count==1];boundary=faces[idx];owners=np.tile(np.arange(len(t)),4)[idx];tri=np.concatenate([boundary[:,v] for v in [[0,3,5],[3,1,4],[5,4,2],[3,4,5]]]);col=np.tile(peak[owners],4);data.append((side,x,tri,col,float(peak.max()),hashlib.sha256(path.read_bytes()).hexdigest()))
if len(data)==2:
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 from matplotlib.colors import Normalize
 norm=Normalize(0,max(r[4] for r in data));fig=plt.figure(figsize=(10,4.3));axes=[]
 for n,(side,x,tri,col,maximum,sha) in enumerate(data):
  ax=fig.add_subplot(1,2,n+1,projection='3d');collection=Poly3DCollection(x[tri],facecolors=plt.cm.viridis(norm(col)),edgecolor='none',linewidth=0,rasterized=True);ax.add_collection3d(collection);ax.set_xlim(x[:,0].min(),x[:,0].max());ax.set_ylim(x[:,1].min(),x[:,1].max());ax.set_zlim(x[:,2].min(),x[:,2].max());ax.set_box_aspect(np.ptp(x,axis=0));ax.view_init(elev=23,azim=-58);ax.set_title(side.title()+'  sampled peak '+format(maximum,'.2f')+' MPa',fontsize=10);ax.set_xlabel('x mm',fontsize=8);ax.set_ylabel('y mm',fontsize=8);ax.set_zlabel('z mm',fontsize=8);ax.tick_params(labelsize=7);axes.append(ax)
 cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap='viridis'),ax=axes,shrink=.7,pad=.04);cb.set_label('Adjacent element interior sampled peak MPa',fontsize=8);cb.ax.tick_params(labelsize=8);fig.suptitle('V19 isolated fork  targeted mesh  calculated field',fontsize=12);fig.text(.5,.025,'125 interior samples per element mapped to undeformed boundary faces. No surface stress bound, material or strength pass.',ha='center',fontsize=8);fig.savefig(P/'documents/images/V22_targeted_fork_stress.png',dpi=170);plt.close(fig)
 (O/'field_plot_provenance.json').write_text(json.dumps(dict(date='2026-10-24',fields=[dict(direction=r[0],source_sha256=r[5],interior_sampled_peak_MPa=r[4]) for r in data],scope='Calculated field visualization only, not measured surface stress or strength qualification.'),indent=2))
print('Recovered fork fields',len(data),flush=True)
