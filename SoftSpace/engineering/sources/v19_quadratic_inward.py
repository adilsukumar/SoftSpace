"""Extend the verified quadratic meshes to an inward reference load.

Reuse exactly the saved outward meshes; preserve failures and all original evidence.
This is an assumed-material ideal-pivot fixture, not a physical product test.
"""
import json,time,gc,hashlib
from pathlib import Path
import v19_quadratic_joint as q
a=q.a;np=q.np;O=a.O/'quadratic-inward';O.mkdir(exist_ok=True)
records=[]
for size in ['child_large','adult_small']:
 previous=None
 for h in [3.,2.3]:
  path=O/(size+'_h'+str(h)+'.json');source=q.O/path.name
  if path.exists():r=json.loads(path.read_text())
  else:
   start=time.time();reference=json.loads(source.read_text());z=np.load(source.with_suffix('.npz'))
   m=a.prepare(size,h,saved_meshes=[(z['xt'],z['tt']),(z['xf'],z['tf'])]);print(size,h,'prepared',flush=True)
   try:
    r,u,n,t,reaction,F=a.solve(m,140,-2,.2,max_iterations=240);r['converged']=True
    np.savez_compressed(path.with_suffix('.npz'),xt=m['xt'],xf=m['xf'],tt=m['tt'],tf=m['tf'],u=u,normal=n,traction=t,reaction=reaction,force=F,contact_points=m['points'],contact_areas=m['areas'],contact_kinds=m['kinds'])
   except RuntimeError as e:r=dict(converged=False,error=str(e),history=getattr(e,'history',[]))
   for key in ['source','source_sha256','nodes','bulk_element','contact_interpolation','boundary_partitions','stress_sampling','quadrature','elastic_E_MPa','assumed_nu','exact_CAD_component_volumes_mm3','quadrature_component_volumes_mm3']:r[key]=reference[key]
   r.update(size=size,mesh_max_mm=h,preload_N=140,side_force_N=-2,assumed_mu=.2,seconds=time.time()-start,mesh_source=str(source.with_suffix('.npz')),mesh_source_sha256=hashlib.sha256(source.with_suffix('.npz').read_bytes()).hexdigest(),maximum_iterations=240)
   path.write_text(json.dumps(r,indent=2));print(size,h,r.get('cup_mean_displacement_x_mm',r.get('error')),flush=True)
   del m;gc.collect()
  if previous and r.get('converged') and previous.get('converged'):
   r['displacement_change_percent']=abs(r['cup_mean_displacement_x_mm']/previous['cup_mean_displacement_x_mm']-1)*100;r['chosen_5_percent_gate_pass']=r['displacement_change_percent']<5;path.write_text(json.dumps(r,indent=2))
  records.append(dict(file=str(path),size=size,h=h,converged=r.get('converged'),change_percent=r.get('displacement_change_percent'),gate=r.get('chosen_5_percent_gate_pass')))
  (O/'status.json').write_text(json.dumps(dict(cases=records,complete=False,whole_joint_validated=False),indent=2));previous=r
(O/'status.json').write_text(json.dumps(dict(cases=records,complete=True,whole_joint_validated=False,scope='Inward 2 N reference fixture, 140 N prescribed preload, assumed friction 0.2 and PA66 elastic reference. Same saved Tet10 meshes as outward cases. No resolved bolt, bearing clearance, creep or full worn model.'),indent=2))
