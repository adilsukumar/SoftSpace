"""Iteratively couple band FEM load-opening curves to membrane/foam compression."""
import csv,json
from pathlib import Path
import numpy as np
import band_fem as b
import contact_membrane_fem as m
import screening as s
ROOT=Path(__file__).parent;OUT=ROOT/'engineering-final-results'

def main():
    curves={};errors=[]
    for family in ['adult','child']:
        c=b.CONFIG[family]
        r,_=b.solve(c['band_radius'],c['band_width'],c['band_thickness'],50,load_steps=20,arch_height=c.get('band_arch_height'))
        curves[family]=[[0,0]]+[[h['opening_mm'],h['force_per_cup_N']] for h in r['history']]
        check,_=b.solve(c['band_radius'],c['band_width'],c['band_thickness'],23.75,arch_height=c.get('band_arch_height'))
        predicted=np.interp(23.75,*np.array(curves[family]).T)
        errors.append({'family':family,'check_opening_mm':23.75,'interpolated_N':float(predicted),'direct_FEM_N':check['force_per_cup_N'],
                       'relative_error':abs(predicted/check['force_per_cup_N']-1)})
    rows=[]
    for head in s.HEADS:
        family='child' if head['name'].startswith('child') else 'adult';c=b.CONFIG[family]
        opening_uncompressed=head['width_mm']+70-2*c['band_radius']
        xx,yy=np.array(curves[family]).T
        for E in [1500,2000,2500]:
            for ratio in [1,.5]:
                F=float(np.interp(opening_uncompressed,xx,yy)*E/2000)
                for iteration in range(30):
                    r,_=m.solve(head,'standard',ratio,F,tension=1)
                    opening=opening_uncompressed-2*r['absolute_approach_mm']
                    if not 0<=opening<=50:raise RuntimeError('Fit leaves precomputed band load curve')
                    target=float(np.interp(opening,xx,yy)*E/2000)
                    mismatch=target-F
                    if abs(mismatch)<2e-4:break
                    F=.5*(F+target)
                else:raise RuntimeError('Band-pad coupled equilibrium did not converge')
                r.update(family=family,E_MPa=E,band_opening_compressed_mm=opening,
                         coupled_force_mismatch_N=mismatch,coupled_iterations=iteration+1)
                rows.append(r)
                print(f"{head['name']} E={E} ratio={ratio}: {F:.3f} N/cup, mismatch {mismatch:.2g}",flush=True)
    with (OUT/'coupled_fit_cases.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'case_count':len(rows),'force_curves':curves,'interpolation_check':errors,'cases':rows,
             'model':'Iterated band FEM and scalar membrane/foam contact; common lateral force and compressed mount separation',
             'limitations':['Not a monolithic 3D assembly contact model','Assumed 35 mm mount offset per side and ideal pinned band ends','Synthetic material/head/frame properties','Tension 1 N/m assumption','Coupled cases use 64x9 mesh; contact peaks require refinement before design limits']}
    (OUT/'coupled_summary.json').write_text(json.dumps(summary,indent=2))

if __name__=='__main__':main()
