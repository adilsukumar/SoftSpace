"""V5 slider + circular cap beam and cushion screening. Synthetic inputs only."""
import csv,json,math
from pathlib import Path
import numpy as np
import band_fem as b
import contact_membrane_fem as m
import screening as s
ROOT=Path(__file__).parent;OUT=ROOT/'engineering-v5-results';OUT.mkdir(exist_ok=True)
CONFIG=json.loads(json.dumps(b.CONFIG));CONFIG['child']['band_thickness']=3.0;CONFIG['adult']['band_thickness']=3.6

def solve(family,R,extension,opening,E=2000,cap_elements=40,leg_elements=8,steps=8):
    c=CONFIG[family];h=c['band_arch_height'];circle=(R*R+h*h)/(2*h)
    a=math.asin(R/circle);theta=np.linspace(-a,a,cap_elements+1)
    cap=np.column_stack([circle*np.sin(theta),circle*np.cos(theta)-(circle-h)])
    length=30+extension
    left=np.column_stack([np.full(leg_elements,-R),np.linspace(-length,0,leg_elements+1)[:-1]])
    right=np.column_stack([np.full(leg_elements,R),np.linspace(0,-length,leg_elements+1)[1:]])
    ref=np.vstack([left,cap,right])
    # Weakest 4x16 sliding tongue model throughout legs. Guides/overlap add stiffness in reality.
    t=np.r_[np.full(leg_elements,4.),np.full(cap_elements,c['band_thickness']),np.full(leg_elements,4.)]
    w=np.r_[np.full(leg_elements,16.),np.full(cap_elements,c['band_width']),np.full(leg_elements,16.)]
    return b.solve(R,c['band_width'],c['band_thickness'],opening,E=E,reference=ref,section_thickness=t,section_width=w,load_steps=steps)

def main():
    b.verification();recipes=[];rows=[];meshes=[]
    candidates=json.loads((OUT/'cushion_summary.json').read_text())['family_candidates']
    for head in s.HEADS:
        family=head['name'].split('_')[0]
        pad=next(p for p in candidates if p['family']==family)
        contact,_=m.solve(head,force=2,contour=pad['contour_fraction'],foam_multiplier=pad['foam_multiplier'])
        spread=head['width_mm']+70-2*contact['absolute_approach_mm']
        lo=(spread-60)/2;hi=(spread-1)/2
        low_force=solve(family,lo,15,spread-2*lo)[0]['force_per_cup_N']
        high_force=solve(family,hi,15,spread-2*hi)[0]['force_per_cup_N']
        if not high_force<2<low_force:raise RuntimeError(f'2 N target not bracketed: {head["name"]} {low_force} {high_force}')
        for _ in range(15):
            R=(lo+hi)/2;r,_=solve(family,R,15,spread-2*R)
            if r['force_per_cup_N']>2:lo=R
            else:hi=R
        R=(lo+hi)/2
        recipe={'name':head['name'],'family':family,'band_halfspan_mm':R,'arch_height_mm':CONFIG[family]['band_arch_height'],
                'band_thickness_mm':CONFIG[family]['band_thickness'],'band_width_mm':CONFIG[family]['band_width'],
                'contour_fraction':pad['contour_fraction'],'foam_multiplier':pad['foam_multiplier'],
                'extension_range_mm':[0,30],'reference_extension_mm':15,'target_comparison_force_N':2,
                'reference_head_width_mm':head['width_mm'],'tongue_thickness_mm':4,'tongue_width_mm':16,
                'guide_internal_clearance_mm':.3,'minimum_engagement_mm':30,'detent_pitch_mm':5}
        recipes.append(recipe)
        for extension in [0,15,30]:
            # Load curve then contact fixed-point iteration; E scales the assumed linear elastic model.
            maximum_opening=head['width_mm']+70-2*R+2
            rr,_=solve(family,R,extension,maximum_opening,steps=30)
            xx=np.array([0]+[x['opening_mm'] for x in rr['history']]);yy=np.array([0]+[x['force_per_cup_N'] for x in rr['history']])
            for E in [1500,2000,2500]:
                F=float(np.interp(head['width_mm']+70-2*R,xx,yy)*E/2000)
                for it in range(35):
                    cc,_=m.solve(head,force=F,contour=pad['contour_fraction'],foam_multiplier=pad['foam_multiplier'])
                    opening=head['width_mm']+70-2*R-2*cc['absolute_approach_mm']
                    assert 0<=opening<=maximum_opening
                    target=float(np.interp(opening,xx,yy)*E/2000)
                    if abs(F-target)<2e-4:break
                    F=(F+target)/2
                else:raise RuntimeError('Slider/contact equilibrium failed')
                direct,_=solve(family,R,extension,opening,E=E)
                cc.update(extension_mm=extension,E_MPa=E,band_halfspan_mm=R,opening_mm=opening,
                          max_elastic_stress_MPa=direct['max_elastic_stress_MPa'],force_interpolation_error_percent=100*abs(direct['force_per_cup_N']/F-1),
                          equilibrium_mismatch_N=abs(F-target))
                rows.append(cc)
            print(head['name'],extension,'complete',flush=True)
        for n in [20,40,80]:
            r,_=solve(family,R,15,spread-2*R,cap_elements=n,leg_elements=n//5)
            meshes.append({'head':head['name'],'cap_elements':n,'force_N':r['force_per_cup_N'],'stress_MPa':r['max_elastic_stress_MPa']})
    with (OUT/'slider_fit.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result={'recipes':recipes,'cases':rows,'mesh_checks':meshes,'material_inputs':'E=1500/2000/2500 MPa, linear elastic assumed, tongue 4x16 mm',
            'comparison_target_is_not_a_comfort_limit':True,'model':'Nonlinear planar cap plus variable-section vertical slider beam; iterated scalar membrane/foam contact',
            'limitations':['Telescopic overlap treated at weakest tongue section; guide slip, detent notches, friction, tolerance and torsion omitted',
                           'Synthetic head widths; vertical head dimensions and ear anatomy not established','Contact peaks remain mesh-sensitive',
                           'No real foam/cover, skin deformation, sensory acceptance, acoustic or safety validation']}
    (OUT/'extendable_summary.json').write_text(json.dumps(result,indent=2))
    (ROOT/'extendable-recipes.json').write_text(json.dumps(recipes,indent=2))
    print('Saved',len(rows),'cases and six size recipes',flush=True)
if __name__=='__main__':main()
