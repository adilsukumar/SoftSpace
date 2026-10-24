# V23 corrected reference verification

Eight corrected joint reference solves are complete. All numerical controls pass: True. The models cover child large and adult small isolated V19 joint geometries, meshes 2.3 and 1.9 mm, and side forces +2 and -2 N. The V22 virtual 0.5 mm spacer uses mean bore rotation. E is assumed 3500 MPa, nu 0.35, preload 140 N and friction 0.2. No CAD was changed.

Of 24 fixed 5 percent stress comparisons, 10 pass. All results, including failures, are in stress_comparisons.csv. Boundary lattice and interior sample peaks are finite samples, not a bounded maximum. Passing equilibrium, rigid motion and force balance is not proof of reliable peak stress or real product strength.

Read remaining_test_register.csv before interpreting this as complete product testing. The current numerical campaign is finished; all product software testing is not finished. Actual edge and fastener details, material curves, Sony mounting dimensions, acoustic and thermal data remain unresolved. Comfort and sensory acceptance require people. More arbitrary generic inputs would not validate the intended product.

Run v23_corrected_mesh_campaign.py then v23_review.py with the recorded dependencies. The first script preserves V19 V21 V22 originals, warm-starts from old fields, checks final equilibrium, records contact derivative checks and saves each new field. Stress sampling is recomputed from displacement gradients. The second script compares identical methods and retains failures; it does not replace peak criteria with averages.
