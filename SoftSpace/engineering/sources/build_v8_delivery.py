"""Bundle the saved Fusion revision and distinguish failed STEP-only experiments."""
from pathlib import Path
import json,hashlib,zipfile,csv,py_compile,html
P=Path(__file__).parent;O=P/'engineering-v8-results'
read=lambda f:json.loads((P/f).read_text())
cad=read('cad_v8_report.json');audit=read('cad_v8_audit.json');steps=read('engineering-v8-results/STEP_verification.json')
solid=read('engineering-v8-results/solid_v8_summary.json');contact=read('engineering-v8-results/material_sensitivity.json');acoustic=read('engineering-v7-results/acoustic_p2_summary.json')
experimental=read('engineering-v9-local-results/summary.json')
assert cad['status']==audit['status']=='complete' and steps['all_pass'] and len(cad['files'])==30
assert all(not r['positive_solid_overlaps'] for r in audit['sizes']) and contact['case_count']==54
mass='\n'.join('|%s|%.1f|%g|%g|%.0f–%.0f|'%(r['name'],2*r['band_halfspan_mm'],r['arch_height_mm'],r['band_thickness_mm'],a['mass_range_g'][0],a['mass_range_g'][1]) for r,a in zip(cad['recipes'],audit['sizes']))
stress='\n'.join('|%s|%.3f|%.2f%%|%s|'%(r['size'],r['meshes'][-1]['max_von_mises_centroid_MPa'],100*r['stress_relative_mesh_change'],'Pass' if r['stress_gate_5pct'] else 'Fail') for r in solid['cases'])
force=[r['force_N'] for r in contact['cases']];compression=[r['max_compression_mm'] for r in contact['cases']]
report=f'''# Ear defender digital concept — V8 review

The six-size lower-crown CAD build and the listed numerical studies are saved. This is an engineering concept, not a finished or validated product. Autistic users remain the primary audience; model-specific replacement cushions for glasses wearers are the second route. We have not established comfort, sensory acceptance, actual attenuation, production cost or superiority to market products.

## CAD delivered

Use CAD/V8 in the ZIP: six local Fusion archives, six nominal defender STEP files, twelve end-position STEP files and six replacement-pad STEP files. Independent imports verified all24 STEP exports:28 solid bodies per defender and4 per replacement pad. All six nominal assemblies passed the recorded positive-volume intersection checks. Discrete slider positions from0 to30mm and cup articulation at±8degrees passed the V8 checks. These are geometric checks, not fit, retention or durability tests.

The lower crown uses40mm adult arches and25mm child arches, with8mm assumed crown padding. The earlier taller crown had poor contact in most synthetic vertical-fit comparisons. V8 improves the simulated height range but has no solved3D scalp-contact force. Widths and heights are synthetic scenarios, not population percentiles. Named parameters on imported geometry do not constitute a fully driving parametric production model.

|Scenario|Unloaded endpoint span mm|Arch height mm|Band thickness mm|Assumed mass g|
|---|---:|---:|---:|---:|
{mass}

Mass follows geometry and assumed density intervals, not a weighed prototype. Adult pad outer dimensions85×105mm and opening50×70mm; child72.25×89.25mm and opening42.5×59.5mm. Slider travel is30mm per side. Actual coverage of adults/children remains unknown.

## Numerical evidence and limits

|Study|Result|What remains unresolved|
|---|---|---|
|Actual V8 crown/guide3D linear FEM|All six deflection mesh comparisons pass5%; four stress comparisons pass, two fail|Material strength, finite rotations, slider/fork contact, locking, full assembly loading|
|54 coupled lateral fit/foam cases|Completed for six widths, three assumed moduli and three slider settings|Measured foam/cover curves, head shape, friction and wear comfort|
|Quadratic3D acoustic cavity proxy|Child/adult6 versus4.5mm mesh changes0.113/0.067dB at48 sampled frequencies31.5Hz–8kHz; exact-tube complex error0.442%|Real sound reduction, porous liner, ear geometry, glasses/seam leakage and coupled shell modes|
|Earlier cushion contact studies|Finite-area pressure averages were more stable; nodal peaks failed convergence|No validated maximum pressure or pain-prevention claim|
|Earlier81 heat/moisture scenarios|Hypothetical resistance/WVTR sensitivity; some humid cases saturated|Actual material heat/moisture properties, Indian field conditions, sweat and wearer preference|
|Sensory acceptance|No simulated or measured result|Voluntary autistic participant feedback and physical wear trials|

The current54-case study predicts force ranges{min(force):.2f}–{max(force):.2f}N per side and maximum foam compression across cases{min(compression):.2f}–{max(compression):.2f}mm under synthetic inputs. These are model outputs, not acceptable limits.2N is a calibration/comparison load, not an autistic comfort threshold. Scalar cover/foam contact and planar band models exclude lateral foam expansion and detailed3D fabric/skin contact. Case pressure peaks should not be treated as reliable pain thresholds.

The3D band solver uses actual exported crown/guide volume, quadratic tetrahedra, assumed E2000MPa and Poisson0.35, quarter symmetry and ideal2N/full-side loads. It excludes the sliding tongues and their contact. The analytical cantilever verification differed2.47% from its elementary beam/shear reference. A stable numerical result does not validate actual material behavior.

|V8 scenario|Latest centroid von Mises MPa|Last stress mesh change|5% comparison|
|---|---:|---:|---|
{stress}

No yield, fatigue or creep allowable has been measured; no safety factor is established. The acoustic mesh result is a numerical check of hypothetical wall/cavity physics. It is neither NRR/SNR nor measured passive insertion loss;48 frequency samples may miss features between samples. Passive cups have no electronic white-noise generator, but seal sensations and contact/rubbing sounds remain untested.

## Corner refinement experiment — not adopted

The local V9Local adult-small STEP candidate rounds eight internal slot corners at0.5mm. Its28 bodies import, the changed band has no positive intersection above0.01mm³ against the static assembly or two tongues at seven slider settings, and the deflection remains numerically stable. Stress rises from3.029MPa at3mm to3.665MPa at2mm to3.884MPa at1.5mm; the final5.97% change fails the chosen5% comparison. The adult-large fillet failed in the local CAD kernel. The experiment was stopped and is explicitly separate from V8; there is no matching V9 Fusion archive. More refinement or a different guide geometry/boundary-load model is needed before claiming resolved stress.

Fusion activation failed twice after refreshing the target window, so its native V9 refinement could not run. The prepared RefineBandV9.py remains available, but its success must not be assumed. Original Fusion files and previous packages were preserved.

## Market and startup assessment

The package includes a29-entry market sample with source URLs and availability caveats, not every headphone sold. Existing glasses relief includes Turtle Beach ProSpecs adjustable channels and Noisefighters relief pads. Therefore glasses accommodation itself is not new. Budget passive defenders also exist in India; low cost alone does not prove differentiation. The most plausible product hypothesis is affordable local access, replaceable comfortable pads, adjustable fit, and user choice about noise reduction. Our design has not outperformed any market model in matched physical tests.

For replacement pads, carrier blanks are not universal compatibility. Each headphone mount, cup opening, available depth and clamp force needs measurement. Changing a pad can alter headphone sound and isolation. For the complete passive defender, headband force, shell, seals and pad behavior must be assessed together. Autistic people have varied sensory preferences; a useful sound-reduction device for some can be uncomfortable or unacceptable to others.

## Remaining engineering work

1. Resolve native corner/guide geometry and stress stability; verify full slider/clamp contact, tolerances, retention and finite rotations.
2. Select real materials and measure foam compression/recovery, cover biaxial behavior/friction/WVTR, liner acoustic impedance, shell damping and band creep/fatigue. Re-run models with those measurements.
3. Define production mount, seams, bonds, threads and assembly; test slider pull-out, wear, drops, small parts and pinch points for the intended age groups.
4. Build a prototype and measure attenuation with and without multiple glasses frames, heat/moisture and pressure distribution. Simulations can support design selection but cannot replace these measurements.
5. Conduct voluntary wear/acceptance trials led by autistic participants; test easy removal, texture, bulk, rubbing noise, movement and communication needs. No claim of universal benefit.
6. Obtain supplier quotes and a pilot manufacturing cost. Compare selected Indian-market alternatives using the same physical test setup before performance or price claims.

These are unresolved work items, not passed gates. Sensory acceptance cannot be completed by simulation alone. This package supplies a reviewable design and bounded evidence; it does not establish readiness for sale.

## References and reproducibility

The adult vertical-fit context is a [500-adult Udaipur tribal-group study](https://www.ijars.net/article_fulltext.asp?id=2915&issn=0973-709x&issue=5&month=September&page=AO01-AO04&volume=12&year=2023), which reports131.7±4.0mm ear-canal-to-vertex height. It does not represent all Indian adults or children. A [small autism headphone study](https://www.frontiersin.org/journals/integrative-neuroscience/articles/10.3389/fnint.2019.00065/full) provides motivation, not validation of this design. Market URLs and research scope are retained in market/MARKET.md.

Python sources and JSON/CSV/NPZ results are supplied. Local numerical dependencies used Gmsh4.13.1, SciPy1.15.3, NumPy2.4.6 and Matplotlib3.10.8. The solver-library binaries are excluded from the ZIP. Hashes in manifest.json identify exact packaged files. V7/V6 retained evidence is labelled by its original revision and must not be presented as complete V8 assembly validation.
'''
(O/'REVIEW.md').write_text(report,encoding='utf-8')
with (O/'BOM_geometry.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['size','body','volume_mm3','mass_min_g_assumed','mass_max_g_assumed'])
 for s in audit['sizes']:
  for b in s['bodies']:w.writerow([s['name'],b['name'],b['volume_mm3'],*b['mass_range_g']])
assets={}
def add(f,name):
 assert f.is_file(),str(f)
 assets[name]=f
for f in cad['files']:add(Path(f),'CAD/V8/'+Path(f).name)
for f in P.glob('OwnPassiveDefender_V9Local_*.step'):add(f,'experimental/STEP_only/'+f.name)
for directory in ['engineering-v8-results','engineering-v9-local-results','engineering-v7-results','engineering-v5-results']:
 for f in (P/directory).glob('*'):
  if f.suffix in ['.json','.csv','.png','.npz','.md'] and 'partial' not in f.name:add(f,'evidence/'+directory+'/'+f.name)
for name in ['market_sample.json','market_sample.csv','MARKET.md','MATERIAL_INPUTS.md']:add(P/'engineering-v6-results'/name,'market/'+name if name.startswith('market') or name=='MARKET.md' else name)
for name in ['cad_v8_report.json','cad_v8_audit.json','lower-crown-recipes.json','validation-plan.md','cad_v7_report.json']:add(P/name,name)
for f in P.glob('*.py'):
 py_compile.compile(str(f),doraise=True);add(f,'sources/'+f.name)
for f in (P/'CushionNext').glob('*.py'):
 py_compile.compile(str(f),doraise=True);add(f,'sources/CushionNext/'+f.name)
add(O/'REVIEW.md','REVIEW.md')
manifest={'revision':'V8 main; V9Local rejected experiment','cad_files':30,'STEP_files_verified':24,'native_V9_complete':False,'items':[{'path':n,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for n,f in assets.items()]}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2))
zip_path=P/'EarDefender_V8_Review_and_Simulations.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,f in assets.items():z.write(f,name)
 z.writestr('manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(zip_path) as z:
 assert z.testzip() is None
 for item in manifest['items']:assert hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256'],item['path']
print(json.dumps({'package':str(zip_path),'bytes':zip_path.stat().st_size,'files':len(assets),'zip_integrity_and_hashes':'pass','sources_compile':'pass'}))
