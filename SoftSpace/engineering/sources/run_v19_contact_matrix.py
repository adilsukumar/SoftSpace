import json,time,sys
from pathlib import Path
import v19_contact_assembly as a
O=a.O;records=[]
for size in ['child_large','adult_small']:
 for h in [3.0,2.0]:
  m=a.prepare(size,h);print(json.dumps(dict(stage='model prepared',size=size,h=h,nodes=len(m['xt'])+len(m['xf']))),flush=True)
  cases=[(70,.1,2),(70,.1,-2),(140,.2,2),(140,.2,-2),(210,.3,2),(210,.3,-2)] if h==3 else [(140,.2,2),(140,.2,-2)]
  for p,mu,F in cases:
   start=time.time();name=size+'_joint_h'+str(h)+'_P'+str(p)+'_mu'+str(mu)+'_F'+str(F);path=O/(name+'.json')
   if path.exists():r=json.loads(path.read_text())
   else:
    try:
     r,u,n,t,reaction,force=a.solve(m,p,F,mu,max_iterations=80);r['converged']=True;a.np.savez_compressed(O/(name+'.npz'),xt=m['xt'],xf=m['xf'],tt=m['tt'],tf=m['tf'],u=u,normal=n,traction=t,reaction=reaction,force=force,contact_points=m['points'],contact_areas=m['areas'],contact_kinds=m['kinds'])
    except RuntimeError as error:r=dict(converged=False,error=str(error),history=getattr(error,'history',[]),preload_N=p,side_force_N=F,assumed_mu=mu)
    r.update(size=size,mesh_max_mm=h,source=m['row']['file'],source_sha256=m['row']['sha256'],elastic_E_MPa=3500,assumed_nu=.35,seconds=time.time()-start,rigid_translation_controls=m['rigid_controls']);path.write_text(json.dumps(r,indent=2))
   records.append(dict(file=str(path),size=size,h=h,preload=p,mu=mu,F=F,converged=r.get('converged',True)));(O/'joint_run_status.json').write_text(json.dumps(dict(cases=records,complete=False),indent=2));print(json.dumps(dict(case=name,converged=r.get('converged',True),seconds=time.time()-start)),flush=True)
(O/'joint_run_status.json').write_text(json.dumps(dict(cases=records,complete=True),indent=2))
