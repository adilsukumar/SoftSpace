"""V2 contact-shape sensitivity study; synthetic inputs, not validated FEA."""
import csv, itertools, json
from pathlib import Path
import numpy as np
import screening as s

OUT=Path(__file__).parent/'shape-study-results'
OUT.mkdir(exist_ok=True)
SHAPES={
    'flat_R5':(5,0),
    'flat_R2':(2,0),
    'half_contour_R2':(2,.5),
    'reference_contour_R2':(2,1),
}

def main():
    rows=[]
    for head,foam,cover,arm,force,ratio,shape,tilt,mount in itertools.product(
        s.HEADS,['soft','medium'],['compliant','moderate'],s.ARMS,[1,2,4],
        [1,.5],SHAPES,[0,5],['fixed','ideal_alignment']):
        # Ideal alignment removes a prescribed 5 degree plane error. It does not
        # predict articulation, hinge friction or a manufactured headband's force.
        alignment=tilt if mount=='ideal_alignment' else 0
        radius,contour=SHAPES[shape]
        r,_=s.solve(head,foam,cover,arm,ratio,force,edge_radius_mm=radius,
                   contour_fraction=contour,tilt_deg=tilt,cup_alignment_deg=alignment)
        r.update(shape=shape,imposed_tilt_deg=tilt,mount=mount)
        rows.append(r)
    assert max(r['force_residual_N'] for r in rows)<1e-7
    with (OUT/'cases.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    nominal=[r for r in rows if r['head']=='adult_medium' and r['foam']=='medium'
             and r['cover']=='compliant' and r['arm']=='standard' and r['pad_force_N']==2
             and r['zone_stiffness_ratio']==.5 and r['imposed_tilt_deg']==0 and r['mount']=='fixed']
    refinement=[]
    for shape,(radius,contour) in SHAPES.items():
        for nt,nu in [(96,10),(192,20),(384,30)]:
            r,_=s.solve(s.HEADS[4],'medium','compliant','standard',.5,2,nt,nu,
                       edge_radius_mm=radius,contour_fraction=contour)
            refinement.append(dict(shape=shape,angular_points=nt,radial_points=nu,
                                   peak_kPa=r['peak_pressure_kPa'],contact_fraction=r['contact_area_fraction'],
                                   lanes_without_contact=r['angular_lanes_without_contact_fraction']))
    # Identical alignment and no tilt must be exactly equivalent to fixed/no tilt.
    test,_=s.solve(s.HEADS[4],'medium','compliant','standard',.5,2,tilt_deg=5,cup_alignment_deg=5)
    baseline,_=s.solve(s.HEADS[4],'medium','compliant','standard',.5,2)
    assert abs(test['peak_pressure_kPa']-baseline['peak_pressure_kPa'])<1e-10
    summary={'case_count':len(rows),'nominal_comparison':nominal,'grid_refinement':refinement,
             'validated':False,'model':'independent nonlinear springs, scalar cover resistance',
             'reference_curvatures_mm':{'adult':[140,200],'child':[110,170]},
             'max_force_residual_N':max(r['force_residual_N'] for r in rows)}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    table='\n'.join(f"| {r['shape']} | {r['peak_pressure_kPa']:.3f} | {r['arm_peak_pressure_kPa']:.3f} | {100*r['contact_area_fraction']:.1f}% | {r['max_surface_gap_mm']:.2f} | {100*r['angular_lanes_without_contact_fraction']:.1f}% |" for r in nominal)
    report=f'''# Contact-shape study V2

These are {len(rows):,} assumption-based numerical cases, not Fusion FEA or measured comfort/noise reduction. Material curves, head shapes, tilt, and forces are invented design inputs. V1 outputs remain preserved.

## Nominal comparison

Adult medium reference, medium foam, compliant scalar cover, standard straight glasses arm, 2 N per cup, local foam stress ratio 0.5, zero imposed tilt.

| Contact shape | Overall peak kPa | Frame peak kPa | Contact area | Largest surface gap mm | Angular lanes without contact |
|---|---:|---:|---:|---:|---:|
{table}

R5/R2 are 5/2 mm nominal edge-rounding radii. Contour subtracts 50% or 100% of a shared family-reference parabolic head sag from the pad contact-gap field. This represents a cushion face recessed at its centre relative to its perimeter. It does not fit each tested head separately. Actual child and adult anatomy can differ considerably.

## Interpretation limits

Lower pressure and fewer gaps within this model justify comparing physical prototypes; they do not establish comfort, safety or attenuation. The angular-lane metric flags rays across the annulus with no sampled contact. It is a coarse gap indicator, not proof of a continuous airtight seal or an acoustic leak calculation. Compare grid refinement before using contact fractions.

Ideal alignment cancels imposed planar tilt only. A manufactured pivot can have friction, stops and unequal load that this model excludes. Fixed/aligned cases are bounds, not an implemented mechanism.

The cover remains a scalar resistance term with no lateral coupling, stitching, friction, tension or bridging across the soft region. A continuous cover must be represented explicitly in a subsequent nonlinear contact model using measured properties.

## Separate product requirements

- Own ear defender: adjustable size families, measured band force versus opening, articulated cups, continuous cover, foam compression/recovery, skin contact, heat/moisture and measured acoustic attenuation. Adult and child fitting require separate validation.
- Replacement cushion: the same materials and contact checks plus each host headphone's clamp force, mounting geometry, ear clearance, acoustic frequency response and seal. Host force is outside our control, but must still be a test input. One cushion does not automatically fit all brands.

## Next engineering gate

Use the contact comparison to choose candidate face profiles, then measure foam compression curves and cover tensile/permeation properties. Check band force over multiple head breadths. Model skin/glasses/cover/foam contact with a nonlinear solver and verify against compression and pressure-map bench measurements. Keep a uniform cushion as the control. Conduct voluntary wearer evaluations for texture, heat, removal and comfort; simulations cannot establish sensory acceptance.

Thermal results from V1 are unchanged and humidity remains unresolved. No air vent or sound-reduction claim follows from this study.
'''
    (OUT/'report.md').write_text(report,encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
