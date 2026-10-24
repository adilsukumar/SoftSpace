"""Higher quadrature and finite Jacobian lattice audit of saved joint fields.
No equilibrium rerun or physical strength claim. Independent tensor-gradient control.
"""
from pathlib import Path
import os,sys,json,time,hashlib,itertools
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
np=q.np;O=P/'engineering-v22-results';O.mkdir(exist_ok=True);rows=[];start=time.time()
E=3500.;nu=.35;mu=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu));D=np.zeros((6,6));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*mu);D[3:,3:]=np.eye(3)*mu

def tensor(x,t,ue,L):
 gr=q.gradients(L);J=np.einsum('eia,ib->eab',x[t],gr);det=np.linalg.det(J);g=np.einsum('ib,eba->eia',gr,np.linalg.inv(J));H=np.einsum('eia,eib->eab',ue,g);strain=np.stack([H[:,0,0],H[:,1,1],H[:,2,2],H[:,0,1]+H[:,1,0],H[:,1,2]+H[:,2,1],H[:,0,2]+H[:,2,0]],axis=1);return strain,det

def vm(s):
 a,b,c,d,e,f=s.T;return np.sqrt(((a-b)**2+(b-c)**2+(c-a)**2)/2+3*(d*d+e*e+f*f))
for size in ['child_large','adult_small']:
 for h in [2.3,1.9]:
  for side in ['outward','inward']:
   folder='quadratic-contact' if side=='outward' else 'quadratic-inward';f=P/'engineering-v19-results'/folder/(size+'_h2.3.npz') if h==2.3 else P/'engineering-v21-results/refinement'/(size+'_'+side+'_h1.9.npz');z=np.load(f);split=3*len(z['xt'])
   for ix,(xn,tn,u) in enumerate([('xt','tt',z['u'][:split]),('xf','tf',z['u'][split:])]):
    x=z[xn];t=z[tn];ue=u.reshape(-1,3)[t];B,_=q.strain_matrix(x,t,[.25]*4);control=float(abs(np.einsum('ebi,ei->eb',B,ue.reshape(-1,30))-tensor(x,t,ue,np.array([.25]*4))[0]).max());assert control<1e-10
    qs=[]
    for order in [3,4,5]:
     energy=0.;vol=0.;peak=0.;minjac=1e99
     for L,w in q.quadrature(order):
      strain,det=tensor(x,t,ue,L);assert det.min()>0;stress=strain@D.T;peak=max(peak,float(vm(stress).max()));energy+=float((.5*np.einsum('ij,ij->i',strain,stress)*det*w).sum());vol+=float((det*w).sum());minjac=min(minjac,float(det.min()))
     qs.append(dict(order=order,points_per_element=order**3,bulk_energy_N_mm=energy,volume_mm3=vol,interior_sampled_peak_MPa=peak,minimum_sampled_Jacobian_mm3=minjac))
    # A finite lattice that includes tetrahedral vertices, edges and faces.
    minj=1e99;neg=set();latticepeak=0.
    for ints in itertools.product(range(5),repeat=3):
     last=4-sum(ints)
     if last<0:continue
     L=np.array([last,*ints])/4;J=np.einsum('eia,ib->eab',x[t],q.gradients(L));det=np.linalg.det(J);minj=min(minj,float(det.min()));neg.update(np.flatnonzero(det<=0).tolist())
     if det.min()>0:latticepeak=max(latticepeak,float(vm(tensor(x,t,ue,L)[0]@D.T).max()))
    change=abs(qs[2]['bulk_energy_N_mm']/qs[1]['bulk_energy_N_mm']-1)*100
    rows.append(dict(size=size,h=h,direction=side,component=['tongue','fork'][ix],source=f.relative_to(P).as_posix(),source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),tensor_gradient_control_max_error=control,quadrature=qs,energy_order4_to5_change_percent=change,chosen_1_percent_energy_comparison_pass=change<1,Jacobian_35_point_lattice_minimum=minj,elements_with_nonpositive_lattice_Jacobian=len(neg),lattice_including_boundary_sampled_peak_MPa=latticepeak if not neg else None))
    print(size,h,side,['tongue','fork'][ix], 'energychange',change,'badJ',len(neg),'boundary_peak',latticepeak,flush=True)
    (O/'quadrature_mesh_audit.json').write_text(json.dumps(dict(date='2026-10-24',complete=False,cases=rows,scope='Finite quadrature and Jacobian checks, no global positivity proof, equilibrium rerun or strength validation.'),indent=2))
r=dict(date='2026-10-24',complete=True,cases=rows,seconds=time.time()-start,scope='Saved-field postprocessing only. Energy sensitivity does not bound stiffness or peak error. A finite 35-point lattice includes vertices/edges/faces but is not a global curved-element positivity certificate. Peak values at different sampling sets are not convergence proof.')
(O/'quadrature_mesh_audit.json').write_text(json.dumps(r,indent=2))
