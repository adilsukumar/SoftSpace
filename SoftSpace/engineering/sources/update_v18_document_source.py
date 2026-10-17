from pathlib import Path
P=Path(__file__).parent;f=P/'documents/build_documents.py';s=f.read_text()
s=s.replace("STAMP='15 October 2026'", "STAMP='16 October 2026'")
needle="if (P/'engineering-v17-results'/'test_register.json').exists():REV='V17 two size entry pilots with V16 six size candidates and V10 native archives'"
s=s.replace(needle,needle+"\nif (P/'engineering-v18-results'/'test_register.json').exists():REV='V18 six size passive hinge candidates with V10 native archives'")
needle="  if (P/'engineering-v17-results'/'test_register.json').exists():rows+=[[STAMP,'V17 two size entry pilots','Larger index holes and entry cones tested on child large and adult small. V16 remains the six size candidate.']]"
s=s.replace(needle,needle+"\n  if (P/'engineering-v18-results'/'test_register.json').exists():rows+=[[STAMP,'V18 passive hinge and wearing stop','Six sizes,18 saved poses,conditional mechanics and static torque comparisons. Real materials,assembly,comfort,acoustics and Sony fit remain open.']]")
s=s.replace(" if (I/'V16_hero.png').exists():picture", " if (I/'V18_hero.png').exists():picture(d,'V18_hero','V18 passive hinge child large and adult small local STEP candidates. Physical validation remains open.',5.7)\n elif (I/'V16_hero.png').exists():picture")
needle=" if (P/'engineering-v17-results'/'test_register.json').exists():\n  para(d,'V16 remains the latest six size local CAD candidate."
replacement=" if (P/'engineering-v18-results'/'test_register.json').exists():\n  para(d,'V18 is our latest six size local STEP candidate. A passive friction hinge and separate wearing stop replace the loaded sliding pin. Sampled geometry and conditional numerical checks are recorded in the new chapters. Actual torque calibration,complete joint strength,comfort,sound reduction and durability remain unvalidated. Native editable Fusion archives remain V10. No manufacturing release is claimed.')\n elif (P/'engineering-v17-results'/'test_register.json').exists():\n  para(d,'V16 remains the latest six size local CAD candidate."
assert needle in s;s=s.replace(needle,replacement)
for flag in ['False','True']:
 needle=" add_v17(d,P,new_page,para,table,picture,"+flag+",link)"
 assert needle in s;s=s.replace(needle,needle+"\n from v18_study_section import add_v18\n add_v18(d,P,new_page,para,table,picture,link,"+flag+")")
needle=" label(d,'Current conclusion','The idea is worth investigating. We have not proved less pain, unchanged music, no sound leakage or universal compatibility. The pad needs tests on each supported headphone model.')"
assert needle in s;s=s.replace(needle,needle+"\n if (P/'engineering-v18-results'/'test_register.json').exists():para(d,'The shared standalone design is now V18,using a passive folding hinge and wearing stop. The Sony WH CH720N replacement cushion is unchanged and still needs the original mounting measurements. The new hinge checks do not prove a pad benefit. The final chapters explain the shared update.')")
f.write_text(s)
