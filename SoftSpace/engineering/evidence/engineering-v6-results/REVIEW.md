# V6 corrected ear defender — engineering review

The result is a six-size digital concept with verified CAD exports and bounded numerical studies. It is not a finished, validated product. Autistic users remain the first priority; glasses-compatible replacement cushions are the second product route. No measured comfort, sensory acceptance, attenuation, manufacturing cost or competitor superiority is established.

## What changed

The mount carrier now lies behind the cover rather than occupying duplicate volume. The cup seat was cleared consistently. Obsolete fork adjustment holes were removed; the actual slider pivot remains. Limited hard-edge fillets were added and individually recorded. All six nominal assemblies have zero positive-volume overlaps above0.01mm3. Slider travel and cup rotation checks passed. Cover seams, attachment methods, threads and material selections are still undefined for manufacturing.

Twelve original pose STEP files were empty because their occurrences were hidden. They are superseded by the `_Verified.step` files in this package. Each was re-exported visibly and independently imported through Gmsh: all contain28 solids. The package contains6 nominal defender STEP,6 replacement cushion STEP,12 verified adjustment STEP and6 Fusion archives. Older exports remain on disk; use this package's manifest.

## Sizes and assumed mass

|Scenario|Unloaded endpoint span mm|Band thickness mm|Estimated product mass g|
|---|---:|---:|---:|
|child_small|158.13|3.0|131.9–195.5|
|child_medium|169.12|3.0|132.5–196.4|
|child_large|179.44|3.0|133.1–197.2|
|adult_small|186.56|3.6|167.8–248.3|
|adult_medium|202.83|3.6|169.0–250.1|
|adult_large|218.83|3.6|170.3–251.9|

Each side has30mm slider travel and a clamp knob. Widths are six synthetic scenarios, not population percentiles. The adult pad is85x105mm with50x70mm opening; child72.25x89.25mm with42.5x59.5mm opening. These dimensions require physical fit checks. Mass ranges come from CAD volume and assumed density intervals; they exclude packaging and any added seams/fasteners. They are not measured product weights.

The hand knob, pin retaining caps and mount carriers are prototype geometry. The thread placeholders do not establish retention. The replacement carrier is a blank, not compatibility with all brands. Existing headphone clamping and cup shape affect replacement-pad behavior even if we do not redesign the headband.

## Evidence gates

|Check|Outcome|
|---|---|
|Six-size nominal CAD and local archives|Complete; 28 product bodies per size|
|External STEP solid import check|Passed: 24 STEP files; 4 replacement bodies or 28 defender bodies|
|Assembly positive-volume overlap|Passed: zero unintended intersections in all six nominal assemblies|
|Slider movement and cup articulation|Passed for sampled CAD positions: 0–30mm slider travel and ±8degree rotation|
|3D structural solver analytical check|Passed: 2.47% difference from cantilever beam-plus-shear reference|
|3D crown/guide deflection mesh stability|Passed within 0.4% for the ideal load and assumed material|
|Small-child crown/guide stress mesh convergence|Failed: peak centroid stress changes7.42% on further3-to2mm refinement|
|3D acoustic solver analytical check|Passed: maximum0.071% complex-pressure error below1kHz|
|3D acoustic proxy mesh stability below1kHz|Passed: transfer change under0.013dB between6/4mm meshes|
|3D acoustic proxy broadband mesh stability|Failed: up to2.95dB mesh change across31.5Hz–8kHz|
|Cushion nodal pressure peaks (V5 retained)|Failed convergence; no peak-pressure or pain-prevention claim|
|Moisture in hot/humid scenarios (V5 retained)|Not guaranteed: 3/27 cases saturated for candidate WVTR3000|
|Actual materials, complete nonlinear worn assembly, fatigue, locking|Not validated|
|Autistic wearer sensory acceptance and perceived comfort|Untested; engineering equations cannot establish acceptance|
|Real sound reduction / NRR / SNR|Untested|
|Replacement cushion brand/model compatibility|Interface blank only; requires measured mount geometry and model-specific testing|
|Lowest cost and superiority to market products|Not demonstrated; supplier quotes and matched comparison needed|

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
