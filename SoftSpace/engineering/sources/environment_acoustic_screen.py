"""Uncalibrated thermal/vapor and low-frequency acoustic sensitivity models.
No measured comfort, attenuation rating, or sound spectrum prediction.
"""
import csv,itertools,json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).parent;OUT=ROOT/'engineering-final-results';OUT.mkdir(exist_ok=True)
CFG=json.loads((ROOT/'engineering-final.json').read_text())

def saturation(T):
    return 610.94*math.exp(17.625*T/(T+243.04))

def thermal(ambient,rh,wvtr,water_mg_h,foam_k):
    # WVTR hypothesis defined at 2000 Pa vapor-pressure difference.
    area=.0044;V=.0002;capacitance=30;skin=34
    ga=1/(.020/(foam_k*area)+.0002/(.15*area)+1/(8*area));gs=5*area
    dt=.5;T=ambient;outside=rh/100*saturation(ambient)
    water_density=outside/(461.5*(ambient+273.15));condensed=0;transferred=0
    source=water_mg_h/1e6/3600;permeance=wvtr/1000/86400/2000
    for _ in range(7200):
        T+=dt*(gs*(skin-T)+ga*(ambient-T))/capacitance
        pv=water_density*461.5*(T+273.15)
        flux=permeance*area*(pv-outside)
        flux=max(flux,-max(water_density,0)*V/dt)
        water_density+=dt*(source-flux)/V;transferred+=flux*dt
        sat=saturation(T)/(461.5*(T+273.15))
        if water_density>sat:condensed+=(water_density-sat)*V;water_density=sat
    inputmass=source*3600
    finalwater=water_density*V;initialwater=outside/(461.5*(ambient+273.15))*V
    residual=abs(inputmass+initialwater-finalwater-condensed-transferred)
    assert residual<1e-12
    return {'ambient_C':ambient,'ambient_RH_percent':rh,'assumed_cover_WVTR_g_m2_day':wvtr,
            'water_source_mg_h':water_mg_h,'foam_k_W_mK':foam_k,'temperature_60min_C':T,
            'RH_60min_percent':100*water_density*461.5*(T+273.15)/saturation(T),
            'condensed_mg':condensed*1e6,'water_balance_error_mg':residual*1e6}

def acoustic(family,gap_mm,panel_K,Q):
    c=CFG[family];rho=1.2;speed=343;mu=1.8e-5
    S=math.pi*(c['pad_outer_width']+5)*(c['pad_outer_height']+5)/4/1e6
    inner=math.pi*(c['pad_outer_width']-1)*(c['pad_outer_height']-1)/4/1e6
    opening=math.pi*c['ear_opening_width']*c['ear_opening_height']/4/1e6
    V=inner*.022+opening*.020
    M=900*.003*S;C=V/(rho*speed**2)
    rows=[]
    for f in np.geomspace(31.5,250,80):
        w=2*math.pi*f
        # A single hypothetical compliant panel DOF; remaining cup walls are rigid.
        Rpanel=panel_K/(w*Q)
        Zpanel=Rpanel+1j*(w*M-panel_K/w)
        Ypanel=S*S/Zpanel
        if gap_mm:
            width=.004;height=gap_mm/1000;length=.020
            Rleak=12*mu*length/(width*height**3)
            Lleak=rho*length/(width*height)
            Yleak=1/(Rleak+1j*w*Lleak)
        else:Yleak=0
        Yc=1j*w*C+w*C/Q
        H=(Ypanel+Yleak)/(Ypanel+Yleak+Yc)
        loss=-20*math.log10(max(abs(H),1e-15))
        rows.append({'family':family,'hypothetical_gap_height_mm':gap_mm,'hypothetical_gap_width_mm':4,
                     'hypothetical_panel_stiffness_N_m':panel_K,'loss_quality_factor':Q,'frequency_Hz':float(f),
                     'model_pressure_ratio':float(abs(H)),'model_pressure_difference_dB':loss})
    return rows

def main():
    thermals=[thermal(a,r,w,s,k) for a,r,w,s,k in itertools.product([28,32,36],[50,70,90],[1,100,500,1000],[20,100,300],[.035,.05])]
    assert all(min(t['ambient_C'],34)-1e-8<=t['temperature_60min_C']<=max(t['ambient_C'],34)+1e-8 for t in thermals)
    assert all(0<=t['RH_60min_percent']<=100+1e-7 for t in thermals)
    sounds=[row for family,gap,K,Q in itertools.product(['adult','child'],[0,.05,.1,.3,1],[1e4,1e5,1e6],[5,20]) for row in acoustic(family,gap,K,Q)]
    for filename,rows in [('thermal_vapor_cases.csv',thermals),('acoustic_sensitivity.csv',sounds)]:
        with (OUT/filename).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    nominal=[t for t in thermals if t['ambient_C']==32 and t['ambient_RH_percent']==70 and t['water_source_mg_h']==100 and t['foam_k_W_mK']==.05]
    summary={'thermal_case_count':len(thermals),'acoustic_scenario_count':len(sounds)//80,'acoustic_frequency_rows':len(sounds),
             'thermal_nominal_comparison':nominal,
             'thermal_model':'one heat-capacity node + conservative water-vapor balance with assumed cover permeance',
             'acoustic_model':'lumped single panel DOF, leak impedance and cavity compliance; hypothetical parameters',
             'limitations':['Thermal model omits sweating feedback, evaporation cooling, spatial skin temperatures and wet-material changes.',
                            'WVTR, skin temperature, water source and material conductivity are assumed, not supplier data.',
                            'Acoustic results are limited to illustrative 31.5-250 Hz lumped behaviour; no broadband attenuation, NRR or SNR prediction.',
                            'Panel stiffness and damping are uncalibrated; resonant pressure amplification can occur.',
                            'Hypothetical leak sizes are independent scenarios; NOT inferred from contact gaps.',
                            'No head/ear transfer function, cup modes, real liner absorption, cover acoustic impedance or acoustic testing.']}
    (OUT/'environment_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
