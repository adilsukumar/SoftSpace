from pathlib import Path
P=Path(__file__).parent;f=P/'documents/build_documents.py';s=f.read_text()
for flag in ['False','True']:
 needle=' add_completion(d,P,new_page,para,table,picture,'+flag+')';assert needle in s
 s=s.replace(needle,needle+'\n from v18_final_screen_section import add_final_screen\n add_final_screen(d,P,new_page,para,table,picture,'+flag+')')
s=s.replace('Six sizes, 18 saved poses, band, stop and fork component checks, and static torque comparisons. Real materials, assembly, comfort, acoustics and Sony fit remain open.','Six sizes and component checks retained. Added final material, pivot clearance, CAD stack and handling load screens. Retention risk and missing physical inputs are recorded.')
f.write_text(s)
