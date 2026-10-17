"""Band size recipes for equal prototype load; 2 N is NOT a comfort/safety limit."""
import json
from pathlib import Path
import band_fem as b
import contact_membrane_fem as m
import screening as s
ROOT=Path(__file__).parent;OUT=ROOT/'engineering-final-results'

def main():
    rows=[]
    for head in s.HEADS:
        family='child' if head['name'].startswith('child') else 'adult';c=b.CONFIG[family]
        contact,_=m.solve(head,'standard',.5,force=2,tension=1)
        worn_span=head['width_mm']+70-2*contact['absolute_approach_mm']
        # Vary rest span rather than force a common band onto very different head widths.
        lo=worn_span/2-25;hi=worn_span/2-1
        for _ in range(13):
            halfspan=(lo+hi)/2;opening=worn_span-2*halfspan
            band,_=b.solve(halfspan,c['band_width'],c['band_thickness'],opening,arch_height=c['band_arch_height'])
            if band['force_per_cup_N']>2:lo=halfspan
            else:hi=halfspan
        halfspan=(lo+hi)/2
        band,_=b.solve(halfspan,c['band_width'],c['band_thickness'],worn_span-2*halfspan,arch_height=c['band_arch_height'])
        r={'scenario':head['name'],'family':family,'target_comparison_force_N':2,'predicted_N':band['force_per_cup_N'],
           'head_breadth_mm':head['width_mm'],'band_rest_halfspan_mm':halfspan,'band_arch_height_mm':c['band_arch_height'],
           'band_thickness_mm':c['band_thickness'],'band_width_mm':c['band_width'],'compressed_mount_span_mm':worn_span,
           'contact_fraction_at_target':contact['contact_area_fraction'],'E_MPa':2000}
        assert abs(r['predicted_N']-2)<.003
        rows.append(r);print(r,flush=True)
    data={'recipes':rows,'status':'numerical size recipes; not yet generated as CAD variants',
          'limitations':['2 N is only a common comparison load, not an acceptable load for any particular person',
                         'Assumed E=2000 MPa and standard rounded frame; other material/frames change fit',
                         'Same two cushion families; actual ears/head anatomy and contact convergence require validation',
                         'Recipes alter circular-cap span; manufacture and material springback unverified']}
    (OUT/'size_band_recipes.json').write_text(json.dumps(data,indent=2))

if __name__=='__main__':main()
