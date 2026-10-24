"""Quadratic face interpolation candidate for the existing isolated joint reference.
This changes contact discretization, not actual washer/contact material qualification.
"""
from pathlib import Path
import os,sys,inspect,json,math
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import v19_quadratic_joint as q
np=q.np;a=q.a;QUAD_ORDER=4;STATS={}

def shape(uv):
 u,v=uv;L=np.array([1-u-v,u,v]);DL=np.array([[-1.,-1.],[1.,0.],[0.,1.]])
 N=np.r_[L*(2*L-1),[4*L[i]*L[j] for i,j in [(0,1),(1,2),(2,0)]]]
 D=np.vstack([(4*L-1)[:,None]*DL,*[4*(DL[i]*L[j]+L[i]*DL[j])[None,:] for i,j in [(0,1),(1,2),(2,0)]]])
 return N,D

def triangle_rule(order=4):
 p,w=np.polynomial.legendre.leggauss(order);p=(p+1)/2;w=w/2
 return [(np.array([u,(1-u)*v]),wu*wv*(1-u)) for u,wu in zip(p,w) for v,wv in zip(p,w)]

def boundary6(t):
 indexes=[]
 for face in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]:indexes.append(face+[q.edge_index[tuple(sorted((face[i],face[j])))] for i,j in [(0,1),(1,2),(2,0)]])
 faces=np.concatenate([t[:,ix] for ix in indexes]);_,index,count=np.unique(np.sort(faces,axis=1),axis=0,return_index=True,return_counts=True)
 return faces[index[count==1]]

def face_points(x,face):
 xyz=x[face]
 for uv,w in triangle_rule(QUAD_ORDER):
  N,D=shape(uv);tangents=xyz.T@D;jac=np.linalg.norm(np.cross(tangents[:,0],tangents[:,1]));assert jac>1e-12
  yield N,N@xyz,float(jac*w)

def face_weights(x,faces,radial=None):
 weights=np.zeros(len(x))
 for face in faces:
  for N,p,weight in face_points(x,face):
   if radial is not None and not radial[0]**2<=p[0]**2+(p[2]-radial[2])**2<=radial[1]**2:continue
   weights[face]+=N*weight
 return weights

def inverse_face(xy,point):
 uv=np.linalg.solve((xy[1:3]-xy[0]).T,point-xy[0])
 for iteration in range(12):
  N,D=shape(uv);res=N@xy-point
  if np.linalg.norm(res)<1e-10:break
  uv-=np.linalg.solve(xy.T@D,res)
 N,D=shape(uv);error=float(np.linalg.norm(N@xy-point));inside=min(1-uv.sum(),*uv)>-1e-7
 return N,error,inside

def contact_pair6(xf,ff,xt,ft,coords,normal,offset,kind,radial=None):
 from scipy.spatial import cKDTree
 tri=xt[ft][:,:,coords];tree=cKDTree(tri[:,:3].mean(axis=1));rows=[];cols=[];vals=[];areas=[];points=[];kinds=[];tangents=[];errors=[]
 for face in ff:
  for ns,pt,weight in face_points(xf,face):
   if radial is not None and not radial[0]**2<=pt[0]**2+(pt[2]-radial[2])**2<=radial[1]**2:continue
   _,candidates=tree.query(pt[coords],k=min(40,len(ft)));chosen=None
   for j in np.atleast_1d(candidates):
    try:nm,error,inside=inverse_face(tri[j],pt[coords])
    except np.linalg.LinAlgError:continue
    if inside and error<1e-9:chosen=(ft[j],nm,error);break
   if chosen is None:raise RuntimeError('Quadratic contact projection failed '+kind+' '+str(pt.tolist()))
   master,nm,error=chosen;assert abs(ns.sum()-1)<1e-12 and abs(nm.sum()-1)<1e-12;index=len(areas);areas.append(weight);points.append(pt);kinds.append(kind);errors.append(error)
   for node,N in zip(face,ns):
    for axis,value in enumerate(normal):
     if value:rows.append(index);cols.append(offset+3*int(node)+axis);vals.append(float(N*value))
   for node,N in zip(master,nm):
    for axis,value in enumerate(normal):
     if value:rows.append(index);cols.append(3*int(node)+axis);vals.append(float(-N*value))
   tangents.append((face.copy(),ns.copy(),master.copy(),nm.copy()))
 STATS.setdefault(kind,[]).append(dict(points=len(areas),area_mm2=sum(areas),maximum_projection_error_mm=max(errors),minimum_quadrature_area_mm2=min(areas)))
 return rows,cols,vals,areas,points,kinds,tangents

def install():
 a.boundary=boundary6;a.contact_pair=contact_pair6;a.face_weights=face_weights
 source=inspect.getsource(a.prepare)
 assert 'baseK=(K+1e5*(C.T@C)).tocsr()' in source
 source=source.replace('baseK=(K+1e5*(C.T@C)).tocsr()','baseK=K')
 start=source.index('  ff=plane_faces(xf,bf,1,sign*outer);weights=np.zeros(len(xf))')
 end=source.index('  assert weights.sum()>80',start)
 source=source[:start]+"  ff=plane_faces(xf,bf,1,sign*outer);weights=face_weights(xf,ff,(2.15,6.,pivot))\n"+source[end:]
 start=source.index('cupfaces=bf[');end=source.index(' assert weights.sum()>140',start)
 source=source[:start]+"cupfaces=bf[np.all(abs(np.hypot(xf[bf,0]-20,xf[bf,2]-35)-2.1)<1e-5,axis=1)];weights=face_weights(xf,cupfaces)\n"+source[end:]
 exec(source,a.__dict__)

def controls():
 max_partition=0.;max_derivative=0.;max_trace=0.;old_trace_error=0.;rng=np.random.default_rng(20261024)
 tet_values=rng.normal(size=10)
 for face in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]:
  indexes=face+[q.edge_index[tuple(sorted((face[i],face[j])))] for i,j in [(0,1),(1,2),(2,0)]]
  reference=np.array([[0.,0.],[1,0],[0,1],[.5,0],[.5,.5],[0,.5]])
  for uv,w in triangle_rule():
   N,D=shape(uv);max_partition=max(max_partition,abs(N.sum()-1),float(abs(D.sum(axis=0)).max()))
   for axis in range(2):
    step=np.eye(2)[axis]*1e-6;fd=(shape(uv+step)[0]-shape(uv-step)[0])/2e-6;max_derivative=max(max_derivative,float(abs(fd-D[:,axis]).max()))
   L=np.zeros(4);L[face]=[1-uv.sum(),*uv];N10=np.r_[L*(2*L-1),[4*L[i]*L[j] for i,j in q.edges]];max_trace=max(max_trace,abs(N@tet_values[indexes]-N10@tet_values))
   for ix in [[0,3,5],[3,1,4],[5,4,2],[3,4,5]]:
    xyz=reference[ix];local=np.linalg.solve((xyz[1:]-xyz[0]).T,uv-xyz[0]);bary=np.r_[1-local.sum(),local]
    if bary.min()>-1e-10:old_trace_error=max(old_trace_error,abs(bary@tet_values[np.array(indexes)[ix]]-N10@tet_values));break
 moment_error=0.
 for i in range(6):
  for j in range(6-i):
   numerical=sum(w*uv[0]**i*uv[1]**j for uv,w in triangle_rule());expected=math.factorial(i)*math.factorial(j)/math.factorial(i+j+2);moment_error=max(moment_error,abs(numerical-expected))
 warped=np.array([[0.,0.],[1.,0.],[0.,1.],[.5,-.08],[.57,.55],[-.04,.5]]);inverse_error=0.
 for uv,w in triangle_rule():
  N,D=shape(uv);solved,error,inside=inverse_face(warped,N@warped);assert inside;inverse_error=max(inverse_error,float(abs(solved-N).max()),error)
 assert max_partition<1e-12 and max_derivative<1e-8 and max_trace<1e-12 and moment_error<1e-14 and inverse_error<1e-8 and old_trace_error>1e-3
 return dict(partition_and_derivative_sum_error=max_partition,shape_derivative_finite_difference_error=max_derivative,quadratic_face_to_Tet10_trace_error=max_trace,old_linear_subtriangle_trace_difference=old_trace_error,triangle_polynomial_moment_error=moment_error,curved_planar_inverse_mapping_error=inverse_error,status='pass',scope='Interpolation and quadrature controls only. Old linear contact is a lower order approximation; this does not prove it caused the observed stress variation or validate real contact physics.')

if __name__=='__main__':
 O=P/'engineering-v25-results';O.mkdir(exist_ok=True);r=controls();(O/'quadratic_face_controls.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
