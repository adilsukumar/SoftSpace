from pathlib import Path
P=Path(__file__).parent;f=P/'documents'/'build_documents.py';s=f.read_text(encoding='utf-8')
def replace(a,b):
 global s
 if a not in s:raise RuntimeError('Expected builder text missing: '+a[:100])
 s=s.replace(a,b,1)
replace("('JBL Tune 770NC manufacturer specifications','https://www.jbl.com/TUNE770NC.html?dwvar_TUNE770NC_color=White-AM-Current&locale=en_US')]", "('JBL Tune 770NC manufacturer specifications','https://www.jbl.com/TUNE770NC.html?dwvar_TUNE770NC_color=White-AM-Current&locale=en_US'),\n ('Sony WH CH720N pad replacement instructions','https://www.sony.co.uk/electronics/support/wireless-headphones-bluetooth-headphones/articles/00295193')]")
replace("if POSE9 and not POSE9['all_pass']:", "NATIVE10=None;NATIVEPOSE10=None;FULLWIDTH10=None\nfor filename,var in [('cad_native_report.json','NATIVE10'),('native_all_pose_pairs.json','NATIVEPOSE10'),('adult_small_full_width_summary.json','FULLWIDTH10')]:\n if (P/'engineering-v10-results'/filename).exists():globals()[var]=json.loads((P/'engineering-v10-results'/filename).read_text())\nNATIVE10DONE=bool(NATIVE10 and NATIVE10['status']=='complete')\nif POSE9 and not POSE9['all_pass']:")
replace("REV='V10 STEP candidates with open native and stress checks'", "REV='V10 native candidates with open structural and physical checks' if NATIVE10DONE else 'V10 STEP candidates with open native and stress checks'")
replace("'Actual adult-small V10 local STEP candidate. This is not yet a native Fusion archive.',", "('Actual adult-small V10 native Fusion STEP export.' if NATIVE10DONE else 'Actual adult-small V10 local STEP candidate. This is not yet a native Fusion archive.'),")
replace("'Six sizes and their nominal and endpoint poses were exported as local STEP candidates. The wider all-body overlap audit covers every pair of solids. Changed guide geometry receives fresh structural calculations.',", "('Native Fusion exported all six sizes, 18 STEP poses and six Fusion archives. The local and native bands agree within the 0.01 cubic mm volume comparison tolerance. ' if NATIVE10DONE else 'Six sizes and their nominal and endpoint poses were exported as local STEP candidates. ')+'The wider all-body overlap audit covers every pair of solids. Changed guide geometry receives fresh structural calculations.',")
replace("Native Fusion rebuilding, locking, measured materials and physical product validation remain open.", "Locking, measured materials and physical product validation remain open.")
replace("'V10 adult small STEP-only candidate. Native Fusion rebuilding and physical validation remain open.' if V10", "('V10 adult small native Fusion STEP export. Physical validation remains open.' if NATIVE10DONE else 'V10 adult small STEP-only candidate. Native rebuilding remains open.') if V10")
replace("This document explains the user need, selected market options, every development stage and what our tests actually mean. Read it alongside Glasses Friendly Headphone Cushions for the replacement-pad project.", "This document explains the user need, selected market options, every development stage and what our tests actually mean. Read it alongside Glasses Friendly Headphone Cushions for the replacement-pad project. That separate route now targets the Sony WH-CH720N, chosen by the user. Sony confirms replaceable pads, but mounting measurements and host-specific results are still missing. [17]")
replace('smaller validated meshes','meshes that passed numerical checks')
needle=" new_page(d,'Current results in plain English')"
replace(needle,"""   if NATIVE10DONE:
    para(d,'Native V10 rebuilding is complete. '+('All 18 native STEP poses independently passed the all-body intersection check and contain 28 solids each.' if NATIVEPOSE10 and NATIVEPOSE10['all_pass'] else 'The independent native STEP audit is still running or has unresolved results.')+' Source hashes remain recorded. Geometry agreement does not remove the quarter-width modelling limitation. Fusion archives were exported; reopening them is a separate check.')
   if FULLWIDTH10:
    r=FULLWIDTH10['meshes'][-1]
    para(d,'A separate adult-small calculation keeps the actual full front-to-rear width and its single front clamp bore. Guide compliance is '+format(r['compliance_mm_per_N'],'.3f')+' mm per N; two meshes differ by '+format(100*FULLWIDTH10['compliance_relative_mesh_change'],'.2f')+'%. It uses an ideal crown fixture and uniform surface load, different from the quarter model. This is one size, not a worn-assembly validation or an isolated symmetry comparison. The earlier 54-case force screen has not been replaced by this result.')
"""+needle)
needle=" new_page(d,'India and existing glasses comfort products')"
if needle not in s:
 # Insert before the next explicit page after the introductory host explanation.
 start=s.index(" para(d,'For replacement pads we do not design the host headband.")
 end=s.index('\n',start)
 s=s[:end]+"""
 new_page(d,'First target Sony WH CH720N')
 para(d,'We selected Sony WH-CH720N. Sony explains that its pad edge fits into a housing groove, with top and bottom slots and arrows aligned. This confirms replaceable pads; the instructions give no manufacturing dimensions for our replacement. [17]')
 para(d,'Sony specifies an over-ear closed headphone, approximately 192 g, with 30 mm drivers and noise cancellation. [9] Our pad must preserve the mounting edge and avoid vents, microphones and driver clearance. The generic pad CAD is not yet compatible with this model.')
 table(d,['What to measure','Why it matters','Current value'],[
 ['Outer pad size, ear opening and depth','Ear space, contact area and cup distance','Not measured'],
 ['Housing groove and pad skirt contour, depth and thickness','Fit and retention without an open leak path','Not measured'],
 ['Top and bottom alignment slots','Correct seating and orientation','Not measured'],
 ['Driver, vent and microphone clearance','Sound response and ANC behaviour','Not measured'],
 ['Host force at worn widths and cup angle','Compression and pressure on glasses','Not measured'],
 ['Glasses arm shape and worn contact path','Softer zone position and width','Not measured']], [2.55,2.9,1.45])
 para(d,'Keep a continuous cover over the softer foam zone. This is a design hypothesis, not proof of zero leakage. Compare the original pad, new uniform pad and new soft-zone pad on this same headphone. Check seating, pressure, incoming noise with ANC off and on, outgoing music and frequency response. All host-specific results are still untested.')
"""+s[end:]
else:raise RuntimeError('Unexpected page anchor; review insertion')
replace("'No new replacement-pad or measured leakage evidence']], [0.7,3.65,2.55])", "'No new replacement-pad or measured leakage evidence'],['V10','Standalone guide clearances corrected; Sony WH-CH720N selected for pad route','Generic pad unchanged; host measurements and leakage results missing']], [0.7,3.65,2.55])")
replace("sources(d,[5,8,10,11,12,13])", "sources(d,[5,8,9,10,11,12,13,17])")
replace("Start with one adult headphone model whose pads can be replaced.", "Start with the selected Sony WH-CH720N, whose pads can be replaced. Measure its original mount before changing the carrier or skirt.")
replace("  if V10:para(d,'The standalone band force screen", "  if NATIVE10DONE:para(d,'Native V10 standalone CAD now has six Fusion archives and 18 STEP poses. This does not change the generic replacement pad. Sony WH-CH720N is the selected host, but the mount dimensions and host-specific pressure and acoustic tests remain open.')\n  if FULLWIDTH10:para(d,'A separate adult-small full-width band fixture calculation is recorded in the companion report. It does not supply the clamping force or acoustic response of the Sony headphone.')\n  if V10:para(d,'The standalone band force screen")
compile(s,str(f),'exec');f.write_text(s,encoding='utf-8');print('Builder updated for native V10 and Sony host')
