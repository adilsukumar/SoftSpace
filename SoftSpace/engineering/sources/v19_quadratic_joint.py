"""Quadratic bulk FE variant with piecewise-linear subtriangle contact.
Positive Duffy product quadrature, geometric washer partitions and original loads.
It remains an ideal-pivot reference model, not a resolved bolt or worn headset.
"""
import json,time,itertools,gc
import v19_contact_assembly as a
np=a.np;O=a.O/'quadratic-contact';O.mkdir(exist_ok=True)
a.gmsh.initialize();props=a.gmsh.model.mesh.getElementProperties(11);local=np.array(props[4]).reshape(-1,3);a.gmsh.finalize();edges=[]
for x in local[4:]:edges.append(next((i,j) for i,j in itertools.combinations(range(4),2) if np.max(abs((local[i]+local[j])/2-x))<1e-10))
edge_index={tuple(sorted(pair)):i+4 for i,pair in enumerate(edges)};GR=np.array([[-1.,-1,-1],[1,0,0],[0,1,0],[0,0,1]])
def gradients(L):
 return np.vstack([(4*L-1)[:,None]*GR,*[4*(L[i]*GR[j]+L[j]*GR[i])[None,:] for i,j in edges]])
def strain_matrix(x,t,L):
 gr=gradients(np.asarray(L));J=np.einsum('eia,ib->eab',x[t],gr);det=np.linalg.det(J);assert min(det)>0;g=np.einsum('ib,eba->eia',gr,np.linalg.inv(J));B=np.zeros((len(t),6,30));B[:,0,0::3]=g[:,:,0];B[:,1,1::3]=g[:,:,1];B[:,2,2::3]=g[:,:,2];B[:,3,0::3]=g[:,:,1];B[:,3,1::3]=g[:,:,0];B[:,4,1::3]=g[:,:,2];B[:,4,2::3]=g[:,:,1];B[:,5,0::3]=g[:,:,2];B[:,5,2::3]=g[:,:,0];return B,det
def quadrature(order=3):
 seq=[]
 for n in [order,order,order]:
  p,w=np.polynomial.legendre.leggauss(n);seq.append(((p+1)/2,w/2))
 out=[]
 for i,j,k in itertools.product(*[range(order)]*3):
  u,v,w=[seq[n][0][q] for n,q in enumerate([i,j,k])];weight=seq[0][1][i]*seq[1][1][j]*seq[2][1][k]*(1-u)**2*(1-v);xi=u;eta=(1-u)*v;zeta=(1-u)*(1-v)*w;out.append((np.array([1-xi-eta-zeta,xi,eta,zeta]),weight))
 assert abs(sum(w for L,w in out)-1/6)<1e-14;return out
def elasticity(x,t,E=3500,nu=.35):
 lam=E*nu/((1+nu)*(1-2*nu));mu=E/(2*(1+nu));D=np.zeros((6,6));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*mu);D[3:,3:]=np.eye(3)*mu;ke=np.zeros((len(t),30,30));vol=np.zeros(len(t))
 for L,w in quadrature(3):
  B,det=strain_matrix(x,t,L);ke+=np.einsum('eai,ab,ebj,e->eij',B,D,B,det*w,optimize=True);vol+=det*w
 dofs=(t[:,:,None]*3+np.arange(3)).reshape(-1,30);K=a.coo_matrix((ke.ravel(),(np.broadcast_to(dofs[:,:,None],ke.shape).ravel(),np.broadcast_to(dofs[:,None,:],ke.shape).ravel())),shape=(3*len(x),3*len(x))).tocsr();Bc,_=strain_matrix(x,t,[.25]*4);return K,Bc,D,dofs,vol
def boundary(t):
 face_indices=[]
 for v in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]:face_indices.append(v+[edge_index[tuple(sorted((v[i],v[j])))] for i,j in [(0,1),(1,2),(2,0)]])
 faces=np.concatenate([t[:,ix] for ix in face_indices]);_,idx,count=np.unique(np.sort(faces,axis=1),axis=0,return_index=True,return_counts=True);f=faces[idx[count==1]];return np.concatenate([f[:,ix] for ix in [[0,3,5],[3,1,4],[5,4,2],[3,4,5]]])
a.elasticity=elasticity;a.boundary=boundary
def controls():
 x=local.copy();t=np.arange(10)[None,:];K,B,D,d,v=elasticity(x,t);affine=np.array([[.001,.0002,0],[.0002,-.0003,.0001],[0,.0001,.0004]]);u=(x@affine.T).ravel();expected=np.array([.001,-.0003,.0004,.0004,.0002,0]);err=float(np.max(abs((B[0]@u)-expected)));energy=float(u@K@u/2);analytic=float(expected@D@expected/12);sym=float(np.max(abs((K-K.T).data)));assert err<1e-12 and abs(energy/analytic-1)<1e-10 and abs(v.sum()-1/6)<1e-12 and sym<1e-9
 r=dict(affine_patch_error=err,energy=energy,analytic_energy=analytic,volume=float(v.sum()),symmetry_error=sym,edge_order=edges,quadrature_points=27,status='pass');(O/'element_controls.json').write_text(json.dumps(r,indent=2));return r
if __name__=='__main__':
 controls();records=[]
 for size in ['child_large','adult_small']:
  previous=None
  for h in [3.,2.3]:
   path=O/(size+'_h'+str(h)+'.json')
   if path.exists():r=json.loads(path.read_text())
   else:
    start=time.time();row,meshes=a.mesh(size,h,conforming=2,order=2,optimize_high_order=size.startswith('adult'));nodes=sum(len(x) for x,t in meshes)
    if nodes>40000:
     (O/(size+'_limit.json')).write_text(json.dumps(dict(nodes=nodes,mesh=h,status='Not solved beyond chosen quadratic 40000 node limit'),indent=2));break
    m=a.prepare(size,h,saved_meshes=meshes);print(size,h,'prepared',nodes,flush=True)
    try:
     r,u,n,t,reaction,F=a.solve(m,140,2,.2,max_iterations=120);r['converged']=True;np.savez_compressed(path.with_suffix('.npz'),xt=m['xt'],xf=m['xf'],tt=m['tt'],tf=m['tf'],u=u,normal=n,traction=t,reaction=reaction,force=F,contact_points=m['points'],contact_areas=m['areas'],contact_kinds=m['kinds'])
    except RuntimeError as e:r=dict(converged=False,error=str(e),history=getattr(e,'history',[]))
    r.update(size=size,mesh_max_mm=h,source=row['file'],source_sha256=row['sha256'],nodes=nodes,seconds=time.time()-start,bulk_element='Tet10',contact_interpolation='Tri3 subtriangles of quadratic boundary faces',boundary_partitions='washer annulus and preload footprint',stress_sampling='centroid only',quadrature='27 positive Duffy Gauss points',preload_N=140,side_force_N=2,assumed_mu=.2,elastic_E_MPa=3500,assumed_nu=.35,exact_CAD_component_volumes_mm3=row['finite_element_reference_volumes_mm3'],quadrature_component_volumes_mm3=[float(m['vol1'].sum()),float(m['vol2'].sum())]);path.write_text(json.dumps(r,indent=2));print(size,h,r.get('cup_mean_displacement_x_mm'),flush=True)
   if not r.get('converged'):break
   if previous:
    r['displacement_change_percent']=abs(r['cup_mean_displacement_x_mm']/previous['cup_mean_displacement_x_mm']-1)*100;r['chosen_5_percent_gate_pass']=r['displacement_change_percent']<5;path.write_text(json.dumps(r,indent=2))
   records.append(dict(file=str(path),size=size,h=h,change_percent=r.get('displacement_change_percent'),gate=r.get('chosen_5_percent_gate_pass')));(O/'status.json').write_text(json.dumps(dict(cases=records,complete=False,whole_joint_validated=False),indent=2));previous=r
   if 'm' in locals():del m
   gc.collect()
 (O/'status.json').write_text(json.dumps(dict(cases=records,complete=True,whole_joint_validated=False,scope='Higher order bulk and piecewise-linear surface contact, ideal pivot and preload, nominal outward fixture only.'),indent=2))
