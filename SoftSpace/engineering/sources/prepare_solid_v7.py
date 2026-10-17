from pathlib import Path
p=Path(__file__).parent;s=(p/'solid_band_3d.py').read_text().replace('engineering-v6-results','engineering-v7-results').replace('OwnPassiveDefender_V6_','OwnPassiveDefender_V7_')
(p/'solid_band_v7.py').write_text(s);compile(s,'solid_band_v7.py','exec')
