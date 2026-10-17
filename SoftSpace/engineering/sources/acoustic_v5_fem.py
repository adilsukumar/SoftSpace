"""1D frequency-domain cavity FEM with hypothetical compliant wall and slit.
This is an acoustic solve, not broadband 3D cup/ear simulation or an attenuation rating.
"""
import json,csv,itertools,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).parent;OUT=ROOT/'engineering-v5-results';OUT.mkdir(exist_ok=True)
CONFIG=json.loads((ROOT/'engineering-final.json').read_text())

def solve(family,f,E=2000,density=1000,Q=10,gap_mm=0,elements=20):
    c=CONFIG[family];rho=1.2;speed=343;mu=1.8e-5;t=.003;nu=.35
    S=math.pi*(c['pad_outer_width']+5)*(c['pad_outer_height']+5)/4/1e6
    inner=math.pi*(c['pad_outer_width']-1)*(c['pad_outer_height']-1)/4/1e6
    opening=math.pi*c['ear_opening_width']*c['ear_opening_height']/4/1e6
    V=inner*.022+opening*.020;L=V/S;dx=L/elements;omega=2*math.pi*f
    # Equivalent clamped circular plate under uniform pressure: K=64*pi*D/a^2.
    a=math.sqrt(S/math.pi);D=E*1e6*t**3/(12*(1-nu*nu));stiffness=64*math.pi*D/(a*a)
    mass=density*t*S;Zpanel=stiffness/(omega*Q)+1j*(omega*mass-stiffness/omega)
    Y=S*S/Zpanel
    if gap_mm:
        h=gap_mm/1000;w=.004;l=.020
        Y+=1/(12*mu*l/(w*h**3)+1j*omega*rho*l/(w*h))
    k2=(omega/speed)**2*(1-1j/20)
    A=np.zeros((elements+1,elements+1),complex)
    local=np.array([[1,-1],[-1,1]])/dx-k2*dx/6*np.array([[2,1],[1,2]])
    for e in range(elements):A[e:e+2,e:e+2]+=local
    boundary=1j*omega*rho/S*Y;A[0,0]+=boundary;rhs=np.zeros(elements+1,complex);rhs[0]=boundary
    p=np.linalg.solve(A,rhs)
    residual=float(np.linalg.norm(A@p-rhs)/max(np.linalg.norm(rhs),1e-30))
    return {'family':family,'frequency_Hz':f,'assumed_E_MPa':E,'assumed_density_kg_m3':density,'assumed_panel_Q':Q,
            'hypothetical_slit_height_mm':gap_mm,'equivalent_plate_stiffness_N_m':stiffness,
            'ear_end_pressure_ratio':float(abs(p[-1])),'model_pressure_difference_dB':float(-20*np.log10(max(abs(p[-1]),1e-15))),
            'linear_system_relative_residual':residual},p

def main():
    verification=[]
    for family in ['adult','child']:
        low,_=solve(family,1);c=CONFIG[family]
        S=math.pi*(c['pad_outer_width']+5)*(c['pad_outer_height']+5)/4/1e6
        V=math.pi*(c['pad_outer_width']-1)*(c['pad_outer_height']-1)/4/1e6*.022+math.pi*c['ear_opening_width']*c['ear_opening_height']/4/1e6*.020
        omega=2*math.pi;K=low['equivalent_plate_stiffness_N_m'];mass=1000*.003*S
        Y=S*S/(K/(omega*10)+1j*(omega*mass-K/omega));C=V/(1.2*343**2)
        lumped=abs(Y/(Y+1j*omega*C*(1-1j/20)))
        assert abs(low['ear_end_pressure_ratio']/lumped-1)<1e-4
        values=[solve(family,250,elements=n)[0]['ear_end_pressure_ratio'] for n in [10,20,40]]
        change=100*abs(values[-1]/values[-2]-1);assert change<.1
        verification.append({'family':family,'low_frequency_pressure_ratio':low['ear_end_pressure_ratio'],'analytic_lumped_pressure_ratio':lumped,'mesh_10_20_40_pressure_ratios':values,'last_mesh_change_percent':change})
    rows=[]
    for family,E,density,Q,gap in itertools.product(['adult','child'],[1500,2500],[900,1200],[5,20],[0,.1,.3]):
        for f in np.geomspace(31.5,250,48):
            r,_=solve(family,float(f),E,density,Q,gap);rows.append(r)
    assert max(r['linear_system_relative_residual'] for r in rows)<1e-8
    with (OUT/'acoustic_cavity_fem.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'scenario_count':48,'frequency_rows':len(rows),'verification':verification,
             'minimum_model_difference_dB':min(r['model_pressure_difference_dB'] for r in rows),
             'maximum_model_difference_dB':max(r['model_pressure_difference_dB'] for r in rows),
             'amplification_rows':sum(r['ear_end_pressure_ratio']>1 for r in rows),
             'validated_attenuation_rating':None,
             'limitations':['1D equivalent cavity; restricted to 31.5-250 Hz','Curved cup replaced by hypothetical clamped circular plate and unmeasured damping',
             'Slits are independent hypothetical inputs, not inferred from cushion contact','No real liner impedance, ear, skin, cover transmission, seams or cup structural modes',
             'Mesh convergence verifies the equations, not that these assumptions represent the real product','No broadband, NRR/SNR, clinical or wearer effectiveness claim']}
    (OUT/'acoustic_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
