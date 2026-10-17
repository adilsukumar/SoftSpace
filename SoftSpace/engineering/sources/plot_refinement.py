import os,sys,json
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
p=Path(__file__).parent;sys.path.insert(0,str(p/'solver-libraries'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
o=p/'engineering-v7-results';v8=p/'engineering-v8-results'
fig,axs=plt.subplots(1,2,figsize=(12,4.5))
for ax,family in zip(axs,['adult','child']):
 for h,style in [(6,'--'),(4.5,'-')]:
  j=json.loads((o/(family+'_P2_h'+str(h)+'.json')).read_text());r=j['rows'][144:]
  ax.semilogx([v['frequency_Hz'] for v in r],[v['model_pressure_transfer_db'] for v in r],style,label='P2 '+str(h)+'mm mesh')
 ax.set_title(family+' proxy cavity');ax.set_xlabel('Frequency / Hz');ax.set_ylabel('Model pressure transfer / dB');ax.grid(alpha=.3);ax.legend(fontsize=9)
fig.suptitle('Refined acoustic proxy • area-integrated receiver • not measured attenuation',fontsize=12);fig.tight_layout();fig.savefig(o/'acoustic_P2.png',dpi=170);plt.close(fig)
j=json.loads((v8/'lower_crown_summary.json').read_text());old=json.loads((o/'vertical_fit_summary.json').read_text())
fig,axs=plt.subplots(1,2,figsize=(12,4.5))
for ax,family in zip(axs,['child','adult']):
 sizes=sorted(set(r['size'] for r in j['height_cases'] if r['family']==family))
 for i,size in enumerate(sizes):
  values=[]
  for ext in [0,15,30]:values.append(next(r['crown_inner_height_mm'] for r in j['height_cases'] if r['size']==size and r['extension_mm']==ext))
  ax.plot([0,15,30],values,marker='o',label=size+' lower crown')
  tall=[s['band_inner_crown_height_mm'] for s in old['shapes'] if s['size']==size]
  if i==1:ax.plot([0,15,30],tall,'--',color='#777',label='Prior medium crown')
 ax.set_title(family+' synthetic lateral fit');ax.set_xlabel('Slider extension / mm');ax.set_ylabel('Inner crown height above ear center / mm');ax.grid(alpha=.3);ax.legend(fontsize=8)
fig.suptitle('Lower-crown geometric screen •8mm assumed crown padding • no scalp-contact forces',fontsize=12);fig.tight_layout();fig.savefig(v8/'crown_height_comparison.png',dpi=170);plt.close(fig)
print('Refinement figures saved')
