"""Read the finer-mesh trial after completion; retain unresolved stress changes."""
from pathlib import Path
import sys,json,hashlib,os
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
np=q.np;O=P/'engineering-v21-results';R=O/'refinement';trial=json.loads((R/'trial.json').read_text())
if trial['status']!='equilibrium converged':raise SystemExit('Refinement has no converged equilibrium to postprocess: '+trial['status'])
z=np.load(R/'child_large_h1.9.npz');E=3500.;nu=.35;mu=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu));D=np.zeros((6,6));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*mu);D[3:,3:]=np.eye(3)*mu
old=json.loads((O/'interior_stress_recovery.json').read_text());reference=next(r for r in old['cases'] if r['direction']=='quadratic-contact' and r['size']=='child_large' and r['h']==2.3)
rows=[];split=3*len(z['xt'])
for j,(xn,tn,u) in enumerate([('xt','tt',z['u'][:split]),('xf','tf',z['u'][split:])]):
 x=z[xn];t=z[tn];dof=(t[:,:,None]*3+np.arange(3)).reshape(-1,30);ue=u[dof];peak=0.;minjac=float('inf')
 for L,w in q.quadrature(3):
  B,det=q.strain_matrix(x,t,L);a,b,c,d,e,f=np.einsum('ab,ebi,ei->ea',D,B,ue,optimize=True).T;v=np.sqrt(((a-b)**2+(b-c)**2+(c-a)**2)/2+3*(d*d+e*e+f*f));peak=max(peak,float(v.max()));minjac=min(minjac,float(min(det)))
 prev=reference['components'][j]['interior_27_point_peak_MPa'];delta=abs(peak/prev-1)*100
 rows.append(dict(component=['tongue','fork'][j],h2_3_peak_MPa=prev,h1_9_peak_MPa=peak,change_percent=delta,chosen_5_percent_comparison_pass=delta<5,minimum_sampled_Jacobian=minjac))
prev=json.loads((P/'engineering-v19-results/quadratic-contact/child_large_h2.3.json').read_text());change=abs(trial['result']['cup_mean_displacement_x_mm']/prev['cup_mean_displacement_x_mm']-1)*100
out=dict(date='2026-10-23',trial_status=trial['status'],nodes=trial['nodes'],comparisons=rows,all_peak_comparisons_pass=all(r['chosen_5_percent_comparison_pass'] for r in rows),displacement_change_percent=change,
 initial_mesh_failure='Unoptimized 1.9 mm curved mesh had a nonpositive quadrature Jacobian and was rejected. High-order optimization was used before the new solve.',
 raw_solution_sha256=hashlib.sha256((R/'child_large_h1.9.npz').read_bytes()).hexdigest(),scope='One additional outward child-large mesh. Same assumed material, prescribed preload, ideal pivot and contact approximations. No all-size/all-load convergence or physical strength claim.')
(R/'comparison.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
