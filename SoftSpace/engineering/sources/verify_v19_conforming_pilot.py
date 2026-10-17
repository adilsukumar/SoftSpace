"""Reassemble every saved pilot mesh without changing its geometry or equations."""
from pathlib import Path
P=Path(__file__).parent
s=(P/'verify_v19_joint.py').read_text().split('comparisons=[]')[0]
s=s.replace("O.glob('*_joint_h*.json')","(O/'conforming-contact').glob('*_h*.json')")
s+="\n(O/'conforming-contact/verification.json').write_text(json.dumps(dict(array_audits=records,scope='Same-equation matrix and contact reassembly, affine patch and source checks for the linear conforming pilot. No physical validation.'),indent=2))\n"
exec(compile(s,str(P/'verify_v19_joint.py'),'exec'))
