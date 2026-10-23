"""Compare the completed finer-mesh matrix and retain original failed pairs."""
from pathlib import Path
import sys,os,json,hashlib
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
np=q.np;O=P/'engineering-v21-results';R=O/'refinement';old=json.loads((O/'interior_stress_recovery.json').read_text());rows=[]
E=3500.;nu=.35;mu=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu));D=np.zeros((6,6));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*mu);D[3:,3:]=np.eye(3)*mu
for size in ['child_large','adult_small']:
 for side in ['outward','inward']:
  path=R/(size+'_'+side+'_h1.9.json');meta=json.loads(path.read_text());assert meta['converged'];z=np.load(path.with_suffix('.npz'));split=3*len(z['xt']);direction='quadratic-contact' if side=='outward' else 'quadratic-inward'
  previous=next(r for r in old['cases'] if r['direction']==direction and r['size']==size and r['h']==2.3)
  values=[]
  for j,(xn,tn,u) in enumerate([('xt','tt',z['u'][:split]),('xf','tf',z['u'][split:])]):
   x=z[xn];t=z[tn];dof=(t[:,:,None]*3+np.arange(3)).reshape(-1,30);ue=u[dof];peak=0.;minjac=float('inf')
   for L,w in q.quadrature(3):
    B,det=q.strain_matrix(x,t,L);a,b,c,d,e,f=np.einsum('ab,ebi,ei->ea',D,B,ue,optimize=True).T;v=np.sqrt(((a-b)**2+(b-c)**2+(c-a)**2)/2+3*(d*d+e*e+f*f));peak=max(peak,float(v.max()));minjac=min(minjac,float(min(det)))
   ref=previous['components'][j]['interior_27_point_peak_MPa'];change=abs(peak/ref-1)*100;values.append(dict(component=['tongue','fork'][j],h2_3_peak_MPa=ref,h1_9_peak_MPa=peak,change_percent=change,chosen_5_percent_comparison_pass=change<5,minimum_sampled_Jacobian=minjac))
  previous_result=json.loads((P/'engineering-v19-results'/direction/(size+'_h2.3.json')).read_text());delta=abs(meta['cup_mean_displacement_x_mm']/previous_result['cup_mean_displacement_x_mm']-1)*100
  # Force and reaction arrays use interleaved xyz components.
  balance=float(np.linalg.norm((z['reaction']+z['force']).reshape(-1,3).sum(axis=0)));assert balance<1e-5
  rows.append(dict(size=size,direction=side,stress=values,displacement_change_percent=delta,displacement_chosen_5_percent_pass=delta<5,force_balance_N=balance,relative_free_residual=meta['relative_free_residual'],source_CAD_sha256=previous_result['source_sha256'],source_CAD=previous_result['source'],factorizations=meta['factorizations'],linear_system_calls=meta['linear_system_calls'],raw_solution_sha256=hashlib.sha256(path.with_suffix('.npz').read_bytes()).hexdigest()))
ctrl=json.loads((R/'child_large_outward_h1.9.json').read_text());assert ctrl['direct_LU_control_pass']
result=dict(date='2026-10-23',cases=rows,all_selected_finer_peak_comparisons_pass=all(v['chosen_5_percent_comparison_pass'] for r in rows for v in r['stress']),all_selected_displacement_comparisons_pass=all(r['displacement_chosen_5_percent_pass'] for r in rows),direct_LU_control_relative_u_error=ctrl['direct_LU_control_relative_u_error'],
 original_coarser_pair_failed_comparisons=8,source_CAD_unchanged=True,
 scope='Two representative isolated V19 ParallelDisc joints and two load directions on optimized 1.9 mm meshes. Projected Anderson acceleration solves the original friction fixed-point equations with direct LU inner solves. Child outward uses mixed acceleration and matches the saved unaccelerated direct-LU field; the other three use full projected acceleration. Final residuals and force balance are checked. Peak comparisons sample 27 interior points, not bounded surface stress, full fastener, fatigue or material qualification. No all-possible-software-testing claim.')

(R/'matrix_review.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
