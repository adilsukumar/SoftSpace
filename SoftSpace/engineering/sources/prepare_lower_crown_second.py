from pathlib import Path
import shutil
p=Path(__file__).parent;o=p/'engineering-v8-results';shutil.copy2(o/'lower_crown_summary.json',o/'lower_crown_initial_50_35.json')
f=p/'lower_crown_screen.py';s=f.read_text().replace("band_arch_height']=50","band_arch_height']=40").replace("band_arch_height']=35","band_arch_height']=25").replace("recipe['band_thickness_mm']/2+5","recipe['band_thickness_mm']/2+8").replace("'Force2N is a comparison target", "'Crown padding8mm is an unmeasured geometric hypothesis','Force2N is a comparison target")
f.write_text(s)
