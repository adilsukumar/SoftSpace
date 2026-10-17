from pathlib import Path
P=Path(__file__).parent;s=(P/'render_v16_candidates.py').read_text()
s=s.replace("O=P/'engineering-v16-results';selected=json.loads((O/'selected_candidates.json').read_text());", "O=P/'engineering-v18-results';selected={'sizes':[json.loads(f.read_text()) for f in O.glob('*_cad_report.json')]};")
start=s.index('def pose(');end=s.index('\ndef draw(',start)
s=s[:start]+'''def pose(row,R,surfaces,phase):
 result=[]
 for name,tri,color in surfaces:
  q=tri.copy()
  if name.startswith(('Left','Right')) and not name.endswith('SliderKnob') and phase!='wear':
   left=name.startswith('Left');i=0 if left else 1;shift=15 if phase=='retracted' else 15-row['fold_extension_mm'][i]
   if phase=='folded' and name.endswith(('Fork','MainFoam','SoftGlassesZone','ContinuousCover','Carrier','Cup','Liner','CupPin','CupPinCap')):
    angle=(-1 if left else 1)*row['fold_angles_deg'][i];a=math.radians(angle);C=math.cos(a);S=math.sin(a);rot=np.array([[C,0,S],[0,1,0],[-S,0,C]]);ctr=np.array([-R if left else R,0,row['pivot_z_mm']]);q=(q-ctr)@rot.T+ctr
   q[:,:,2]+=shift
  result.append((q,color))
 return result
''' +s[end:]
s=s.replace("'LockPin' in name", "'HingeBolt' in name or 'HingeNut' in name").replace("'KnobCrossRivet' in name", "'FrictionWasher' in name")
s=s.replace('V16','V18').replace(' selected local CAD candidates',' passive hinge and wearing stop').replace(' folded pins engaged',' folded').replace('checked folding poses with pins returned','sampled folding poses').replace('spring return force and holding strength remain unvalidated','friction torque and holding strength remain unvalidated').replace('folded pins at zero release stroke','folded friction hinge without a release pin')
(P/'render_v18_candidates.py').write_text(s)
