from pathlib import Path
f=Path(__file__).parent/'documents'/'build_documents.py';s=f.read_text(encoding='utf-8');a='sources(d,[5,8,9,10,11,12,13,17])';b='sources(d,[5,8,9,10,11,12,13,17,18,19])';assert s.count(a)==1;s=s.replace(a,b)
a=" para(d,'This document explains the user need, selected market options, every development stage and what our tests actually mean. Read it alongside Glasses Friendly Headphone Cushions for the replacement-pad project. That separate route now targets the Sony WH-CH720N, chosen by the user. Sony confirms replaceable pads, but mounting measurements and host-specific results are still missing. [17]')"
assert a in s
s=s.replace(a,a+"\n para(d,'Competing WH-CH720N replacement pads are already listed by Crysendo and Geekria. The companion report records current and older indexed price evidence separately. Our softer glasses zone still needs a measured advantage; it is not enough to offer memory foam or claim local availability. [18, 19]')")
compile(s,str(f),'exec');f.write_text(s,encoding='utf-8')
