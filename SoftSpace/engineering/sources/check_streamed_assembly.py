"""Check memory-efficient assembly against the existing solver on identical mesh."""
from pathlib import Path
import json
import solid_band_v9 as b
np=b.np;P=Path(__file__).parent
x,t=b.mesh_geometry('verification_beam',.7,True);f=np.zeros(len(x)*3)
fixed=(np.flatnonzero(np.isclose(x[:,0],0))[:,None]*3+np.arange(3)).ravel();end=np.flatnonzero(np.isclose(x[:,0],20));f[end*3+2]=-1/len(end)
u1,v1,r1=b.mechanics(x,t,f,fixed);u2,v2,r2=b.mechanics(x,t,f,fixed,stream_assembly=True,reduced_storage=True,coarse_precondition=True)
du=float(np.linalg.norm(u2-u1)/np.linalg.norm(u1));dv=float(np.linalg.norm(v2-v1)/np.linalg.norm(v1))
out={'status':'complete','same_mesh_elements':len(t),'displacement_relative_difference':du,'stress_vector_relative_difference':dv,'pass':du<1e-6 and dv<1e-6,'ordinary':r1,'streamed':r2,'limit':'Assembly comparison on a clamped beam, not product validation.'}
(P/'engineering-v10-results'/'streamed_assembly_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True);assert out['pass']
