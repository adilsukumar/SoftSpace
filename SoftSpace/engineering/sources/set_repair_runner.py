from pathlib import Path
p=Path(__file__).parent/'CushionNext'/'CushionNext.py'
s=p.read_text(encoding='utf-8-sig').replace('EngineeringV6.py','RepairV6Exports.py')
p.write_text(s)
