from pathlib import Path
P=Path(__file__).parent
f=P/'documents'/'build_documents.py';s=f.read_text(encoding='utf-8')
s=s.replace("This is one size, not a worn-assembly validation or an isolated symmetry comparison. The 54-case screen still uses the quarter model.","This adult-small result is part of the size study below. It is not a worn-assembly validation or an isolated symmetry comparison. The quarter-force screen is retained separately.")
s=s.replace("The earlier adult-medium comparison changed by 8.37%; its finer result is recorded in the table.","Earlier adult-medium comparisons changed by 8.37% and 18%; the final 0.9 to 0.8 mm comparison is recorded in the table.")
needle="   if FULLFORCE10:\n"
addition="   if (P/'engineering-v10-results'/'child_medium_full_width_prior_memory_failure.json').exists():para(d,'The first child-medium 1.5 mm run also ran out of memory while extracting the constrained matrix. Direct assembly of that matrix and its reaction rows matched the original solver on the same verification beam; the product retry is recorded in the size table when completed. Resource failures remain in the project history.')\n"
if addition not in s:s=s.replace(needle,addition+needle,1)
needle="  para(d,'The standalone 54-case force screen uses assumed materials"
addition="  if FULLSIZES10:para(d,'The actual-width standalone fixture study has completed '+str(len(FULLSIZES10['cases']))+' of six sizes. Its recorded guide-compliance comparisons '+('pass' if FULLSIZES10['all_compliance_comparisons_pass'] else 'do not all pass')+' our chosen 5% limit. These checks still omit scalp, clamp and joint contact. The child-medium first refinement ran out of memory; the numerical method was verified before retrying. This does not test the Sony replacement pad.')\n  if FULLFORCE10:para(d,'An additional '+str(FULLFORCE10['case_count'])+'-case reduced force screen uses the actual-width standalone fixture. The old quarter-fixture screen remains separately recorded. Neither supplies a measured Sony host force or a cushion pressure result.')\n"
if addition not in s:s=s.replace(needle,addition+needle,1)
compile(s,str(f),'exec');f.write_text(s,encoding='utf-8')
q=P/'documents'/'check_document_layout.py';s=q.read_text(encoding='utf-8').replace('unavailable: LibreOffice missing; Word app approval timed out','unverified: bundled LibreOffice missing; Word control returned unavailable controls and activation failure');q.write_text(s,encoding='utf-8')
print('Both report templates now use the recorded completed size count and retain memory failures.')
