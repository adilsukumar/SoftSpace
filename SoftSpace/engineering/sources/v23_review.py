"""Review all corrected reference fields without turning numerical passes into product claims."""
from pathlib import Path
import json,sys,os,ast,csv,hashlib,itertools
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
np=q.np;O=P/'engineering-v23-results';rows=[]
for size in ['child_large','adult_small']:
 for h in [2.3,1.9]:
  for side in ['outward','inward']:
   f=O/f'{size}_h{h}_{side}.json';r=json.loads(f.read_text());assert r['converged'] and r['independent_residual']<1e-7;rows.append(r)
module=ast.parse((P/'v23_corrected_mesh_campaign.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='stress_summary'],type_ignores=[]),'v23_stress','exec'))
comparisons=[]
for size in ['child_large','adult_small']:
 for side in ['outward','inward']:
  coarse=next(r for r in rows if r['size']==size and r['mesh_size_mm']==2.3 and r['direction']==side);fine=next(r for r in rows if r['size']==size and r['mesh_size_mm']==1.9 and r['direction']==side)
  for c,f in zip(coarse['stress'],fine['stress']):
   for method in ['interior125','boundary35']:
    a,b=c['sampled_peaks_MPa'][method],f['sampled_peaks_MPa'][method];change=abs(b/a-1)*100;comparisons.append(dict(size=size,direction=side,component=c['component'],comparison='2.3 to 1.9',sampling=method,coarse_MPa=a,fine_MPa=b,change_percent=change,chosen_5_percent_pass=change<5))
local=[]
for side in ['outward','inward']:
 path=P/'engineering-v22-results'/f'objective_spacer_{side}.npz';j=P/'engineering-v22-results'/f'objective_spacer_{side}.json';original=json.loads(j.read_text());assert original['converged'];summary=stress_summary(np.load(path));local.append(dict(direction=side,raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),stress=summary))
 fine=next(r for r in rows if r['size']=='adult_small' and r['mesh_size_mm']==1.9 and r['direction']==side)
 for f,l in zip(fine['stress'],summary):
  for method in ['interior125','boundary35']:
   a,b=f['sampled_peaks_MPa'][method],l['sampled_peaks_MPa'][method];change=abs(b/a-1)*100;comparisons.append(dict(size='adult_small',direction=side,component=f['component'],comparison='1.9 to local 0.9',sampling=method,coarse_MPa=a,fine_MPa=b,change_percent=change,chosen_5_percent_pass=change<5))
for r in rows:
 r['numerical_controls_pass']=r['independent_residual']<1e-7 and r['force_balance_N']<1e-6 and r['moment_balance_Nmm']<1e-5 and r['coulomb_excess_MPa']<1e-10 and min(r['contact_derivative_errors'])<1e-3 and all(c['passed'] for c in r['rigid_motion_controls'])
assert len(comparisons)==24
summary=dict(date='2026-10-24',revision='V23',campaign_complete=True,corrected_equilibrium_cases=len(rows),all_numerical_controls_pass=all(r['numerical_controls_pass'] for r in rows),rigid_controls=sum(len(r['rigid_motion_controls']) for r in rows)//2,mesh_comparisons=len(comparisons),mesh_comparison_passes=sum(r['chosen_5_percent_pass'] for r in comparisons),whole_part_strength_demonstrated=False,all_product_software_testing_complete=False,physical_tests=0,CAD_changed=False,cases=rows,stress_comparisons=comparisons,local_corrected_fields=local,scope='Eight new corrected virtual-spacer reference solves across two isolated joint geometries, two meshes and two load directions. Two previously solved corrected local adult fields postprocessed separately. Finite stress sampling and pairwise mesh checks cannot bound stress everywhere. Parameters are assumptions, not calibrated manufactured materials.')
(O/'review_status.json').write_text(json.dumps(summary,indent=2))
with (O/'stress_comparisons.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(comparisons[0]));writer.writeheader();writer.writerows(comparisons)
register=[['Corrected joint numerical controls','Complete with recorded pass or fail','8 new equilibrium fields and 24 distinct rigid motion controls','Isolated joints and fixed assumed loads'],['Corrected joint stress recovery','Complete with failed comparisons retained','24 comparisons with fixed 5 percent threshold','No reliable whole part strength claim'],['Six size adjustment folding and packing','Earlier finite CAD checks retained','V19 shapes and V21 sampled paths','Continuous collision clearance and pinch protection unresolved'],['Headband material and load','Conditional screens only','Earlier assumed material and force screens','Named grade process and final load design needed'],['Cushion compression and glasses pressure','Conditional reduced model screens complete','V20 V21 V22 pressure studies','Traceable foam cover friction and worn geometry needed'],['Sony compatibility','Missing interface dimensions','V20 envelope study','Actual skirt groove carrier and tolerances needed'],['Incoming sound outgoing sound and ANC','Not validated','Earlier illustrative acoustic proxies only','Actual seal geometry and acoustic impedance needed for predictive simulation'],['Heat moisture creep fatigue drop and cleaning','Not validated','Prior proxies and conditional screens only','Real material curves process joints and acceptance criteria needed'],['Comfort sensory acceptance and usability','Requires wearer testing','No person tested','Cannot be passed by computer'],['Whole product software sign off','Not complete','Input and design gaps recorded','Do not treat a completed numerical campaign as finished product testing']]
with (O/'remaining_test_register.csv').open('w',newline='') as f:
 writer=csv.writer(f);writer.writerow(['Test area','Status','Evidence','Limit or required input']);writer.writerows(register)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
selected=[r for r in comparisons if r['comparison']=='2.3 to 1.9']
fig,ax=plt.subplots(figsize=(9,4));labels=[];interior=[];boundary=[]
for size in ['child_large','adult_small']:
 for side in ['outward','inward']:
  for comp in ['tongue','fork']:
   labels.append(('Child' if size=='child_large' else 'Adult')+'\n'+side+'\n'+comp)
   for method,values in [('interior125',interior),('boundary35',boundary)]:values.append(next(r['change_percent'] for r in selected if r['size']==size and r['direction']==side and r['component']==comp and r['sampling']==method))
x=np.arange(len(labels));ax.bar(x-.18,interior,.36,label='125 interior samples');ax.bar(x+.18,boundary,.36,label='35 samples including boundaries');ax.axhline(5,color='#a52a2a',ls='--',label='Chosen 5 percent comparison');ax.set_xticks(x,labels,fontsize=8);ax.set_ylabel('Peak change between meshes percent');ax.legend(fontsize=8,loc='lower center',bbox_to_anchor=(.5,1.01),ncol=3);ax.set_title('Corrected reference stress still needs a mesh reliability check',pad=35);fig.tight_layout();fig.savefig(P/'documents/images/V23_corrected_mesh.png',dpi=160);plt.close(fig)
text=f'''# V23 corrected reference verification\n\nEight corrected joint reference solves are complete. All numerical controls pass: {summary['all_numerical_controls_pass']}. The models cover child large and adult small isolated V19 joint geometries, meshes 2.3 and 1.9 mm, and side forces +2 and -2 N. The V22 virtual 0.5 mm spacer uses mean bore rotation. E is assumed 3500 MPa, nu 0.35, preload 140 N and friction 0.2. No CAD was changed.\n\nOf 24 fixed 5 percent stress comparisons, {summary['mesh_comparison_passes']} pass. All results, including failures, are in stress_comparisons.csv. Boundary lattice and interior sample peaks are finite samples, not a bounded maximum. Passing equilibrium, rigid motion and force balance is not proof of reliable peak stress or real product strength.\n\nRead remaining_test_register.csv before interpreting this as complete product testing. The current numerical campaign is finished; all product software testing is not finished. Actual edge and fastener details, material curves, Sony mounting dimensions, acoustic and thermal data remain unresolved. Comfort and sensory acceptance require people. More arbitrary generic inputs would not validate the intended product.\n\nRun v23_corrected_mesh_campaign.py then v23_review.py with the recorded dependencies. The first script preserves V19 V21 V22 originals, warm-starts from old fields, checks final equilibrium, records contact derivative checks and saves each new field. Stress sampling is recomputed from displacement gradients. The second script compares identical methods and retains failures; it does not replace peak criteria with averages.\n'''
(O/'README.md').write_text(text)
print(json.dumps({k:v for k,v in summary.items() if k not in ['cases','stress_comparisons','local_corrected_fields']},indent=2))
