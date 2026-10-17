import json

def add_inward(d,P,new_page,para,table):
 O=P/'engineering-v19-results/quadratic-inward'
 if not (O/'verification.json').exists():return
 s=json.loads((O/'status.json').read_text());v=json.loads((O/'verification.json').read_text())
 new_page(d,'V19 Inward joint load comparison')
 para(d,'We extended the higher order joint calculation to a 2 N inward load. The four cases reuse exactly the saved child large and adult small meshes from the outward study. The assumed PA66 elastic reference, ideal pivot, 140 N prescribed preload and friction coefficient 0.2 are unchanged. The CAD geometry is unchanged. These are separate static equilibrium cases, not a load reversal sequence or a cycling test.')
 rows=[]
 for item in s['cases']:
  r=json.loads(__import__('pathlib').Path(item['file']).read_text())
  rows.append([r['size'].replace('_',' '),str(r['mesh_max_mm']),f"{r['cup_mean_displacement_x_mm']:.4f}" if r.get('converged') else 'Unsolved',f"{r['stop_reaction_N']:.3f}" if r.get('converged') else 'Unsolved',str(r.get('iterations','No convergence'))])
 table(d,['Family','Mesh mm','Mean X motion mm','Stop force N','Iterations'],rows,[1.8,1.0,1.6,1.2,1.3])
 for item in s['cases']:
  if item['change_percent'] is not None:para(d,item['size'].replace('_',' ').capitalize()+' displacement changed by '+f"{item['change_percent']:.2f}"+' percent between these meshes. This '+('passes' if item['gate'] else 'fails')+' the chosen 5 percent comparison.')
 failed=sum(not r.get('converged') for r in s['cases'])
 para(d,str(len(s['cases'])-failed)+' cases converged and '+str(failed)+' did not. Saved-array reassembly, source hashes, CAD volume and force-balance checks passed for '+str(len(v['array_audits']))+' accepted solves. Negative X motion describes direction; it is not evidence of a comfort benefit.')
 para(d,'The new inward cases extend the numerical record. They do not establish convergence of local stress or qualify the bolt, bearing, friction across different materials, long-term retention or the full worn headset. The spring torque target remains uncalibrated. This does not prove the proposed hinge stays closed during a drop or bag transport.')
 para(d,'The Sony WH CH720N replacement cushion is unchanged. No model-specific fit, pressure, sound isolation, playback leakage or ANC pass is added. Real pad and mounting measurements, material curves and fixture measurements remain the next inputs for both product routes.')
