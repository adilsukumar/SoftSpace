from pathlib import Path
f=Path(__file__).parent/'build_documents.py';s=f.read_text(encoding='utf-8')
begin=s.index(" if V10:\n  new_page(d,'Latest shared CAD and simulation results')",s.index('def glasses_doc():'))
end=s.index(" new_page(d,'Sources and project records')",begin)
block=""" if V10:
  new_page(d,'Latest shared CAD and simulation results')
  para(d,'V10 corrects the guide and knob clashes found in the standalone V9 shortest setting. All 18 native V10 STEP poses passed the all-body overlap audit. Six saved Fusion archives reopened with 28 solids in each V10 component. This is geometry evidence; it does not test glasses comfort or sealing.')
  if IDENTITY10 and IDENTITY10['all_match']:para(d,'The '+str(IDENTITY10['unique_CAD_files'])+' current native and local standalone CAD files also match the hashes recorded in their checks. This ties those results to the saved files.')
  para(d,'The quarter-band displacement comparisons pass in all six sizes. '+stress10+' That ideal model mirrors a front clamp bore onto the rear wall. It is not the complete worn assembly.')
  if FULLSIZES10:
   n_actual=len(FULLSIZES10['cases']);n_stress=sum(abs(c['meshes'][-1]['max_von_mises_centroid_MPa']/c['meshes'][-2]['max_von_mises_centroid_MPa']-1)<.05 for c in FULLSIZES10['cases'])
   para(d,'The separate actual-width fixture study covers '+str(n_actual)+' of six sizes. Its recorded guide-compliance comparisons '+('all pass' if FULLSIZES10['all_compliance_comparisons_pass'] else 'do not all pass')+' our chosen 5% limit. Sampled peak-stress comparisons pass in '+str(n_stress)+' of those sizes. Earlier coarse-to-fine peak changes above 5% and memory failures remain in the history. Read the main report for the current refinements. These ideal fixtures still omit real scalp, joint and clamp contact.')
  extra=(' An additional '+str(FULLFORCE10['case_count'])+'-case screen uses the actual-width fixture.' if FULLFORCE10 else '')
  material=(' A conditional material-strength screen uses predicted forces and illustrative margins; it has no measured strength or durability pass.' if STRENGTH10 else '')
  para(d,'The standalone quarter-fixture force screen has 54 cases.'+extra+' Both routes use assumed materials and synthetic heads.'+material+' These calculations do not measure the Sony headband force or prove a replacement pad reduces pressure, incoming noise or outgoing music.')
  para(d,'The generic V8 replacement pad is unchanged and is not claimed to fit Sony WH-CH720N. The user owns that headphone and will measure its mount later. Host fit, retention, incoming noise, outgoing playback, frequency response, ANC behaviour and wearer comfort remain untested. Both reports will be updated when those dimensions or results arrive.')
"""
s=s[:begin]+block+s[end:];compile(s,str(f),'exec');f.write_text(s,encoding='utf-8');print('Shared update shortened while retaining every evidence limit and current comparison count.')
