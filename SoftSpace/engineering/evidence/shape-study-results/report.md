# Contact-shape study V2

These are 9,216 assumption-based numerical cases, not Fusion FEA or measured comfort/noise reduction. Material curves, head shapes, tilt, and forces are invented design inputs. V1 outputs remain preserved.

## Nominal comparison

Adult medium reference, medium foam, compliant scalar cover, standard straight glasses arm, 2 N per cup, local foam stress ratio 0.5, zero imposed tilt.

| Contact shape | Overall peak kPa | Frame peak kPa | Contact area | Largest surface gap mm | Angular lanes without contact |
|---|---:|---:|---:|---:|---:|
| flat_R5 | 1.359 | 1.192 | 70.9% | 3.32 | 0.0% |
| flat_R2 | 1.400 | 1.206 | 63.3% | 1.79 | 0.0% |
| half_contour_R2 | 1.111 | 1.111 | 88.2% | 0.55 | 0.0% |
| reference_contour_R2 | 0.979 | 0.979 | 100.0% | 0.00 | 0.0% |

R5/R2 are 5/2 mm nominal edge-rounding radii. Contour subtracts 50% or 100% of a shared family-reference parabolic head sag from the pad contact-gap field. This represents a cushion face recessed at its centre relative to its perimeter. It does not fit each tested head separately. Actual child and adult anatomy can differ considerably.

## Interpretation limits

Lower pressure and fewer gaps within this model justify comparing physical prototypes; they do not establish comfort, safety or attenuation. The angular-lane metric flags rays across the annulus with no sampled contact. It is a coarse gap indicator, not proof of a continuous airtight seal or an acoustic leak calculation. Compare grid refinement before using contact fractions.

Ideal alignment cancels imposed planar tilt only. A manufactured pivot can have friction, stops and unequal load that this model excludes. Fixed/aligned cases are bounds, not an implemented mechanism.

The cover remains a scalar resistance term with no lateral coupling, stitching, friction, tension or bridging across the soft region. A continuous cover must be represented explicitly in a subsequent nonlinear contact model using measured properties.

## Separate product requirements

- Own ear defender: adjustable size families, measured band force versus opening, articulated cups, continuous cover, foam compression/recovery, skin contact, heat/moisture and measured acoustic attenuation. Adult and child fitting require separate validation.
- Replacement cushion: the same materials and contact checks plus each host headphone's clamp force, mounting geometry, ear clearance, acoustic frequency response and seal. Host force is outside our control, but must still be a test input. One cushion does not automatically fit all brands.

## Next engineering gate

Use the contact comparison to choose candidate face profiles, then measure foam compression curves and cover tensile/permeation properties. Check band force over multiple head breadths. Model skin/glasses/cover/foam contact with a nonlinear solver and verify against compression and pressure-map bench measurements. Keep a uniform cushion as the control. Conduct voluntary wearer evaluations for texture, heat, removal and comfort; simulations cannot establish sensory acceptance.

Thermal results from V1 are unchanged and humidity remains unresolved. No air vent or sound-reduction claim follows from this study.
