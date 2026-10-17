"""Design comparisons and finite-area pressure convergence; no comfort thresholds."""
import json,csv
from pathlib import Path
import numpy as np
import contact_membrane_fem as m
import screening as s
ROOT=Path(__file__).parent;OUT=ROOT/'engineering-v5-results';OUT.mkdir(exist_ok=True)

def sensor_pressure(head,fields):
    xy,tri,area,p,gap,d=fields;scale=head['pad_scale']
    # Fixed 6 mm diameter virtual sensors; not nodal point peaks.
    means=[]
    for x in [-38,-32,-26,-20]:
        for y in [-19,-16,-13]:
            mask=((xy[:,0]-x*scale)**2+(xy[:,1]-y*scale)**2)<9
            if area[mask].sum():means.append(float(np.sum(p[mask]*area[mask])/np.sum(area[mask])/1000))
    return max(means)

def main():
    rows=[]
    for head in s.HEADS:
        for multiplier in [.5,1]:
            for contour in [.5,.75,1]:
                for arm in ['standard','thick']:
                    r,f=m.solve(head,arm=arm,contour=contour,foam_multiplier=multiplier)
                    r.update(foam_multiplier=multiplier,max_virtual_sensor_6mm_kPa=sensor_pressure(head,f))
                    rows.append(r)
        print(head['name'],'12 cushion comparisons complete',flush=True)
    # Rank family candidates by worst modeled gap, then greatest minimum contact area.
    picks=[]
    for family in ['adult','child']:
        ranked=[]
        for mult in [.5,1]:
            for contour in [.5,.75,1]:
                selected=[r for r in rows if r['head'].startswith(family) and r['foam_multiplier']==mult and r['contour_fraction']==contour]
                ranked.append({'family':family,'foam_multiplier':mult,'contour_fraction':contour,
                               'worst_gap_mm':max(r['max_gap_mm'] for r in selected),'minimum_contact_fraction':min(r['contact_area_fraction'] for r in selected)})
        picks.append(sorted(ranked,key=lambda r:(r['worst_gap_mm'],-r['minimum_contact_fraction']))[0])
    refs=[]
    for family in ['adult','child']:
        pick=next(p for p in picks if p['family']==family);head=next(h for h in s.HEADS if h['name']==family+'_medium')
        for nt,nr in [(64,9),(96,13),(128,17),(192,25),(256,33)]:
            r,f=m.solve(head,contour=pick['contour_fraction'],foam_multiplier=pick['foam_multiplier'],nt=nt,nr=nr)
            r.update(foam_multiplier=pick['foam_multiplier'],max_virtual_sensor_6mm_kPa=sensor_pressure(head,f));refs.append(r)
            print(family,nt,'refinement complete',flush=True)
    convergence=[]
    for family in ['adult','child']:
        rr=[r for r in refs if r['head'].startswith(family)];a,z=rr[-2:]
        change=100*abs(z['max_virtual_sensor_6mm_kPa']/a['max_virtual_sensor_6mm_kPa']-1)
        point=100*abs(z['peak_kPa']/a['peak_kPa']-1)
        convergence.append({'family':family,'virtual_sensor_change_percent':change,'virtual_sensor_converged_under_5_percent':change<5,
                            'nodal_peak_change_percent':point,'nodal_peak_converged_under_5_percent':point<5})
    with (OUT/'cushion_comparisons.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result={'cases':rows,'family_candidates':picks,'refinements':refs,'convergence':convergence,
            'ranking_is_not_a_comfort_or_safety_criterion':True,'limitations':['Synthetic foam stiffness multipliers and rounded frame geometries',
            '6 mm virtual-sensor averages do not replace point peak validation or wearer comfort','Selection screened at 2 N; coupled bands must be rerun with selected pad']}
    (OUT/'cushion_summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(picks),flush=True)
if __name__=='__main__':main()
