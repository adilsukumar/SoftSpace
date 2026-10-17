import json,hashlib,gc,sys
from pathlib import Path
import v19_quadratic_joint as q
a=q.a;np=q.np;O=Path(sys.argv[1]) if len(sys.argv)>1 else q.O;records=[]
for f in sorted(O.glob('*_h*.json')):
 r=json.loads(f.read_text())
 if not r.get('converged'):continue
 if r.get('mesh_source'):
  mesh_source=Path(r['mesh_source']);assert hashlib.sha256(mesh_source.read_bytes()).hexdigest()==r['mesh_source_sha256']
  with np.load(mesh_source) as original,np.load(f.with_suffix('.npz')) as current:
   for key in ['xt','xf','tt','tf']:assert np.array_equal(original[key],current[key]),('Mesh reuse mismatch',key)
 z=np.load(f.with_suffix('.npz'));m=a.prepare(r['size'],r['mesh_max_mm'],saved_meshes=[(z['xt'],z['tt']),(z['xf'],z['tf'])]);u=z['u'];area=m['areas'];w=m['washer'];gap=m['G']@u;normal=r['normal_penalty_N_mm3']*np.maximum(gap,0)*area;t=r['tangential_penalty_N_mm3']*(m['T']@u).reshape(-1,2);cap=r['assumed_mu']*r['normal_penalty_N_mm3']*np.maximum(gap[w],0);traction=t*np.minimum(1,cap/np.maximum(np.linalg.norm(t,axis=1),1e-20))[:,None];F=m['FP']*r['preload_N']+m['Fc']*r['side_force_N'];reaction=m['A']@u+m['G'].T@normal+m['T'].T@(traction*area[w,None]).ravel()-F;res=float(np.linalg.norm(reaction[m['free']])/np.linalg.norm(F[m['free']]));balance=float(np.linalg.norm((reaction+F).reshape(-1,3).sum(axis=0)));err=float(max(np.max(abs(reaction-z['reaction'])),np.max(abs(normal-z['normal'])),np.max(abs(traction-z['traction']))));volume_error=[abs(v/c-1)*100 for v,c in zip([m['vol1'].sum(),m['vol2'].sum()],r['exact_CAD_component_volumes_mm3'])];assert hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['source_sha256'];assert res<2e-5 and balance<1e-7 and err<1e-8 and max(volume_error)<1,(res,balance,err,volume_error)
 records.append(dict(file=str(f),residual_recomputed=res,force_balance_N=balance,saved_array_error=err,CAD_volume_error_percent=volume_error,status='pass'));print(f.name,'audited',flush=True);del m;gc.collect()
s=json.loads((O/'status.json').read_text());(O/'verification.json').write_text(json.dumps(dict(array_audits=records,element_controls=json.loads((q.O/'element_controls.json').read_text()),mesh_comparisons=[r for r in s['cases'] if r['change_percent'] is not None],scope='Same-equation reassembly and saved-array checks, source hashes, reference CAD volumes and analytic element controls. No independent physical validation. Centroid stress samples only.'),indent=2))
