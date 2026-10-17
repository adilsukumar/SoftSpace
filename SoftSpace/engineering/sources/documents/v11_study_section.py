import json

def add_v11(d,P,new_page,para,table,picture,link,is_glasses):
 O=P/'engineering-v11-results';mp=O/'materials_screen.json'
 if not mp.exists():return
 m=json.loads(mp.read_text());s=json.loads((O/'folding_summary.json').read_text())
 new_page(d,'V11 Material and folding study')
 para(d,'We expanded the search after the request to consider ordinary and unusual materials, folding and resistance to breakage. The current native CAD is still V10. V11 records material calculations and folding poses made from those saved solids. It is not a new finished hinge assembly or a physical durability test.')
 para(d,'The register contains 70 candidate families: 32 for the band and hardware, 20 for cushioning, and 18 for covers and liners. Ten specific material references have numerical band screens. The other families are ideas awaiting grade data, not tested winners. A material family can contain many formulations with very different behaviour.')
 roles=['cushion and compliant zone','cover and liner'] if is_glasses else ['band and hardware','cushion and compliant zone','cover and liner']
 for role in roles:
  names=[r['family'] for r in m['families'] if r['role']==role]
  para(d,role.capitalize()+': '+', '.join(names)+'.')
 para(d,'The aim is to identify useful combinations, not to find an unusual material at any cost. No Indian supplier prices, production yield or novelty search has been completed. Comfortable, cheap and hard to break remain design goals.')
 if not is_glasses:
  new_page(d,'Specific band material calculations')
  table(d,['Published material reference','Modulus MPa','Yield or proof MPa'],[[r['grade'],f"{r['modulus_MPa']:.0f}",f"{r['typical_yield_MPa']:.1f}"] for r in m['numeric_grades']],[3.7,1.45,1.75])
  para(d,'The screen has 60 size and material combinations and 240 imposed-load calculations at 2, 5, 10 and 20 N per side. It rescales the existing linear band fixture; it is not 240 new nonlinear simulations. The Poisson ratio stays at the earlier assumed 0.35. The imposed loads are comparison inputs, not a product test standard.')
  para(d,'At fixed load and fixed Poisson ratio, changing only the modulus changes displacement but not the linear elastic stress field. At fixed displacement, force and stress scale with modulus. A higher coupon strength alone does not prove the finished headset will survive a fall. Large deformation, yield, creep, fatigue and joints remain outside this screen.')
  para(d,'The PP value is a published flexural modulus used only as a stiffness proxy. The 301 references use published wire data for two tempers; a selected strip still needs qualification. Other properties are manufacturer typical coupon values, not allowable stresses for our moulded or printed parts. Test method, moisture and manufacturing differences matter.')
  para(d,'Using the same 3 mm section in the referenced steel makes the ideal band 96.5 times as stiff in this linear comparison. An equal bending stiffness strip estimate gives about 0.65 mm steel thickness for a 3 mm, 2000 MPa reference strip. This is an EI estimate only. Guides, inserts, bends and hinge loads would need a new design and analysis.')
  para(d,'Two routes remain worth investigating: a thin spring core with separate polymer guides, and a tough polymer band with reinforced joints. Neither route has passed fatigue, drops or manufacturing tests. Printed plastics and fibre composites need directional property data before receiving a material model.')
  for key in ['ensinger_catalog','abs_natural','pet','peek','pc','pp','steel301']:link(d,'Material data '+key.replace('_',' '),m['sources'][key])
 new_page(d,'Cushion and cover material findings')
 # Adult projected area proxy: this is kept separate from curved pad contact.
 point_rows=[r for r in m['foam_cases'] if r['geometry_scale']==1]
 table(d,['Published foam reference','Reference point','Flat ring force N'],[[r['grade'],('CFD test point' if r['reference_compression_strain'] is None else str(round(r['reference_compression_strain']*100))+' percent compression'),f"{r['uniform_compression_force_N']:.1f}"] for r in point_rows],[3.15,2.15,1.6])
 para(d,'These 14 calculations cover adult and scaled child projected rings at individual published stress points. They do not model our curved cushion, actual contact area, cover tension or a real glasses arm. The forces in the table are what uniform compression across the entire flat ring would require at that point. They are not measured headband forces or a comfort ranking.')
 para(d,'The industrial foam examples need much more force at their reported points than our earlier few-newton band estimates. That is a warning against substituting a foam because it is called soft. The test conditions differ, and the low-load compression curves are still missing. The cited PORON sheets are also much thinner than our pad; a 20 mm layered pad is not validated by those data.')
 para(d,'A continuous breathable TPU film under a soft textile face is a useful cover experiment. Covestro describes Platilon M as wind tight, water vapour transmitting and low noise. Baltex describes spacer fabrics for airflow and cushioning. We infer that a thin film plus textile may help us study moisture and surface feel while retaining a continuous layer. Neither source proves headphone isolation, lower ear temperature or autistic acceptance.')
 para(d,'Keep flexible PU and memory foam as comparison samples. Investigate softer silicone or a TPU lattice for the local glasses region only after obtaining its compression curve. Lattice shape, rubbing noise, recovery, seam life and sealing need tests. No material is selected as a final winner yet.')
 for key in ['poron','silicone','silicone_soft','etpu','film','spacer']:link(d,'Material data '+key.replace('_',' '),m['sources'][key])
 new_page(d,'Folding results across six sizes')
 table(d,['Size','Best sampled angles','Envelope change'],[[r['size'].replace('_',' '),str(r['best_reached_sample_angles_deg'][0])+' and '+str(r['best_reached_sample_angles_deg'][1])+' degrees',f"{100*r['reduction_fraction_from_original_nominal']:.1f} percent smaller"] for r in s['sizes']],[2,2.35,2.55])
 para(d,'These poses use the existing fork pins as rotation axes. Before folding, the left side is set to 0 mm extension and the right to 30 mm. Both cups and their forks then rotate inward in sequence. The comparison is with each original nominal V10 bounding box, not with a market headset or a carrying case.')
 para(d,'The first symmetric folds, direct cup-pivot folds and some 75 or 90 degree staggered attempts collided. Those failures are saved. Two child sizes needed a shallower first rotation. A final pose is counted only when its preceding sampled sequence is also clear. Packing volume alone does not establish ease of carrying or protection in a bag.')
 fine_path=O/'fine_fold_paths.json'
 if fine_path.exists():
  fine=json.loads(fine_path.read_text())
  para(d,'The finer check covers '+str(fine['case_count'])+' poses at 5 degree intervals. '+('All recorded samples passed' if fine['all_pass'] else 'Some samples failed')+' the 0.01 cubic mm intersection threshold. '+str(len(fine['exports']))+' candidate STEP files were exported from passing size sequences. This remains sampled rigid motion; it does not prove continuous clearance or clearance under tolerances and loads.')
 para(d,'Rigid when worn and foldable for carrying require a controlled joint. The saved model still lacks a validated angular latch, rotation stops, friction specification and protection against pinching. The earlier intact-band stress results do not certify these joints. No drop, repeated folding or bag compression pass is claimed.')
 if is_glasses:para(d,'This folding study belongs to our standalone defender. It does not make the Sony WH-CH720N foldable or change its original headband. Replacement pad compatibility and sound tests still need the Sony measurements and physical samples.')
 new_page(d,'Folding CAD and the next durability checks')
 picture(d,'V11_folding_study','Actual adult medium STEP geometry before and after an exploratory fold. Views fit each shape independently. The triangles are display tessellation, not the cover texture. This is not a manufactured headset or a native Fusion hinge simulation.',6.55)
 table(d,['Goal','Required validation'],[
 ['Rigid in use','Final latch geometry, bending and torsion stiffness, joint play and release force'],
 ['Not easily broken','Material curves, stress at pins and stops, large deformation and physical overload tests'],
 ['Repeated folding','Hinge cycles, fastener loosening, cracks, wear and force drift'],
 ['Easy to carry','Continuous folding path, hand access, folded dimensions and real bag fit'],
 ['Transport survival','Defined drop orientations, packed compression, crush recovery and repeat function'],
 ['Comfort after ageing','Foam recovery, cover damage, sealing and voluntary wear feedback']],[1.6,5.3])
 para(d,'All material data in this study were checked on 14 October 2026. They supplement the market review dated 13 October. The next engineering step is to specify and model the latch and final materials, then use samples to calibrate compression, friction, fatigue and acoustic inputs. These results do not establish an unbreakable product, zero leakage or a universal sensory preference.')
 para(d,'Both living reports were updated together with the 70 family register, grade calculations, foam point screens and folding passes and failures. Primary local records are in engineering-v11-results. The Sony pad geometry and its untested compatibility status are unchanged.')
