"""Recover interior-point stresses from unchanged saved Tet10 displacements.
No new equilibrium solves, surface extrapolation, fatigue or strength qualification.
"""
from pathlib import Path
import os,sys,json,hashlib,time
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
np=q.np;O=P/'engineering-v21-results';start=time.time();rows=[]
E=3500.;nu=.35;lam=E*nu/((1+nu)*(1-2*nu));mu=E/(2*(1+nu));D=np.zeros((6,6));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*mu);D[3:,3:]=np.eye(3)*mu
def vm(stress):
 a,b,c,d,e,f=stress.T;return np.sqrt(((a-b)**2+(b-c)**2+(c-a)**2)/2+3*(d*d+e*e+f*f))
for folder in ['quadratic-contact','quadratic-inward']:
 for f in sorted((P/'engineering-v19-results'/folder).glob('*_h*.npz')):
  z=np.load(f);meta=json.loads(f.with_suffix('.json').read_text());split=3*len(z['xt']);components=[]
  for ix,(xn,tn,u) in enumerate([('xt','tt',z['u'][:split]),('xf','tf',z['u'][split:])]):
   x=z[xn];t=z[tn];dofs=(t[:,:,None]*3+np.arange(3)).reshape(-1,30);ue=u[dofs]
   B,_=q.strain_matrix(x,t,[.25]*4);centroid=vm(np.einsum('ab,ebi,ei->ea',D,B,ue,optimize=True));reference=meta['component_stresses'][ix]['peak_element_MPa'];assert abs(centroid.max()/reference-1)<1e-9
   maximum=0.;integral=0.;volume=0.;location=None
   for L,w in q.quadrature(3):
    B,det=q.strain_matrix(x,t,L);stress=vm(np.einsum('ab,ebi,ei->ea',D,B,ue,optimize=True));j=int(np.argmax(stress))
    if stress[j]>maximum:maximum=float(stress[j]);location=dict(element=j,barycentric=L.tolist())
    integral+=float(stress@(det*w));volume+=float(sum(det*w))
   components.append(dict(component=['tongue','fork'][ix],centroid_peak_MPa=float(centroid.max()),interior_27_point_peak_MPa=maximum,volume_weighted_mean_MPa=integral/volume,peak_to_centroid_ratio=maximum/float(centroid.max()),location=location))
  rows.append(dict(source=f.relative_to(P).as_posix(),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),direction=folder,size=meta['size'],h=meta['mesh_max_mm'],components=components));print(f.name,folder,flush=True)
comparisons=[]
for direction in ['quadratic-contact','quadratic-inward']:
 for size in ['adult_small','child_large']:
  pair=sorted([r for r in rows if r['direction']==direction and r['size']==size],key=lambda r:r['h'],reverse=True);assert len(pair)==2
  for i in range(2):
   coarse=pair[0]['components'][i]['interior_27_point_peak_MPa'];fine=pair[1]['components'][i]['interior_27_point_peak_MPa'];delta=abs(fine/coarse-1)*100
   comparisons.append(dict(direction=direction,size=size,component=pair[0]['components'][i]['component'],coarse_peak_MPa=coarse,fine_peak_MPa=fine,change_percent=delta,chosen_5_percent_comparison_pass=delta<5))
result=dict(date='2026-10-23',saved_solutions=len(rows),interior_points_per_element=27,centroid_reproduction_pass=True,cases=rows,mesh_comparisons=comparisons,all_peak_comparisons_pass=all(c['chosen_5_percent_comparison_pass'] for c in comparisons),seconds=time.time()-start,
 scope='Postprocessing saved V19 displacements at positive interior quadrature points using the same assumed isotropic PA66 E=3500 MPa nu=0.35. Not a new solve, certified material stress limit, converged surface/contact-edge stress, bolt bearing or fatigue result. V19 displacement comparisons cannot be used as stress convergence evidence.')
(O/'interior_stress_recovery.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(comparisons=comparisons,all_pass=result['all_peak_comparisons_pass']),indent=2))
