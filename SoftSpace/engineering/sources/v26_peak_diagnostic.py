from pathlib import Path
import os,sys,json,hashlib,itertools
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
np=q.np;O=P/'engineering-v26-results';O.mkdir(exist_ok=True)
records=[]
for h in [1.9,1.5]:
 f=P/'engineering-v25-results'/f'child_large_h{h}_outward.npz';z=np.load(f);split=3*len(z['xt'])
 for component,x,t,u in [('tongue',z['xt'],z['tt'],z['u'][:split]),('fork',z['xf'],z['tf'],z['u'][split:])]:
  ue=u.reshape(-1,3)[t];best={}
  for method,points in [('interior125',[L for L,w in q.quadrature(5)]),('boundary35',[np.array([4-sum(v),*v])/4 for v in itertools.product(range(5),repeat=3) if sum(v)<=4])]:
   peaks=np.zeros(len(t));locations=np.zeros((len(t),3));bary=np.zeros((len(t),4));quality=np.zeros(len(t))
   for L in points:
    B,det=q.strain_matrix(x,t,L);_,_,D,_,_= (None,None,np.zeros((6,6)),None,None)
    E=3500.;nu=.35;mu=E/2/(1+nu);lam=E*nu/((1+nu)*(1-2*nu));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*mu);D[3:,3:]=np.eye(3)*mu
    s=np.einsum('ab,ebi,ei->ea',D,B,ue.reshape(-1,30),optimize=True);xx,yy,zz,xy,yz,xz=s.T;vm=np.sqrt(((xx-yy)**2+(yy-zz)**2+(zz-xx)**2)/2+3*(xy*xy+yz*yz+xz*xz));take=vm>peaks
    N=np.r_[L*(2*L-1),[4*L[i]*L[j] for i,j in q.edges]];peaks[take]=vm[take];locations[take]=np.einsum('i,eia->ea',N,x[t[take]]);bary[take]=L;quality[take]=det[take]
   top=np.argsort(peaks)[-10:][::-1];best[method]=[dict(element=int(i),peak_MPa=float(peaks[i]),xyz_mm=locations[i].tolist(),barycentric=bary[i].tolist(),Jacobian=float(quality[i]),nodes=t[i].tolist()) for i in top]
  records.append(dict(h_mm=h,component=component,raw_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),peaks=best));print(h,component,{k:v[0] for k,v in best.items()},flush=True)
(O/'peak_location_diagnostic.json').write_text(json.dumps(dict(records=records,scope='Location diagnostic of saved V25 reference fields only. Not a product pass.'),indent=2))
