"""Package the V5 design and numerical evidence without asserting product validation."""
import json,zipfile,hashlib,html
from pathlib import Path
import extendable_study as e
ROOT=Path(__file__).parent;OUT=ROOT/'engineering-v5-results'

def main():
    fit=json.loads((OUT/'extendable_summary.json').read_text());pad=json.loads((OUT/'cushion_summary.json').read_text())
    moisture=json.loads((OUT/'moisture_summary.json').read_text());sound=json.loads((OUT/'acoustic_summary.json').read_text())
    cad=json.loads((ROOT/'cad_v5_report.json').read_text())
    neighbors=json.loads((OUT/'size_overlap_summary.json').read_text())
    recipes=fit['recipes'];rows=fit['cases']
    gates={'CAD exports':cad['status'],'Slider travel clearance':'passed' if not cad.get('failed_gates') else 'FAILED: '+', '.join(cad['failed_gates']),
           'Beam mesh and force balance':'passed under reduced-model assumptions',
           '6 mm virtual pressure sensor mesh change':'passed <5% for both nominal family cases',
           'Nodal point pressure peak convergence':'FAILED for both families; do not make peak-pressure claims',
           'Moisture over all screened conditions':'FAILED: 3 of 27 cases saturate at the 3000 WVTR hypothesis',
           'Acoustic FEM numerical checks':'passed for assumed 1D 31.5–250 Hz model',
           'Broadband attenuation and real sound reduction':'not established',
           'Sensory acceptance, texture and perceived safety':'not simulatable with these mechanical/acoustic equations; wearer evidence required',
           'Vertical head fit / scalp pressure':'not established; synthetic head breadths only',
           'Material durability and clamp retention':'not established; no measured allowables or fatigue/creep data',
           'Manufacturing cost / brand compatibility':'not established'}
    nominal=[r for r in rows if r['extension_mm']==15 and r['E_MPa']==2000]
    table='\n'.join(f"| {p['name']} | {2*p['band_halfspan_mm']:.2f} | {p['band_thickness_mm']:.1f} | {next(r['force_N'] for r in nominal if r['head']==p['name']):.3f} |" for p in recipes)
    checks='\n'.join(f'| {k} | {v} |' for k,v in gates.items())
    force_min=min(r['force_N'] for r in rows);force_max=max(r['force_N'] for r in rows)
    area_min=min(r['contact_area_fraction'] for r in rows);gap_max=max(r['max_gap_mm'] for r in rows)
    last_mesh=[]
    for p in recipes:
        mesh=[r for r in fit['mesh_checks'] if r['head']==p['name']]
        last_mesh.append(100*abs(mesh[-1]['force_N']/mesh[-2]['force_N']-1))
        plots=[]
        for extension,color in [(0,'#147868'),(15,'#e88735'),(30,'#446dba')]:
            r=next(r for r in rows if r['head']==p['name'] and r['extension_mm']==extension and r['E_MPa']==2000)
            _,xy=e.solve(p['family'],p['band_halfspan_mm'],extension,r['opening_mm'])
            plots.append('<polyline points="'+' '.join(f'{260+x*1.6:.2f},{180-y*1.6:.2f}' for x,y in xy)+f'" fill="none" stroke="{color}" stroke-width="3"/>')
        svg='<svg xmlns="http://www.w3.org/2000/svg" width="520" height="360"><rect width="100%" height="100%" fill="white"/><text x="15" y="25" font-family="sans-serif">'+p['name']+' — reduced FEM deformed band</text>'+''.join(plots)+'<text x="15" y="325" font-family="sans-serif">Green: 0 mm; orange: 15 mm; blue: 30 mm extension</text><text x="15" y="347" font-family="sans-serif">Assumed E=2000 MPa; not a measured worn shape</text></svg>'
        (OUT/(p['name']+'-slider-beam.svg')).write_text(svg)
    report=f'''# V5 extendable ear defender — simulation review

Six provisional sizes now have 30 mm sliding crown-to-cup adjustment. Each side has a 4×16 mm tongue, a sleeve with 0.3 mm nominal clearance per face, and a hand clamp knob. It requires loosening/tightening a knob; it is not a validated click-detent mechanism. The new cushion curvature fraction is 1.0, selected from 72 synthetic comparisons. Main/soft-zone foam ratios remain assumed 1/0.5. Adult/child band sections were changed to 3.6/3.0 mm for the longer arms.

This completes a defined digital screening exercise, not every test required for a finished product. The result supports a conditional physical prototype investigation. It does not establish comfort, noise reduction, sensory benefit, a safety rating, mass-production readiness or cost.

## Sizes

| Synthetic scenario | Unloaded band width mm | Cap thickness mm | Nominal force per cup N |
|---|---:|---:|---:|
{table}

Each width is calibrated at 15 mm slider extension, E=2000 MPa and a 2 N comparison load after modeled cushion compression. 2 N is not a clinical, comfort or safety threshold. These sizes are based on six hypothetical head breadths, not anthropometric percentiles. Sliding changes crown-to-cup distance, not a substitute for width selection. Real vertical head dimensions and ear/scalp clearance are still missing.

## Verification and unresolved gates

| Check | Status |
|---|---|
{checks}

The CAD report is the authoritative export/clearance record. It contains 30 exports when the six-size run is complete: replacement cushion STEP, nominal defender STEP/F3D, and retracted/extended STEP for each size. Documents contain hidden source construction geometry and pose components; use designated product components for meshing. Bodies are imported/frozen; regenerate from recipes. Recipe widths and local sections correspond to the beam model, but the model omits 3D guide details and horizontal fork offsets.

## Mechanical results

54 iterated slider/cushion cases cover six sizes, three extensions and three assumed moduli. Force ranges from {force_min:.2f} to {force_max:.2f} N per cup. Minimum predicted contact area is {100*area_min:.1f}%, and the largest predicted local gap is {gap_max:.3f} mm. These gaps do not establish a leak path or an acoustic seal. Maximum nominal elastic stress across cases is {max(r['max_elastic_stress_MPa'] for r in rows):.2f} MPa; no measured allowable exists, so no safety factor is claimed.

The six beam meshes (20/40/80 cap elements plus legs) change nominal force by at most {max(last_mesh):.3f}% between the last two refinements. Direct FEM checks differ from interpolated forces by at most {max(r['force_interpolation_error_percent'] for r in rows):.3f}%. Equilibrium residuals are recorded. Variable-section beam elements represent the weakest sliding tongue over the whole leg, omitting overlap stiffening, joint friction, notches, shear, torsion, creep and fatigue. Stabilized Newton directions converge the original equilibrium residual; this is not dynamic buckling or a global stability proof.

72 cushion comparisons rank whole-foam stiffness multipliers and curvature at 2 N under standard/thick hypothetical frames. Fraction 1.0 achieved at least 98.4% contact area in that comparison grid. Coupled force variations reduce the worst contact fraction to the value above. Ranking minimizes modeled gap; it is not a user comfort criterion.

The pressure refinement compares fixed 6 mm diameter virtual sensors as well as nodal peaks. Adult/child averaged-pressure changes are {pad['convergence'][0]['virtual_sensor_change_percent']:.2f}%/{pad['convergence'][1]['virtual_sensor_change_percent']:.2f}%; nodal-peak changes remain {pad['convergence'][0]['nodal_peak_change_percent']:.2f}%/{pad['convergence'][1]['nodal_peak_change_percent']:.2f}%. A stable area average does not repair unstable point peaks. No numerical pressure reduction or pain-prevention claim is warranted.

12 further cases vary head breadth by ±5 mm around each size at nominal extension/modulus while holding synthetic curvature fixed. Their force range is {min(r['force_N'] for r in neighbors['cases']):.2f}–{max(r['force_N'] for r in neighbors['cases']):.2f} N/cup. This checks local width sensitivity only, not anatomical population coverage.

## Moisture and heat

81 further one-hour scenarios compare WVTR hypotheses 1000/3000/5000 g/m²/day at a specified 2000 Pa test difference. At 32°C, 70% RH and assumed 100 mg/h water input, the 3000 hypothesis predicts 71.7% cavity RH and no condensation. Nevertheless, 3 of its 27 scenarios saturate. More vapor transmission helps under favorable gradients, but cannot guarantee drying in hot humid air. No fabric with these properties has been selected or measured. The lumped thermal model omits local skin temperature, sweating feedback and evaporation cooling. No vent holes were added to sacrifice sealing.

## Sound

48 acoustic parameter combinations / 2304 frequency rows solve a 1D Helmholtz cavity FEM with a hypothetical compliant wall and slit. Analytic low-frequency and 10/20/40 element checks pass. It is restricted to 31.5–250 Hz and replaces the curved cup with an equivalent clamped circular plate; material and damping are assumptions. The predicted differences are model outputs, not a product rating. Real cover transmission, liner impedance, ear transfer, seams and structural cup modes are absent. No broadband, NRR/SNR, real noise-reduction or autism-benefit claim follows from this solve.

## What cannot be finished by simulation alone

Sensory acceptance, willingness to wear, perceived safety, tactile texture, cleaning feel and actual discomfort require voluntary wearer feedback. Measured foam/cover/band properties are needed to validate the numerical inputs. Child-safe adjustment, clamp retention, pinch/access hazards, fatigue, drop tests and acoustics need physical evaluation. The lowest-cost design cannot be established without manufacturing quotations.

Before wearer trials: measure material curves; compare band force versus spread/extension; use a dummy-head compression rig with glasses; verify slider/clamp retention; measure sound reduction with/without glasses; verify fit, weight and surface finish. Begin with a supervised adult prototype investigation. Child use requires separate fit and hardware assessment.

## Reproduce

Python + NumPy: `cushion_v5_study.py`, `extendable_study.py`, `moisture_v5_study.py`, `acoustic_v5_fem.py`, then `prepare_v5_builder.py`. Run registered `CushionNext` in Fusion to build `EngineeringV5.py`, then run `build_v5_review.py`. The recipe source is `extendable-recipes.json`, with base cushion inputs in `engineering-final.json`. Previous V4 studies remain separate.
'''
    (OUT/'REVIEW.md').write_text(report,encoding='utf-8')
    (OUT/'readiness.json').write_text(json.dumps({'gates':gates,'production_ready':False,'physical_validation_complete':False,'cad_files':cad['files']},indent=2))
    data=json.dumps({'cases':rows,'gates':gates,'recipes':recipes})
    page='''<!doctype html><meta charset="utf-8"><title>V5 extendable design review</title><style>body{font:16px system-ui;color:#203b33;background:#f3f6f2}main{max-width:1050px;margin:35px auto;background:white;padding:30px;border-radius:18px}aside{padding:18px;background:#fff1d6}select{padding:8px;margin:8px}table{border-collapse:collapse;width:100%}th,td{text-align:left;padding:10px;border-bottom:1px solid #ddd}h2{margin-top:32px}</style><main><h1>Six sizes · sliding headbands</h1><aside>Provisional digital prototypes. Sensory acceptance and real sound reduction remain untested. Point pressure peaks and some moisture scenarios fail current gates.</aside><h2>Explore modeled fit</h2><label>Extension <select id="ext"><option>15</option><option>0</option><option>30</option></select>mm</label><label>Assumed modulus <select id="mod"><option>2000</option><option>1500</option><option>2500</option></select>MPa</label><table><thead><tr><th>Size</th><th>Force / cup</th><th>Contact area</th><th>Largest gap</th></tr></thead><tbody id="fit"></tbody></table><p>2 N is a comparison choice, not a comfortable-force limit. Contact does not establish sealing.</p><h2>Evidence and gates</h2><table><tbody id="gates"></tbody></table><p>Read REVIEW.md for assumptions, omissions and required physical evidence.</p></main><script>const D=__DATA__;function draw(){fit.innerHTML=D.cases.filter(r=>r.extension_mm===Number(ext.value)&&r.E_MPa===Number(mod.value)).map(r=>`<tr><td>${r.head}</td><td>${r.force_N.toFixed(2)} N</td><td>${(r.contact_area_fraction*100).toFixed(1)}%</td><td>${r.max_gap_mm.toFixed(3)} mm</td></tr>`).join('')}ext.onchange=mod.onchange=draw;draw();gates.innerHTML=Object.entries(D.gates).map(([k,v])=>`<tr><td>${k}</td><td>${v}</td></tr>`).join('');</script>'''.replace('__DATA__',data)
    (OUT/'review.html').write_text(page,encoding='utf-8')
    inputs=['engineering-final.json','extendable-recipes.json','screening.py','band_fem.py','contact_membrane_fem.py','environment_acoustic_screen.py','extendable_study.py','cushion_v5_study.py','moisture_v5_study.py','acoustic_v5_fem.py','prepare_v5_builder.py','build_v5_review.py','CushionNext/EngineeringFinal.py','CushionNext/EngineeringV5.py','CushionNext/CushionNext.py','CushionNext/CushionNext.manifest','cad_v5_report.json']
    inputs.append('size_overlap_v5.py')
    package=ROOT/'EarDefender_V5_Extendable_Review.zip'
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
        for name in inputs:z.write(ROOT/name,name)
        for f in OUT.iterdir():
            if f.is_file():z.write(f,'results/'+f.name)
        for name in cad['files']:
            f=Path(name);assert f.stat().st_size>1000;z.write(f,'cad/'+f.name)
    with zipfile.ZipFile(package) as z:assert z.testzip() is None
    print(json.dumps({'package':str(package),'bytes':package.stat().st_size,'cad_failed_gates':cad.get('failed_gates',[]),'sha256':hashlib.sha256(package.read_bytes()).hexdigest()},indent=2))
if __name__=='__main__':main()
