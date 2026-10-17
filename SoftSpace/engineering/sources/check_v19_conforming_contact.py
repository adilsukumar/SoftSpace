"""Improve contact-domain quadrature using washer-boundary surface partitions.
Earlier masking cases remain untouched. This is a numerical model variant only.
"""
import json,time,hashlib
import v19_contact_assembly as a
O=a.O/'conforming-contact';O.mkdir(exist_ok=True);records=[]
for size in ['child_large','adult_small']:
 previous=None
 for h in [3.,2.,1.4,1.0]:
  path=O/(size+'_h'+str(h)+'.json')
  if path.exists():r=json.loads(path.read_text())
  else:
   start=time.time();row,meshes=a.mesh(size,h,conforming=True);nodes=sum(len(x) for x,t in meshes)
   if nodes>30000:break
   m=a.prepare(size,h,saved_meshes=meshes);print(size,h,'prepared',nodes,flush=True)
   try:
    r,u,n,t,reaction,F=a.solve(m,140,2,.2,max_iterations=120);r['converged']=True;a.np.savez_compressed(path.with_suffix('.npz'),xt=m['xt'],xf=m['xf'],tt=m['tt'],tf=m['tf'],u=u,normal=n,traction=t,reaction=reaction,force=F,contact_points=m['points'],contact_areas=m['areas'],contact_kinds=m['kinds'])
   except RuntimeError as e:r=dict(converged=False,error=str(e),history=getattr(e,'history',[]))
   r.update(size=size,mesh_max_mm=h,source=row['file'],source_sha256=row['sha256'],nodes=nodes,seconds=time.time()-start,washer_boundary_partitioned=True,preload_N=140,side_force_N=2,assumed_mu=.2,elastic_E_MPa=3500,assumed_nu=.35);path.write_text(json.dumps(r,indent=2));print(size,h,r.get('cup_mean_displacement_x_mm'),flush=True)
  if not r.get('converged'):break
  if previous:
   change=abs(r['cup_mean_displacement_x_mm']/previous['cup_mean_displacement_x_mm']-1)*100;r['previous_mesh_displacement_change_percent']=change;r['chosen_5_percent_gate_pass']=change<5;path.write_text(json.dumps(r,indent=2))
  records.append(dict(file=str(path),size=size,h=h,change_percent=r.get('previous_mesh_displacement_change_percent'),gate=r.get('chosen_5_percent_gate_pass')));(O/'status.json').write_text(json.dumps(dict(cases=records,complete=False,scope='Nominal outward joint numerical variant with geometry-aligned washer annulus partitions. No complete joint or physical validation.'),indent=2));previous=r
  if h<=2 and r.get('chosen_5_percent_gate_pass'):break
(O/'status.json').write_text(json.dumps(dict(cases=records,complete=True,scope='Nominal outward joint numerical variant with geometry-aligned washer annulus partitions. No complete joint or physical validation.'),indent=2))
