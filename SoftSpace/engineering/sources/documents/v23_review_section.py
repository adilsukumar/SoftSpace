"""Shared corrected-reference results for both living reports."""
import json

def add_v23(d,P,new_page,para,table,picture):
 O=P/'engineering-v23-results'
 if not (O/'review_status.json').exists():return
 r=json.loads((O/'review_status.json').read_text())
 new_page(d,'V23 Corrected hinge checks across two size families')
 para(d,'24 October 2026. The new campaign runs the corrected virtual spacer model on both the child large and adult small isolated joints. Each uses two mesh sizes and two load directions, giving eight new equilibrium calculations. The previous V22 local adult fields stay separate and unchanged. No CAD, material or actual fastener design is changed.')
 table(d,['Joint family','Mesh mm','Direction','Relative force error'],[[x['size'].replace('_',' '),str(x['mesh_size_mm']),x['direction'],format(x['independent_residual'],'.2e')] for x in r['cases']],[2.1,1.0,1.5,2.3])
 para(d,'All eight new calculations passed the chosen equilibrium, independent residual, net force, net moment, friction bound and contact derivative checks. Twenty four distinct common rigid motions also passed across the four meshes. These checks tell us that the defined mathematical model behaves consistently. They do not establish that an actual hinge will have the same behaviour.')
 para(d,'The fixed assumptions are stiffness 3500 MPa, Poisson ratio 0.35, preload 140 N, friction coefficient 0.2 and side force plus or minus 2 N. The virtual spacer is 0.5 mm. Actual washer contact, threads, production tolerances, material history and complete headset loads are still missing from this reference model.')
 new_page(d,'V23 What the stronger stress check shows')
 picture(d,'V23_corrected_mesh','Same corrected reference equations and the same stress sampling methods on both meshes. The dashed line is our chosen comparison limit, not a safety standard.',6.55)
 para(d,str(r['mesh_comparison_passes'])+' of 24 stress comparisons meet the fixed 5 percent check. Sixteen compare 2.3 mm and 1.9 mm meshes across the two joint families. Eight compare the adult 1.9 mm fields with the previously solved local 0.9 mm fields. Both the 125 interior samples and the 35 samples including element boundaries are retained.')
 para(d,'A stress comparison that exceeds the limit stays a failed comparison. We have not used average stress, a different allowable stress or a different sampling method to hide it. Even a passing pair does not prove that the largest stress anywhere in a part is known. Whole part strength and break resistance remain unproved. The next useful design work is to define the real edge, spacer and fastener details and repeat the relevant models.')
 para(d,'The new raw fields, source hashes, solver histories, numerical controls and every comparison are saved in engineering v23 results. The older raw fields are preserved. This is a completed numerical campaign with unresolved design conclusions, not a finished headphone or a physical test.')
 new_page(d,'V23 Software status and the remaining inputs')
 table(d,['Area','Current conclusion','What is needed next'],[
 ['Corrected hinge equations','Eight new solves and numerical checks completed','Detailed physical joint and reliable stress model'],
 ['Six size folding and adjustment','Earlier sampled CAD checks retained','Continuous path and pinch protection verification'],
 ['Cushion and glasses pressure','Reduced assumed models compared','Foam curves cover friction and worn head geometry'],
 ['Sony mounting','Envelope only exact fit unproved','Skirt groove carrier dimensions and tolerances'],
 ['Sound leakage and noise reduction','No predictive product pass','Seal geometry and acoustic material data'],
 ['Heat moisture and durability','No validated product pass','Traceable material and process properties'],
 ['Comfort and sensory acceptance','No wearer result','Voluntary wearer testing']],[2.0,2.5,2.4])
 para(d,'Both projects remain in development. The glasses cushion geometry is unchanged in this update; shared hinge results do not prove Sony fit or cushion benefit. Earlier local and whole pad softness screens remain useful comparisons, with their failed and out of range cases retained. There is no demonstrated improvement in comfort, sound leakage, ANC or heat.')
 para(d,'We have finished the eight case corrected reference campaign and its numerical checks. We cannot call all product software testing complete. Missing material and interface inputs must be supplied before realistic full product simulations can be completed. Inventing those values would give misleading confidence. The remaining test register separates those input gaps from completed checks and from tests that require people.')
