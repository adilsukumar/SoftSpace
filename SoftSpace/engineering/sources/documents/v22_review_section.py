"""Shared V22 review for both living reports, with numerical limits visible."""
import json

def add_v22(d,P,new_page,para,table,picture):
 O=P/'engineering-v22-results'
 if not (O/'review_status.json').exists():return
 r=json.loads((O/'review_status.json').read_text());audit=json.loads((O/'recovery_comparisons.json').read_text())
 new_page(d,'V22 How reliable are the stress numbers')
 para(d,'24 October 2026. We checked the saved joint results more deeply before relying on them. The material properties, loads and CAD are unchanged. A second method of calculating strain matched the original method. Increasing numerical integration from 64 to 125 points changed total elastic energy by less than 0.00004 percent in the saved fields. The 35 point mesh check found no turned inside out elements at the points tested. An additional adaptive Gmsh check was positive on all ten component meshes. These are mesh shape checks, not stress accuracy checks.')
 picture(d,'V22_stress_recovery','Changing where we sample stress changes the mesh comparison. This chart is a numerical diagnostic, not a material or product strength test.',6.55)
 para(d,'The energy check passed, but peak stress depends strongly on the points being inspected. At 125 interior points, only two of the eight 2.3 to 1.9 mm comparisons meet the chosen 5 percent check. The earlier six passes used 27 interior points. Those were true for that limited test; they do not establish stable stress throughout a part.')
 para(d,'The additional 35 point set includes element corners, edges and faces. Seven of its eight comparisons exceed 5 percent. These are sampled values, not a proof of the largest stress everywhere. No global stress, material strength, hinge life or break resistance pass is established. We have kept the earlier results and explained their limits.')
 new_page(d,'V22 Targeted adult fork refinement')
 para(d,'The adult fork had two recorded stress hotspots. We generated a mesh with a 0.9 mm local target around them, keeping the earlier tongue mesh and the same CAD. This mesh has 46,413 nodes. Both load directions use the same assumed stiffness, friction and preload as V21. Warm starting only speeds the calculation; each result must satisfy the final force residual check.')
 table(d,['Load direction','Equilibrium','Displacement change','125 point fork peak change'],[[x['direction'], 'Passed' if x['equilibrium_pass'] else 'Failed',format(x['displacement_change_percent'],'.2f')+' percent',format(x['fork_peak_125_change_percent'],'.2f')+' percent'] for x in r['targeted_cases']],[1.45,1.25,1.85,2.35])
 para(d,r['targeted_plain_english'])
 if (P/'documents/images/V22_targeted_fork_stress.png').exists():picture(d,'V22_targeted_fork_stress','Original interface reference interior stress samples mapped to the unchanged fork mesh. These are not measured surface stresses or a strength pass.',6.1)
 para(d,'The complete fields, mesh, force residuals, force balance and sampling comparisons are saved in engineering-v22-results. The local target is not a promise that every edge in the mesh has that size. A finite positive Jacobian check does not certify curved elements everywhere. This isolated fork and tongue fixture does not include a real bolt, thread, worn head or complete headset loading.')
 para(d,'We did not change the CAD or raise the allowable stress to make a test pass. We also did not use average stress to replace a peak criterion. Further model or design changes need to state the actual contact and edge geometry, material and production process being represented.')
 new_page(d,'V22 Contact consistency and correction')
 ctrl=json.loads((O/'contact_rigid_motion_controls.json').read_text())
 para(d,'A rigid motion test moves the entire joint together. It should create no relative slip. The original friction interface passed common translations and rotation about the intended hinge axis, but failed rotations about the other two axes. The two representative sizes each showed 0.5 mm of false tangential motion per radian in those failed checks. This is a modelling issue, not a broken physical part.')
 table(d,['Rigid motion checks across two sizes','Original interface','Proposed correction'],[
 ['Three common translations per size','6 passed','6 passed'],
 ['Rotation about hinge axis per size','2 passed','2 passed'],
 ['Other two common rotation axes per size','4 failed','4 passed']],[3.8,1.55,1.55])
 para(d,'The correction accounts for a virtual 0.5 mm spacer rotating with the mean fitted bore rotation. It passes all twelve rigid motion checks. This is an explicit mathematical reference model. It does not replace a real washer, bolt, friction history or a physical contact measurement.')
 objective=[]
 for side in ['outward','inward']:
  f=O/('objective_spacer_'+side+'.json')
  if f.exists():objective.append((side,json.loads(f.read_text())))
 if len(objective)==2:
  table(d,['Corrected reference load','Equilibrium status','Final relative residual'],[[side,'Passed' if v['converged'] else 'Failed',format(v['relative_free_residual'],'.2e')] for side,v in objective],[2.65,2.15,2.1])
  para(d,'The corrected reference uses new equilibrium calculations, starting from the saved refined fields. Contact derivative checks and linear solver residuals are recorded. The full pivot penalty is evaluated without building a large dense matrix. This changes storage, not its equation. A separate force, moment and equilibrium recheck also passed for both corrected fields. These solver checks do not resolve peak stress throughout the part or qualify an actual material.')
 para(d,'The earlier stress fields remain saved with their original interface identified. The corrected reference remains conditional. Complete spacer contact, actual edge shape, material properties, preload and manufactured tolerances must be specified before treating it as the intended product.')
 new_page(d,'V22 A simpler cushion control')
 soft=json.loads((O/'uniform_softness_summary.json').read_text())
 para(d,'We also checked a simpler option: make the entire foam pad softer, rather than adding a soft patch near the glasses arm. We ran 25,272 assumed cases using the same exact area foam model as V21. The glasses arm still acts on one side of the annulus; both sides of the foam are softened in this control.')
 table(d,['Computer result','Whole pad softer foam'],[
 ['Assumed cases',str(soft['scenarios'])],
 ['Cases within chosen 40 percent compression range',str(soft['eligible_within_chosen_40_percent_compression'])],
 ['Local pressure increases within that range',str(soft['eligible_local_pressure_increases'])],
 ['Peak pressure increases within that range',str(soft['eligible_peak_pressure_increases'])],
 ['Model detachment cases within that range',str(soft['eligible_detachment_cases'])],
 ['Cases outside the compression range',str(soft['scenarios']-soft['eligible_within_chosen_40_percent_compression'])]],[4.6,2.3])
 para(d,'No eligible case increased the calculated local or peak pressure in this simplified model. This makes uniformly softer foam a useful control for future comparison with the patch designs. The model still has four detachment cases, and 3,260 cases fall outside the chosen compression range. It is not a final material choice or proof of less pain.')
 para(d,'The added numerical control gives exactly the same active area pressures when we replace the whole pad modulus with its softer value directly. The force totals agree to numerical rounding. These check the arithmetic, not the behaviour of a real foam, cover or Sony headset.')
 para(d,'The earlier 100 mm strip is not this whole pad control. That strip changes the arm facing half of the annulus. The new control changes both halves. Pad shape and mounting CAD are unchanged. No sound leakage, noise reduction, heat, durability or sensory acceptance result is added.')
 new_page(d,'V22 Computer test status and next inputs')
 table(d,['Area','What this means now'],[
 ['Six size CAD and folding','Finite geometry checks and smaller carrying poses are saved. Continuous motion, finger access and loaded clearances are not qualified.'],
 ['Headband and hinge calculations','Idealized calculations are recorded. Reliable whole part peak stress and complete fastener behaviour are not established.'],
 ['Glasses cushion','126,360 assumed position cases and numerical controls are recorded. Soft zones can shift pressure elsewhere. No final foam or zone winner.'],
 ['Materials and wear contact','Need named grades, measured or supplier compression curves, cover tension and friction, seam details and head geometry. Generic material names do not supply these.'],
 ['Sound and heat','Need seal geometry, pad acoustic properties, permeability and assembled thermal inputs. Earlier proxy models are not current product performance.'],
 ['Sony attachment','Need a dimensioned mounting skirt and groove. Published outer pad size and fitting instructions do not provide them.'],
 ['Durability and manufacturing','Need final joint and material details, process tolerances and acceptance criteria before meaningful drop, fatigue, creep or cleaning models.'],
 ['Comfort and sensory acceptance','Requires voluntary feedback from intended users. No computer model proves that a person will feel comfortable or safe.']],[1.65,5.25])
 para(d,'This review finishes the listed V22 calculations and records the failures. It does not finish all possible software testing or release either product for production. Some remaining work is a model or design decision; other work needs real material and mounting inputs before the software can represent the intended product.')
 para(d,'Both documents use the same update. SoftSpace keeps V19 part geometry with V21 carrying poses. SoftSpace Flex keeps its three V20 reference bodies. There is no new physical test, success probability, sound rating, market price check or proof of benefit for autistic users in this update.')
