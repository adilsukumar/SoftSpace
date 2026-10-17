"""Conditional 3D two-flexible-body hinge assembly with stop/washer contact.
Rigid distributing pivot connector and prescribed bolt preload replace pin/thread solids.
This is explicitly not a resolved threaded-fastener or whole-headset contact model.
"""
import os,sys,json,math,time
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1'
from v12_geometry import P,gmsh,import_parts
import numpy as np
from scipy.sparse import coo_matrix,csr_matrix,block_diag,diags
from scipy.sparse.linalg import spsolve,splu
from scipy.spatial import cKDTree
O=P/'engineering-v19-results';O.mkdir(exist_ok=True)

def elasticity(x,t,E=3500,nu=.35):
 n=len(x);r=np.array([[-1,-1,-1],[1,0,0],[0,1,0],[0,0,1.]])
 J=np.einsum('eia,ib->eab',x[t],r);det=np.linalg.det(J);assert np.min(det)>0;g=np.einsum('ib,eba->eia',r,np.linalg.inv(J));B=np.zeros((len(t),6,12));B[:,0,0::3]=g[:,:,0];B[:,1,1::3]=g[:,:,1];B[:,2,2::3]=g[:,:,2];B[:,3,0::3]=g[:,:,1];B[:,3,1::3]=g[:,:,0];B[:,4,1::3]=g[:,:,2];B[:,4,2::3]=g[:,:,1];B[:,5,0::3]=g[:,:,2];B[:,5,2::3]=g[:,:,0]
 lam=E*nu/((1+nu)*(1-2*nu));mu=E/(2*(1+nu));D=np.zeros((6,6));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*mu);D[3:,3:]=np.eye(3)*mu;ke=np.einsum('eai,ab,ebj,e->eij',B,D,B,det/6,optimize=True);dofs=(t[:,:,None]*3+np.arange(3)).reshape(-1,12);K=coo_matrix((ke.ravel(),(np.broadcast_to(dofs[:,:,None],ke.shape).ravel(),np.broadcast_to(dofs[:,None,:],ke.shape).ravel())),shape=(3*n,3*n)).tocsr();return K,B,D,dofs,det/6

def boundary(t):
 faces=np.concatenate([t[:,v] for v in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]]);_,idx,c=np.unique(np.sort(faces,axis=1),axis=0,return_index=True,return_counts=True);return faces[idx[c==1]]

def mesh(size,h,conforming=False,order=1,optimize_high_order=False):
 row=json.loads((O/(size+'_cad_report.json')).read_text());R=next(r['band_halfspan_mm'] for r in json.loads((P/'lower-crown-recipes.json').read_text()) if r['name']==size);gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);parts=import_parts(row);occ=gmsh.model.occ;keep=[parts['RightTongue'],parts['RightFork']];occ.remove([dt for dt in gmsh.model.getEntities(3) if dt not in keep],recursive=True);occ.translate(keep,-R,0,0)
 result,_=occ.cut([keep[0]],[(3,occ.addBox(-20,-40,row['guide_bottom_mm'],55,80,70))]);tongue=[dt for dt in result if dt[0]==3];assert len(tongue)==1;keep=[tongue[0],keep[1]]
 # Partition both actual stop faces into the same nominal rectangle.
 for i,body in enumerate(keep):
  patches=[(2,occ.addRectangle(8,a,row['pivot_z_mm'],4,b-a)) for a,b in [(-row['fork_outer_halfspacing_mm'],-row['fork_inner_halfspacing_mm']),(row['fork_inner_halfspacing_mm'],row['fork_outer_halfspacing_mm'])]];res,_=occ.fragment([body],patches);v=[dt for dt in res if dt[0]==3];assert len(v)==1;keep[i]=v[0]
 if conforming:
  for i,body in enumerate(keep):
   face_y=row['fork_inner_halfspacing_mm']-(.5 if i==0 else 0)
   disks=[(2,occ.addDisk(0,sign*face_y,row['pivot_z_mm'],5.5,5.5,zAxis=[0,1,0],xAxis=[1,0,0])) for sign in [-1,1]]
   if conforming==2 and i==1:disks.extend((2,occ.addDisk(0,sign*row['fork_outer_halfspacing_mm'],row['pivot_z_mm'],6,6,zAxis=[0,1,0],xAxis=[1,0,0])) for sign in [-1,1])
   res,_=occ.fragment([body],disks);v=[dt for dt in res if dt[0]==3];assert len(v)==1;keep[i]=v[0]
 row=dict(row,finite_element_reference_volumes_mm3=[occ.getMass(*body) for body in keep])
 occ.synchronize();gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',h*.4);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',16);gmsh.model.mesh.generate(3)
 if order==2:
  gmsh.model.mesh.setOrder(2)
  if optimize_high_order:gmsh.model.mesh.optimize('HighOrder')
 tags,xyz,_=gmsh.model.mesh.getNodes();allx=np.array(xyz).reshape(-1,3);lookup={int(k):i for i,k in enumerate(tags)};out=[]
 for body in keep:
  _,con=gmsh.model.mesh.getElementsByType(4 if order==1 else 11,body[1]);t=np.array([lookup[int(i)] for i in con],np.int32).reshape(-1,4 if order==1 else 10);used=np.unique(t);remap=np.full(len(allx),-1);remap[used]=np.arange(len(used));out.append((allx[used],remap[t]))
 gmsh.finalize();return row,out

def plane_faces(x,faces,axis,value):return faces[np.all(abs(x[faces,axis]-value)<1e-6,axis=1)]
Q=np.array([[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]])

def contact_pair(xf,ff,xt,ft,coords,normal,offset,kind,radial=None):
 tri=xt[ft][:,:,coords];cent=tri.mean(axis=1);tree=cKDTree(cent);origin=tri[:,0];inv=np.linalg.inv(np.transpose(tri[:,1:]-tri[:,:1],(0,2,1)));rows=[];cols=[];vals=[];areas=[];tangents=[];kinds=[];points=[]
 for face in ff:
  points3=xf[face];area=np.linalg.norm(np.cross(points3[1]-points3[0],points3[2]-points3[0]))/2
  for ns in Q:
   pt=ns@points3
   if radial is not None and not radial[0]**2<=pt[0]**2+(pt[2]-radial[2])**2<=radial[1]**2:continue
   _,candidates=tree.query(pt[coords],k=min(30,len(ft)));chosen=None
   for j in np.atleast_1d(candidates):
    uv=inv[j]@(pt[coords]-origin[j]);nm=np.array([1-uv.sum(),uv[0],uv[1]])
    if nm.min()>-1e-7:chosen=(ft[j],nm);break
   if chosen is None:raise RuntimeError('Contact projection failed '+kind)
   master,nm=chosen;idx=len(areas);areas.append(area/3);points.append(pt);kinds.append(kind)
   for node,N in zip(face,ns):
    for axis,value in enumerate(normal):
     if value:rows.append(idx);cols.append(offset+3*int(node)+axis);vals.append(N*value)
   for node,N in zip(master,nm):
    for axis,value in enumerate(normal):
     if value:rows.append(idx);cols.append(3*int(node)+axis);vals.append(-N*value)
   tangents.append((face.copy(),ns.copy(),master.copy(),nm.copy()))
 return rows,cols,vals,areas,points,kinds,tangents

def fit_reference(x,nodes,pivot):
 R=np.zeros((3*len(nodes),6))
 for i,node in enumerate(nodes):
  a,b,c=x[node]-np.array([0,0,pivot]);R[3*i:3*i+3,:3]=np.eye(3);R[3*i:3*i+3,3:]=[[0,c,-b],[-c,0,a],[b,-a,0]]
 H=np.linalg.solve(R.T@R,R.T);return H,(nodes[:,None]*3+np.arange(3)).ravel()

def prepare(size,h,saved_meshes=None):
 if saved_meshes is None:row,meshes=mesh(size,h)
 else:row=json.loads((O/(size+'_cad_report.json')).read_text());meshes=saved_meshes
 (xt,tt),(xf,tf)=meshes;pivot=row['pivot_z_mm'];inner=row['fork_inner_halfspacing_mm'];outer=row['fork_outer_halfspacing_mm'];nt=len(xt);offset=3*nt;nd=3*(nt+len(xf));bt=boundary(tt);bf=boundary(tf);K1,B1,D1,d1,v1=elasticity(xt,tt);K2,B2,D2,d2,v2=elasticity(xf,tf);K=block_diag([K1,K2],format='csr');del K1,K2;fixed=(np.flatnonzero(abs(xt[:,2]-row['guide_bottom_mm'])<1e-6)[:,None]*3+np.arange(3)).ravel();assert len(fixed)>0
 normalrows=[];normalcols=[];normalvals=[];areas=[];points=[];kinds=[];tangentdata=[]
 pairs=[]
 for sign in [-1,1]:pairs.append((plane_faces(xf,bf,1,sign*inner),plane_faces(xt,bt,1,sign*(inner-.5)),[0,2],[0,-sign,0],'washer',(2.15,5.5,pivot)))
 pairs.append((plane_faces(xf,bf,2,pivot),plane_faces(xt,bt,2,pivot),[0,1],[0,0,1],'stop',None))
 for ff,ft,coords,n,kind,radial in pairs:
  if kind=='stop':
   ff=ff[np.all((xf[ff,0]>=8-1e-6)&(xf[ff,0]<=12+1e-6),axis=1)];ft=ft[np.all((xt[ft,0]>=8-1e-6)&(xt[ft,0]<=12+1e-6),axis=1)]
  assert len(ff) and len(ft),(kind,len(ff),len(ft));r,c,val,a,p,k,t=contact_pair(xf,ff,xt,ft,coords,n,offset,kind,radial);base=len(areas);normalrows.extend([i+base for i in r]);normalcols.extend(c);normalvals.extend(val);areas.extend(a);points.extend(p);kinds.extend(k);tangentdata.extend(t)
 G=coo_matrix((normalvals,(normalrows,normalcols)),shape=(len(areas),nd)).tocsr();areas=np.array(areas);kinds=np.array(kinds);points=np.array(points);washer=np.flatnonzero(kinds=='washer');tr=[];tc=[];tv=[]
 for j,index in enumerate(washer):
  f,ns,m,nm=tangentdata[index]
  for k,axis in enumerate([0,2]):
   for node,N in zip(f,ns):tr.append(2*j+k);tc.append(offset+3*int(node)+axis);tv.append(N)
   for node,N in zip(m,nm):tr.append(2*j+k);tc.append(3*int(node)+axis);tv.append(-N)
 T=coo_matrix((tv,(tr,tc)),shape=(2*len(washer),nd)).tocsr()
 # Best-fit relative pivot translation and X/Z rotation constraints; Y rotation remains free.
 radt=np.hypot(xt[:,0],xt[:,2]-pivot);radf=np.hypot(xf[:,0],xf[:,2]-pivot);tn=np.flatnonzero(abs(radt-2.15)<1e-5);fn=np.flatnonzero(abs(radf-2.15)<1e-5);assert len(tn)>10 and len(fn)>10;Ht,it=fit_reference(xt,tn,pivot);Hf,jf=fit_reference(xf,fn,pivot);Cr=[];Cc=[];Cv=[]
 for i,axis in enumerate([0,1,2,3,5]):
  scale=1 if axis<3 else 10
  Cr.extend([i]*len(it));Cc.extend(it);Cv.extend(-scale*Ht[axis]);Cr.extend([i]*len(jf));Cc.extend(offset+jf);Cv.extend(scale*Hf[axis])
 C=coo_matrix((Cv,(Cr,Cc)),shape=(5,nd)).tocsr();free=np.setdiff1d(np.arange(nd),fixed);baseK=(K+1e5*(C.T@C)).tocsr();FP=np.zeros(nd);Fc=np.zeros(nd)
 # Prescribed compressive preload on outer fork circular backup-washer footprints.
 for sign in [-1,1]:
  ff=plane_faces(xf,bf,1,sign*outer);weights=np.zeros(len(xf))
  for face in ff:
   tri=xf[face];area=np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))/2
   for N in Q:
    p=N@tri
    if 2.15**2<=p[0]**2+(p[2]-pivot)**2<=6**2:weights[face]+=N*area/3
  assert weights.sum()>80;FP[offset+1::3]+=-sign*weights/weights.sum()
 cupfaces=bf[np.all(abs(np.hypot(xf[bf,0]-20,xf[bf,2]-35)-2.1)<1e-5,axis=1)];weights=np.zeros(len(xf))
 for face in cupfaces:
  tri=xf[face];area=np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))/2;weights[face]+=area/3
 assert weights.sum()>140;Fc[offset::3]=weights/weights.sum()
 # Rigid translations/rotations must have negligible bulk elastic energy.
 xyz=np.concatenate([xt,xf]);rigid=[]
 for axis in range(3):
  u=np.zeros(nd);u[axis::3]=1;rigid.append(float(np.linalg.norm(K@u)/max(np.linalg.norm(K.data),1)))
 assert max(rigid)<1e-12
 return dict(row=row,xt=xt,xf=xf,tt=tt,tf=tf,K=K,A=baseK,G=G,T=T,C=C,areas=areas,points=points,kinds=kinds,washer=washer,free=free,fixed=fixed,FP=FP,Fc=Fc,B1=B1,B2=B2,D1=D1,D2=D2,d1=d1,d2=d2,vol1=v1,vol2=v2,rigid_controls=rigid)

def solve(model,preload=140,side_force=2,mu=.2,kn=10000,kt=1000,solver='woodbury',max_iterations=160):
 G=model['G'];T=model['T'];area=model['areas'];w=model['washer'];free=model['free'];F=model['FP']*preload+model['Fc']*side_force;u=np.zeros(len(F));active=np.ones(len(area),bool);fric=np.ones(len(w));history=[]
 for it in range(max_iterations):
  contactK=G.T@diags(kn*area*active)@G+T.T@diags(np.repeat(kt*area[w]*fric,2))@T;trial=np.zeros(len(F))
  if solver=='woodbury':
   A0=(model['K']+contactK)[free][:,free].tocsc();C=model['C'][:,free].toarray();Y=splu(A0).solve(np.column_stack([F[free],C.T]));b=Y[:,0];Z=Y[:,1:];trial[free]=b-Z@np.linalg.solve(np.eye(5)/1e5+C@Z,C@b)
  else:
   Ka=model['A']+contactK;trial[free]=spsolve(Ka[free][:,free].tocsc(),F[free])
  q=G@trial;pressure=kn*np.maximum(q,0);t=kt*(T@trial).reshape(-1,2);norm=np.linalg.norm(t,axis=1);target=np.minimum(1,mu*pressure[w]/np.maximum(norm,1e-20));newactive=q>0;newfric=.5*fric+.5*target;du=np.linalg.norm(trial-u)/max(np.linalg.norm(trial),1e-15);actual=model['A']@trial+G.T@(pressure*area)+T.T@(t*target[:,None]*area[w,None]).ravel()-F;equilibrium=np.linalg.norm(actual[free])/max(np.linalg.norm(F[free]),1e-12);history.append(dict(iteration=it,relative_u_change=float(du),relative_equilibrium_residual=float(equilibrium),active=int(newactive.sum()),slip_points=int((target<.999).sum())));u=trial
  if np.array_equal(newactive,active) and equilibrium<1e-6 and du<1e-5:break
  active=newactive;fric=newfric
 else:
  failure=RuntimeError('Assembly contact iteration did not converge; no static equilibrium pass')
  failure.history=history
  raise failure
 q=G@u;normal=kn*np.maximum(q,0)*area;ttrial=kt*(T@u).reshape(-1,2);tnorm=np.linalg.norm(ttrial,axis=1);cap=mu*kn*np.maximum(q[w],0);traction=ttrial*np.minimum(1,cap/np.maximum(tnorm,1e-20))[:,None];internal=model['A']@u+G.T@normal+T.T@(traction*area[w,None]).ravel();reaction=internal-F;res=np.linalg.norm(reaction[free])/max(np.linalg.norm(F[free]),1e-12);assert res<2e-5,(res,it)
 split=3*len(model['xt']);stress=[]
 for B,D,d,v,uu in [(model['B1'],model['D1'],model['d1'],model['vol1'],u[:split]),(model['B2'],model['D2'],model['d2'],model['vol2'],u[split:])]:
  s=np.einsum('ab,ebi,ei->ea',D,B,uu[d],optimize=True);a,b,c,d,e,f=s.T;vm=np.sqrt(((a-b)**2+(b-c)**2+(c-a)**2)/2+3*(d*d+e*e+f*f));stress.append(dict(peak_element_MPa=float(vm.max()),volume_weighted_mean_MPa=float(vm@v/v.sum())))
 stop=model['kinds']=='stop';washer=model['kinds']=='washer';force_balance=(reaction.reshape(-1,3)+F.reshape(-1,3)).sum(axis=0);out=dict(preload_N=preload,side_force_N=side_force,assumed_mu=mu,normal_penalty_N_mm3=kn,tangential_penalty_N_mm3=kt,iterations=it+1,relative_free_residual=float(res),maximum_numerical_penetration_mm=float(np.maximum(q,0).max()),maximum_pivot_constraint_error_mm=float(abs(model['C']@u).max()),stop_reaction_N=float(normal[stop].sum()),washer_normal_sum_N=float(normal[washer].sum()),washer_quadrature_area_mm2=float(area[washer].sum()),stop_quadrature_area_mm2=float(area[stop].sum()),global_force_balance_error_N=float(np.linalg.norm(force_balance)),cup_mean_displacement_x_mm=float(model['Fc']@u),component_stresses=stress,history=history,coulomb_bound_error_MPa=float(np.maximum(np.linalg.norm(traction,axis=1)-cap,0).max()))
 return out,u,normal,traction,reaction,F

if __name__=='__main__':
 size=sys.argv[1];h=float(sys.argv[2]);start=time.time();m=prepare(size,h);print(json.dumps(dict(stage='joint prepared',size=size,h=h,nodes=len(m['xt'])+len(m['xf']),contact_points=len(m['areas']))),flush=True);r,u,n,t,reaction,F=solve(m,140,2,.2);r.update(size=size,mesh_max_mm=h,source=m['row']['file'],source_sha256=m['row']['sha256'],elastic_E_MPa=3500,assumed_nu=.35,seconds=time.time()-start,rigid_translation_controls=m['rigid_controls'],scope='Two flexible 3D solids with unilateral stop and washer contact,Coulomb-limited tangential springs,prescribed bolt preload and ideal distributing revolute pivot. No resolved bolt/thread/disc/washer solids or guide contact.');f=O/(size+'_contact_h'+str(h));Path(str(f)+'.json').write_text(json.dumps(r,indent=2));np.savez_compressed(str(f)+'.npz',xt=m['xt'],xf=m['xf'],tt=m['tt'],tf=m['tf'],u=u,normal=n,traction=t,reaction=reaction,force=F,contact_points=m['points'],contact_areas=m['areas'],contact_kinds=m['kinds']);print(json.dumps(r),flush=True)
