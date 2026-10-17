"""Consistent uniform traction weights for quadratic triangular surface elements."""
import numpy as np
grads=np.array([[-1,-1],[1,0],[0,1]],float)
edges=[(0,1),(1,2),(2,0)]
q=[]
for a,w in [(.445948490915965,.111690794839005),(.091576213509771,.054975871827661)]:
 for j in range(3):q.append((np.array([1-2*a if i==j else a for i in range(3)]),w))

def nodal_surface_weights(x,tri):
 weights=np.zeros(len(x));area=0
 for l,w in q:
  shape=np.r_[l*(2*l-1),[4*l[i]*l[j] for i,j in edges]]
  ds=np.vstack([(4*l[:,None]-1)*grads,[4*(l[i]*grads[j]+l[j]*grads[i]) for i,j in edges]])
  J=np.einsum('eia,ib->eab',x[tri],ds);jac=np.linalg.norm(np.cross(J[:,:,0],J[:,:,1]),axis=1)
  if np.any(jac<=0):raise RuntimeError('Invalid surface load element')
  np.add.at(weights,tri.ravel(),(jac[:,None]*w*shape).ravel());area+=float(np.sum(jac*w))
 if abs(weights.sum()/area-1)>1e-10:raise RuntimeError('Surface partition of unity failed')
 return weights,area
