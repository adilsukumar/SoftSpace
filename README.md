<p align="center">
  <img src=".github/assets/softspace-cover.svg" width="100%" alt="SoftSpace â€” exploring affordable passive headphones and glasses-friendly cushions. Research in progress." />
</p>

<p align="center">
  <img alt="Stage: research prototype" src="https://img.shields.io/badge/STAGE-Research_prototype-183e45?style=for-the-badge&amp;labelColor=0b2028" />
  <img alt="Current STEP design: V19" src="https://img.shields.io/badge/STEP-V19-90dac0?style=for-the-badge&amp;labelColor=0b2028" />
  <img alt="Six adjustable size variants" src="https://img.shields.io/badge/SIZES-6_variants-cdb89c?style=for-the-badge&amp;labelColor=0b2028" />
  <img alt="Focus: India" src="https://img.shields.io/badge/FOCUS-India-b0cad1?style=for-the-badge&amp;labelColor=0b2028" />
</p>

<p align="center">
  <a href="SoftSpace/README.md"><strong>Explore SoftSpace</strong></a> &nbsp; Â· &nbsp;
  <a href="SoftSpace%20Flex/README.md"><strong>Explore SoftSpace Flex</strong></a> &nbsp; Â· &nbsp;
  <a href="#the-evidence-so-far">Test results</a> &nbsp; Â· &nbsp;
  <a href="#start-with-the-reports">Read the reports</a>
</p>

## Small details. A more comfortable possibility.

Loud surroundings can be overwhelming for some autistic people. A headphone can also introduce its own problems: heat, pressure, an awkward fit, an irritating surface, or a cushion pushing against glasses.

**SoftSpace explores those problems together.** The first priority is an affordable passive over-ear product for sound-sensitive autistic users in India. A second product route explores replacement cushions for people who wear glasses.

This repository makes the work inspectable: actual CAD, illustrated reports, numerical results, failures, source code and the measurements still needed.

**Current stage: a digital prototype for bench review.** Selected geometry and numerical checks have passed. Comfort, sensory acceptance, sound reduction, outgoing sound leakage, heat and long-term durability have not been demonstrated on real samples. The project is not a finished or certified product.

## Two routes, one shared design question

<table>
  <tr>
    <th width="50%">01 &nbsp; SoftSpace</th>
    <th width="50%">02 &nbsp; SoftSpace Flex</th>
  </tr>
  <tr>
    <td align="center"><img src="SoftSpace/media/V19_assemblies.png" alt="Actual V19 child large and adult small STEP assemblies" width="440" /></td>
    <td align="center"><img src="SoftSpace%20Flex/media/generic_cushion.png" alt="Earlier generic replacement-cushion CAD, not a measured Sony mounting interface" width="440" /></td>
  </tr>
  <tr>
    <td><strong>A complete passive headphone concept</strong><br/>Six adjustable child/adult size variants, a folding mechanism and a developing cushion system. Autistic users are the first priority.</td>
    <td><strong>A replacement-cushion concept</strong><br/>A softer zone around glasses arms with a continuous cover. The first intended host is the Sony WH-CH720N; its mounting dimensions are still required.</td>
  </tr>
  <tr>
    <td><a href="SoftSpace/README.md">Open product overview â†’</a><br/><a href="SoftSpace/reports/SoftSpace_Report.docx">Download illustrated Word report â†’</a></td>
    <td><a href="SoftSpace%20Flex/README.md">Open product overview â†’</a><br/><a href="SoftSpace%20Flex/reports/SoftSpace_Flex_Report.docx">Download illustrated Word report â†’</a></td>
  </tr>
</table>

*The product images above come from saved CAD. Colours show parts, not selected materials. Cushion surface triangles are the display mesh, not a proposed fabric texture. The cover illustration at the top is decorative concept artwork.*

## What we are trying to improve

| Design question | Direction under investigation | What will establish whether it works |
| :--- | :--- | :--- |
| Pressure and fit | Adjustable sizes, headband compliance and cushion compression | Measured headband force, material curves and worn-fit checks |
| Glasses discomfort | A more compliant cushion zone around the glasses arm | Contact measurements and voluntary comparisons with the original pad |
| Noise and sealing | Passive cups and a continuous cushion cover | Repeated acoustic measurements with different fits and glasses |
| Heat and surface feel | Compare foam, cover, seam and padding options | Traceable samples, heat/moisture measurements and individual feedback |
| Carrying and robustness | Folding geometry, stops and a revised hinge proposal | Assembly checks, measured hinge torque, cycling and handling tests |
| Affordability in India | Simple construction and replaceable cushions | Supplier quotations, tooling costs, sourcing and prototype yield |

Autistic people have different sensory preferences. A design that works for one person may be uncomfortable for another. The project does not assume one universal fit, pressure or sound-reduction preference.

## The evidence so far

The latest standalone geometry is **V19**. The numerical results are conditional reference calculations; the reports explain the assumptions and earlier failures.

| Check | Recorded outcome | Practical limit |
| :--- | :--- | :--- |
| Six V19 assembly variants | 42 solids per assembly | CAD structure, not assembly or strength qualification |
| Folding/adjustment geometry | 189 sampled rigid poses and 24 outward-stop queries | Sampled poses do not prove every point in continuous motion clears |
| Saved pose exports | 18 wear/retracted/folded STEP files reimported and checked | Geometry and file checks only |
| Original 3D joint study | 22 current accepted solves; failed trials retained | Ideal pivot and prescribed preload; original linear mesh limits remain recorded |
| Boundary-alignment pilot | 8 recorded linear-solid cases | Did not resolve the earlier linear mesh sensitivity |
| Higher-order joint extension | 4 outward and 4 inward reference cases | Selected two-mesh displacement checks; no complete joint or wearer validation |

### Selected displacement comparisons

| Reference fixture | Child large | Adult small | Chosen numerical comparison |
| :--- | ---: | ---: | :--- |
| Outward load | 0.39% | 0.41% | Pass, below 5% |
| Inward load | 0.37% | 0.34% | Pass, below 5% |

These percentages describe **how much computed displacement changed between two meshes**. They are not comfort scores or improvements over another headphone. The fixtures use an assumed elastic PA66 reference, an ideal pivot, 140 N prescribed **joint preload**, friction coefficient 0.2 and a Â±2 N side load. They are separate static cases, not a folding-cycle or load-reversal test.

All eight higher-order cases have saved-result audits. Passing these selected checks does not establish convergence of every stress, qualify the real fastener, calibrate the proposed hinge torque, or prove real sound isolation.

**Read the evidence:** [outward results](SoftSpace/engineering/evidence/engineering-v19-results/quadratic-contact/status.json) Â· [inward results](SoftSpace/engineering/evidence/engineering-v19-results/quadratic-inward/status.json) Â· [inward audits](SoftSpace/engineering/evidence/engineering-v19-results/quadratic-inward/verification.json) Â· [full workstream status](SoftSpace/engineering/evidence/engineering-v19-results/workstream_status.csv).

## A closer look at the fold

<p align="center">
  <img src="SoftSpace/media/V19_folding.png" width="850" alt="V19 child large and adult small assemblies in retracted and folded sampled poses" />
</p>

The saved poses illustrate the current folding proposal. Actual locking, tool access, friction, pin/washer behaviour and durability still need prototype checks. Proposed threads use cosmetic CAD envelopes; they are not manufacturing-ready thread geometry.

## Start with the reports

| Document | What is inside |
| :--- | :--- |
| [**SoftSpace report**](SoftSpace/reports/SoftSpace_Report.docx) | User needs, selected market comparisons, version history, CAD pictures, numerical tests, failed trials and the next measurements |
| [**SoftSpace Flex report**](SoftSpace%20Flex/reports/SoftSpace_Flex_Report.docx) | Glasses/cushion problem, existing alternatives, continuous-cover concept, generic CAD, Sony measurement needs and leakage/fit test plan |
| [**Prototype handoff notes**](SoftSpace/engineering/evidence/engineering-v19-results/prototype-handoff/READ_FIRST.md) | Nominal hardware, assembly proposal, sample selection and bench-test sequence |
| [**Nominal dimension review**](SoftSpace/engineering/evidence/engineering-v19-results/prototype-handoff/Prototype_dimension_review.pdf) | Prototype dimensions for review; not a complete production drawing |
| [**Engineering guide**](SoftSpace/engineering/README.md) | File provenance, dependencies and how to materialize a workspace for saved-result checks |

The Word reports were checked structurally and through approximate rendered page previews. Native Word pagination remains unverified.

## Complete research archive

[**Download the complete V19 research bundle (450 MB)**](https://github.com/adilsukumar/SoftSpace/releases/download/v19-research/SoftSpace_Complete_V19_Research.zip) for historical CAD and older raw numerical arrays. Git keeps the current CAD, both reports, source, result summaries and all eight higher-order saved solutions. The bundle includes 1,735 files and an integrity manifest; every recorded SHA-256 and ZIP CRC was checked before upload.

Bundle SHA-256: `13eb06a9162fab0dbcf2a6b495e84aa301b0f2840df34c2888a1e1d3e588914c`.

## Repository map

```text
SoftSpace/
â”œâ”€â”€ README.md
â”œâ”€â”€ reports/                  Illustrated SoftSpace report
â”œâ”€â”€ CAD/
â”‚   â”œâ”€â”€ V19/                  Six current assemblies and 18 saved poses
â”‚   â””â”€â”€ V10-native/           Earlier editable Fusion archives
â”œâ”€â”€ media/                    Saved CAD views and research figures
â””â”€â”€ engineering/
    â”œâ”€â”€ evidence/             Recorded results, arrays, failures and blank forms
    â”œâ”€â”€ CAD/                  Current V19 analysis-source CAD
    â”œâ”€â”€ sources/              Simulation, CAD and report-authoring scripts
    â”œâ”€â”€ figures/              Figures used in the living reports
    â”œâ”€â”€ tools/                Workspace preparation and repository verification
    â””â”€â”€ publication_manifest.json

SoftSpace Flex/
â”œâ”€â”€ README.md
â”œâ”€â”€ reports/                  Illustrated SoftSpace Flex report
â”œâ”€â”€ CAD/generic-V8/           Generic cushion candidates; Sony fit unverified
â”œâ”€â”€ measurements/            Blank measurement and sample-test records
â””â”€â”€ media/                    Cushion view and measurement guide
```

Shared calculations live in `SoftSpace/engineering` so both routes refer to the same evidence. Historical technical filenames are preserved there for traceability. Installed libraries, cached wheels, temporary screenshots and duplicate release ZIPs are excluded.

<details>
<summary><strong>Design history at a glance</strong></summary>

| Stage | Main focus |
| :--- | :--- |
| V1â€“V9 | Cushion concepts, continuous-cover exploration, extendable sizes and early structural screens |
| V10 | Native Fusion candidates and actual-width component fixtures |
| V11â€“V14 | Materials, folding geometry, locks and service-cap experiments; rejected routes retained |
| V15â€“V17 | Retention, packing, index holes and entry pilots |
| V18 | Passive hinge and wearing-stop proposal; handling and material screens |
| V19 | Parallel disc-spring proposal, revised pin/nuts, six-size exports and coupled joint calculations |

Current **V19 is STEP CAD**. The latest saved native editable Fusion archives remain **V10**. An illustration or file export is not a manufactured prototype.

</details>

## What happens next

1. **Measure the Sony mount and original pad.** Complete the [model-specific form](SoftSpace%20Flex/measurements/Sony_WH_CH720N_measurements_REQUIRED.csv) before designing a compatible carrier.
2. **Obtain traceable material samples.** Measure foam compression/recovery, cover stretch/friction, headband force and hinge torque.
3. **Build a bench hinge and cushion sample.** Compare measurements with the models and revise the assumptions.
4. **Complete a fixture prototype.** Check fit, assembly, retention, acoustics, outgoing leakage, heat and durability.
5. **Collect voluntary wearer feedback.** Include individual sensory preferences, easy removal and glasses variations before making comfort or autism-related benefit claims.

The material work is a finite reference screen, not a test of every possible material. No novel material winner, lowest-cost claim, zero-leakage claim or superiority over market headphones has been established.

## Contributing evidence

Useful contributions include measured mounting dimensions, traceable material curves, reproducible fixture results and clearly documented model corrections. Include units, method, sample/grade, conditions and uncertainty. Keep simulations, manufacturer statements, physical measurements and wearer feedback separate.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the evidence format and report-update rule.

---

<p align="center"><strong>SoftSpace Â· SoftSpace Flex</strong><br/>Built around a comfort question. Documented with evidence.<br/><sub>Working names; trademark clearance is incomplete. No open-source licence has been selected.</sub></p>
