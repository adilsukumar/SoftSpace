from pathlib import Path
import json
f=Path(__file__).parent/'documents'/'build_documents.py';s=f.read_text(encoding='utf-8');bad={"\u00e2\u20ac\u2122":"\u2019","\u00e2\u20ac\u201c":"\u2013","\u00e2\u20ac\u201d":"\u2014","\u00c2\u00b1":"\u00b1"};count=0
bad["\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u201e\u00a2"]="\u2019"
for a,b in bad.items():count+=s.count(a);s=s.replace(a,b)
compile(s,str(f),'exec');f.write_text(s,encoding='utf-8');print(json.dumps({'repaired_sequences':count,'remaining_nonASCII_lines':[line for line in s.splitlines() if any(ord(c)>127 for c in line)]},ensure_ascii=True))
