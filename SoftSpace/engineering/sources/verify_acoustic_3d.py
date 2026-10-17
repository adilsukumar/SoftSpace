from acoustic_3d_v6 import mesh,np,spsolve,out
import json
c,x,tet,K,M,B,b,sample,V,A=mesh('verification',4)
rows=[]
for f in [31.5,125,500,1000]:
 omega=2*np.pi*f;k=omega/343*(1+.5j/20);stiff=1e8;mass=3.15;resistance=3000
 beta=1.2*omega**2/(stiff-mass*omega**2-1j*resistance*omega)
 sys=(K-k*k*M-beta*B).tocsc();rhs=-beta*b
 pressure=spsolve(sys,rhs);numeric=pressure[sample].mean()
 exact=beta/(k*np.sin(k*.042)+beta*np.cos(k*.042))
 rows.append({'frequency_Hz':f,'numerical_complex_pressure':[float(numeric.real),float(numeric.imag)],'analytical_complex_pressure':[float(exact.real),float(exact.imag)],'relative_complex_error':float(abs(numeric/exact-1))})
report={'status':'complete','test':'Uniform elliptical tube, rigid side/front walls, uniform compliant back; exact 1D Helmholtz solution','nodes':len(x),'cases':rows,'max_relative_complex_error':max(r['relative_complex_error'] for r in rows),'gate_1pct':max(r['relative_complex_error'] for r in rows)<.01}
(out/'acoustic_3d_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
