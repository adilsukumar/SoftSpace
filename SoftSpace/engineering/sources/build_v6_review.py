"""Package corrected CAD, verified exports and bounded numerical evidence."""
import json,csv,zipfile,hashlib,html
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v6-results';V5=P/'engineering-v5-results'
def read(path):return json.loads(path.read_text())
cad=read(P/'cad_v6_report.json');audit=read(P/'cad_v6_audit.json');poses=read(P/'cad_v6_pose_exports.json');step=read(P/'cad_v6_step_verification.json')
solid=read(O/'solid_3d_summary.json');sound=read(O/'acoustic_3d_summary.json');av=read(O/'acoustic_3d_verification.json');market=read(O/'market_sample.json')
assert cad['status']==audit['status']==poses['status']=='complete'
assert not cad.get('failed_gates') and step['all_pass']
files=[f for f in cad['files'] if 'Extension' not in f]+poses['files']
assert len(files)==30 and len(step['exports'])==24
gates={
 'Six-size nominal CAD and local archives':'Complete; 28 product bodies per size',
 'External STEP solid import check':'Passed: 24 STEP files; 4 replacement bodies or 28 defender bodies',
 'Assembly positive-volume overlap':'Passed: zero unintended intersections in all six nominal assemblies',
 'Slider movement and cup articulation':'Passed for sampled CAD positions: 0–30mm slider travel and ±8degree rotation',
 '3D structural solver analytical check':'Passed: 2.47% difference from cantilever beam-plus-shear reference',
 '3D crown/guide deflection mesh stability':'Passed within 0.4% for the ideal load and assumed material',
 'Small-child crown/guide stress mesh convergence':'Failed: peak centroid stress changes7.42% on further3-to2mm refinement',
 '3D acoustic solver analytical check':'Passed: maximum0.071% complex-pressure error below1kHz',
 '3D acoustic proxy mesh stability below1kHz':'Passed: transfer change under0.013dB between6/4mm meshes',
 '3D acoustic proxy broadband mesh stability':'Failed: up to2.95dB mesh change across31.5Hz–8kHz',
 'Cushion nodal pressure peaks (V5 retained)':'Failed convergence; no peak-pressure or pain-prevention claim',
 'Moisture in hot/humid scenarios (V5 retained)':'Not guaranteed: 3/27 cases saturated for candidate WVTR3000',
 'Actual materials, complete nonlinear worn assembly, fatigue, locking':'Not validated',
 'Autistic wearer sensory acceptance and perceived comfort':'Untested; engineering equations cannot establish acceptance',
 'Real sound reduction / NRR / SNR':'Untested',
 'Replacement cushion brand/model compatibility':'Interface blank only; requires measured mount geometry and model-specific testing',
 'Lowest cost and superiority to market products':'Not demonstrated; supplier quotes and matched comparison needed'}
size_rows='\n'.join('|%s|%.2f|%.1f|%.1f–%.1f|'%(r['name'],2*r['band_halfspan_mm'],r['band_thickness_mm'],s['mass_range_g'][0],s['mass_range_g'][1]) for r,s in zip(cad['recipes'],audit['sizes']))
gates_table='\n'.join('|'+k+'|'+v+'|' for k,v in gates.items())
report=f'''# V6 corrected ear defender — engineering review

The result is a six-size digital concept with verified CAD exports and bounded numerical studies. It is not a finished, validated product. Autistic users remain the first priority; glasses-compatible replacement cushions are the second product route. No measured comfort, sensory acceptance, attenuation, manufacturing cost or competitor superiority is established.

## What changed

The mount carrier now lies behind the cover rather than occupying duplicate volume. The cup seat was cleared consistently. Obsolete fork adjustment holes were removed; the actual slider pivot remains. Limited hard-edge fillets were added and individually recorded. All six nominal assemblies have zero positive-volume overlaps above0.01mm3. Slider travel and cup rotation checks passed. Cover seams, attachment methods, threads and material selections are still undefined for manufacturing.

Twelve original pose STEP files were empty because their occurrences were hidden. They are superseded by the `_Verified.step` files in this package. Each was re-exported visibly and independently imported through Gmsh: all contain28 solids. The package contains6 nominal defender STEP,6 replacement cushion STEP,12 verified adjustment STEP and6 Fusion archives. Older exports remain on disk; use this package's manifest.

## Sizes and assumed mass

|Scenario|Unloaded endpoint span mm|Band thickness mm|Estimated product mass g|
|---|---:|---:|---:|
{size_rows}

Each side has30mm slider travel and a clamp knob. Widths are six synthetic scenarios, not population percentiles. The adult pad is85x105mm with50x70mm opening; child72.25x89.25mm with42.5x59.5mm opening. These dimensions require physical fit checks. Mass ranges come from CAD volume and assumed density intervals; they exclude packaging and any added seams/fasteners. They are not measured product weights.

The hand knob, pin retaining caps and mount carriers are prototype geometry. The thread placeholders do not establish retention. The replacement carrier is a blank, not compatibility with all brands. Existing headphone clamping and cup shape affect replacement-pad behavior even if we do not redesign the headband.

## Evidence gates

|Check|Outcome|
|---|---|
{gates_table}

## New structural3D calculations

Gmsh imported the actual nominal crown and guide-housing STEP volume. Quadratic10-node tetrahedra solved small-strain isotropic linear elasticity with assumed E2000MPa and Poisson0.35. Six sizes were meshed at5/3mm; the smallest child also at2mm. A quarter model used symmetry planes, one vertical datum and an ideal direct guide-housing load corresponding to2N per full side. Reactions balance and free residuals remain below1e-6. The cantilever verification differs2.47% from its elementary beam/shear approximation; it is a code check, not a material validation.

The latest computed guide displacements are about7.05–7.77mm for adult and10.11–10.79mm for child under this ideal load. Their mesh differences are small. The displacement/geometry scale is large enough that finite-rotation effects can matter. This linear solve does not replace the earlier geometrically nonlinear beam model. It excludes slider contact, guide locking, fork loading offsets, skin/scalp contact, and full assembly dynamics.

The smallest child's centroid stress rises to4.71MPa with refinement and has not stabilized. Sharp guide corners and ideal boundary/load transfer can influence it. Other two-mesh comparisons are within5%, which is only a provisional check. No yield/fatigue/creep allowable was measured; no safety factor is claimed. The2N load is a comparison choice, not an autistic comfort threshold.

## New acoustic3D calculations

Linear tetrahedral Helmholtz FEM solves a straight-wall air cavity reconstructed from cup/pad dimensions. A uniform compliant back uses four hypothetical stiffness/damping combinations. Adult/child models were run at6/4mm mesh with48 frequencies from31.5Hz to8kHz:768 frequency/scenario/mesh rows. An elliptical uniform-tube verification against the exact1D Helmholtz solution has maximum0.071% complex-pressure error at31.5/125/500/1000Hz.

The proxy cavity is not the complete product. It omits porous liner/foam impedance, cover/seam transmission, glasses leaks, actual shell modes and ear transfer. Below1kHz mesh changes are under0.013dB; across the full sweep changes reach2.95dB. Upper-frequency outputs remain exploratory. The plotted pressure transfers are not attenuation, NRR, SNR or clinical-benefit ratings.

## Retained V5 studies

The source assumptions for foam compression, cover tension, glasses shapes, head curvature and humidity remain synthetic. V6 changes the carrier/rigid assembly, not these constitutive inputs. The package retains the72 cushion comparisons,54 coupled slider/cushion scenarios,12 neighboring head-width cases,81 heat/moisture cases and48 low-frequency acoustic parameter combinations. See `v5-results/REVIEW.md` for full assumptions. Its claim that the original pose exports were complete is superseded by this revision's independent import check.

Area-averaged pressure converged for a6mm virtual sensor, but nodal peaks did not. Lower stiffness does not automatically prove less discomfort. Some humidity cases saturate. Texture, sweating response, tactile noise, perceived safety and the decision to keep wearing the product require wearer feedback.

## Market interpretation

The29-entry documented sample spans Indian low-cost passive earmuffs, child defenders, ANC audio headsets, gaming headsets and replacement cushions. It is not an exhaustive list of every product. Manufacturer statements and prices are not matched performance tests. See `MARKET.md` and source-linkedCSV. The opportunity is an affordable, locally available product developed with autistic users; its success is not yet demonstrated.

Basic glasses relief already exists: Turtle Beach ProSpecs uses adjustable relief channels, and Noisefighters Sightlines uses gel/foam with relief cuts. No verified Indian stock for Sightlines was found in this search, which does not prove none exists. Cheap Indian passive defenders also exist; our product cannot be called the cheapest without quotes. Our assumed mass overlaps competitor reported mass, so no universal lightweight advantage follows.

## What is required before treating this as a product

1. Select actual band/foam/cover/liner materials and obtain measured nonlinear compression, recovery, modulus, damping, acoustic flow resistivity, thermal conductivity and vapor-transmission data.
2. Resolve guide corner geometry, define real locking/retention, attachment and seam construction; validate nonlinear assembled contact, drop/fatigue/creep and adjustment durability.
3. Measure head/ear/scalp geometry for intended sizes, force versus spread/extension, frame pressure, seal and real sound reduction on physical rigs. Use a measured headphone mount for every replacement-pad version.
4. Evaluate physical prototype texture, handling noise, heat and comfort with voluntary autistic adult feedback; evaluate child fit/hardware separately. A simulation cannot substitute for these outcomes.
5. Obtain manufacturing/assembly/packaging/delivery quotes and compare against physical market samples under the same protocol.

These are dependencies for validation, not completed tests. We can responsibly investigate a prototype after addressing retention and material choices; we cannot promise that it will help every autistic person or prevent glasses pain.

## Reproduction

The frozen CAD bodies come from `CushionNext/EngineeringV6.py`; recipe dimensions are in `extendable-recipes.json`. The named Fusion parameters annotate imported bodies and do not directly drive them. Build with the registered Fusion script, then run `RepairV6Exports.py` for visible pose export. The wrapper currently invokes the repair script. Use the module directly or switch the wrapper deliberately to rebuild.

The local Python solver uses NumPy2.4.6, SciPy1.15.3 and Gmsh4.13.1. `extract_solver_dll.py` recovers the DLL from the Windows wheel if pip's target layout omits it. Numerical scripts, meshes/results, verification files and the property BOM are included. No Fusion cloud solve was run: Fusion reported an outage. No physical tests or purchases were performed.
'''
(O/'REVIEW.md').write_text(report,encoding='utf-8')
(O/'readiness.json').write_text(json.dumps({'revision':'V6','digital_screening_recorded':True,'production_ready':False,'physical_validation_complete':False,'gates':gates,'cad_files':files},indent=2))
# A body-level bill of materials without fictional prices or material allowables.
with (O/'BOM_geometry.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['size','body','volume_mm3','assumed_density_low_kg_m3','assumed_density_high_kg_m3','assumed_mass_low_g','assumed_mass_high_g','material','unit_cost_INR'])
 for s in audit['sizes']:
  for b in s['bodies']:w.writerow([s['name'],b['name'],b['volume_mm3'],*b['density_range_kg_m3'],*b['mass_range_g'],'UNSELECTED','UNQUOTED'])
(O/'MATERIAL_INPUTS.md').write_text('''# Material inputs needed

|Part|Current numerical input|Required measured data|
|---|---|---|
|Band and sliders|E1500/2000/2500MPa sweep;3Dnu0.35|Elastic/plastic curves, creep and fatigue versus temperature, actual molding/print orientation|
|Main foam|Synthetic nonlinear foundation curve|Compression/unloading/recovery curves versus strain rate/temperature; density, lateral expansion|
|Glasses zone|Half main-foam stiffness hypothesis|Same measurements; bonding and transition behavior|
|Cover|Synthetic membrane tension; geometric0.2mm wrap|Thickness, biaxial stress, friction, pretension, seam durability, tactile noise, WVTR test conditions|
|Liner|Annular geometry with assumed foam density|Flow resistivity, porosity, complex impedance and absorption by frequency|
|Shell|Hypothetical panel stiffness/mass/damping|Actual modulus, density, damping, shell modal response and seam leakage|
|Pins/clamps/carrier|Thread and attachment blanks|Real fastener interface, retention and pull-out tests; production tolerances|

No unmeasured input is a selected material specification. No material supplier price has been quoted. SeeBOM_geometry.csv for actual CAD volume and assumed mass intervals.
''',encoding='utf-8')
# Interactive comparison browser keeps unknown outcomes visible.
data=json.dumps({'gates':gates,'market':market,'sizes':audit['sizes']})
page='''<!doctype html><html><meta charset="utf-8"><title>V6 ear defender review</title><style>body{font:16px system-ui;background:#f3f6f5;color:#213f36;margin:0}main{max-width:1150px;margin:30px auto;padding:28px;background:white;border-radius:18px}aside{padding:16px;background:#fff1d6;border-left:5px solid #c07822}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}input,select{font:inherit;padding:8px;margin:8px 12px 8px 0}img{max-width:100%}a{color:#075b9e}.scroll{overflow:auto}h2{margin-top:35px}</style><main><h1>V6 · six sizes, verified CAD</h1><aside>Digital concept review. Actual comfort, sensory acceptance, sound reduction and lowest cost remain unproven. Small-child peak stress and high-frequency acoustic mesh checks remain unresolved.</aside><p><a href="REVIEW.md">Full engineering review</a> · <a href="MARKET.md">Market interpretation</a> · <a href="market_sample.csv">Comparison CSV</a> · <a href="BOM_geometry.csv">Geometry BOM</a></p><h2>Evidence gates</h2><table id="gates"></table><h2>Assumed mass, not measured weight</h2><table id="sizes"></table><h2>Market sample:29 entries</h2><p>Documented sample, not every market headphone. Blank values mean unverified. Manufacturer features are not evidence of comparative comfort.</p><input id="search" placeholder="Search brand or feature"><select id="category"><option value="">All categories</option></select><div class="scroll"><table><thead><tr><th>Product</th><th>Feature</th><th>Reported mass</th><th>Price observation</th><th>Indian access</th></tr></thead><tbody id="market"></tbody></table></div><h2>Numerical plots</h2><img src="band_3d.png" alt="Actual CAD band linear FEM displacement"><img src="acoustic_proxy.png" alt="Hypothetical cavity transfer and mesh differences"><p>Plots represent stated idealizations. Read REVIEW.md before interpreting them as a product prediction.</p></main><script>const D=__DATA__;const esc=s=>String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));document.getElementById('gates').innerHTML=Object.entries(D.gates).map(([k,v])=>`<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`).join('');document.getElementById('sizes').innerHTML=D.sizes.map(r=>`<tr><td>${esc(r.name)}</td><td>${r.mass_range_g.map(v=>v.toFixed(1)).join('–')}g</td><td>${r.bbox_mm.map(v=>v.toFixed(1)).join('×')}mm unloaded</td></tr>`).join('');const select=document.getElementById('category');[...new Set(D.market.map(r=>r.category))].forEach(c=>select.add(new Option(c,c)));function draw(){const q=document.getElementById('search').value.toLowerCase();document.getElementById('market').innerHTML=D.market.filter(r=>(!select.value||r.category===select.value)&&JSON.stringify(r).toLowerCase().includes(q)).map(r=>`<tr><td><a href="${esc(r.source)}" target="_blank" rel="noopener">${esc(r.product)}</a></td><td>${esc(r.manufacturer_feature)}</td><td>${esc(r.manufacturer_mass_g)||'Unverified'}</td><td>${esc(r.price_observation)||'Unverified'}</td><td>${esc(r.india_availability)}</td></tr>`).join('')}document.getElementById('search').oninput=select.onchange=draw;draw();</script></html>'''.replace('__DATA__',data)
(O/'review.html').write_text(page,encoding='utf-8')
source=['engineering-final.json','extendable-recipes.json','band_fem.py','contact_membrane_fem.py','extendable_study.py','cushion_v5_study.py','moisture_v5_study.py','acoustic_v5_fem.py','size_overlap_v5.py','environment_acoustic_screen.py','screening.py','solid_band_3d.py','run_solid_v6.py','acoustic_3d_v6.py','verify_acoustic_3d.py','verify_step_exports.py','extract_solver_dll.py','prepare_v6_builder.py','prepare_memory_v6.py','finalize_v6_records.py','market_benchmark_v6.py','build_v6_review.py','plot_v6.py','CushionNext/EngineeringV6.py','CushionNext/RepairV6Exports.py','CushionNext/CushionNext.py','CushionNext/CushionNext.manifest','cad_v6_report.json','cad_v6_audit.json','cad_v6_pose_exports.json','cad_v6_step_verification.json']
package=P/'EarDefender_V6_CAD_and_Evidence.zip'
manifest=[]
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for filename in source:
  f=P/filename
  if f.exists():z.write(f,'source/'+filename)
 for folder,label in [(O,'results'),(V5,'v5-results')]:
  for f in folder.iterdir():
   if f.is_file():z.write(f,label+'/'+f.name)
 for filename in files:
  f=Path(filename);assert f.stat().st_size>1000
  manifest.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});z.write(f,'cad/'+f.name)
 z.writestr('cad_manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(package) as z:assert z.testzip() is None
(O/'package_manifest.json').write_text(json.dumps({'package':str(package),'bytes':package.stat().st_size,'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'cad_files':manifest},indent=2))
print('Packaged',len(files),'CAD files;',len(market),'market entries;',package.stat().st_size,'bytes')
