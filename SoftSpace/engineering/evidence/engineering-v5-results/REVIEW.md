# V5 extendable ear defender — simulation review

Six provisional sizes now have 30 mm sliding crown-to-cup adjustment. Each side has a 4×16 mm tongue, a sleeve with 0.3 mm nominal clearance per face, and a hand clamp knob. It requires loosening/tightening a knob; it is not a validated click-detent mechanism. The new cushion curvature fraction is 1.0, selected from 72 synthetic comparisons. Main/soft-zone foam ratios remain assumed 1/0.5. Adult/child band sections were changed to 3.6/3.0 mm for the longer arms.

This completes a defined digital screening exercise, not every test required for a finished product. The result supports a conditional physical prototype investigation. It does not establish comfort, noise reduction, sensory benefit, a safety rating, mass-production readiness or cost.

## Sizes

| Synthetic scenario | Unloaded band width mm | Cap thickness mm | Nominal force per cup N |
|---|---:|---:|---:|
| child_small | 158.13 | 3.0 | 2.000 |
| child_medium | 169.12 | 3.0 | 2.000 |
| child_large | 179.44 | 3.0 | 2.000 |
| adult_small | 186.56 | 3.6 | 2.000 |
| adult_medium | 202.83 | 3.6 | 2.000 |
| adult_large | 218.83 | 3.6 | 2.000 |

Each width is calibrated at 15 mm slider extension, E=2000 MPa and a 2 N comparison load after modeled cushion compression. 2 N is not a clinical, comfort or safety threshold. These sizes are based on six hypothetical head breadths, not anthropometric percentiles. Sliding changes crown-to-cup distance, not a substitute for width selection. Real vertical head dimensions and ear/scalp clearance are still missing.

## Verification and unresolved gates

| Check | Status |
|---|---|
| CAD exports | complete |
| Slider travel clearance | passed |
| Beam mesh and force balance | passed under reduced-model assumptions |
| 6 mm virtual pressure sensor mesh change | passed <5% for both nominal family cases |
| Nodal point pressure peak convergence | FAILED for both families; do not make peak-pressure claims |
| Moisture over all screened conditions | FAILED: 3 of 27 cases saturate at the 3000 WVTR hypothesis |
| Acoustic FEM numerical checks | passed for assumed 1D 31.5–250 Hz model |
| Broadband attenuation and real sound reduction | not established |
| Sensory acceptance, texture and perceived safety | not simulatable with these mechanical/acoustic equations; wearer evidence required |
| Vertical head fit / scalp pressure | not established; synthetic head breadths only |
| Material durability and clamp retention | not established; no measured allowables or fatigue/creep data |
| Manufacturing cost / brand compatibility | not established |

The CAD report is the authoritative export/clearance record. It contains 30 exports when the six-size run is complete: replacement cushion STEP, nominal defender STEP/F3D, and retracted/extended STEP for each size. Documents contain hidden source construction geometry and pose components; use designated product components for meshing. Bodies are imported/frozen; regenerate from recipes. Recipe widths and local sections correspond to the beam model, but the model omits 3D guide details and horizontal fork offsets.

## Mechanical results

54 iterated slider/cushion cases cover six sizes, three extensions and three assumed moduli. Force ranges from 1.09 to 3.55 N per cup. Minimum predicted contact area is 89.4%, and the largest predicted local gap is 0.593 mm. These gaps do not establish a leak path or an acoustic seal. Maximum nominal elastic stress across cases is 8.05 MPa; no measured allowable exists, so no safety factor is claimed.

The six beam meshes (20/40/80 cap elements plus legs) change nominal force by at most 0.055% between the last two refinements. Direct FEM checks differ from interpolated forces by at most 0.018%. Equilibrium residuals are recorded. Variable-section beam elements represent the weakest sliding tongue over the whole leg, omitting overlap stiffening, joint friction, notches, shear, torsion, creep and fatigue. Stabilized Newton directions converge the original equilibrium residual; this is not dynamic buckling or a global stability proof.

72 cushion comparisons rank whole-foam stiffness multipliers and curvature at 2 N under standard/thick hypothetical frames. Fraction 1.0 achieved at least 98.4% contact area in that comparison grid. Coupled force variations reduce the worst contact fraction to the value above. Ranking minimizes modeled gap; it is not a user comfort criterion.

The pressure refinement compares fixed 6 mm diameter virtual sensors as well as nodal peaks. Adult/child averaged-pressure changes are 2.46%/0.62%; nodal-peak changes remain 18.86%/14.21%. A stable area average does not repair unstable point peaks. No numerical pressure reduction or pain-prevention claim is warranted.

12 further cases vary head breadth by ±5 mm around each size at nominal extension/modulus while holding synthetic curvature fixed. Their force range is 1.52–2.50 N/cup. This checks local width sensitivity only, not anatomical population coverage.

## Moisture and heat

81 further one-hour scenarios compare WVTR hypotheses 1000/3000/5000 g/m²/day at a specified 2000 Pa test difference. At 32°C, 70% RH and assumed 100 mg/h water input, the 3000 hypothesis predicts 71.7% cavity RH and no condensation. Nevertheless, 3 of its 27 scenarios saturate. More vapor transmission helps under favorable gradients, but cannot guarantee drying in hot humid air. No fabric with these properties has been selected or measured. The lumped thermal model omits local skin temperature, sweating feedback and evaporation cooling. No vent holes were added to sacrifice sealing.

## Sound

48 acoustic parameter combinations / 2304 frequency rows solve a 1D Helmholtz cavity FEM with a hypothetical compliant wall and slit. Analytic low-frequency and 10/20/40 element checks pass. It is restricted to 31.5–250 Hz and replaces the curved cup with an equivalent clamped circular plate; material and damping are assumptions. The predicted differences are model outputs, not a product rating. Real cover transmission, liner impedance, ear transfer, seams and structural cup modes are absent. No broadband, NRR/SNR, real noise-reduction or autism-benefit claim follows from this solve.

## What cannot be finished by simulation alone

Sensory acceptance, willingness to wear, perceived safety, tactile texture, cleaning feel and actual discomfort require voluntary wearer feedback. Measured foam/cover/band properties are needed to validate the numerical inputs. Child-safe adjustment, clamp retention, pinch/access hazards, fatigue, drop tests and acoustics need physical evaluation. The lowest-cost design cannot be established without manufacturing quotations.

Before wearer trials: measure material curves; compare band force versus spread/extension; use a dummy-head compression rig with glasses; verify slider/clamp retention; measure sound reduction with/without glasses; verify fit, weight and surface finish. Begin with a supervised adult prototype investigation. Child use requires separate fit and hardware assessment.

## Reproduce

Python + NumPy: `cushion_v5_study.py`, `extendable_study.py`, `moisture_v5_study.py`, `acoustic_v5_fem.py`, then `prepare_v5_builder.py`. Run registered `CushionNext` in Fusion to build `EngineeringV5.py`, then run `build_v5_review.py`. The recipe source is `extendable-recipes.json`, with base cushion inputs in `engineering-final.json`. Previous V4 studies remain separate.
