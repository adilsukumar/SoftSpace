import json,hashlib,gc
from pathlib import Path
import v19_contact_assembly as a
np=a.np;O=a.O;records=[];cache={}
for f in sorted(O.glob('*_joint_h*.json')):
 r=json.loads(f.read_text())
 if not r.get('converged',True):continue
 z=np.load(f.with_suffix('.npz'));key=(r['size'],r['mesh_max_mm'])
 if key not in cache:
  cache.clear();gc.collect();cache[key]=a.prepare(*key,saved_meshes=[(z['xt'],z['tt']),(z['xf'],z['tf'])])
 m=cache[key];u=z['u'];area=m['areas'];w=m['washer'];kn=r['normal_penalty_N_mm3'];kt=r['tangential_penalty_N_mm3'];q=m['G']@u;normal=kn*np.maximum(q,0)*area;trial=kt*(m['T']@u).reshape(-1,2);cap=r['assumed_mu']*kn*np.maximum(q[w],0);traction=trial*np.minimum(1,cap/np.maximum(np.linalg.norm(trial,axis=1),1e-20))[:,None];F=m['FP']*r['preload_N']+m['Fc']*r['side_force_N'];reaction=m['A']@u+m['G'].T@normal+m['T'].T@(traction*area[w,None]).ravel()-F;res=float(np.linalg.norm(reaction[m['free']])/np.linalg.norm(F[m['free']]));eq=float(np.linalg.norm((reaction+F).reshape(-1,3).sum(axis=0)));saved=float(max(np.max(abs(reaction-z['reaction'])),np.max(abs(normal-z['normal'])),np.max(abs(traction-z['traction'])),np.max(abs(F-z['force']))));assert res<2e-5 and eq<1e-7 and saved<1e-8
 source=Path(r['source']);assert hashlib.sha256(source.read_bytes()).hexdigest()==r['source_sha256']
 # Affine strain patch control: tetrahedra must reproduce an imposed constant strain.
 affine=np.array([[.001,.0002,0],[.0002,-.0003,.0001],[0,.0001,.0004]]);expected=np.array([.001,-.0003,.0004,.0004,.0002,0]);err=0
 for x,t,B,d in [(m['xt'],m['tt'],m['B1'],m['d1']),(m['xf'],m['tf'],m['B2'],m['d2'])]:
  uu=(x@affine.T).ravel();strain=np.einsum('eai,ei->ea',B,uu[d]);err=max(err,float(np.max(abs(strain-expected))))
 assert err<1e-10
 records.append(dict(file=str(f),nodes=len(m['xt'])+len(m['xf']),residual_recomputed=res,force_balance_N=eq,saved_array_error=saved,affine_strain_patch_error=err,source_sha256='pass',status='pass'));print(f.name,'audited',flush=True)
comparisons=[]
for size in ['child_large','adult_small']:
 rr=[]
 for h in [3.,2.,1.4,1.0,.8]:
  f=O/(size+'_joint_h'+str(h)+'_P140_mu0.2_F2.json')
  if f.exists():
   result=json.loads(f.read_text())
   if result.get('converged',True):rr.append(result)
 for x,y in zip(rr,rr[1:]):
  change=abs(y['cup_mean_displacement_x_mm']/x['cup_mean_displacement_x_mm']-1)*100;comparisons.append(dict(size=size,from_h=x['mesh_max_mm'],to_h=y['mesh_max_mm'],displacement_change_percent=change,chosen_5_percent_gate_pass=change<5))
(O/'joint_verification.json').write_text(json.dumps(dict(array_audits=records,all_recorded_arrays_pass=bool(records) and all(r['status']=='pass' for r in records),mesh_comparisons=comparisons,scope='Reassembled matrices and contact laws from saved mesh arrays, affine strain control and source hash verification. Same model equations, not an independent solver or physical validation. Full assembly, bearing clearance, threads and measured friction are absent.'),indent=2))
