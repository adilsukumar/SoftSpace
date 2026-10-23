"""Locate sampled stress hotspots and curved-element quality; no averaging away failures."""
from pathlib import Path
import os,sys,json,hashlib
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
np=q.np;O=P/'engineering-v21-results';rows=[]
E=3500.;nu=.35;mu=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu));D=np.zeros((6,6));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*mu);D[3:,3:]=np.eye(3)*mu
files=list((P/'engineering-v19-results/quadratic-contact').glob('*_h*.npz'))+list((P/'engineering-v19-results/quadratic-inward').glob('*_h*.npz'))+[f for f in (O/'refinement').glob('*_h1.9.npz') if '_outward_' in f.name or '_inward_' in f.name]
for f in files:
 meta=json.loads(f.with_suffix('.json').read_text());size=meta['size'];side='inward' if 'inward' in str(f) else 'outward';h=meta.get('h',meta.get('mesh_max_mm'));cad=json.loads((P/'engineering-v19-results'/(size+'_cad_report.json')).read_text());z=np.load(f);split=3*len(z['xt'])
 for ix,(xn,tn,u) in enumerate([('xt','tt',z['u'][:split]),('xf','tf',z['u'][split:])]):
  x=z[xn];t=z[tn];ue=u[(t[:,:,None]*3+np.arange(3)).reshape(-1,30)];peak=-1.;energy=0.;totalvolume=0.;samples=[];weights=[];peakdata=None
  for L,w in q.quadrature(3):
   B,det=q.strain_matrix(x,t,L);strain=np.einsum('ebi,ei->eb',B,ue);sig=strain@D.T;a,b,c,d,e,fv=sig.T;vm=np.sqrt(((a-b)**2+(b-c)**2+(c-a)**2)/2+3*(d*d+e*e+fv*fv));j=int(vm.argmax());samples.append(vm);weights.append(det*w);energy+=float((.5*np.einsum('ij,ij->i',strain,sig)*det*w).sum());totalvolume+=float((det*w).sum())
   if vm[j]>peak:
    peak=float(vm[j]);N=np.r_[L*(2*L-1),[4*L[i]*L[k] for i,k in q.edges]];pt=N@x[t[j]];J=x[t[j]].T@q.gradients(L);sv=np.linalg.svd(J,compute_uv=False);radius=float(np.hypot(pt[0],pt[2]-cad['pivot_z_mm']));peakdata=dict(xyz_mm=pt.tolist(),element=j,barycentric=L.tolist(),Jacobian_condition_number=float(sv[0]/sv[-1]),Jacobian_determinant_mm3=float(det[j]),distance_to_nominal_bore_mm=abs(radius-2.15),radial_distance_to_washer_edge_mm=abs(radius-5.5),radial_distance_to_preload_edge_mm=abs(radius-6),distance_to_fixture_plane_mm=abs(float(pt[2])-cad['guide_bottom_mm']),distance_to_fork_inner_plane_mm=abs(abs(float(pt[1]))-cad['fork_inner_halfspacing_mm']),distance_to_stop_plane_mm=abs(float(pt[2])-cad['pivot_z_mm']))
  vals=np.concatenate(samples);ww=np.concatenate(weights);order=np.argsort(vals);cum=np.cumsum(ww[order])/ww.sum();quant={str(p):float(vals[order[min(np.searchsorted(cum,p),len(vals)-1)]]) for p in [.5,.95,.99,.999]}
  rows.append(dict(size=size,direction=side,h=h,component=['tongue','fork'][ix],source=str(f.relative_to(P)),source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),sampled_peak_MPa=peak,peak_location=peakdata,volume_weighted_stress_quantiles_MPa=quant,bulk_strain_energy_N_mm=energy,quadrature_volume_mm3=totalvolume));print(size,side,h,['tongue','fork'][ix],peak,peakdata['xyz_mm'],peakdata['Jacobian_condition_number'],flush=True)
result=dict(review_date='2026-10-24',cases=rows,scope='Diagnostic postprocessing, not a strength pass. Distances are to nominal geometric features; proximity does not prove a singularity. Quantiles and energy are context only and do not replace failed peak comparisons. Positive determinants at 27 sampled points do not guarantee globally valid curved elements.')
(O/'hotspot_diagnostics.json').write_text(json.dumps(result,indent=2))

