from pathlib import Path
f=Path(__file__).parent/'build_documents.py';s=f.read_text(encoding='utf-8')
s=s.replace('V8 Lower crown and the current main design','V8 Lower crown foundation')
s=s.replace('This is the main design in the current package.','This lower-crown design is the foundation for the later V9 and V10 revisions.')
s=s.replace('Adult CAD mass is estimated at about 166 to 250 g','The earlier V8 CAD mass was estimated at about 166 to 250 g for adults')
compile(s,str(f),'exec');f.write_text(s,encoding='utf-8')
print('Historical V8 labels clarified.')
