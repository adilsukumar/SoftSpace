"""Canonical fork/tongue geometry comparison for the two fixture families.
Does not transfer whole-headset loads or real-world safety across sizes.
"""
import json,hashlib
from audit_v14_motion import P,load,moved,mass,common,recipes
O=P/'engineering-v21-results';records=[]
for family,sizes in [('adult',['adult_small','adult_medium','adult_large']),('child',['child_large','child_medium','child_small'])]:
 reference=None
 for size in sizes:
  row=json.loads((P/'engineering-v19-results'/f'{size}_cad_report.json').read_text());parts,_=load(row);R=recipes[size]['band_halfspan_mm'];normalized={name:moved(parts['Left'+name],(R,0,-row['pivot_z_mm'])) for name in ['Fork','Tongue']}
  if reference is None:reference=normalized
  diffs=[]
  for name,shape in normalized.items():
   a=mass(shape);b=mass(reference[name]);intersection=common(shape,reference[name]);delta=max(0,a+b-2*intersection);assert abs(common(shape,shape)-a)<.01
   diffs.append(dict(part=name,volume_mm3=a,symmetric_difference_mm3=delta,chosen_001_mm3_pass=delta<.01))
  records.append(dict(size=size,family=family,source_sha256=row['sha256'],parts=diffs,pivot_z_mm=row['pivot_z_mm'],guide_bottom_mm=row['guide_bottom_mm']))
assert all(x['chosen_001_mm3_pass'] for r in records for x in r['parts'])
(O/'joint_family_geometry.json').write_text(json.dumps(dict(date='2026-10-23',all_selected_parts_equivalent=True,cases=records,scope='Whole left fork and tongue solids from V19 ParallelDisc CAD match within each family after translation to a pivot origin. This supports two representative isolated fixture geometries only. Actual per-size headband force, worn loading, all other components, materials and assembled joint performance remain distinct or unverified.'),indent=2));print('Twelve normalized part comparisons passed')
