# V22 software review on 24 October 2026

This bounded review is complete with passes and failures retained. It does not establish all possible software testing, final product performance or manufacturing readiness. The two Word reports contain the same update.

The V21 six passing stress comparisons applied only to 27 interior points. V22 recomputed strains with a separate tensor-gradient expression and used 64 and 125 interior points, plus a finite 35-point lattice including corners, edges and faces. Energy changes between orders 4 and 5 were below 0.00004 percent; no nonpositive lattice Jacobian was found in these saved fields. These checks do not certify curved elements everywhere or bound stiffness error. Only two of eight 125-point peak comparisons and one of eight boundary-lattice comparisons met the chosen 5 percent mesh comparison. No globally stable peak or real strength pass is supported.

Two additional adult load cases use a 0.9 mm local fork mesh around the recorded hotspots, retaining the V21 tongue and unchanged V19 CAD. Read targeted_joint_review.json for all sampling comparisons, residuals and force balance. No different sampling method is substituted to erase a failed comparison. Nearest-node interpolation only warm-starts the iteration; acceptance requires actual final equilibrium. These fixtures use idealized pivot/contact and prescribed preload, not a real resolved bolt or worn headset.

A whole-annulus softer-foam control adds 25,272 assumed cases. 22,012 meet the chosen 40 percent compression limit. None of those eligible cases raises local or peak pressure in the reduced model; four have model detachment. The remaining 3,260 exceed the compression limit. A direct uniform-modulus control matches active-area pressures exactly. This makes uniformly softer foam a comparison candidate, not a selected material, comfort benefit, seal or acoustic result. The earlier 100 mm strip altered only the arm-facing half; this new control alters both halves. No cushion or headset part shapes are changed.

## Remaining work

Whole-part peak stress, detailed fastener contact and manufactured edge geometry remain a software/design problem. Material curves, cover and worn contact data, exact Sony mounting, acoustics, heat, creep/fatigue and production tolerances remain input-dependent. Comfort and sensory acceptance require people. Arbitrary extra generic material values do not supply these missing inputs. Read the complete test register before making claims or buying production tooling.

## Reproduce

Use a prepared repository workspace and the recorded numerical dependencies. Run v22_quadrature_mesh_audit.py, v22_recovery_summary.py and v22_uniform_softness.py. The targeted mesh uses v22_local_fork_mesh.py 0.9 and v22_local_fork_solve.py 0.9; these can take substantial time. Then run v22_review.py. Original V19 and V21 raw solutions are preserved. The new solve is fixed-point Anderson acceleration with direct LU and a recorded force-residual gate. It does not calibrate material properties or validate physical performance.

## Contact model correction

The original virtual separated-face tangential operator fails four common rigid-rotation checks across the two size families. Common translations and the hinge-axis rotation pass. A proposed 0.5 mm virtual-spacer mean-bore-rotation correction passes all twelve rigid-motion checks. This defines a mathematical reference, not an actual washer or a validated physical contact law. The original fields fail the corrected equilibrium residual gate, so new corrected reference fields are computed separately by v22_objective_spacer_solve.py with checked matrix-free Newton and GMRES. Read objective_spacer_outward.json and objective_spacer_inward.json for the exact converged status, residuals and derivative controls. No corrected field is accepted merely because the kinematic checks pass. The original histories and failed model checks remain preserved.

Both corrected reference load cases converged. A separate matrix-free residual implementation rechecked them at about 3e-11 relative residual. Net force balance errors are below 7e-10 N and moment balance errors below 1e-8 N mm. The original reference had about 0.06 N mm unbalanced internal moment in this test. The correction resolves this mathematical consistency issue in the defined virtual-spacer reference. It does not establish real washer mechanics, manufactured material strength or stable stress over further meshes and recovery points.
