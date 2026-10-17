"""Derive a standalone actual-surface renderer from the verified V14 renderer."""
from pathlib import Path
P=Path(__file__).parent;s=(P/'render_v14_folded.py').read_text()
replacements={
"O=P/'engineering-v14-results'":"O=P/'engineering-v15-results'",
"cad=json.loads((O/'cad_report.json').read_text())":"cad=json.loads((P/'engineering-v14-results/cad_report.json').read_text())",
"fig=plt.figure(figsize=(11,8))":"fig=plt.figure(figsize=(11,5))",
"packing={r['size']:r for r in json.loads((O/'packing_summary.json').read_text())['sizes']}":"packing={'child_large':{'angles_deg':[30,60]}}",
"enumerate(['child_medium','adult_medium'])":"enumerate(['child_large'])",
"nominal=[(tri,color) for name,tri,color in surfaces]":"nominal=[(tri+np.array([0,0,15]) if name.startswith(('Left','Right')) and not name.endswith('SliderKnob') else tri,color) for name,tri,color in surfaces]",
"15 if left else -15":"15 if left else -5",
"80 if left else 50":"80 if left else 60",
"fig.add_subplot(2,2,ri*2+ci+1)":"fig.add_subplot(1,2,ci+1)",
"' nominal' if ci==0 else ' sampled fold'":"' retracted unfolded' if ci==0 else ' new sampled fold'",
"V14 CAD and recorded folding poses":"V15 child large folding experiment on V14 parts",
"Same display scale within each row. Nominal STEP surfaces use the recorded rigid fold transforms. Triangles are not fabric texture.":"Same display scale. Actual V14 surfaces moved by checked transforms. Folded release pins are held back 6 mm.",
"V14_folded_CAD.png":"V15_child_large_fold.png",
"folded_image_sources.json":"child_large_fold_image_sources.json"
 ,"fig.subplots_adjust(0,.06,1,.90,wspace=0,hspace=.10)":"fig.subplots_adjust(0,.06,1,.83,wspace=0,hspace=.10)"
}
for a,b in replacements.items():
 assert a in s,a;s=s.replace(a,b)
(P/'render_v15_child_large.py').write_text(s)
print('Standalone V15 child-large renderer prepared')
