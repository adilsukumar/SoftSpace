"""Retry a nearly converged outward case; preserve the original failed iteration limit."""
import json,shutil,time
import v19_contact_assembly as a
O=a.O;D=O/'iteration-limit-trials';D.mkdir(exist_ok=True)
for size,F in [('adult_small',2),('child_large',-2),('adult_small',-2)]:
 name=size+'_joint_h3.0_P70_mu0.1_F'+str(F);path=O/(name+'.json');old=json.loads(path.read_text())
 if old.get('converged',True):continue
 if not (D/path.name).exists():shutil.copy2(path,D/path.name)
 m=a.prepare(size,3);start=time.time()
 try:
  r,u,n,t,reaction,force=a.solve(m,70,F,.1,max_iterations=240);r['converged']=True;a.np.savez_compressed(O/(name+'.npz'),xt=m['xt'],xf=m['xf'],tt=m['tt'],tf=m['tf'],u=u,normal=n,traction=t,reaction=reaction,force=force,contact_points=m['points'],contact_areas=m['areas'],contact_kinds=m['kinds'])
 except RuntimeError as e:r=dict(converged=False,error=str(e),history=getattr(e,'history',[]))
 r.update(size=size,mesh_max_mm=3.,preload_N=70,side_force_N=F,assumed_mu=.1,source=m['row']['file'],source_sha256=m['row']['sha256'],elastic_E_MPa=3500,assumed_nu=.35,seconds=time.time()-start,rigid_translation_controls=m['rigid_controls'],iteration_limit=240,prior_failed_iteration_limit_preserved=str(D/path.name));path.write_text(json.dumps(r,indent=2));print(name,r.get('converged'),r.get('iterations'),flush=True)
s=json.loads((O/'joint_run_status.json').read_text())
for c in s['cases']:c['converged']=json.loads(a.Path(c['file']).read_text()).get('converged',True)
(O/'joint_run_status.json').write_text(json.dumps(s,indent=2))
