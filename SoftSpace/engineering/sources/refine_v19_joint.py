"""One further outward-load refinement per family, with saved arrays and no automatic pass."""
import json,time
import v19_contact_assembly as a
for size in ['child_large','adult_small']:
 previous=json.loads((a.O/(size+'_joint_h2.0_P140_mu0.2_F2.json')).read_text())
 for h in [1.4,1.0,.8]:
  name=size+'_joint_h'+str(h)+'_P140_mu0.2_F2';path=a.O/(name+'.json')
  if path.exists():r=json.loads(path.read_text())
  else:
   start=time.time();row,meshes=a.mesh(size,h);nodes=sum(len(x) for x,t in meshes)
   if nodes>30000:
    (a.O/(size+'_refinement_resource_limit.json')).write_text(json.dumps(dict(mesh_mm=h,nodes=nodes,limit_nodes=30000,status='Not solved',reason='Bounded 90000 DOF limit for sparse direct contact solve on the shared laptop',mesh_gate_pass=False),indent=2));print(size,'resource limit',nodes,flush=True);break
   m=a.prepare(size,h,saved_meshes=meshes);print(size,'prepared',nodes,flush=True)
   try:
    r,u,n,t,reaction,F=a.solve(m,140,2,.2,max_iterations=80);r['converged']=True;a.np.savez_compressed(a.O/(name+'.npz'),xt=m['xt'],xf=m['xf'],tt=m['tt'],tf=m['tf'],u=u,normal=n,traction=t,reaction=reaction,force=F,contact_points=m['points'],contact_areas=m['areas'],contact_kinds=m['kinds'])
   except RuntimeError as e:r=dict(converged=False,error=str(e),history=getattr(e,'history',[]))
   r.update(size=size,mesh_max_mm=h,preload_N=140,side_force_N=2,assumed_mu=.2,source=m['row']['file'],source_sha256=m['row']['sha256'],elastic_E_MPa=3500,assumed_nu=.35,seconds=time.time()-start,rigid_translation_controls=m['rigid_controls']);path.write_text(json.dumps(r,indent=2));print(size,r.get('cup_mean_displacement_x_mm'),flush=True)
  if not r.get('converged',True):break
  change=abs(r['cup_mean_displacement_x_mm']/previous['cup_mean_displacement_x_mm']-1)
  previous=r
  if change<.05:break
