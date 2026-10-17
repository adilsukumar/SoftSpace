from pathlib import Path
P=Path(__file__).parent;f=P/'documents/build_documents.py';s=f.read_text()
for flag in ['False','True']:
 needle=' add_v18(d,P,new_page,para,table,picture,link,'+flag+')';assert needle in s
 s=s.replace(needle,needle+'\n from v18_completion_section import add_completion\n add_completion(d,P,new_page,para,table,picture,'+flag+')')
s=s.replace('Six sizes, 18 saved poses, conditional mechanics and static torque comparisons. Real materials, assembly, comfort, acoustics and Sony fit remain open.','Six sizes, 18 saved poses, band, stop and fork component checks, and static torque comparisons. Real materials, assembly, comfort, acoustics and Sony fit remain open.')
s=s.replace("keywords='living project document simulation evidence V8'","keywords='living project document simulation evidence V18'")
f.write_text(s)
