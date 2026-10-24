"""Recheck saved fields with a matrix-free pivot penalty and candidate spacer kinematics.
No new equilibrium solve. Candidate residual determines whether old fields are acceptable.
"""
from pathlib import Path
import sys,os,json,inspect,hashlib
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
from scipy.sparse import coo_matrix
np=q.np;a=q.a;O=P/'engineering-v22-results';src=inspect.getsource(a.prepare);assert 'baseK=(K+1e5*(C.T@C)).tocsr()' in src;exec(src.replace('baseK=(K+1e5*(C.T@C)).tocsr()','baseK=K'),a.__dict__)
z=np.load(O/'adult_fork_local_0.9_mesh.npz');m=a.prepare('adult_small',1.9,saved_meshes=[(z['xt'],z['tt']),(z['xf'],z['tf'])]);nd=m['K'].shape[0];rr=[];cc=[];vv=[]
for xyz,offset in [(z['xt'],0),(z['xf'],3*len(z['xt']))]:
 nodes=np.flatnonzero(abs(np.hypot(xyz[:,0],xyz[:,2]-m['row']['pivot_z_mm'])-2.15)<1e-5);H,dofs=a.fit_reference(xyz,nodes,m['row']['pivot_z_mm'])
 for index,component in enumerate([3,5]):rr.extend([index]*len(dofs));cc.extend((dofs+offset).tolist());vv.extend((.5*H[component]).tolist())
H=coo_matrix((vv,(rr,cc)),shape=(2,nd)).tocsr();w=m['washer'];gap=.5*np.sign(m['points'][w,1]);idx=np.arange(len(gap));L=coo_matrix((np.r_[-gap,gap],(np.r_[2*idx,2*idx+1],np.r_[np.ones(len(gap),int),np.zeros(len(gap),int)])),shape=(2*len(gap),2)).tocsr();rows=[]
for kind,side in [('original','outward'),('original','inward'),('corrected','outward'),('corrected','inward')]:
 path=O/(('adult_fork_local_0.9_' if kind=='original' else 'objective_spacer_')+side+'.npz')
 if not path.exists():continue
 z=np.load(path);u=z['u'];F=z['force'];free=m['free'];normal=10000*np.maximum(m['G']@u,0);normal_force=m['G'].T@(normal*m['areas']);pivot=np.zeros(nd)
 for i in range(5):ci=m['C'].getrow(i);pivot+=1e5*np.asarray(ci.T.toarray()).ravel()*float((ci@u)[0])
 bulk=m['K']@u;variants=[]
 for corrected in [False,True]:
  displacement=m['T']@u-(L@(H@u) if corrected else 0);trial=1000*displacement.reshape(-1,2);ratio=np.minimum(1,.2*normal[w]/np.maximum(np.linalg.norm(trial,axis=1),1e-20));tau=trial*ratio[:,None];weighted=(tau*m['areas'][w,None]).ravel();tforce=m['T'].T@weighted-(H.T@(L.T@weighted) if corrected else 0);res=bulk+pivot+normal_force+tforce-F;relative=float(np.linalg.norm(res[free])/np.linalg.norm(F[free]));variants.append(dict(candidate_corrected=corrected,relative_equilibrium_residual=relative,chosen_1e_7_equilibrium_check_pass=relative<1e-7,Coulomb_bound_error_MPa=float(max(np.linalg.norm(tau,axis=1)-.2*normal[w]))))
 positions=np.r_[z['xt'],z['xf']]-np.array([0,0,m['row']['pivot_z_mm']]);internal=z['reaction']+F;balance=float(np.linalg.norm(internal.reshape(-1,3).sum(axis=0)));moment=float(np.linalg.norm(np.cross(positions,internal.reshape(-1,3)).sum(axis=0)))
 rows.append(dict(kind=kind,direction=side,global_force_balance_N=balance,global_moment_balance_N_mm=moment,variants=variants,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest()));print(side,variants,flush=True)
r=dict(date='2026-10-24',complete=len(rows)==4,cases=rows,candidate_corrected_fields_satisfy_residual=all(x['variants'][1]['chosen_1e_7_equilibrium_check_pass'] for x in rows if x['kind']=='corrected'),method='Original pivot penalty evaluated as sum of five rank-one actions, avoiding dense C transpose C. Candidate mean bore rotation subtracts the finite separated-face offset from tangential slip.',scope='Saved-field residual recheck only, no new solve. Candidate virtual-spacer mechanics are an idealization, not resolved actual washer contact. Failure means a corrected equilibrium solve is still needed; kinematic invariance alone is insufficient.')
(O/'spacer_candidate_residual_check.json').write_text(json.dumps(r,indent=2))
