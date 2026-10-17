from pathlib import Path
import sys,json
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
s=json.loads((P/'engineering-v9-results'/'solid_v9_summary.json').read_text())
cases=s['cases'];fig,ax=plt.subplots(figsize=(10,4.6))
values=[100*c['stress_relative_mesh_change'] for c in cases]
ax.bar([c['size'].replace('_','\n') for c in cases],values,color=['#246b7a' if v<5 else '#b35b37' for v in values])
ax.axhline(5,color='#b35b37',linestyle='--',label='Chosen 5% comparison threshold')
for i,v in enumerate(values):ax.text(i,v+.08,f'{v:.2f}%',ha='center',fontsize=10)
ax.set_ylim(0,max(6,max(values,default=0)*1.25));ax.set_ylabel('Change in calculated peak stress (%)')
ax.set_title('V9 change between the last two structural meshes',loc='left',fontsize=14,pad=18)
ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False,loc='upper right')
fig.text(.12,.025,'Ideal 2 N per side and assumed material. A numerical pass does not prove strength or comfort.',fontsize=9)
fig.tight_layout(rect=(0,.065,1,1));target=P/'documents'/'images'/'V9_mesh_comparison.png';fig.savefig(target,dpi=180,facecolor='white');print(target)
