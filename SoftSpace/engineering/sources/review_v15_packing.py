"""Compare searched endpoints with the already checked V14 fold, never promote a worse result."""
import json,math,hashlib,sys,os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v15-results'
prior=json.loads((P/'engineering-v14-results/packing_summary.json').read_text());motion=json.loads((P/'engineering-v14-results/ocp_motion_audit.json').read_text());rows=[]
for f in sorted(O.glob('child_*_packing_search.json')):
 s=json.loads(f.read_text());old=next(r for r in prior['sizes'] if r['size']==s['size']);identity=next(r for r in motion['sources'] if r['size']==s['size']);assert s['source_sha256']==identity['sha256']==hashlib.sha256(Path(s['source']).read_bytes()).hexdigest()
 proof=[r for r in motion['cases'] if r['size']==s['size'] and r['phase']=='folding released' and r['angles_deg']==old['angles_deg']];assert len(proof)==1 and proof[0]['pass']
 original_volume=math.prod(old['folded_box_mm']);candidate=s['best_clear_endpoint'];improves=candidate is not None and candidate['box_volume_mm3']<original_volume-1e-5
 volume=candidate['box_volume_mm3'] if improves else original_volume;box=candidate['box_mm'] if improves else old['folded_box_mm']
 rows.append({'size':s['size'],'source':s['source'],'source_sha256':s['source_sha256'],'ranked_boxes':s['ranked_pose_count'],'new_endpoint_checks':len(s['shortlisted_pose_checks']),'new_clear_endpoint_improves_previous_V14_fold':improves,'previous_clear_fold_angles_deg':old['angles_deg'],'previous_clear_fold_extension_mm':[0,30],'previous_clear_fold_proof':proof[0],'best_recorded_box_mm':box,'best_recorded_source':'new search endpoint' if improves else 'previous V14 checked endpoint','change_from_retracted_unfolded_percent':100*(volume/math.prod(s['retracted_unfolded_box_mm'])-1),'change_from_nominal_percent':100*(volume/math.prod(s['nominal_box_mm'])-1)})
out={'revision':'V15 finite packing search on V14 parts','sizes':rows,'limits':['Previous source-matched V14 clear endpoint retained whenever a new endpoint is worse','Finite sampled search, not global optimum or new path proof','Held6mm pin release; no stable folded storage latch established','Axis aligned CAD boxes, not physical carrying or travel survival']};(O/'packing_review.json').write_text(json.dumps(out,indent=2))
sys.path.insert(0,str(P/'solver-libraries'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(9,4.4));values=[r['change_from_retracted_unfolded_percent'] for r in rows];bars=ax.barh([r['size'].replace('_',' ').title() for r in rows],values,color=['#bb654e' if v>=0 else '#488479' for v in values]);ax.axvline(0,color='#334653',lw=1);ax.set_xlabel('Box volume change from fully retracted unfolded headset percent');ax.set_title('Best recorded clear child fold compared with no fold',pad=18);ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
for b,v in zip(bars,values):ax.text(v+.05,b.get_y()+b.get_height()/2,f'{abs(v):.2f}% '+('larger' if v>=0 else 'smaller'),va='center')
ax.set_xlim(min(0,min(values))-.2,max(values)+1.8);fig.text(.5,.025,'V14 parts. Clear endpoints only; paths are checked separately. Release pins held back 6 mm.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.07,1,1));image=P/'documents/images/V15_child_packing.png';fig.savefig(image,dpi=160,facecolor='white');plt.close(fig)
print(json.dumps({'sizes':[{'size':r['size'],'improved':r['new_clear_endpoint_improves_previous_V14_fold'],'percent_larger_than_retracted':r['change_from_retracted_unfolded_percent']} for r in rows],'image':str(image)}))
