"""Euler Bernoulli beam with unilateral distributed guide contact.
This is a reduced one-plane pin model, not full 3D joint contact FEA.
Units mm,N,MPa. Actual source guide intervals are extracted separately.
"""
import os,sys,json,math
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1';P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import numpy as np
from scipy.sparse import lil_matrix,diags
from scipy.sparse.linalg import spsolve

def solve(force,front=(-12.999,-10),rear=(-32,-21),load=-6.35,gap=.05,kline=1000,h=.5,point_supports=None):
 key=sorted(set([-37.,-5.,*front,*rear,load]));y=np.unique(np.concatenate([np.linspace(a,b,int(math.ceil((b-a)/h))+1) for a,b in zip(key,key[1:])]))
 n=len(y);nd=2*n;K=lil_matrix((nd,nd));EI=193000*math.pi*2.2**4/64
 for i,L in enumerate(np.diff(y)):
  a=EI/L**3*np.array([[12,6*L,-12,6*L],[6*L,4*L*L,-6*L,2*L*L],[-12,-6*L,12,-6*L],[6*L,2*L*L,-6*L,4*L*L]]);d=[2*i,2*i+1,2*i+2,2*i+3]
  for j in range(4):
   for k in range(4):K[d[j],d[k]]+=a[j,k]
 K=K.tocsr();weights=np.zeros(n)
 for i,L in enumerate(np.diff(y)):
  mid=(y[i]+y[i+1])/2
  if front[0]<=mid<=front[1] or rear[0]<=mid<=rear[1]:weights[i:i+2]+=L/2
 if point_supports is not None:
  weights[:]=0
  for support in point_supports:weights[int(np.argmin(abs(y-support)))]=1
 kval=kline*weights;f=np.zeros(nd);li=int(np.argmin(abs(y-load)));f[2*li]=force
 if force==0:return {'y':y,'u':np.zeros(nd),'reaction':np.zeros(n),'force':f,'normal_reaction_sum_N':0.,'maximum_displacement_mm':0.,'force_balance_error_N':0.,'moment_balance_error_Nmm':0.,'relative_residual':0.,'iterations':0,'nominal_max_bending_stress_MPa':0.}
 u=np.zeros(nd);u[::2]=math.copysign(gap+.001,force);reg=1e-8
 def evaluate(v):
  w=v[::2];penetration=np.maximum(np.abs(w)-gap,0);gcontact=kval*penetration*np.sign(w);g=K@v-f+reg*v;g[::2]+=gcontact;energy=.5*v@(K@v)-f@v+.5*np.dot(kval,penetration**2)+.5*reg*v@v;return energy,g,gcontact
 for it in range(100):
  energy,g,gc=evaluate(u)
  if np.max(abs(g))<2e-6:break
  active=(abs(u[::2])>gap)&(kval>0);dg=np.zeros(nd);dg[::2]=kval*active;H=K+diags(dg+reg);step=spsolve(H,-g);alpha=1.
  for ls in range(45):
   trial=u+alpha*step
   if evaluate(trial)[0]<=energy+1e-4*alpha*np.dot(g,step)+1e-12:break
   alpha*=.5
  u=trial
 else:raise RuntimeError('Contact iteration did not converge: '+str({'residual':float(np.max(abs(evaluate(u)[1]))),'energy':float(evaluate(u)[0]),'alpha':alpha}))
 energy,g,gc=evaluate(u);reaction=-gc;beam_moments=[]
 for i,L in enumerate(np.diff(y)):
  a=EI/L**3*np.array([[12,6*L,-12,6*L],[6*L,4*L*L,-6*L,2*L*L],[-12,-6*L,12,-6*L],[6*L,2*L*L,-6*L,4*L*L]]);q=a@u[2*i:2*i+4];beam_moments.extend([abs(q[1]),abs(q[3])])
 return {'y':y,'u':u,'reaction':reaction,'force':f,'normal_reaction_sum_N':float(np.sum(abs(reaction))),'maximum_displacement_mm':float(np.max(abs(u[::2]))),'force_balance_error_N':float(abs(reaction.sum()+force)),'moment_balance_error_Nmm':float(abs(reaction@y+force*load)),'relative_residual':float(np.max(abs(g))/max(abs(force),1)),'iterations':it+1,'nominal_max_bending_stress_MPa':float(max(beam_moments)*32/(math.pi*2.2**3)),'regularization_force_sum_N':float(reg*np.sum(abs(u[::2])))}

if __name__=='__main__':
 for h in [1,.5,.25]:
  r=solve(11.627553,h=h);print(json.dumps({k:v for k,v in r.items() if k not in ['y','u','reaction','force']}))
