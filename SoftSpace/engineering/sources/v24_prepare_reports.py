from pathlib import Path
P=Path(__file__).resolve().parent
s=(P/'v23_update_reports.py').read_text(encoding='utf-8-sig').replace('V23','V24').replace('v23','v24')
s=s.replace('V22_before_V24','V23_before_V24')
s=s.replace("p.text.startswith('V24 Corrected hinge')","p.text.startswith('V24 Finer child')")
s=s.replace("design_status='V24 Corrected hinge checks across two size families'","design_status='V24 Finer child and adult joint calculations'")
current='Current update on 24 October 2026: V24 adds four finer joint reference calculations. All numerical consistency checks pass, but only 2 of 16 refined stress comparisons meet the chosen limit. Reliable whole part strength is still unproved. The main CAD readers now work with verified D drive sources, and four exact historical CAD versions were restored. Both products still have open design and input gates. Read the final V24 chapters.'
lines=s.splitlines()
for i,line in enumerate(lines):
 if line.startswith('current='):lines[i]='current='+repr(current)
s='\n'.join(lines)+'\n';(P/'v24_update_reports.py').write_text(s,encoding='utf8',newline='\n')
# New render metadata is separate from earlier review records.
D=P/'documents';s=(D/'check_native_word_layout_v23.py').read_text().replace('native_v23_','native_v24_');(D/'check_native_word_layout_v24.py').write_text(s,encoding='utf8',newline='\n')
s=(D/'verify_documents.py').read_text().replace("layout=O/'qa/native_v23_layout_checks.json'","layout=O/'qa/native_v24_layout_checks.json'");(D/'verify_documents.py').write_text(s,encoding='utf8',newline='\n')
