"""Assumption-based screening, NOT validated FEA, acoustic or clinical testing.

Units: geometry mm, cell areas mm2, pressure Pa, forces N.
Independent nonlinear foam springs support a curved rigid contact surface.
An illustrative membrane term approximates cover resistance. This is not a
membrane finite element model. Glasses arms are rigid local thickness offsets.
"""
import csv
import itertools
import json
import math
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parent / 'screening-results'
OUT.mkdir(exist_ok=True)
STRAIN = np.array([0, .05, .1, .2, .4, .6, .7, .8, .9])
FOAMS = {
    'soft': np.array([0, 300, 600, 1000, 1500, 2200, 4000, 10000, 35000]),
    'medium': np.array([0, 600, 1200, 2000, 3000, 4400, 8000, 20000, 70000]),
    'firm': np.array([0, 1000, 2000, 3500, 5500, 8000, 15000, 35000, 100000]),
}
COVERS = {
    'compliant': {'E_Pa': 1e6, 'thickness_mm': .2, 'poisson': .45, 'k_W_mK': .15},
    'moderate': {'E_Pa': 3e6, 'thickness_mm': .3, 'poisson': .45, 'k_W_mK': .18},
    'stiff': {'E_Pa': 8e6, 'thickness_mm': .5, 'poisson': .45, 'k_W_mK': .20},
}
HEADS = [
    {'name':'child_small', 'width_mm':120, 'pad_scale':.85, 'Rx_mm':90, 'Ry_mm':140},
    {'name':'child_medium', 'width_mm':130, 'pad_scale':.85, 'Rx_mm':110, 'Ry_mm':170},
    {'name':'child_large', 'width_mm':140, 'pad_scale':.85, 'Rx_mm':130, 'Ry_mm':190},
    {'name':'adult_small', 'width_mm':140, 'pad_scale':1, 'Rx_mm':110, 'Ry_mm':170},
    {'name':'adult_medium', 'width_mm':155, 'pad_scale':1, 'Rx_mm':140, 'Ry_mm':200},
    {'name':'adult_large', 'width_mm':170, 'pad_scale':1, 'Rx_mm':180, 'Ry_mm':240},
]
ARMS = {'none':(0,0), 'thin':(4,1.5), 'standard':(8,3), 'thick':(10,5)}


def grid(scale=1, nt=96, nu=10, edge_radius_mm=5):
    theta = (np.arange(nt)+.5)*2*np.pi/nt
    u = (np.arange(nu)+.5)/nu
    tt, uu = np.meshgrid(theta,u,indexing='ij')
    ai, bi, da, db = 25*scale, 35*scale, 17.5*scale, 17.5*scale
    a, b = ai+uu*da, bi+uu*db
    x, y = a*np.cos(tt), b*np.sin(tt)
    area = (a*db*np.cos(tt)**2+da*b*np.sin(tt)**2)*2*np.pi/nt/nu
    crosswidth = np.sqrt((da*np.cos(tt))**2+(db*np.sin(tt))**2)
    dist = np.minimum(uu,1-uu)*crosswidth
    r = edge_radius_mm*scale
    drop = np.where(dist<r, r-np.sqrt(np.maximum(0,r*r-(dist-r)**2)), 0)
    zone=(x>=-45*scale)&(x<=-10*scale)&(y>=-22*scale)&(y<=-10*scale)
    return x.ravel(),y.ravel(),area.ravel(),drop.ravel(),zone.ravel()


def solve(head, foam, cover, arm, softness, force, nt=96, nu=10,
          edge_radius_mm=5, contour_fraction=0, tilt_deg=0, cup_alignment_deg=0):
    x,y,area,drop,zone=grid(head['pad_scale'],nt,nu,edge_radius_mm)
    width,thickness=ARMS[arm]
    center_y=-16*head['pad_scale']
    arm_mask=(x>=-52*head['pad_scale'])&(x<=-9*head['pad_scale'])&(np.abs(y-center_y)<=width/2) if width else np.zeros(x.shape,dtype=bool)
    sag=x*x/(2*head['Rx_mm'])+y*y/(2*head['Ry_mm'])
    if head.get('flat_verification'):
        drop=np.zeros_like(drop)
        sag=np.zeros_like(sag)
    # Reference contour is shared by a size family, not fitted to each test head.
    ref_rx,ref_ry=(110,170) if head['name'].startswith('child') else (140,200)
    pad_contour=contour_fraction*(x*x/(2*ref_rx)+y*y/(2*ref_ry))
    tilt=x*np.tan(np.deg2rad(tilt_deg-cup_alignment_deg))
    shape_gap=drop+sag-pad_contour+tilt
    shape_gap-=shape_gap.min()
    material=np.where(zone,softness,1)
    thickness_foam=20.0  # same depth for both illustrative sizes
    effective_gap=shape_gap-thickness*arm_mask
    span=.020
    c=COVERS[cover]
    def field(approach):
        compression=np.maximum(0,approach-effective_gap)
        strain=compression/thickness_foam
        stress=np.interp(np.minimum(strain,.9),STRAIN,FOAMS[foam])*material
        # Synthetic densification extension: retain monotonic load at excessive strain.
        stress+=np.maximum(0,strain-.9)*2e6*material
        membrane=c['E_Pa']*(c['thickness_mm']/1000)*(compression/1000)**3/(6*span**4)
        pressure=stress+membrane
        return pressure,compression,strain
    low=-max(thickness,1)-1
    high=30.0
    for _ in range(43):
        middle=(low+high)/2
        pressure,comp,strain=field(middle)
        load=float(np.sum(pressure*area)*1e-6)
        if load<force:low=middle
        else:high=middle
    approach=(low+high)/2
    pressure,comp,strain=field(approach)
    contact=pressure>1
    load=float(np.sum(pressure*area)*1e-6)
    gap=np.maximum(0,effective_gap-approach)
    arm_peak=float(np.max(pressure[arm_mask])) if arm_mask.any() else 0
    result={
        'head':head['name'],'width_mm':head['width_mm'],'pad_scale':head['pad_scale'],
        'foam':foam,'cover':cover,'arm':arm,'zone_stiffness_ratio':softness,'pad_force_N':force,
        'peak_pressure_kPa':float(pressure.max()/1000),
        'arm_peak_pressure_kPa':arm_peak/1000,
        'mean_contact_pressure_kPa':float(force/(np.sum(area[contact])*1e-6)/1000),
        'contact_area_fraction':float(np.sum(area[contact])/np.sum(area)),
        'max_compression_mm':float(comp.max()),'max_strain':float(strain.max()),
        'gap_area_fraction_over_0_1mm':float(np.sum(area[gap>.1])/np.sum(area)),
        'max_surface_gap_mm':float(gap.max()),'force_residual_N':abs(load-force),
        'approach_mm':approach,
        'angular_lanes_without_contact_fraction':float(np.mean(np.all(gap.reshape(nt,nu)>.1,axis=1))),
    }
    return result,(x,y,area,pressure,gap)


def thermal(ambient, cover, foam_k, vent_l_min):
    # One thermal node for enclosed air/surface and one well-mixed vapor node.
    # No sweat feedback, spatial gradients or acoustic interaction is calculated.
    skin=34.0; skin_h=5.0; ambient_h=8.0; area=.0044
    depth=.020; capacitance=30.0  # synthetic effective pad+air heat capacity J/K
    c=COVERS[cover]
    resistance=depth/(foam_k*area)+(c['thickness_mm']/1000)/(c['k_W_mK']*area)+1/(ambient_h*area)
    ga=1/resistance
    gs=skin_h*area
    volume=.00010  # enclosed air volume m3, hypothesis
    def sat_density(temp):
        saturation_pa=610.94*math.exp(17.625*temp/(temp+243.04))
        return saturation_pa/(461.5*(temp+273.15)) # kg/m3
    vapor_ambient=.7*sat_density(ambient)
    vapor=vapor_ambient; temp=ambient; condensed=0.0
    dt=.5; ventilation=vent_l_min/1000/60
    water_source=.000020/3600 # illustrative 20 mg/h entering cavity
    for _ in range(int(3600/dt)):
        temp+=dt*(gs*(skin-temp)+ga*(ambient-temp))/capacitance
        vapor+=dt*(water_source/volume+ventilation*(vapor_ambient-vapor)/volume)
        saturated=sat_density(temp)
        if vapor>saturated:
            condensed+=(vapor-saturated)*volume
            vapor=saturated
    return {'ambient_C':ambient,'ambient_RH_percent':70,'cover':cover,'foam_k_W_mK':foam_k,
            'effective_vapor_exchange_L_min':vent_l_min,'temperature_60min_C':temp,
            'RH_60min_percent':100*vapor/sat_density(temp),'condensed_60min_mg':condensed*1e6}


def plot_map(name,fields,title):
    x,y,area,p,gap=fields
    peak=max(p.max(),1)
    elements=[]
    for xx,yy,aa,pp in zip(x,y,area,p):
        value=pp/peak
        red=int(50+205*value); blue=int(230*(1-value)); green=int(110*(1-value))
        elements.append(f'<circle cx="{260+xx*3.3:.2f}" cy="{250-yy*3.3:.2f}" r="3" fill="rgb({red},{green},{blue})"/>')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="520" height="520" viewBox="0 0 520 520"><rect width="520" height="520" fill="#fff"/><text x="20" y="25" font-family="sans-serif" font-size="15">{title}</text><text x="20" y="47" font-family="sans-serif" font-size="12">ASSUMPTION-BASED SPRING MODEL; NOT FEA</text>{"".join(elements)}<text x="20" y="492" font-family="sans-serif" font-size="13">Blue: low pressure. Red: peak {peak/1000:.2f} kPa.</text></svg>'
    (OUT/name).write_text(svg,encoding='utf-8')


def main():
    for curve in FOAMS.values():
        assert np.all(np.diff(curve)>0),'Nonmonotonic synthetic foam curve'
    x,y,area,drop,zone=grid()
    exact=math.pi*(42.5*52.5-25*35)
    assert abs(area.sum()-exact)<1e-7,'Annulus quadrature area mismatch'
    COVERS['verification_only']={'E_Pa':0,'thickness_mm':0,'poisson':0,'k_W_mK':.15}
    flat=dict(HEADS[4],flat_verification=True)
    expected_pressure=1200.0
    expected_force=expected_pressure*exact*1e-6
    flat_result,flat_fields=solve(flat,'medium','verification_only','none',1,expected_force)
    assert abs(flat_result['max_compression_mm']-2)<1e-8,'Flat uniform compression verification failed'
    assert abs(flat_fields[3].max()-expected_pressure)<1e-6,'Pressure conversion verification failed'
    del COVERS['verification_only']
    rows=[]
    for head,foam,cover,arm,softness,force in itertools.product(HEADS,FOAMS,COVERS,ARMS,[1,.75,.5],[1,2,3,4,6]):
        result,_=solve(head,foam,cover,arm,softness,force)
        rows.append(result)
    assert max(r['force_residual_N'] for r in rows)<1e-7,'Force balance did not converge'
    with (OUT/'mechanical_cases.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    thermals=[thermal(a,c,k,v) for a,c,k,v in itertools.product([28,32,36],COVERS,[.03,.05,.08],[.001,.01,.1])]
    for t in thermals:
        assert min(t['ambient_C'],34)-1e-6<=t['temperature_60min_C']<=max(t['ambient_C'],34)+1e-6
        assert 0<=t['RH_60min_percent']<=100.00001
    with (OUT/'thermal_cases.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(thermals[0]));writer.writeheader();writer.writerows(thermals)
    head=next(h for h in HEADS if h['name']=='adult_medium')
    baseline,bmap=solve(head,'medium','compliant','standard',1,2)
    candidate,cmap=solve(head,'medium','compliant','standard',.5,2)
    plot_map('uniform-pressure.svg',bmap,'Uniform material, standard frame, 2 N per pad')
    plot_map('soft-zone-pressure.svg',cmap,'Local stiffness ratio 0.5, standard frame, 2 N per pad')
    convergence=[]
    for nt,nu in [(48,6),(96,10),(192,20),(384,30)]:
        r,_=solve(head,'medium','compliant','standard',.5,2,nt,nu)
        convergence.append({'angular_points':nt,'radial_points':nu,'peak_kPa':r['peak_pressure_kPa'],
                            'arm_peak_kPa':r['arm_peak_pressure_kPa'],'contact_fraction':r['contact_area_fraction']})
    lookup={(r['head'],r['foam'],r['cover'],r['arm'],r['pad_force_N'],r['zone_stiffness_ratio']):r for r in rows}
    comparisons=[]
    for r in rows:
        if r['zone_stiffness_ratio']==.5 and r['arm']!='none':
            base=lookup[(r['head'],r['foam'],r['cover'],r['arm'],r['pad_force_N'],1)]
            comparisons.append(100*(base['arm_peak_pressure_kPa']-r['arm_peak_pressure_kPa'])/base['arm_peak_pressure_kPa'])
    inputs={'all_numbers_are_design_assumptions':True,'heads':HEADS,'covers':COVERS,
            'foam_strain_points':STRAIN.tolist(),'foam_compression_stress_Pa':{k:v.tolist() for k,v in FOAMS.items()},
            'arms_width_thickness_mm':ARMS,'pad_forces_N':[1,2,3,4,6],
            'headband_law':'F_pad = 2 N + k*(head_width-reference_width)/2; illustrative k=0.05 to 0.15 N/mm. This is a prescribed spring law, not a manufactured-band prediction.',
            'headband_reference_widths_mm':{'adult':155,'child':130},
            'cover_model':'p_cover=E*t*(compression_m)^3/(6*span_m^4), span=0.020 m. Illustrative scalar membrane surrogate, not a resolved cover model.',
            'thermal_assumptions':{'skin_C':34,'cavity_m3':.0001,'effective_heat_capacity_J_K':30,'water_entering_cavity_mg_h':20,'ambient_RH_percent':70}}
    (OUT/'assumptions.json').write_text(json.dumps(inputs,indent=2),encoding='utf-8')
    summary={'mechanical_case_count':len(rows),'thermal_case_count':len(thermals),
             'uniform_example':baseline,'soft_zone_example':candidate,'grid_refinement':convergence,
             'paired_frame_pressure_reduction_percent':{'minimum':min(comparisons),'median':float(np.median(comparisons)),'maximum':max(comparisons)},
             'max_force_residual_N':max(r['force_residual_N'] for r in rows),
             'model_type':'reduced independent nonlinear spring and lumped thermal/vapor screening; not Fusion FEA',
             'validated_materials':False,'clinical_or_acoustic_outcome_tested':False}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    headband=[]
    for h,k in itertools.product(HEADS,[.05,.1,.15]):
        reference=130 if h['name'].startswith('child') else 155
        headband.append({'head':h['name'],'width_mm':h['width_mm'],'reference_width_mm':reference,
                        'assumed_per_cup_spring_N_mm':k,'assumed_force_per_cup_N':2+k*(h['width_mm']-reference)/2})
    with (OUT/'headband_force_cases.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(headband[0]));w.writeheader();w.writerows(headband)
    reduction=100*(1-candidate['arm_peak_pressure_kPa']/baseline['arm_peak_pressure_kPa'])
    thermal_example=next(t for t in thermals if t['ambient_C']==32 and t['cover']=='compliant' and t['foam_k_W_mK']==.05 and t['effective_vapor_exchange_L_min']==.01)
    text=f'''# Prototype screening results

**These are hypothetical design scenarios, not validated FEA, measured material properties, acoustic protection ratings or evidence of wearer comfort.**

Both objectives remain: a standalone passive ear defender for sound-sensitive autistic users, and replacement cushions for glasses wearers. No diagnosis-specific pressure threshold is assumed.

## Completed numerical work
- {len(rows):,} nonlinear spring/contact cases, including no glasses and three arm thicknesses.
- {len(thermals)} lumped heat/vapor cases for 28, 32 and 36 C ambient at 70% RH.
- {len(headband)} prescribed spring-force cases across separate child/adult head-size hypotheses.
- Force residual below {summary['max_force_residual_N']:.2g} N.
- Closed-form flat-pad verification: 1200 Pa produces exactly 2 mm compression with the synthetic medium foam curve.
- Grid refinement tested. The nominal contact fraction varies from 70.9% to 67.6% at higher resolution; gap/coverage estimates must not be treated as converged precise predictions. Peak pressure is more stable for this example.

## Illustrative comparison
Adult-medium surrogate; 2 N per cup; standard 8 x 3 mm arm; synthetic medium foam; compliant cover.

| Quantity | Uniform material | Local stiffness ratio 0.5 |
|---|---:|---:|
| Peak pressure under frame | {baseline['arm_peak_pressure_kPa']:.2f} kPa | {candidate['arm_peak_pressure_kPa']:.2f} kPa |
| Overall peak pressure | {baseline['peak_pressure_kPa']:.2f} kPa | {candidate['peak_pressure_kPa']:.2f} kPa |
| Maximum compression | {baseline['max_compression_mm']:.2f} mm | {candidate['max_compression_mm']:.2f} mm |
| Approximate contact coverage | {100*baseline['contact_area_fraction']:.1f}% | {100*candidate['contact_area_fraction']:.1f}% |
| Maximum predicted surface gap | {baseline['max_surface_gap_mm']:.2f} mm | {candidate['max_surface_gap_mm']:.2f} mm |

The local frame-pressure reduction is {reduction:.1f}% **within this assumed model**. A stiffness reduction is built into the hypothesis; this is consistency/sensitivity evidence, not proof that an available foam will behave this way. Gaps remain, so this design has not established an adequate acoustic seal. Pressure on a rigid frame is only a proxy; it is not the pressure behind the glasses arm on a compliant human head.

## Working design targets to investigate
- Separate adult/child band sizes; initial per-cup force target 2 N at 155/130 mm head breadth respectively.
- Test sensitivity to spring slope 0.05-0.15 N/mm and head breadth changes. This prescribed law has not been derived from a curved band geometry or real band material.
- Initial medium foam target stress: 1.2 kPa at 10% compression, 3 kPa at 40%, 8 kPa at 70%. These are synthetic procurement/test targets, not manufacturer data.
- Test compliant region at 0.5 and 0.75 of base compression stress. Check extra compression and load transfer.
- Initial compliant cover assumption: 0.2 mm, E=1 MPa, Poisson ratio 0.45. Poisson ratio is recorded but not used in this scalar model. Actual material selection and continuous-skin modelling remain open.
- For replacement pads, screen 1-6 N per cup because clamp force belongs to the existing headphone. Actual compatibility needs measurements.

## Heat and humidity
At 32 C ambient, the illustrative compliant-cover, k=0.05 W/mK, 0.01 L/min exchange case predicts {thermal_example['temperature_60min_C']:.1f} C and {thermal_example['RH_60min_percent']:.0f}% RH after one hour. Moisture exchange strongly depends on the assumed leakage/permeation. This model cannot resolve sweat comfort, material sorption, moisture transport through a particular cover or cooling claims. Exchange levels are not proposed open vents; acoustic consequences must be checked separately.

## Model equations and omissions
Foam stress is a monotonic interpolation of the synthetic compression table. Local normal pressure is foam stress plus E*t*compression^3/(6*span^4), span=20 mm, as an illustrative cover-resistance surrogate. Total force is the area-weighted sum of pressure and is solved by bisection. Head contact surface is parabolic with separate principal radii. Frame thickness adds local compression. Foam cells are independent: no lateral shear, cover stress transfer, friction, skin compliance, ear geometry, actual frame bending, cup rocking or nonlinear 3D interaction is resolved. Actual 3D FEA and tests must address these omissions.

Heat/vapor use a single temperature node and well-mixed air volume, specified skin temperature and prescribed water input. No acoustic simulation was performed. No conclusions about autism, pain relief, hearing protection or universal fit follow from these calculations.

## Next engineering work
Improve head conformity or cup articulation to reduce seal gaps, then model the continuous cover and material interfaces. Obtain or measure foam/cover curves and band force, validate a nonlinear contact solver, build one physical comparison, and perform voluntary wearer trials. Develop headphone adapters per model; one pad does not fit all brands.

Files: assumptions.json, mechanical_cases.csv, thermal_cases.csv, headband_force_cases.csv, summary.json and explore.html.
'''
    (OUT/'report.md').write_text(text,encoding='utf-8')
    rows_for_ui=[{k:r[k] for k in ['head','foam','cover','arm','zone_stiffness_ratio','pad_force_N','peak_pressure_kPa','arm_peak_pressure_kPa','contact_area_fraction','max_strain','max_surface_gap_mm']} for r in rows]
    html='''<!doctype html><html><head><meta charset="utf-8"><title>Cushion scenario screening</title><style>body{font:16px system-ui;max-width:1050px;margin:35px auto;padding:20px;color:#173042;background:#f6f8fa}select{padding:8px;margin:5px}table{border-collapse:collapse;width:100%;background:white}td,th{padding:12px;text-align:left;border-bottom:1px solid #ddd}.warning{background:#fff0c2;padding:18px;border-radius:10px}img{width:48%;background:white}small{color:#536575}</style></head><body><h1>Cushion design: scenario screening</h1><p class="warning"><b>Hypothetical materials and head shapes.</b> These are reduced numerical models, not validated FEA, acoustic attenuation or evidence of comfort for autistic people or glasses wearers. Values compare assumptions only.</p><p>Choose a scenario to compare uniform material with a softer local region. Wearer comfort thresholds are not assumed.</p><div id="filters"></div><table><thead><tr><th>Local stiffness / main foam</th><th>Peak pressure, kPa</th><th>Frame-region peak, kPa</th><th>Contact area</th><th>Max strain</th><th>Max gap, mm</th></tr></thead><tbody id="results"></tbody></table><h2>One illustrative pressure comparison</h2><img src="uniform-pressure.svg"><img src="soft-zone-pressure.svg"><p>Adult-medium surrogate; medium synthetic foam; compliant synthetic cover; standard frame; 2 N per pad. Colour scales are independent; read the peak labels.</p><h2>Interpretation limits</h2><p>Lower local stiffness can redistribute load, but contact coverage, compression and gaps must also be inspected. A gap proxy cannot predict decibel reduction. Higher humidity-exchange assumptions can improve cavity humidity but may conflict with acoustic sealing.</p><p>For replacement cushions, evaluate several headphone clamp forces. For the standalone ear defender, headband geometry and force must be calibrated separately. Child sizing remains a separate fit problem.</p><p>Full results: <a href="mechanical_cases.csv">mechanical CSV</a>, <a href="thermal_cases.csv">thermal CSV</a>, <a href="assumptions.json">assumptions</a>.</p><script>const data=DATA;const keys=['head','foam','cover','arm','pad_force_N'];const defaults={head:'adult_medium',foam:'medium',cover:'compliant',arm:'standard',pad_force_N:2};for(const k of keys){const label=document.createElement('label');label.textContent=k.replaceAll('_',' ')+': ';const s=document.createElement('select');s.id=k;for(const v of [...new Set(data.map(r=>r[k]))]){const o=document.createElement('option');o.value=v;o.textContent=v;s.append(o)}s.value=defaults[k];s.onchange=render;label.append(s);document.querySelector('#filters').append(label)}function render(){const rows=data.filter(r=>keys.every(k=>String(r[k])===document.getElementById(k).value));document.querySelector('#results').innerHTML=rows.map(r=>`<tr><td>${r.zone_stiffness_ratio}</td><td>${r.peak_pressure_kPa.toFixed(2)}</td><td>${r.arm_peak_pressure_kPa.toFixed(2)}</td><td>${(100*r.contact_area_fraction).toFixed(1)}%</td><td>${(100*r.max_strain).toFixed(1)}%</td><td>${r.max_surface_gap_mm.toFixed(2)}</td></tr>`).join('')}render();</script></body></html>'''
    (OUT/'explore.html').write_text(html.replace('DATA',json.dumps(rows_for_ui)),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
