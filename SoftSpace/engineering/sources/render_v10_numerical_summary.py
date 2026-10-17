"""Plots from saved numerical results, not measured headphone performance."""
from pathlib import Path
import os,sys,json,hashlib
os.environ['OPENBLAS_NUM_THREADS']='1'
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt;import numpy as np
plt.rcParams.update({'font.size':15,'axes.titlesize':16,'axes.labelsize':15,'xtick.labelsize':14,'ytick.labelsize':14})
O=P/'engineering-v10-results';s=json.loads((O/'solid_v10_summary.json').read_text());full=json.loads((O/'full_width_sizes_summary.json').read_text());assert full['status']=='complete' and len(full['cases'])==6
fig,axes=plt.subplots(1,2,figsize=(11,4.5));c=next(c for c in s['cases'] if c['size']=='adult_medium');h=[r['mesh_max_mm'] for r in c['meshes']];stress=[r['max_von_mises_centroid_MPa'] for r in c['meshes']]
axes[0].plot(h,stress,'o-',color='#bb7040');axes[0].invert_xaxis();axes[0].set_xlabel('Maximum mesh size mm');axes[0].set_ylabel('Sampled peak stress MPa');axes[0].set_title('Adult medium quarter model history');axes[0].grid(alpha=.2)
names=[c['size'] for c in full['cases']];lookup={c['size']:c for c in s['cases']};old=[lookup[n]['meshes'][-1]['guide_mean_x_displacement_mm']/2 for n in names];actual=[c['meshes'][-1]['compliance_mm_per_N'] for c in full['cases']];x=np.arange(6)
axes[1].bar(x-.18,old,.36,label='Quarter fixture',color='#8fa8b5');axes[1].bar(x+.18,actual,.36,label='Actual width fixture',color='#4a877b');axes[1].set_xticks(x,[n.replace('_','\n') for n in names],fontsize=14);axes[1].set_ylabel('Guide compliance mm per N');axes[1].set_title('Different ideal fixtures\nAssumed E 2000 MPa');axes[1].legend(fontsize=14);axes[1].set_ylim(0,max(max(old),max(actual))*1.4);axes[1].grid(axis='y',alpha=.2)
fig.suptitle('Numerical refinement and band fixture comparison',fontsize=19);fig.tight_layout(rect=(0,0,1,.90));target=P/'documents'/'images'/'V10_numerical_summary.png';fig.savefig(target,dpi=180,bbox_inches='tight');plt.close(fig)
(O/'numerical_plot_sources.json').write_text(json.dumps({'figure':str(target),'source_files':[{'path':str(O/name),'sha256':hashlib.sha256((O/name).read_bytes()).hexdigest()} for name in ['solid_v10_summary.json','full_width_sizes_summary.json']],'limit':'Different constraints and load distributions, not an isolated symmetry comparison or market headphone test.'},indent=2));print(target)
