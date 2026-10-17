"""Assemble a reproducible, explicitly provisional engineering review package."""
import csv,json,html,zipfile,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).parent;OUT=ROOT/'engineering-final-results'

def main():
    cad=json.loads((ROOT/'cad_final_report.json').read_text())
    assert cad['status']=='complete' and not cad.get('failed_gates'), 'CAD clearance gates must pass before publishing this review'
    band=json.loads((OUT/'band_summary.json').read_text())
    contact=json.loads((OUT/'contact_summary.json').read_text())
    coupled=json.loads((OUT/'coupled_summary.json').read_text())
    env=json.loads((OUT/'environment_summary.json').read_text())
    sizing=json.loads((OUT/'size_band_recipes.json').read_text())
    cases=[r for r in coupled['cases'] if r['E_MPa']==2000 and r['zone_stiffness_ratio']==.5]
    rows='\n'.join(f"| {r['head']} | {r['force_N']:.3f} | {r['contact_area_fraction']*100:.1f}% | {r['max_gap_mm']:.2f} |" for r in cases)
    sizes='\n'.join(f"| {r['scenario']} | {r['band_rest_halfspan_mm']*2:.2f} | {r['predicted_N']:.3f} |" for r in sizing['recipes'])
    passed=['Positive-volume curved foam and solid cover wrap in adult and child CAD',
            'Curved foam volume within 0.05% of the analytic target',
            'Cup/fork clearance sampled at 1 degree increments from -8 to +8 degrees in both assemblies',
            'Band-to-fork clearance at all three discrete height positions in both assemblies',
            'Beam analytic small-opening check and consistent tangent derivative check',
            'Beam 20/40/80-element mesh comparison',
            'Membrane constant-displacement null mode, mesh area and T=0 analytic foundation check',
            'Nodal force balance and projected obstacle-equilibrium residual checks',
            'Iterated common band/contact force and compressed mount separation',
            'Thermal temperature bounds and conservative water mass balance']
    states={
        'CAD and local computational package':'completed for the currently saved provisional revision',
        'Prototype materials':'assumed; supplier characterization missing',
        'Peak contact pressure convergence':'not passed: refinement remains mesh-sensitive',
        'Thermal/moisture design':'not passed: saturation persists for several cover scenarios',
        'Acoustic attenuation':'not validated; only uncalibrated low-frequency sensitivity model',
        'Production hardware':'not ready: friction stops, retention, fatigue, drop and assembly validation missing',
        'Height adjustment and crown padding':'three pin positions and 5 mm crown padding exported; scalp contact and retention strength untested',
        'Head/ear/scalp fit and sensory acceptance':'not validated',
        'Replacement brand compatibility':'interface blank only; no brand-specific fit established',
        'Full Fusion cloud/3D nonlinear study':'not run; local reduced FEM calculations provided',
    }
    gate_table='\n'.join(f'| {a} | {b} |' for a,b in states.items())
    files='\n'.join('- '+Path(f).name for f in cad['files'])
    checks='\n'.join('- '+x for x in passed)
    refine=contact.get('peak_pressure_mesh_change_percent',None)
    report=f'''# Ear defender and glasses cushion — engineering review

This is a provisional digital design and local simulation package. It is not a finished, manufactured, clinically evaluated or certified product. All numerical material/head/frame inputs are documented assumptions. Local beam and membrane FEM are real numerical solves, but they are reduced models rather than full 3D Fusion contact analysis.

## Current status

| Item | Status |
|---|---|
{gate_table}

## CAD produced

Adult and separate smaller child cushions have curved contact faces, main/softer foam regions, a solid cover envelope and a mounting carrier blank. Standalone passive defenders include closed cups, liner volume, circular-cap bands, three-position pinned forks, retained pins, 5 mm crown padding and exterior cup bosses. The pivot bore stays in the exterior boss and does not intentionally penetrate the sound cavity. Geometry is shown at the unloaded rest band span; it is not the shape on a wearer.

Cover thickness is 0.2 mm in the vertical/radial envelope construction, not uniform normal thickness. Lofted rims still need production rounding and seam/adhesive construction. The two family sizes are hypotheses; child ear clearance and anatomy have not been established. Source bodies are frozen imports; regenerate from `engineering-final.json` using the saved Fusion builder for geometry changes. Named Fusion parameters are annotations, not live drivers of the imported bodies.

Saved exports:
{files}

`cad_final_report.json` records the exact files, volume verification and clearance results. STEP exports select the intended product components, avoiding the duplicate hidden construction solids in the document root. F3D documents contain both the replacement cushion and own-product assembly plus hidden construction geometry; select the intended components before meshing.

## Band and cushion coupling

The band solver uses geometrically nonlinear corotational Euler–Bernoulli beam elements with an assumed linear elastic modulus. Circular-cap centreline dimensions match the JSON/CAD recipe; pinned endpoints and a constant rectangular section are assumed. Local pin lugs are treated as rigid connections, not separately meshed. Material creep, fatigue, stress relaxation and out-of-plane behaviour are not represented.

The coupled model iterates band load and cushion approach until the same lateral force and compressed mounting separation are obtained. It uses a 35 mm mount offset per side and a load-curve interpolation check against direct FEM. Cover bridging is represented by scalar triangle membrane elements under prescribed tension on a nonlinear compressive spring foundation, constrained by a rigid synthetic head and rounded hypothetical frame profile. It excludes actual fabric in-plane displacement, friction, skin deformation and lateral foam coupling.

Illustrative E=2000 MPa, local foam ratio=0.5 and cover tension=1 N/m cases:

| Head scenario | Coupled force per cup N | Sampled contact area | Largest model gap mm |
|---|---:|---:|---:|
{rows}

These forces are not comfortable/safe force limits. The size/material dependence is substantial, so one band is not shown to suit every head. Contact area and gaps are numerical estimates, not proof of an airtight seal.

### Size-specific band recipes

To avoid forcing one rest span onto very different head widths, six numerical band recipes solve for a common 2 N comparison load after cushion compression. This load is an engineering comparison choice, not an acceptable pressure/force threshold. These additional recipes have not been generated as CAD variants. They use E=2000 MPa and the standard rounded hypothetical frame only.

| Head scenario | Unloaded endpoint span mm | Computed comparison force N |
|---|---:|---:|
{sizes}

Peak pressure remains mesh-sensitive. The final two refinements change the nominal peak by {refine:.1f}% (128x17 to 192x25 nodes). The solver's equilibrium checks pass, but a quantitative peak-pressure comfort claim does not pass this convergence gate. Do not reuse the earlier independent-spring model's claimed pressure reductions as a product outcome.

## Heat and moisture

{env['thermal_case_count']} one-hour thermal/vapor cases cover ambient 28/32/36 C, RH 50/70/90%, cover water-vapor transmission hypotheses, water-source rates and foam conductivity. The model conserves water, but is spatially lumped and does not simulate sweat feedback or evaporation cooling.

At 32 C/70% RH and a hypothetical 100 mg/h water input, WVTR=1–500 g/m2/day covers reach saturation in this model. WVTR=1000 gives approximately 85.9% RH. This is a material screening target under defined assumptions, not evidence that a chosen cover will perform that way. Vapor permeation cannot be replaced by acoustic-leaking vents without a separate sound assessment.

## Acoustic sensitivity

{env['acoustic_scenario_count']} hypothetical scenarios ({env['acoustic_frequency_rows']} frequency rows) use a lumped panel spring/mass/loss DOF, cavity compliance and slit-leak impedance over 31.5–250 Hz. Stiffness, loss and leak sizes are arbitrary sensitivity inputs. Leak dimensions are not derived from the contact model. This is not broadband acoustic FEM and supplies no NRR/SNR or validated dB rating. Cup modes, ears, actual absorber impedance and cover transmission remain unmeasured.

## Verification completed

{checks}

## Required physical evidence

1. Measure foam stress–strain and recovery at relevant temperature/humidity; test both foam regions and their joining method.
2. Measure cover tensile behaviour, pretension, WVTR, seam properties and cleaning durability.
3. Measure actual band force versus spread and compare against FEM; check creep and repeated flexing.
4. Compression-rig and pressure-map tests with real glasses arms; check low, nominal and high host clamp forces for replacement cushions.
5. Measure sound attenuation with/without glasses; measure frequency-response changes on each host headphone model.
6. Voluntary wearer evaluations: texture, heat, pressure, ease of removal and sensory preference. Autism does not determine one universal acceptable fit or sound reduction.
7. Validate dimensions and mounting retention by headphone model; do not advertise universal brand compatibility.

## Reproduction

Run `band_fem.py`, `contact_membrane_fem.py`, `coupled_fit.py`, `size_band_recipes.py`, `environment_acoustic_screen.py`, then `build_review_package.py` using Python with NumPy. `engineering-final.json` is the recipe. The Fusion script `CushionNext/EngineeringFinal.py` produces CAD through the registered `CushionNext` script. The saved CAD includes the discrete-height and crown-padding refinement. Height changes require releasing pins; threads, pull-out strength, scalp contact and gravity are not solved.
'''
    (OUT/'REVIEW.md').write_text(report,encoding='utf-8')
    packet={'states':states,'verification_passes':passed,'saved_cad':cad['files'],'assumed_inputs':True,'production_ready':False}
    (OUT/'readiness.json').write_text(json.dumps(packet,indent=2))
    # Lightweight local viewer; no network libraries or uploads.
    data=json.dumps({'coupled':coupled['cases'],'thermal':env['thermal_nominal_comparison'],'band':band['cases'],'states':states},separators=(',',':'))
    page='''<!doctype html><html><meta charset="utf-8"><title>Ear defender engineering review</title><style>body{font:16px system-ui;background:#f4f5f2;color:#20342f;margin:0}main{max-width:1050px;margin:40px auto;padding:30px;background:white;border-radius:18px}h1{font-size:32px}aside{padding:18px;background:#fff0d8;border-radius:10px}select{padding:9px;margin:8px;border:1px solid #ccc;border-radius:6px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:11px;text-align:left;border-bottom:1px solid #ddd}.bar{height:14px;background:#17786b;border-radius:4px}small{color:#657670}section{margin-top:30px}</style><main><h1>Ear defender / glasses cushion</h1><aside><b>Provisional engineering package.</b> Synthetic inputs. Not a tested or certified product. Peak contact pressure fails the current mesh-convergence gate; moisture remains unresolved.</aside><section><h2>Coupled band and cushion</h2><label>Material modulus<select id="E"><option>2000</option><option>1500</option><option>2500</option></select>MPa</label><label>Local foam ratio<select id="ratio"><option>0.5</option><option>1</option></select></label><table><thead><tr><th>Head scenario</th><th>Force / cup</th><th>Model contact area</th><th>Largest model gap</th></tr></thead><tbody id="cases"></tbody></table><small>Forces are predictions under assumptions, not comfort thresholds. No seal or attenuation claim.</small></section><section><h2>Moisture sensitivity</h2><p>32 C, 70% ambient RH, hypothetical 100 mg/h water source.</p><table><thead><tr><th>Assumed WVTR</th><th>RH after 1 h</th><th>Condensation</th></tr></thead><tbody id="water"></tbody></table></section><section><h2>Readiness</h2><table><tbody id="status"></tbody></table></section><p>Full equations, omissions, tests and CSV data are included beside this file. Read REVIEW.md before using the results.</p></main><script>const D=__DATA__;function render(){const rows=D.coupled.filter(r=>r.E_MPa===Number(E.value)&&r.zone_stiffness_ratio===Number(ratio.value));cases.innerHTML=rows.map(r=>`<tr><td>${r.head.replaceAll('_',' ')}</td><td>${r.force_N.toFixed(2)} N<div class="bar" style="width:${Math.min(100,r.force_N/6*100)}%"></div></td><td>${(100*r.contact_area_fraction).toFixed(1)}%</td><td>${r.max_gap_mm.toFixed(2)} mm</td></tr>`).join('')}E.onchange=ratio.onchange=render;render();water.innerHTML=D.thermal.map(r=>`<tr><td>${r.assumed_cover_WVTR_g_m2_day} g/m²/day</td><td>${r.RH_60min_percent.toFixed(1)}%</td><td>${r.condensed_mg.toFixed(1)} mg</td></tr>`).join('');status.innerHTML=Object.entries(D.states).map(([k,v])=>`<tr><td>${k}</td><td>${v}</td></tr>`).join('');</script></html>'''.replace('__DATA__',data)
    (OUT/'review.html').write_text(page,encoding='utf-8')
    inputs=['screening.py','engineering-final.json','band_fem.py','contact_membrane_fem.py','coupled_fit.py','environment_acoustic_screen.py','size_band_recipes.py','build_review_package.py','cad_final_report.json','CushionNext/EngineeringFinal.py','CushionNext/CushionNext.py','CushionNext/CushionNext.manifest']
    package=ROOT/'EarDefender_Engineering_Review.zip'
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
        for rel in inputs:z.write(ROOT/rel,rel)
        for f in OUT.iterdir():
            if f.is_file():z.write(f,'results/'+f.name)
        for name in cad['files']:
            f=Path(name);assert f.stat().st_size>1000;z.write(f,'cad/'+f.name)
    print(json.dumps({'review':str(OUT/'REVIEW.md'),'viewer':str(OUT/'review.html'),'package':str(package),'bytes':package.stat().st_size,'sha256':hashlib.sha256(package.read_bytes()).hexdigest()},indent=2))

if __name__=='__main__':main()

