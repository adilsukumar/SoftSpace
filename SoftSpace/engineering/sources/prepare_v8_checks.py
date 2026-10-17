from pathlib import Path
p=Path(__file__).parent;s=(p/'solid_band_3d.py').read_text().replace('engineering-v6-results','engineering-v8-results').replace('OwnPassiveDefender_V6_','OwnPassiveDefender_V8_').replace('g>165','g>125')
(p/'solid_band_v8.py').write_text(s)
batch=(p/'run_solid_v7.py').read_text().replace('solid_band_v7','solid_band_v8').replace('Rounded entry','Lower crown').replace('rounded entry','lower crown').replace("  if size=='child_small':rows.append(json.loads((OUT/'child_small_h1.5.json').read_text()))",'')
(p/'run_solid_v8.py').write_text(batch.replace('solid_v7_summary','solid_v8_summary'))
verify=(p/'verify_v7_exports.py').read_text().replace('cad_v7_report','cad_v8_report').replace('engineering-v7-results','engineering-v8-results')
(p/'verify_v8_exports.py').write_text(verify)
print('Prepared V8 structural/import checks')
