# Software review on 24 October 2026

This V21 round adds checks to the unchanged SoftSpace V19 headset and SoftSpace Flex V20 reference cushions. It does not finish all possible software work. The most important new result is a failed peak-stress refinement comparison that remains software work, as well as the material and mounting inputs already missing.

## What changed

Six sizes were checked at folding midpoints between the old 5 degree samples, at selected unequal slider settings, and at four simultaneous folding positions. These are finite rigid checks, not continuous motion or pinch safety proof. Read the six JSON files for every pass and failure and the source STEP hashes.

All 11,664 V20 cushion rows were compared with closed-form elliptical areas. 334 exceeded the chosen 1 percent numerical comparison, with a maximum difference of 3.35 percent. The 12 selected V20 checks were true but did not establish accuracy of every row. V21 uses exact areas and explicit force-root brackets; the original CSV is preserved.

The wider assumed-position study has 126,360 cases, covering arm centres from -10 to 40 mm at 2 mm increments, widths 3/5/8 mm and zone heights 12/18/24/32/100 mm. Other force, foam, cover and protrusion assumptions are the same as V20. 127 selected rows were verified with independently implemented adaptive integration and a scalar root; this checks implementation, not realism. No random population sampling or probability is implied.

The 18 and 32 mm zones can raise local pressure when the arm misses them. A 100 mm zone avoids that local increase in eligible cases but still has 780 peak-pressure increases elsewhere and four model-detachment cases. That 100 mm zone is a computational alternative only, with no new STEP release or final material selection. No patch is declared a winner. The cover is a parallel-stiffness hypothesis, not a real membrane. Model detachment is not a measured seal gap or an acoustic result.

Eight saved V19 joint solutions were postprocessed at 27 interior points per element. Centroid values were reproduced. All eight peak comparisons between the two existing meshes exceeded the chosen 5 percent gate, with changes about 5 to 57 percent. Displacement checks do not establish peak-stress convergence. The following finer-mesh section records four new equilibrium solves. No material-strength pass is claimed. Further numerical work on mesh quality, stress locations and contact/bearing idealizations remains open; it cannot honestly be relabelled as only a physical-testing requirement.

Hinge and fit formulas were inverted to show conditional limits. At the assumed lowest friction and equivalent static 3g loading, the earlier mass screen needs about 206 N preload. This is not a permitted setting: actual friction, locking, spring curve and stresses must be checked. A nominal 4.3 mm bore supports the tight allocated errors but not the broad raw-error scenario. Enlarging to 4.7 mm would satisfy only that arithmetic clearance target and change bearing behaviour; CAD was not changed blindly.

## Scope and remaining work

The accompanying test_scope_register.csv covers geometry, folding, fit, structural calculations, materials, contact, sound, heat, durability, manufacturing and user acceptance. It identifies completed screens, failed comparisons, missing inputs and tests that need people. Prior acoustic/thermal models belong to earlier idealized geometries and are not current-headset performance tests. Not every possible material, headphone or head shape has been tested.

No all-software-complete, zero-leakage, clinically helpful, strongest, cheapest or market-superiority claim is supported. No production tooling is released. Small traceable material samples and exact reference-pad dimensions are useful inputs, but this review does not force the user to buy hardware or treat unresolved numerical issues as solved.

## Reproduce

Use the repository engineering prepare_workspace.py tool and recorded dependencies. From that workspace run v21_contact_envelope.py, v21_verify_and_limits.py, run_v21_motion.py, v21_stress_recovery.py and v21_compile_review.py. The motion script uses original STEP hashes and the existing positive-control OCC import procedure. The stress script reads the eight existing NPZ files without modifying them. New source/output hashes are recorded in the publication manifest.

## Additional finer joint matrix

The four representative joint/load cases now have an optimized 1.9 mm result. The original failed 3.0 to 2.3 mm comparisons above remain recorded. Read refinement/matrix_review.json for all new comparisons and their exact pass/fail status. The final accepted route uses projected Anderson acceleration of the original fixed-point contact equations with direct-LU inner solves. The child outward run uses mixed acceleration and matches the saved unaccelerated reference field; the other three use full projected acceleration. A separate Newton warm-start control is retained as an implementation check only. Failed mesh and stopped performance/solver experiments remain in the logs and solver_experiments.json; they are not passes.

These isolated joint fixtures come from the V19 ParallelDisc geometry, not a complete loaded final AssemblyPrototype. They use E=3500 MPa, nu=0.35, 140 N preload, friction 0.2 and +/-2 N side load. The peak check samples 27 interior points; it is not a globally bounded surface/contact-edge stress or a resolved bolt/thread/bearing model. A numerical comparison pass does not supply a real material allowable stress, durability or a manufactured joint qualification.

Some finer peak comparisons did not pass. Further numerical work remains before relying on peak stress.

## Final review on 24 October

Six of eight finer sampled-peak comparisons pass. The adult fork still changes 27.52 percent outward and 28.31 percent inward, so the peak-stress check remains failed. All four displacement comparisons change less than 0.63 percent and pass separately; final force-balance errors are below 7e-10 N. These do not erase the peak failure. Hotspot locations, curved-element condition numbers, energy and volume-weighted quantiles are recorded in hotspot_diagnostics.json. Quantiles are diagnostic context, never substitute pass criteria. Proximity to a nominal contact boundary does not prove a singularity.

All six sizes have a smaller carrying pose. Each search ranked 625 candidate angle pairs, rejected actual collisions, and stopped at the first passing endpoint and left-first path sampled every 2.5 degrees. Six pose-only STEP exports reimport as 42 solids with matching volume. Part shapes are unchanged. The 12 canonical joint-part comparisons within the adult/child families pass; this does not transfer whole-headset worn loads. The older heat proxy matched its analytic equation in 216 rows, but 155 assumed moisture rows saturated. This is no cooling-performance validation.

The finite V21 review is complete. All possible software testing is not complete. Remaining software work includes the adult fork peak prediction, detailed fastener/contact and manufactured geometry, actual material curves, full worn contact, calibrated acoustics and thermal models, and exact Sony mounting geometry. These need defined inputs; arbitrary extra simulated cases would not establish real performance. Both products remain development concepts, not manufacturing-ready or proven beneficial.

Accepted reproduction sources include v21_anderson_matrix.py (mixed child source archived in solver-sources), v21_matrix_review.py, v21_hotspot_diagnostics.py, v21_family_equivalence.py, v21_compact_pose.py and run_v21_compact.py. Replaying equilibrium and geometry searches can take hours. Read solver_experiments.json for stopped and rejected attempts.
