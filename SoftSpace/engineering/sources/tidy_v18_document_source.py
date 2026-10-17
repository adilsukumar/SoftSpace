from pathlib import Path
p=Path(__file__).parent/'documents/build_documents.py';s=p.read_text()
for revision in ['V10 actual width','V12','V14','V15','V16','V17']:
 s=s.replace("[[STAMP,'"+revision,"[['15 October 2026','"+revision)
s=s.replace('V18,using','V18, using').replace('calibration,complete joint strength,comfort,sound reduction','calibration, complete joint strength, comfort, sound reduction').replace('Six sizes,18 saved poses,conditional mechanics','Six sizes, 18 saved poses, conditional mechanics').replace('Real materials,assembly,comfort,acoustics','Real materials, assembly, comfort, acoustics')
p.write_text(s)
