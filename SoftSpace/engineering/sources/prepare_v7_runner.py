from pathlib import Path
import json
p=Path(__file__).parent;f=p/'CushionNext'/'CushionNext.py';s=f.read_text(encoding='utf-8-sig').replace('InspectBandEdges.py','RefineBandV7.py');f.write_text(s)
(p/'v7-variants.json').write_text(json.dumps(['child_small']))
