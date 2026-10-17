from pathlib import Path
f=Path(__file__).parent/'build_documents.py';s=f.read_text(encoding='utf-8')
old="+' recorded actual-width sizes. Other peak comparisons remain open until separately refined. Stable guide displacement alone does not establish stable peak stress."
new="+' recorded actual-width sizes. '+('Some peak comparisons remain open until separately refined. ' if actual_stress_passes<len(actual_stress_changes) else 'Earlier larger peak changes remain in history. ')+'Stable guide displacement alone does not establish stable peak stress."
assert old in s;s=s.replace(old,new)
s=s.replace("new_page(d,'V10 actual width and material screening')","new_page(d,'V10 actual width band results')")
s=s.replace('the product retry is recorded in the size table when completed. Resource failures remain in the project history.','the table records the completed runs and later refinements. Resource failures remain in the project history.')
s=s.replace("' Both routes use assumed materials and synthetic heads.'","' The force screens use assumed materials and synthetic heads.'")
compile(s,str(f),'exec');f.write_text(s,encoding='utf-8');print('Final wording now follows the actual pass count.')
