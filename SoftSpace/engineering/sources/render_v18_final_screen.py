import sys,json
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import numpy as np,matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
O=P/'engineering-v18-results';s=json.loads((O/'final_available_data_screen.json').read_text());fig,ax=plt.subplots(figsize=(9,4.5));a=np.linspace(0,3,120)
for prefix,color,label in [('adult','#365e80','Adult high density scenario'),('child','#378371','Child high density scenario')]:
 worst=max(r['maximum_gravity_moment_over_orientation_Nmm'] for r in s['acceleration_thresholds'] if r['size'].startswith(prefix));ax.plot(a,a*worst,label=label,color=color,lw=2)
ax.axhline(64,ls='--',color='#b87929',label='Proposed minimum holding torque64Nmm');ax.axhline(96,ls=':',color='#8a5b85',label='Proposed maximum holding torque96Nmm');ax.set(xlabel='Equivalent resultant acceleration magnitude in g',ylabel='Moment about folding axis Nmm',title='Friction holding is sensitive to the handling load');ax.grid(alpha=.2);ax.legend(fontsize=8);fig.text(.5,.02,'Equivalent static loading at worst orientation. No transient impact, measured friction or real handling pass is represented.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.06,1,1));fig.savefig(P/'documents/images/V18_final_retention_screen.png',dpi=160);plt.close(fig)
