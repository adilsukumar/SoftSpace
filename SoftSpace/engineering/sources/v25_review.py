"""Review a quadratic surface pilot without promoting a product pass."""
from pathlib import Path
import json,csv,hashlib,sys,os
P=Path(__file__).resolve().parent;O=P/'engineering-v25-results';sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np

def read(folder,h):
 f=folder/f'child_large_h{h}_outward.json';r=json.loads(f.read_text());assert r['converged'] and hashlib.sha256(f.with_suffix('.npz').read_bytes()).hexdigest()==r['raw_sha256']
 r['numerical_controls_pass']=r['independent_residual']<1e-7 and r['force_balance_N']<1e-6 and r['moment_balance_Nmm']<1e-5 and r['coulomb_excess_MPa']<1e-10 and min(r['contact_derivative_errors'])<1e-3 and all(x['passed'] for x in r['rigid_motion_controls'])
 assert r['numerical_controls_pass'];return r
cases=[read(O,h) for h in [1.9,1.5]];quadrature=read(O/'quadrature6',1.9);rows=[]
for kind,old,new in [('mesh refinement',cases[0],cases[1]),('quadrature refinement',cases[0],quadrature)]:
 for a,b in zip(old['stress'],new['stress']):
  for method in ['interior125','boundary35']:
   v=a['sampled_peaks_MPa'][method];w=b['sampled_peaks_MPa'][method];delta=abs(w/v-1)*100
   rows.append(dict(comparison=kind,component=a['component'],sampling=method,old_peak_MPa=v,new_peak_MPa=w,change_percent=delta,chosen_5_percent_pass=delta<5))
summary=dict(date='2026-10-24',revision='V25',pilot_completed=True,new_equilibrium_fields=3,CAD_shapes_changed=False,all_product_software_testing_complete=False,whole_part_strength_demonstrated=False,physical_tests=0,mesh_passes=sum(r['chosen_5_percent_pass'] for r in rows if r['comparison']=='mesh refinement'),quadrature_passes=sum(r['chosen_5_percent_pass'] for r in rows if r['comparison']=='quadrature refinement'),cases=cases,quadrature_case=quadrature,comparisons=rows,scope='Child large outward isolated V19 joint only. Quadratic surface contact AND consistent surface loads replace linear subtriangles. Same continuum parameters and virtual spacer. Not a pure contact-only change, physical contact model, new CAD, material qualification or product validation.')
(O/'review_status.json').write_text(json.dumps(summary,indent=2))
with (O/'stress_comparisons.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Record the exact manufacturer pages reviewed, without mixing test methods or grades.
materials=dict(checked='2026-10-24',sources=[dict(name='BASF Ultramid A3K uncoloured PA66 product information September 2026',url='https://download.basf.com/p1/8a8082587fd4b608017fd64108ab6d3b/en/ULTRAMID%3Csup%3E%C2%AE%3Csup%3E_A3K_Product_Data_Sheet_Asia_PacificEurope_English.pdf',facts='At 23 C tensile modulus dry/conditioned 3000/1100 MPa; yield stress 85/50 MPa; conditioned creep modulus at 1000 h and strain <=0.5% 700 MPa.',limit='Typical grade values. No complete constitutive curve, fatigue law, manufactured-part qualification or equivalence to the assumed E3500 model.'),dict(name='Rogers PORON 4701-40 product page',url='https://www.rogerscorp.com/elastomeric-material-solutions/poron-industrial-polyurethanes/poron-4701-40',facts='4701-40-15 listed density 240 kg/m3 and typical 25% compression force deflection 41 kPa.',limit='Product-page value only. Not mixed with ISO global sheet values. Not a full foam law or headphone comfort result.'),dict(name='Rogers global standards datasheet',url='https://www.rogerscorp.com/-/media/project/rogerscorp/documents/elastomeric-material-solutions/poron/english/data-sheets/17-320-poron-4701-40-soft-global-standards-data-sheet.pdf',facts='ISO 6916-1 compression measured at 25% deflection and 30 mm/min; typical values are not specification limits.',limit='Different test conditions from product-page table; no substituted or combined curve.'),dict(name='Sony India WH-CH720N support article 00198705',url='https://www.sony.co.in/electronics/support/wireless-headphones-bluetooth-headphones/wh-ch720n/articles/00198705',facts='Replacement methods depend on model; article refers users to authorised service.',limit='This reviewed article supplies no skirt/groove/carrier tolerances. Not a claim that dimensions cannot exist elsewhere.')],calculations=[dict(name='Same linear beam geometry and imposed deflection modulus ratio',equation='1100 / 3000',value=1100/3000,meaning='Conditional linear force and stiffness ratio only. No assertion that a finished band behaves linearly or matches this grade.'),dict(name='Uniform reference foam compression force',equation='0.041 N/mm2 * 1000 mm2',value_N=41.,meaning='Illustrative 1000 mm2 coupon at the product-page 25% compression point. Not real pad contact area, head force, comfort or seal.')],scope='Candidate source and dimensional-analysis screen only; no final material selection, purchase recommendation or new physical validation.')
(O/'manufacturer_input_review.json').write_text(json.dumps(materials,indent=2))
register=list(csv.DictReader((P/'engineering-v24-results/remaining_test_register.csv').open()))
register[0].update(Status='V25 pilot completed',Evidence='Three quadratic surface fields pass numerical controls',Limit='Child large outward reference only')
register[1].update(Status='Failed comparison remains open',Evidence=str(summary['mesh_passes'])+' of 4 quadratic surface mesh comparisons pass',Limit='Interpolation change did not close stress reliability')
register[5]['Evidence']='Manufacturer foam point available; full foam and cover laws still missing'
register.append(dict(Area='Material condition',Status='Candidate data sourced only',Evidence='Named PA66 dry and conditioned typical values differ',Limit='Do not use E3500 as calibrated humid or creep data'))
with (O/'remaining_test_register.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(register[0]));w.writeheader();w.writerows(register)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(9,4));labels=[r['component']+'\n'+r['sampling'].replace('interior125','125 interior').replace('boundary35','35 boundary') for r in rows[:4]]
x=np.arange(4);ax.bar(x-.18,[r['change_percent'] for r in rows[:4]],.36,label='Mesh 1.9 to 1.5 mm');ax.bar(x+.18,[r['change_percent'] for r in rows[4:]],.36,label='Integration 4 to 6 points per axis');ax.axhline(5,color='firebrick',ls='--',label='Chosen 5 percent check');ax.set_xticks(x,labels);ax.set_ylabel('Sampled peak change percent');ax.legend(fontsize=8);ax.set_title('Quadratic surface pilot retains failed stress checks');fig.tight_layout();fig.savefig(P/'documents/images/V25_contact_comparison.png',dpi=160);plt.close(fig)
(O/'README.md').write_text('''# V25 quadratic surface pilot

Three child-large outward reference fields are complete. Both meshes use six-node quadratic face interpolation and consistent surface loads; a third calculation increases quadrature from 4 to 6 Gauss points per Duffy axis on the 1.9 mm mesh. Mathematical basis, projection, rigid-motion, derivative, equilibrium, force, moment and friction controls passed. All raw fields and failed stress comparisons are retained.

Read stress_comparisons.csv and review_status.json. Mesh agreement still fails; this candidate does not close reliable peak prediction. It changes surface contact and consistent loads together, so it does not isolate contact as the cause of V24 differences. The chosen 5 percent pairwise gate is not a safety standard, a global peak bound or full convergence proof. No adult or inward expansion is claimed; expanding a failed pilot would not qualify the missing real joint details.

Run v25_quadratic_contact.py, v25_contact_campaign.py, v25_quadrature_campaign.py and v25_review.py in that order using saved mesh and warm-field hashes. The quadratic face module is installed only in each worker process; earlier model files and raw results remain unchanged. The Q6 case intentionally reuses the Q4 field on identical nodes as a warm start and must independently reach equilibrium. MMD_AT_PLUS_A changes sparse factor ordering only.

Manufacturer sources and simple conditional screens are in manufacturer_input_review.json. They improve input traceability but do not supply complete foam, cover, acoustic, thermal or durability laws. Sony's reviewed support article does not define mounting tolerances. Full product software validation remains open for both routes, with requirements listed in remaining_test_register.csv. Sensory acceptance still requires voluntary wearer testing. No purchase or manufacturing release is issued.
''',encoding='utf-8')
print({k:summary[k] for k in ['pilot_completed','new_equilibrium_fields','mesh_passes','quadrature_passes','all_product_software_testing_complete']})
