# SoftSpace

**An affordable passive over-ear headphone concept, with sound-sensitive autistic users in India as the first priority.**

[Read the illustrated report](reports/SoftSpace_Report.docx) Â· [Open V19 CAD](CAD/V19) Â· [Browse engineering evidence](engineering/README.md) Â· [Back to the project](../README.md)

![V19 saved child and adult STEP assemblies](media/V19_assemblies.png)

We are investigating fit, pressure, heat, texture, glasses contact, bulk and passive sound reduction together. The current concept has six adjustable child/adult size variants and a sampled folding proposal. No electronic noise-cancellation system or audio playback circuit has been implemented in this CAD study.

## Current files

| Folder | Contents | Status |
| :--- | :--- | :--- |
| [reports](reports) | SoftSpace Word report with development history and selected market comparisons | Living evidence record |
| [CAD/V19](CAD/V19) | Six STEP assemblies and 18 sampled wear/retracted/folded exports | Current local geometry; prototype proposal |
| [CAD/V10-native](CAD/V10-native) | Earlier native Fusion archives | V10, not a native V19 rebuild |
| [engineering](engineering) | Shared CAD sources, numerical arrays, results, failures and handoff forms | Assumptions and scope must be read with each result |

## Recorded checks

The six V19 assemblies contain 42 solids each. The recorded geometry work includes 189 sampled rigid poses, 24 outward-stop queries and 18 reimported pose exports.

Selected higher-order joint comparisons pass the chosen 5% displacement-change check: outward 0.39% / 0.41% and inward 0.37% / 0.34% for child large / adult small. These are ideal-pivot fixture calculations with assumed material/contact properties. They do not prove complete-joint strength, comfort, acoustic performance or durability.

![Saved retracted and folded poses](media/V19_folding.png)

## Before a complete product prototype

Collect real material curves, headband force and hinge torque, then build and measure a bench hinge and cushion sample. The proposed nut/pin stack still needs tool-access, locking, thread/tolerance and supplier review. Current threads are cosmetic CAD envelopes. The nominal dimension review is not a production drawing.

Individual sensory acceptance requires voluntary feedback. No universal autistic preference, guaranteed comfort, real sound-reduction result or market-superiority claim is established.

The related [SoftSpace Flex](../SoftSpace%20Flex/README.md) cushion route shares material and contact-design learning. Its Sony fit remains unverified.

## Latest pre prototype review

The [V20 evidence update](engineering/evidence/engineering-v20-results/README.md) leaves the V19 headset CAD unchanged, reruns eight saved joint audits and adds hinge/tolerance scenarios with failures retained. Start with material and bench-hinge samples. Calibrated full-headset performance remains open. The companion Flex route adds three reference cushion bodies; it has no verified Sony fit.

## V21 software review

The [additional software review](../SoftSpace/engineering/evidence/engineering-v21-results/README.md) records wider glasses-position pressure risks and failed joint peak-stress comparisons. Further software work remains. Both reports are updated. Six carrying pose STEP exports are added; part shapes are unchanged. Six finer stress checks pass and two adult fork checks still fail.

<!-- BLOCK_SOLVER:BEGIN -->
## Joint solver update 26 October 2026

The lower memory V26B pilot reduced stored factor entries from 92.64 to 27.78 million. Its second linear solve failed the unchanged accuracy gate, so there is **no accepted new strength result**. Both reports retain this failure. Full headset validation and exact Sony replacement fit remain open.
<!-- BLOCK_SOLVER:END -->

<!-- MATERIAL_LOADING:BEGIN -->
## Named material loading screen 26 October 2026

The [new material screen](../SoftSpace/engineering/evidence/material-screen-2026-10-26/README.md) uses source-checked loading points for eight named Confor grades rather than an assumed foam law. Of 1152 cases, 559 are solved within the published strain range and 593 are left outside the supported domain. Cases with higher local pressure are retained. One 8 N reference gives about 35 percent lower calculated glasses-strip pressure with CF-40M in a CF-42M ring; this is a simplified uncovered 12.7 mm reference, **not pain relief, seal, fit or product validation**.

Both illustrated reports are updated together and native Word layouts checked. Grade availability and price in India are unverified. The loading-input gap has advanced; unloading, recovery, cover, mounting and full product gates remain open. Source URLs, hashes, extracted facts and all scenario results are published; manufacturer PDFs remain local for source checking.
<!-- MATERIAL_LOADING:END -->

<!-- VALIDATION_DECISION:BEGIN -->
## Software validation decision

**Neither product has passed full software validation or is approved for manufacturing release.** The evidence assessment is complete; outstanding tests are not complete. SoftSpace has unresolved joint strength and full assembly validation. Flex lacks verified Sony mounting geometry. Both routes still need qualified inputs and complete contact, sound, heat and durability models; wearer acceptance needs people.

The [decision and requirement register](../SoftSpace/engineering/evidence/validation-decision/README.md) identifies existing evidence, missing inputs and acceptance requirements. Both Word reports contain the same final decision. This review reused saved results and ran no new simulation campaign. Further computation should address a specific changed design or newly qualified input; repeated assumed runs cannot supply missing measurements or mounting dimensions.
<!-- VALIDATION_DECISION:END -->

<!-- V26:BEGIN -->
## V26 rounded local joint trials

Two separate local CAD candidates investigate the failed stress predictions. Candidate A meets the fork mesh comparison but still fails the tongue checks, and introduces folding interference at two sampled angles. Candidate B relieves that corner and passes all 25 local folding samples plus both wearing-stop checks. These two-part candidates are **not integrated full headset releases**. Read the [CAD, raw fields and failure records](../SoftSpace/engineering/evidence/engineering-v26-results/README.md).

Candidate B has **no accepted strength field**: low-memory solvers failed their accuracy gates, and the stronger attempt was stopped at a five-minute operational cap with about 8.7 GB committed. That stop does not prove physical weakness or mathematical divergence. Both illustrated Word reports are updated together and checked in native Word. The [remaining requirements](../SoftSpace/engineering/evidence/engineering-v26-results/remaining_test_register.csv) still apply to both projects. **Full product software and physical validation remain open.** Sony fit, comfort, sound, heat and durability gains remain unproved.
<!-- V26:END -->

<!-- V25:BEGIN -->
## V25 surface calculation investigation

Three new child-large outward reference calculations test quadratic surface contact and consistent surface loads. All numerical consistency controls pass. Increasing integration accuracy changes sampled peaks by less than 0.4 percent, but mesh changes still give roughly 6 to 19 percent differences: **0 of 4 mesh comparisons pass** the chosen 5 percent check. This candidate does not fix reliable stress prediction or establish strength. Read the [pilot evidence and raw fields](../SoftSpace/engineering/evidence/engineering-v25-results/README.md).

Both illustrated Word reports are updated together and checked in native Word. A [manufacturer input review](../SoftSpace/engineering/evidence/engineering-v25-results/manufacturer_input_review.json) records specific BASF, Rogers and Sony sources; it does not turn typical data into a complete foam law or verified Sony mount. The [remaining requirements](../SoftSpace/engineering/evidence/engineering-v25-results/remaining_test_register.csv) still include actual joint details, material condition, cushion contact, exact mounting, sound, heat and durability. **Neither product has full software or physical sign off.** No product performance or prototype purchase release is claimed.
<!-- V25:END -->

<!-- V24:BEGIN -->
## V24 corrected joint verification

Four new corrected virtual-spacer reference calculations use finer 1.5 mm target meshes on both joint families and load directions. Only 2 of 16 refined peak comparisons meet the fixed 5 percent limit. Their [raw results and stress comparisons](../SoftSpace/engineering/evidence/engineering-v24-results/README.md) retain every failed comparison. Numerical consistency does not establish reliable whole-part stress or physical strength.

Primary CAD source loaders now resolve the moved workspace by recorded hashes. Four exact historical V12 sources are restored separately; all 304 recorded source path/hash pairs match. Both illustrated Word reports are updated together. Read the [remaining test register](../SoftSpace/engineering/evidence/engineering-v24-results/remaining_test_register.csv): actual material curves, detailed joints, Sony mounting, sound and heat inputs remain unresolved. This completed numerical campaign is **not all product software testing completed**. No physical validation or product performance claim is added.
<!-- V24:END -->

<!-- V23:BEGIN -->
## V23 corrected joint verification

Eight new corrected virtual-spacer reference calculations cover two joint families, two meshes and both load directions. Their [raw results and stress comparisons](../SoftSpace/engineering/evidence/engineering-v23-results/README.md) retain every failed comparison. Numerical consistency does not establish reliable whole-part stress or physical strength.

Both illustrated Word reports are updated together. Read the [remaining test register](../SoftSpace/engineering/evidence/engineering-v23-results/remaining_test_register.csv): actual material curves, detailed joints, Sony mounting, sound and heat inputs remain unresolved. This completed numerical campaign is **not all product software testing completed**. No physical validation or product performance claim is added.
<!-- V23:END -->

<!-- V22:BEGIN -->
## V22 update

Read the [numerical confidence review](../SoftSpace/engineering/evidence/engineering-v22-results/README.md) and the updated Word report. New joint/model checks retain their failures; whole-pad softness is an added comparison control. Current geometry has no new physical, comfort, acoustic or manufacturing pass. Native Word pagination and layout were checked in this update.
<!-- V22:END -->

