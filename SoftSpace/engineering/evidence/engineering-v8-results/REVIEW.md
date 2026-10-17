# Ear defender digital concept — V8 review

The six-size lower-crown CAD build and the listed numerical studies are saved. This is an engineering concept, not a finished or validated product. Autistic users remain the primary audience; model-specific replacement cushions for glasses wearers are the second route. We have not established comfort, sensory acceptance, actual attenuation, production cost or superiority to market products.

## CAD delivered

Use CAD/V8 in the ZIP: six local Fusion archives, six nominal defender STEP files, twelve end-position STEP files and six replacement-pad STEP files. Independent imports verified all24 STEP exports:28 solid bodies per defender and4 per replacement pad. All six nominal assemblies passed the recorded positive-volume intersection checks. Discrete slider positions from0 to30mm and cup articulation at±8degrees passed the V8 checks. These are geometric checks, not fit, retention or durability tests.

The lower crown uses40mm adult arches and25mm child arches, with8mm assumed crown padding. The earlier taller crown had poor contact in most synthetic vertical-fit comparisons. V8 improves the simulated height range but has no solved3D scalp-contact force. Widths and heights are synthetic scenarios, not population percentiles. Named parameters on imported geometry do not constitute a fully driving parametric production model.

|Scenario|Unloaded endpoint span mm|Arch height mm|Band thickness mm|Assumed mass g|
|---|---:|---:|---:|---:|
|child_small|172.9|25|3|131–194|
|child_medium|184.1|25|3|131–195|
|child_large|194.6|25|3|132–196|
|adult_small|195.4|40|3.6|166–246|
|adult_medium|211.9|40|3.6|167–248|
|adult_large|228.1|40|3.6|169–250|

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

The current54-case study predicts force ranges1.01–3.80N per side and maximum foam compression across cases3.49–5.87mm under synthetic inputs. These are model outputs, not acceptable limits.2N is a calibration/comparison load, not an autistic comfort threshold. Scalar cover/foam contact and planar band models exclude lateral foam expansion and detailed3D fabric/skin contact. Case pressure peaks should not be treated as reliable pain thresholds.

The3D band solver uses actual exported crown/guide volume, quadratic tetrahedra, assumed E2000MPa and Poisson0.35, quarter symmetry and ideal2N/full-side loads. It excludes the sliding tongues and their contact. The analytical cantilever verification differed2.47% from its elementary beam/shear reference. A stable numerical result does not validate actual material behavior.

|V8 scenario|Latest centroid von Mises MPa|Last stress mesh change|5% comparison|
|---|---:|---:|---|
|child_small|2.494|2.96%|Pass|
|child_medium|2.957|3.92%|Pass|
|child_large|2.460|2.63%|Pass|
|adult_small|2.974|12.72%|Fail|
|adult_medium|2.950|4.36%|Pass|
|adult_large|2.942|10.84%|Fail|

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
