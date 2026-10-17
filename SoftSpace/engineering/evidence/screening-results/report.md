# Prototype screening results

**These are hypothetical design scenarios, not validated FEA, measured material properties, acoustic protection ratings or evidence of wearer comfort.**

Both objectives remain: a standalone passive ear defender for sound-sensitive autistic users, and replacement cushions for glasses wearers. No diagnosis-specific pressure threshold is assumed.

## Completed numerical work
- 3,240 nonlinear spring/contact cases, including no glasses and three arm thicknesses.
- 81 lumped heat/vapor cases for 28, 32 and 36 C ambient at 70% RH.
- 18 prescribed spring-force cases across separate child/adult head-size hypotheses.
- Force residual below 6.1e-12 N.
- Closed-form flat-pad verification: 1200 Pa produces exactly 2 mm compression with the synthetic medium foam curve.
- Grid refinement tested. The nominal contact fraction varies from 70.9% to 67.6% at higher resolution; gap/coverage estimates must not be treated as converged precise predictions. Peak pressure is more stable for this example.

## Illustrative comparison
Adult-medium surrogate; 2 N per cup; standard 8 x 3 mm arm; synthetic medium foam; compliant cover.

| Quantity | Uniform material | Local stiffness ratio 0.5 |
|---|---:|---:|
| Peak pressure under frame | 2.33 kPa | 1.19 kPa |
| Overall peak pressure | 2.33 kPa | 1.36 kPa |
| Maximum compression | 5.22 mm | 5.29 mm |
| Approximate contact coverage | 69.9% | 70.9% |
| Maximum predicted surface gap | 3.40 mm | 3.32 mm |

The local frame-pressure reduction is 48.9% **within this assumed model**. A stiffness reduction is built into the hypothesis; this is consistency/sensitivity evidence, not proof that an available foam will behave this way. Gaps remain, so this design has not established an adequate acoustic seal. Pressure on a rigid frame is only a proxy; it is not the pressure behind the glasses arm on a compliant human head.

## Working design targets to investigate
- Separate adult/child band sizes; initial per-cup force target 2 N at 155/130 mm head breadth respectively.
- Test sensitivity to spring slope 0.05-0.15 N/mm and head breadth changes. This prescribed law has not been derived from a curved band geometry or real band material.
- Initial medium foam target stress: 1.2 kPa at 10% compression, 3 kPa at 40%, 8 kPa at 70%. These are synthetic procurement/test targets, not manufacturer data.
- Test compliant region at 0.5 and 0.75 of base compression stress. Check extra compression and load transfer.
- Initial compliant cover assumption: 0.2 mm, E=1 MPa, Poisson ratio 0.45. Poisson ratio is recorded but not used in this scalar model. Actual material selection and continuous-skin modelling remain open.
- For replacement pads, screen 1-6 N per cup because clamp force belongs to the existing headphone. Actual compatibility needs measurements.

## Heat and humidity
At 32 C ambient, the illustrative compliant-cover, k=0.05 W/mK, 0.01 L/min exchange case predicts 33.4 C and 100% RH after one hour. Moisture exchange strongly depends on the assumed leakage/permeation. This model cannot resolve sweat comfort, material sorption, moisture transport through a particular cover or cooling claims. Exchange levels are not proposed open vents; acoustic consequences must be checked separately.

## Model equations and omissions
Foam stress is a monotonic interpolation of the synthetic compression table. Local normal pressure is foam stress plus E*t*compression^3/(6*span^4), span=20 mm, as an illustrative cover-resistance surrogate. Total force is the area-weighted sum of pressure and is solved by bisection. Head contact surface is parabolic with separate principal radii. Frame thickness adds local compression. Foam cells are independent: no lateral shear, cover stress transfer, friction, skin compliance, ear geometry, actual frame bending, cup rocking or nonlinear 3D interaction is resolved. Actual 3D FEA and tests must address these omissions.

Heat/vapor use a single temperature node and well-mixed air volume, specified skin temperature and prescribed water input. No acoustic simulation was performed. No conclusions about autism, pain relief, hearing protection or universal fit follow from these calculations.

## Next engineering work
Improve head conformity or cup articulation to reduce seal gaps, then model the continuous cover and material interfaces. Obtain or measure foam/cover curves and band force, validate a nonlinear contact solver, build one physical comparison, and perform voluntary wearer trials. Develop headphone adapters per model; one pad does not fit all brands.

Files: assumptions.json, mechanical_cases.csv, thermal_cases.csv, headband_force_cases.csv, summary.json and explore.html.
