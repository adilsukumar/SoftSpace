from pathlib import Path
import json,sys,os
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=json.loads((P/'engineering-v22-results/quadrature_mesh_audit.json').read_text());rows=[]
for size in ['child_large','adult_small']:
 for side in ['outward','inward']:
  for comp in ['tongue','fork']:
   a=sorted([x for x in r['cases'] if x['size']==size and x['direction']==side and x['component']==comp],key=lambda x:x['h'],reverse=True)
   changes=[abs(a[1]['quadrature'][j]['interior_sampled_peak_MPa']/a[0]['quadrature'][j]['interior_sampled_peak_MPa']-1)*100 for j in [0,2]];changes.append(abs(a[1]['lattice_including_boundary_sampled_peak_MPa']/a[0]['lattice_including_boundary_sampled_peak_MPa']-1)*100)
   rows.append(dict(size=size,direction=side,component=comp,change_27_point_percent=changes[0],change_125_point_percent=changes[1],change_boundary_lattice_percent=changes[2]))
summary=dict(date='2026-10-24',cases=rows,energy_order4_to5_max_change_percent=max(x['energy_order4_to5_change_percent'] for x in r['cases']),nonpositive_Jacobian_lattice_cases=sum(x['elements_with_nonpositive_lattice_Jacobian']>0 for x in r['cases']),tensor_control_max_error=max(x['tensor_gradient_control_max_error'] for x in r['cases']),all_27_point_checks_pass=False,all_125_point_checks_pass=all(x['change_125_point_percent']<5 for x in rows),all_boundary_lattice_checks_pass=all(x['change_boundary_lattice_percent']<5 for x in rows),scope='2.3 versus 1.9 mm saved fields. Finite sampling, not global stress bounds or strength certification. Energy agreement does not imply peak agreement.')
(P/'engineering-v22-results/recovery_comparisons.json').write_text(json.dumps(summary,indent=2))
fig,ax=plt.subplots(figsize=(9,4.7));labels=[x['size'].replace('_',' ')+' '+x['direction']+' '+x['component'] for x in rows];y=list(range(len(rows)));width=.23
for offset,key,label,color in [(-width,'change_27_point_percent','27 interior points','#315f73'),(0,'change_125_point_percent','125 interior points','#bd8749'),(width,'change_boundary_lattice_percent','35 points including boundary','#a53a49')]:ax.barh([n+offset for n in y],[x[key] for x in rows],height=width,label=label,color=color)
ax.axvline(5,color='black',linestyle='--',linewidth=1);ax.set_yticks(y,labels,fontsize=8);ax.invert_yaxis();ax.set_xlabel('Change in sampled peak between 2.3 and 1.9 mm meshes percent');ax.set_title('Peak stress depends on the recovery sampling');ax.grid(axis='x',alpha=.2);ax.legend(fontsize=8,loc='lower right');fig.text(.5,.02,'Chosen 5 percent comparison line. Diagnostic saved-field calculations; no strength or wearer validation.',ha='center',fontsize=8);fig.tight_layout(rect=[0,.045,1,1]);fig.savefig(P/'documents/images/V22_stress_recovery.png',dpi=170);plt.close(fig)
print(json.dumps(summary,indent=2))
