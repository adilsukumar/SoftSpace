"""Check contact operators under infinitesimal common rigid-body motion.
Assembly uses zero bulk matrices only to obtain G/T/C; no equilibrium solve is claimed.
"""
from pathlib import Path
import sys,os,json,hashlib
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
from scipy.sparse import csr_matrix,coo_matrix
np=q.np;a=q.a;O=P/'engineering-v22-results'
def zero_bulk(x,t):return csr_matrix((3*len(x),3*len(x))),None,None,None,np.zeros(len(t))
a.elasticity=zero_bulk
# G/T/C do not require explicitly materializing the dense rank-five pivot penalty.
import inspect
prepare_source=inspect.getsource(a.prepare)
assert 'baseK=(K+1e5*(C.T@C)).tocsr()' in prepare_source
exec(prepare_source.replace('baseK=(K+1e5*(C.T@C)).tocsr()','baseK=K'),a.__dict__)
rows=[]
for size in ['child_large','adult_small']:
 source=P/'engineering-v21-results/refinement'/(size+'_h1.9_mesh.npz');z=np.load(source);m=a.prepare(size,1.9,saved_meshes=[(z['xt'],z['tt']),(z['xf'],z['tf'])]);x=np.r_[z['xt'],z['xf']];pivot=np.array([0,0,m['row']['pivot_z_mm']]);cases=[]
 # Candidate virtual-spacer mean rotation. This is an explicit idealization,
 # not a resolved material washer or a validated physical contact law.
 rotrows=[];rotcols=[];rotvals=[]
 for xyz,offset in [(z['xt'],0),(z['xf'],3*len(z['xt']))]:
  nodes=np.flatnonzero(abs(np.hypot(xyz[:,0],xyz[:,2]-pivot[2])-2.15)<1e-5);H,dofs=a.fit_reference(xyz,nodes,pivot[2])
  for index,component in enumerate([3,5]):
   rotrows.extend([index]*len(dofs));rotcols.extend((dofs+offset).tolist());rotvals.extend((.5*H[component]).tolist())
 Hmean=coo_matrix((rotvals,(rotrows,rotcols)),shape=(2,3*len(x))).tocsr();gap=.5*np.sign(m['points'][m['washer'],1]);idx=np.arange(len(gap));L=coo_matrix((np.r_[-gap,gap],(np.r_[2*idx,2*idx+1],np.r_[np.ones(len(gap),int),np.zeros(len(gap),int)])),shape=(2*len(gap),2)).tocsr()
 corrected_cases=[]
 for kind in ['translation','rotation']:
  for axis in range(3):
   v=np.eye(3)[axis];u=np.tile(v,(len(x),1)) if kind=='translation' else np.cross(v,x-pivot);u=u.ravel();normal=float(abs(m['G']@u).max());slip=float(abs(m['T']@u).max());connector=float(abs(m['C']@u).max());cases.append(dict(kind=kind,axis='XYZ'[axis],maximum_normal_operator_motion=normal,maximum_tangential_operator_motion=slip,maximum_relative_pivot_constraint_motion=connector,chosen_1e_8_zero_motion_pass=max(normal,slip,connector)<1e-8));corrected=float(abs(m['T']@u-L@(Hmean@u)).max());corrected_cases.append(dict(kind=kind,axis='XYZ'[axis],maximum_tangential_motion=corrected,chosen_1e_8_zero_motion_pass=max(normal,corrected,connector)<1e-8))
 rows.append(dict(size=size,cases=cases,corrected_candidate_cases=corrected_cases,source_mesh_sha256=hashlib.sha256(source.read_bytes()).hexdigest()));print(size,cases,flush=True)
 del m

r=dict(date='2026-10-24',cases=rows,complete=True,corrected_candidate_all_rigid_motion_checks_pass=all(c['chosen_1e_8_zero_motion_pass'] for r in rows for c in r['corrected_candidate_cases']),all_common_rigid_motion_checks_pass=all(c['chosen_1e_8_zero_motion_pass'] for r in rows for c in r['cases']),units='Translations in mm per mm of common translation; rotations in mm per radian of infinitesimal common rotation. Rotation basis is a linearized invariance test, not an imposed finite movement.',scope='Contact and pivot operators only. Bulk stiffness replaced by zero solely to obtain operators cheaply; no FE equilibrium result. A failure indicates the virtual separated-face friction kinematics are not generally objective, not that physical parts broke. Actual washer/spacer contact is not resolved. The candidate subtracts the 0.5 mm separated-face offset cross the mean best-fit bore rotation. Candidate kinematic checks do not establish equilibrium, stress or physical washer behaviour.')
(O/'contact_rigid_motion_controls.json').write_text(json.dumps(r,indent=2))
