import json,sys
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import numpy as np,matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
O=P/'engineering-v17-results';data=json.loads((O/'pin_contact_and_return.json').read_text());spring=json.loads((O/'spring_design_tradeoff.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(10,3.8))
for size,label in [('child_large','Child large'),('adult_small','Adult small')]:
 a=np.load(O/(size+'_pin_contact_h0.25.npz'));axes[0].plot(a['y'],a['u'][::2],label=label)
axes[0].axhline(.05,color='grey',ls='--',lw=1);axes[0].axhline(-.05,color='grey',ls='--',lw=1);axes[0].axvspan(-32,-21,color='grey',alpha=.12);axes[0].axvspan(-12.999,-10,color='grey',alpha=.12);axes[0].set(xlabel='Local pin axis coordinate in mm',ylabel='Sideways displacement in mm',title='Reduced guide contact at 2 N side load');axes[0].legend(fontsize=8)
rows=[r for r in data['cases'] if r['radial_gap_mm']==.05 and r['guide_line_stiffness_N_per_mm2']==1000 and r['size']=='child_large'];axes[1].plot([r['side_force_N'] for r in rows],[.1*r['normal_reaction_sum_N']+.1 for r in rows],marker='o',label='Assumed friction 0.1 and other drag 0.1 N');axes[1].axhline(data['spring_reference']['wear_preload_N'],color='#cc6600',ls='--',label='Earlier illustrative spring preload');axes[1].set(xlabel='Assumed external side load in N',ylabel='Force in N',title='Conditional drag compared with preload');axes[1].legend(fontsize=7)
for ax in axes:ax.grid(alpha=.2)
fig.text(.5,.02,'Assumed elastic pin and guide stiffness. Reduced static contact and Coulomb drag only; not measured joint or spring-return performance.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.06,1,1));fig.savefig(P/'documents/images/V17_contact_return.png',dpi=160);plt.close(fig)
