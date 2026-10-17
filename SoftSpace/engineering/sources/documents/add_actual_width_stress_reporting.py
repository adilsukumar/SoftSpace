from pathlib import Path
f=Path(__file__).parent/'build_documents.py';s=f.read_text(encoding='utf-8')
old="    table(d,['Actual width size','Final mesh mm','Guide compliance mm per N','Mesh change'],[[c['size'].replace('_',' '),str(c['meshes'][-1]['mesh_max_mm']),format(c['meshes'][-1]['compliance_mm_per_N'],'.3f'),format(100*c['compliance_relative_mesh_change'],'.3f')+'%'] for c in FULLSIZES10['cases']],[1.8,1.3,2.4,1.4])"
new="""    actual_stress_changes=[abs(c['meshes'][-1]['max_von_mises_centroid_MPa']/c['meshes'][-2]['max_von_mises_centroid_MPa']-1) for c in FULLSIZES10['cases']]
    actual_stress_passes=sum(v<.05 for v in actual_stress_changes)
    table(d,['Actual width size','Final mesh mm','Guide compliance mm per N','Compliance change','Sampled stress change'],[[c['size'].replace('_',' '),str(c['meshes'][-1]['mesh_max_mm']),format(c['meshes'][-1]['compliance_mm_per_N'],'.3f'),format(100*c['compliance_relative_mesh_change'],'.3f')+'%',format(100*v,'.2f')+'% / '+('Pass' if v<.05 else 'Open')] for c,v in zip(FULLSIZES10['cases'],actual_stress_changes)],[1.45,1.05,1.85,1.15,1.4])
    para(d,'The sampled peak-stress comparison meets our chosen 5% limit in '+str(actual_stress_passes)+' of '+str(len(actual_stress_changes))+' recorded actual-width sizes. Other peak comparisons remain open until separately refined. Stable guide displacement alone does not establish stable peak stress. Even a final peak comparison pass is not an absolute error bound or physical strength result.')"""
if old in s:s=s.replace(old,new)
elif 'actual_stress_changes=' not in s:raise RuntimeError('Expected table not found')
needle="  if FULLFORCE10:para(d,'An additional '"
addition="  if FULLSIZES10:para(d,'Peak stress is checked separately from guide compliance in the actual-width study. Earlier coarse-to-fine peak changes exceeded 5% in several sizes, so displacement passes alone are not structural strength passes. Read the main report for the current peak refinements and conditional material limits.')\n"
if addition not in s:s=s.replace(needle,addition+needle,1)
compile(s,str(f),'exec');f.write_text(s,encoding='utf-8')
print('Actual-width stress and displacement are reported separately in both documents.')
