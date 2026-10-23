"""Both living project documents are rebuilt together from the same evidence snapshot."""
from pathlib import Path
import json,shutil,datetime,hashlib
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
P=Path(__file__).resolve().parents[1];O=P/'documents';I=O/'images'
STAMP='21 October 2026';REV='V8 main design and V9 local experiment'
NATIVE=None
nv=P/'engineering-v9-results'/'native_verification.json'
if nv.exists():
 NATIVE=json.loads(nv.read_text());REV='V8 main design with V9 native candidates'
refs=[
 ('Sensory differences and individual needs','https://www.autism.org.uk/advice-and-guidance/about-autism/sensory-processing'),
 ('Williams and colleagues 2021 sound sensitivity review','https://pmc.ncbi.nlm.nih.gov/articles/PMC8349927/'),
 ('Pfeiffer and colleagues 2019 six child headphone study','https://www.frontiersin.org/journals/integrative-neuroscience/articles/10.3389/fnint.2019.00065/full'),
 ('Robustt Indian earmuff listing','https://www.robustt.in/products/earmuffs-for-noise-reduction-red-and-black'),
 ('SYGA Indian child earmuff listing','https://syga.in/products/1001106'),
 ('Alpine Muffy Kids manufacturer page','https://www.alpinehearingprotection.com/products/muffy-kids'),
 ('boAt Nirvana 751 ANC Indian listing','https://www.boat-lifestyle.com/products/nirvana-751-anc-headphone'),
 ('Sony WH CH720N Indian store price','https://shopatsc.com/collections/festive-season-sale/products/wh-ch720n-bcin'),
 ('Sony WH CH720N specifications','https://www.sony.co.in/electronics/support/wireless-headphones-bluetooth-headphones/wh-ch720n/specifications'),
 ('Turtle Beach adjustable ProSpecs glasses relief','https://uk.turtlebeach.com/blog/memory-foam-ear-cushions-prospecs-glasses-gamers'),
 ('Noisefighters Sightlines gel relief pads','https://noisefighters.com/collections/hearing/products/sightlines1'),
 ('Brainwavz replacement pad fit guide','https://www.brainwavzaudio.com/pages/brainwavz-earpad-guide'),
 ('Wicked Cushions cooling replacement pads','https://wickedcushions.com/products/wc-freeze-cooling-gel-gaming-ear-cushions?variant=39299092807759'),
 ('3M X4A UK rating','https://www.3m.co.uk/3M/en_GB/p/d/v000137013/'),
 ('Udaipur adult ear to crown height study','https://www.ijars.net/article_fulltext.asp?id=2915&issn=0973-709x&issue=5&month=September&page=AO01-AO04&volume=12&year=2023'),
 ('JBL Tune 770NC manufacturer specifications','https://www.jbl.com/TUNE770NC.html?dwvar_TUNE770NC_color=White-AM-Current&locale=en_US'),
 ('Sony WH CH720N pad replacement instructions','https://www.sony.co.uk/electronics/support/wireless-headphones-bluetooth-headphones/articles/00295193'),
 ('Crysendo indexed Sony replacement pad listing','https://www.crysendo.com/collections/bestseller-products'),
 ('Geekria Sony cooling gel replacement pads','https://shop.geekria.com/products/geekria-sport-cooling-gel-infused-cloth-ear-pads-for-sony-wh-ch700n-wh-ch710n-headphone-ear-pad-ear-cushion-ear-cups-ear-cover-earpads-repair-parts-extra-thick-black')]
versions=[
 ('V1','First cushion and glasses zone','V1','Saved cushion snapshot with simplified glasses arms. The original hand-built oval cushion came first; the saved file adds the frame references.',
  'We made an oval pad with a separate softer area where the glasses arm rests. We also added simple thin, standard and thick arm shapes to explore the idea.',
  'The first screening study ran 3,240 contact cases and 81 heat and humidity cases. A separate 18-case band-force screen used a prescribed spring law, not force calculated from the CAD headband.',
  'The basic compression equation and force balance checks passed for the chosen inputs.',
  'Contact coverage changed when the grid was refined. Gaps remained. One warm and humid example reached 100% humidity. There was no real seal or comfort pass.',
  'This tested a simplified idea. It did not compare our pad with a real market headphone or prove pain relief.',
  'cad_build_report.json; screening-results/report.md; screening-results/summary.json'),
 ('V2','Trying shapes and a continuous cover','V2','Saved flat cover surface prototype. The shaped pads in this study were numerical candidates, not this exact CAD surface.',
  'We compared flat and curved contact faces, smaller edge rounding, and ideal cup alignment. We also made a connected cover surface so the pad would not expose a gap between materials.',
  'The V2 shape screen ran 9,216 assumption-based cases. The cover CAD was checked for one connected surface body. It was not a solid cover with tested strength.',
  'The cover faces connected. In one ideal reference case, the curved face reached 100% calculated contact.',
  'The cover was only a surface. Its 0.2 mm thickness was metadata. There was no seam, side wrap, fabric tension or measured leakage result.',
  'A perfectly matched synthetic head is easier to seal than a real head. The 100% result is not an airtight-pad claim.',
  'shape-study-results/report.md; cover_prototype_report.json'),
 ('V3','Curved pads and a more complete defender','V3','Actual saved adult V3 assembly. Colours only help distinguish parts.',
  'We added curved adult and child pads, a solid cover envelope, carrier blanks, closed cups and a fuller standalone defender. The child now had a separate scaled pad.',
  'The contact model used a simple tensioned cover over compressible foam. It ran 48 cases. A nonlinear planar band model and 36 coupled band and pad cases replaced the earlier prescribed force.',
  'Solver checks included basic compression, mesh area and force balance. Separate child geometry was generated.',
  'Pressure peaks still needed refinement. Cover seams, skin friction, real foam and acoustic ratings were missing. The CAD cover did not have uniform normal thickness.',
  'A manufacturer can sell a finished headset; ours was still imported concept geometry with assumed material values.',
  'cad_v3_report.json; engineering-v3-results/contact_summary.json; band_summary.json; coupled_summary.json'),
 ('V4','Cup movement and three height positions','V4','Actual saved adult V4 assembly with pinned forks and crown padding.',
  'We added pinned forks, retained pin placeholders, exterior cup bosses, 5 mm crown padding and three pin heights. The cups could turn slightly to help align with the head.',
  'CAD checks sampled cup rotation from minus 8 to plus 8 degrees and pin heights of 55, 65 and 75 mm. The numerical work included band and pad coupling and 216 one-hour heat and moisture cases.',
  'The recorded cup and pin-position clearance checks passed. The solver balance checks passed.',
  'The final pressure peak changed by 15.2% with finer meshes. Several cover scenarios still saturated. Threads, retention, fatigue, drops and scalp contact were untested.',
  'Movement clearance only means the selected CAD parts do not overlap at those positions. It says nothing about real joint friction or whether a child can adjust it safely.',
  'cad_final_report.json; engineering-final-results/REVIEW.md'),
 ('V5','Six sizes and sliding adjustment','V5','Actual saved adult medium V5 assembly. Each side has 30 mm of slider travel.',
  'We introduced three child and three adult widths, 30 mm sliders, 4 by 16 mm tongues and clamp knobs. We chose a more curved pad after comparing candidate shapes.',
  'The study ran 72 cushion comparisons, 54 coupled force and compression cases, 12 nearby head-width cases and 81 additional moisture cases. A simple acoustic model used 48 parameter combinations at 48 frequencies from 31.5 to 250 Hz.',
  'Sampled slider clearance and beam force-balance checks passed. Pressure averaged over a 6 mm virtual sensor changed by less than 5% in both nominal family cases. The low-frequency acoustic code checks passed.',
  'Point pressure peaks did not converge. At the assumed middle water-vapour transmission level, 3 of 27 conditions saturated. Twelve end-position STEP files were later found empty because their components were hidden.',
  'No physical market headset was tested alongside these cases. The empty exports were an output failure and were corrected in V6.',
  'cad_v5_report.json; engineering-v5-results/REVIEW.md'),
 ('V6','Cleaner geometry and checked exports','V6','Actual saved adult medium V6 assembly after overlap corrections.',
  'We moved the carrier behind the cover, cleared the cup seat, removed unused fork holes and softened some hard edges. We also repaired the hidden end-position exports.',
  'All six assemblies had an overlap audit. All 24 STEP files were imported independently. A 3D band and guide model and a 3D acoustic cavity model were added.',
  'The nominal overlap check passed for all six. All STEP imports passed. Band deflection was stable. A separate beam code check differed by 2.47% from its reference equation.',
  'Small-child stress changed by 7.42% on further refinement. The first acoustic model changed by up to 2.95 dB at higher frequencies. Both exceeded the chosen checks.',
  'Passing a solver check is not the same as passing a commercial hearing-protection rating. The geometry still had no measured material data.',
  'cad_v6_report.json; cad_v6_audit.json; engineering-v6-results/REVIEW.md'),
 ('V7','Rounded entries and a better acoustic calculation','V7','Actual saved adult medium V7 assembly. The taller crown was later reconsidered.',
  'We rounded four arc-shaped slider entries by 0.5 mm. We also improved the acoustic calculation using curved quadratic elements and an area-averaged receiver.',
  'All six structural cases were refined. Eighteen defender STEP files were checked. The acoustic model compared 6 and 4.5 mm meshes at 48 frequencies from 31.5 Hz to 8 kHz. A separate vertical-fit screen compared 90 synthetic head and extension cases.',
  'All six recorded stress and deflection comparisons passed 5%. Defender STEP imports passed. Acoustic mesh differences were 0.113 dB for child and 0.067 dB for adult. The tube code check had 0.442% maximum complex-pressure error.',
  'The tall crown missed the synthetic scalp in 78 of 90 vertical comparisons; 8 suggested a rigid intersection. A stress pass did not fix that fit issue.',
  'We did not prove a stronger or more comfortable product. The acoustic model still omitted real glasses leakage, porous liners and actual ear shapes.',
  'cad_v7_report.json; engineering-v7-results/solid_v7_summary.json; acoustic_p2_summary.json; vertical_fit_summary.json'),
 ('V8','Lower crown foundation','V8','Actual saved adult medium V8 assembly. This lower-crown design is the foundation for the later V9 and V10 revisions.',
  'We lowered the arch to 40 mm for adults and 25 mm for children, added an assumed 8 mm crown pad and recalculated all six widths. The sliders still travel 30 mm per side.',
  'There are 30 CAD files: six Fusion archives and 24 STEP exports. We checked overlap, slider travel and cup movement. The current force study ran 54 cases across three assumed band stiffness values and three extension settings.',
  'All 24 STEP imports and six nominal overlap audits passed. Recorded slider and cup clearance checks passed. All six deflection comparisons and four stress comparisons passed.',
  'Adult-small stress changed by 12.72% and adult-large by 10.84% with mesh refinement. They failed the chosen 5% check. Full scalp pressure, materials, locking and actual sound reduction remain untested.',
  'The 54 cases predict 1.01 to 3.80 N per side and 3.49 to 5.87 mm maximum pad compression across the cases. These are calculations, not comfort limits. The design has not beaten any real headset.',
  'cad_v8_report.json; cad_v8_audit.json; engineering-v8-results/REVIEW.md'),
 ('V9','Local corner experiment that was not adopted','V9','Actual adult-small STEP-only candidate. There is no matching V9 Fusion archive.',
  'We tried rounding eight internal slider corners by 0.5 mm to address the remaining stress sensitivity. This was a local exported-geometry experiment.',
  'Adult-small was calculated at 3, 2 and 1.5 mm mesh sizes. The changed band was checked against the other 27 bodies and two tongues at seven slider positions.',
  'The adult-small file contained 28 solids. The sampled static and slider overlap checks passed. Deflection was stable.',
  'Adult-small stress still changed by 5.97%, so it failed the 5% check. The local adult-large fillet could not be created. Native Fusion refinement did not run successfully because desktop activation was blocked.',
  'V9 is not a finished replacement for V8. A failed experiment is useful information, but it cannot become a product claim.',
  'engineering-v9-local-results/summary.json; clearance.json; engineering-v9-results/adult_small_local_fillet.json')]

STRUCTURAL=None
ss=P/'engineering-v9-results'/'solid_v9_summary.json'
if ss.exists():STRUCTURAL=json.loads(ss.read_text())
if NATIVE and STRUCTURAL and NATIVE['status']=='complete' and STRUCTURAL['status']=='complete' and STRUCTURAL['all_available_stress_comparisons_pass'] and all(c['deflection_gate_5pct'] for c in STRUCTURAL['cases']):REV='V9 band candidate with V8 replacement cushions'
FORCE=None
fs=P/'engineering-v9-results'/'nominal_force_screen.json'
if fs.exists():FORCE=json.loads(fs.read_text())
if NATIVE:
 results=[];failed_results=[]
 for s in NATIVE['sizes']:
  meshes=[]
  for f in (P/'engineering-v9-results').glob(s['name']+'_h*.json'):
   try:r=json.loads(f.read_text())
   except Exception:continue
   if 'mesh_max_mm' in r:meshes.append(r)
  meshes.sort(key=lambda r:r['mesh_max_mm'],reverse=True)
  if len(meshes)>1:
   a,b=meshes[-2:];change=100*abs(b['max_von_mises_centroid_MPa']/a['max_von_mises_centroid_MPa']-1)
   message=s['name'].replace('_',' ')+' has a '+format(change,'.3f')+'% stress change between its last two meshes'
   (results if change<5 else failed_results).append(message)
 n=len(NATIVE['sizes']);steps=len(NATIVE['STEP_checks'])
 versions[-1]=('V9','Native corner refinement and digital checks','V9','Actual native adult-small V9 STEP render. Its matching local Fusion archive has now been exported.',
 'The earlier local corner experiment is retained as a failed trial. Fusion then rounded eight internal guide corners by 0.5 mm in '+str(n)+' of the six sizes. V9 is the latest band candidate. V8 retains the replacement cushion and earlier screening evidence.',
 'Native build records check the changed band against the static assembly and sampled slider positions. Independently imported '+str(steps)+' available native STEP files. Structural calculations refine the actual native band geometry. The local Fusion archives were exported but have not been reopened for a separate check.',
 'All available native STEP imports contain 28 solids. Recorded static and slider overlap checks passed for the exported candidates. '+('All six stress comparisons are within our 5% limit. See the next page for the size-by-size results. ' if len(results)==6 else ('; '.join(results)+', within our 5% comparison limit. ' if results else ''))+'These are digital checks, not a strength or comfort pass.',
 ('; '.join(failed_results)+', above our 5% comparison limit. ' if failed_results else '')+('Structural refinement is not complete for every size. ' if len(results)+len(failed_results)<6 else '')+('Other sizes remain to be built. ' if n<6 else '')+'Real material strength, full joint contact, retention, sound reduction and wearer acceptance remain untested.',
 'The native Fusion build succeeded for the recorded sizes; the earlier desktop failure is no longer the whole story. V9 changes the band, not the replacement cushion. No new real leakage or pressure result follows from this update.',
 'engineering-v9-results/native_verification.json; solid_v9_summary.json; numerical_audit.json; nominal_force_screen.json; export_audit.json; engineering-v9-local-results/summary.json')

POSE9=None;V10=None;POSE10=None;STRUCT10=None;GAPS10=None;FORCE10=None;SLIDER10=None
if (P/'engineering-v9-results'/'all_pose_pairs.json').exists():POSE9=json.loads((P/'engineering-v9-results'/'all_pose_pairs.json').read_text())
if (P/'engineering-v10-results'/'cad_local_report.json').exists():V10=json.loads((P/'engineering-v10-results'/'cad_local_report.json').read_text())
if (P/'engineering-v10-results'/'all_pose_pairs.json').exists():POSE10=json.loads((P/'engineering-v10-results'/'all_pose_pairs.json').read_text())
if (P/'engineering-v10-results'/'solid_v10_summary.json').exists():STRUCT10=json.loads((P/'engineering-v10-results'/'solid_v10_summary.json').read_text())
if (P/'engineering-v10-results'/'clearance_distances.json').exists():GAPS10=json.loads((P/'engineering-v10-results'/'clearance_distances.json').read_text())
if (P/'engineering-v10-results'/'adjustment_force_screen.json').exists():FORCE10=json.loads((P/'engineering-v10-results'/'adjustment_force_screen.json').read_text())
if (P/'engineering-v10-results'/'slider_compliance.json').exists():SLIDER10=json.loads((P/'engineering-v10-results'/'slider_compliance.json').read_text())
NATIVE10=None;NATIVEPOSE10=None;FULLWIDTH10=None;NATIVEARCH10=None;STRENGTH10=None;LOCKREACH10=None;FULLSIZES10=None;FULLFORCE10=None;IDENTITY10=None
for filename,var in [('cad_native_report.json','NATIVE10'),('native_all_pose_pairs.json','NATIVEPOSE10'),('adult_small_full_width_summary.json','FULLWIDTH10'),('native_archive_reopen.json','NATIVEARCH10'),('conditional_strength_screen.json','STRENGTH10'),('lock_reach_audit.json','LOCKREACH10'),('full_width_sizes_summary.json','FULLSIZES10'),('adjustment_force_full_width.json','FULLFORCE10'),('source_identity_audit.json','IDENTITY10')]:
 if (P/'engineering-v10-results'/filename).exists():globals()[var]=json.loads((P/'engineering-v10-results'/filename).read_text())
NATIVE10DONE=bool(NATIVE10 and NATIVE10['status']=='complete')
if POSE9 and not POSE9['all_pass']:
 REV='V9 shortest setting clashes and V10 guide candidates'
 old=list(versions[-1]);old[6]=old[6].replace('Recorded static and slider overlap checks passed for the exported candidates.','The earlier selected-body motion checks passed, but the wider audit below found missed clashes.')
 old[7]='A later all-body audit found clashes in all six shortest-setting exports. Both slider pivot pins intersect the guides. Child thumb knobs also intersect the forks. The earlier motion check omitted those parts. '+old[7]
 old[8]='The V9 nominal structural results remain recorded, but its shortest setting is not geometrically acceptable. The earlier package must not be treated as a cleared full-travel design. The replacement cushion is unchanged; no real leakage or wearer result has been added.'
 old[4]=old[4].replace('V9 is the latest band candidate.','V9 was the native band candidate before the wider audit.')
 old[9]+='; engineering-v9-results/all_pose_pairs.json';versions[-1]=tuple(old)
if V10:
 REV='V10 native candidates with open structural and physical checks' if NATIVE10DONE else 'V10 STEP candidates with open native and stress checks'
 stress10=(str(sum(c['stress_gate_5pct'] for c in STRUCT10['cases']))+' of '+str(len(STRUCT10['cases']))+' recorded stress comparisons pass 5%.' if STRUCT10 else 'Structural refinement is not yet recorded.')
 failed10=(', '.join(c['size'].replace('_',' ') for c in STRUCT10['cases'] if not c['stress_gate_5pct']) if STRUCT10 else '')
 versions.append(('V10','Guide and knob clearance candidates','V10',('Actual adult-small V10 native Fusion STEP export.' if NATIVE10DONE else 'Actual adult-small V10 local STEP candidate. This is not yet a native Fusion archive.'),
 'We shortened the guide bottoms by 2 mm and moved the clamp bores and knobs upward by 4 mm. The crown, cushion, pins, forks and intended 30 mm slider travel are retained.',
 ('Native Fusion exported all six sizes, 18 STEP poses and six Fusion archives. The local and native bands agree within the 0.01 cubic mm volume comparison tolerance. ' if NATIVE10DONE else 'Six sizes and their nominal and endpoint poses were exported as local STEP candidates. ')+'The wider all-body overlap audit covers every pair of solids. Changed guide geometry receives fresh structural calculations.',
 ('All 18 local poses pass the recorded all-body overlap checks.' if POSE10 and POSE10['all_pass'] else 'The candidate files were generated; the full audit is still running or has remaining clashes.')+' '+stress10,
 (failed10+' does not meet the chosen stress mesh comparison. ' if failed10 else '')+'The first adult-large 1.25 mm mesh was rejected for an invalid element and replaced with an optimized mesh that passed the validity check. Locking, measured materials and physical product validation remain open.',
 'This revision addresses actual CAD interference, not autistic sensory acceptance or glasses sealing. Those remain separate test questions.',
 'engineering-v10-results/cad_local_report.json; all_pose_pairs.json'))

if (P/'engineering-v12-results'/'cad_report.json').exists():
 REV='V12 local folding lock candidate with V10 native archives'
if (P/'engineering-v14-results'/'cad_report.json').exists():
 REV='V14 local rear cap candidate with V10 native archives'
if (P/'engineering-v15-results'/'adult_small_retention_cad.json').exists():
 REV='V15 retention pilot and V14 six size candidates'
if (P/'engineering-v16-results'/'selected_candidates.json').exists():
 REV='V16 indexed folding candidates with V10 native archives'
if (P/'engineering-v17-results'/'test_register.json').exists():REV='V17 two size entry pilots with V16 six size candidates and V10 native archives'
if (P/'engineering-v18-results'/'test_register.json').exists():REV='V18 six size passive hinge candidates with V10 native archives'
if (P/'engineering-v19-results'/'test_register.json').exists():REV='V19 six size assembly prototype with conditional joint calculations and V10 native archives'

def para(doc,text,style=None):
 p=doc.add_paragraph(text,style);return p
def heading(doc,text):doc.add_heading(text,1)
def new_page(doc,title):doc.add_page_break();heading(doc,title)
def label(doc,title,text):
 p=doc.add_paragraph();p.add_run(title+': ').bold=True;p.add_run(text)
def picture(doc,name,caption,width=6.55):
 if name in ['V3','V4','V5','V6','V7','V8','V9','V10','pad']:caption+=' Surface triangles show the display mesh, not fabric texture.'
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True
 shape=p.add_run().add_picture(str(I/(name+'.png')),width=Inches(width));shape._inline.docPr.set('descr',caption)
 p=para(doc,caption,'Caption');p.paragraph_format.space_after=Pt(10)
def table(doc,headers,rows,widths):
 if NATIVE and headers[0]=='Update date':
  rows=[['13 October 2026','Initial living reports',r[2]] for r in rows]+[['13 October 2026','V9 native candidates','Updated native V9 export and structural evidence for '+str(len(NATIVE['sizes']))+' sizes. The replacement pad has no new physical leakage or comfort evidence.']]
  if V10:rows+= [['13 October 2026','V10 clearance candidates','Wider audit found missed V9 shortest-setting clashes. Added V10 guide and knob candidates. Replacement cushion unchanged.']]
  if FULLSIZES10:rows+=[['15 October 2026','V10 actual width fixture study','Actual-width fixture checks completed for '+str(len(FULLSIZES10['cases']))+' of six sizes. Updated refinement and conditional strength evidence, solver failure history and Sony pad competitors. No measured cushion benefit.']]
  if (P/'engineering-v12-results'/'cad_report.json').exists():rows+=[['15 October 2026','V12 local folding candidate','Added wider guide channels, a folding lock candidate, component calculations, revised motion checks and unresolved assembly and product-validation requirements. Replacement Sony cushion compatibility is still untested.']]
  if (P/'engineering-v14-results'/'cad_report.json').exists():rows+=[['15 October 2026','V14 rear cap candidates','Retained the failed V13 assembly path and added the rear cap candidate with explicit test status. Sony mount and physical benefits remain untested.']]
  if (P/'engineering-v15-results'/'adult_small_retention_cad.json').exists():rows+=[['15 October 2026','V15 retention and packing experiments','Added one adult small threaded knob and jam nut experiment, a child packing search on unchanged V14 parts and conditional retention load calculations. No physical or Sony pad pass is added.']]
  if (P/'engineering-v16-results'/'selected_candidates.json').exists():rows+=[['15 October 2026','V16 indexed folding candidates','Added folded-position index holes, recessed rivet retention, different child and adult layouts, retained failures, material-reference calculations and blank physical-test records. Sony fit and physical benefit remain untested.']]
  if (P/'engineering-v17-results'/'test_register.json').exists():rows+=[['15 October 2026','V17 two size entry pilots','Larger index holes and entry cones tested on child large and adult small. V16 remains the six size candidate.']]
  if (P/'engineering-v18-results'/'test_register.json').exists():rows+=[['16 October 2026','V18 passive hinge and wearing stop','Six sizes and component checks retained. Added final material, pivot clearance, CAD stack and handling load screens. Retention risk and missing physical inputs are recorded.']]
  if (P/'engineering-v19-results'/'test_register.json').exists():rows+=[['16 October 2026','V19 prototype handoff','Six sizes revised. Added two disc springs, longer pin envelopes, second nuts, coupled joint development, retained failures and measurement forms. No physical validation or manufacturing release.']]
 t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 for c,w in zip(t.columns,widths):c.width=Inches(w)
 for c,s in zip(t.rows[0].cells,headers):c.text=s
 repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
 for row in rows:
  for c,s in zip(t.add_row().cells,row):c.text=str(s)
 for ri,row in enumerate(t.rows):
  tr=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(tr)
  for ci,c in enumerate(row.cells):
   c.width=Inches(widths[ci]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;pr=c._tc.get_or_add_tcPr()
   sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'203E4B' if ri==0 else ('F0F5F5' if ri%2 else 'FFFFFF'));pr.append(sh)
   margins=OxmlElement('w:tcMar')
   for side in ['top','left','bottom','right']:
    e=OxmlElement('w:'+side);e.set(qn('w:w'),'90');e.set(qn('w:type'),'dxa');margins.append(e)
   pr.append(margins);borders=OxmlElement('w:tcBorders')
   for side in ['top','left','bottom','right']:
    e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
   pr.append(borders)
   for p in c.paragraphs:
    p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1.08
    for r in p.runs:r.font.size=Pt(10);r.bold=ri==0;r.font.color.rgb=RGBColor.from_string('FFFFFF' if ri==0 else '000000')
 para(doc,'')
 return t
def link(doc,text,url):
 p=doc.add_paragraph();h=OxmlElement('w:hyperlink');h.set(qn('r:id'),doc.part.relate_to(url,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True));r=OxmlElement('w:r');pr=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'24536A');pr.append(color);r.append(pr);t=OxmlElement('w:t');t.text=text;r.append(t);h.append(r);p._p.append(h)
def setup(title,subtitle):
 d=Document();s=d.sections[0];s.page_width=Inches(8.5);s.page_height=Inches(11);s.top_margin=s.bottom_margin=Inches(.65);s.left_margin=s.right_margin=Inches(.8)
 for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Caption']:
  st=d.styles[name];st.font.name='Calibri';st.font.color.rgb=RGBColor(0,0,0)
 d.styles['Normal'].font.size=Pt(11);d.styles['Normal'].paragraph_format.line_spacing=1.12;d.styles['Normal'].paragraph_format.space_after=Pt(7)
 d.styles['Title'].font.size=Pt(28);d.styles['Title'].font.bold=True;d.styles['Heading 1'].font.size=Pt(19);d.styles['Heading 1'].paragraph_format.space_after=Pt(10)
 d.styles['Heading 2'].font.size=Pt(13);d.styles['Caption'].font.size=Pt(9);d.styles['Caption'].font.italic=True
 d.core_properties.title=title;d.core_properties.subject=subtitle;d.core_properties.author='SoftSpace Project';d.core_properties.keywords='living project document simulation evidence V19'
 hp=s.header.paragraphs[0];hp.text='SOFTSPACE    |    24 October 2026';hp.runs[0].font.size=Pt(8)
 fp=s.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.RIGHT;r=fp.add_run('Concept under development  |  ');r.font.size=Pt(8)
 fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');fp._p.append(fld)
 d.add_paragraph(title,'Title');d.add_paragraph(subtitle,'Subtitle');return d
def sources(doc,ids):
 for i in ids:link(doc,'['+str(i)+'] '+refs[i-1][0],refs[i-1][1])
 para(doc,'Web information was checked on 13 October 2026. Prices, coupons and stock can change. Links are evidence sources, not buying recommendations. CAD images were rendered from our saved STEP files; they are not manufactured product photos. SYGA and Sony photographs came from the linked seller pages and are used only to identify the compared products.')
def save(doc,name):
 dest=O/name
 if dest.exists():
  b=O/'history';b.mkdir(exist_ok=True);shutil.copy2(dest,b/(dest.stem+'_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.docx'))
 doc.save(dest);return dest

def main_doc():
 d=setup('SoftSpace','Headphones for sound sensitive autistic people')
 para(d,'Current update on 24 October 2026: the V21 review adds folding, glasses-position and stress checks to the unchanged V19 headset and V20 cushion bodies. Six of eight finer stress checks pass, but the adult fork still fails two. All six sizes have a smaller sampled carrying pose. The wider cushion tests reveal pressure risks. All software work is not complete. Neither product is physically validated. See the final V21 chapter.')
 para(d,'We are developing a low-cost passive over-ear defender for India. The aim is to make loud surroundings easier to manage while keeping the device comfortable, easy to remove and simple to use. Autistic users are our first priority; other sound-sensitive people may also find the idea useful.')
 if (I/'V19_hero.png').exists():picture(d,'V19_hero','V19 child large and adult small final local STEP prototype assemblies. Physical validation remains open.',5.7)
 elif (I/'V18_hero.png').exists():picture(d,'V18_hero','V18 passive hinge child large and adult small local STEP candidates. Physical validation remains open.',5.7)
 elif (I/'V16_hero.png').exists():picture(d,'V16_hero','Selected V16 child large and adult small local STEP candidates. Colours do not select materials. Physical validation remains open.',5.7)
 else:picture(d,'V10' if V10 else ('V9' if NATIVE else 'V8'),('V10 adult small native Fusion STEP export. Physical validation remains open.' if NATIVE10DONE else 'V10 adult small STEP-only candidate. Native rebuilding remains open.') if V10 else ('Latest V9 adult small CAD. This is a digital concept with assumed materials.' if NATIVE else 'V8 adult medium CAD. This is a digital concept with assumed materials.'),5.7)
 label(d,'Where we are now','Six sizes and sliding adjustment are saved. Some geometry and numerical checks passed. Comfort, sensory acceptance and real sound reduction have not been proved.')
 if (P/'engineering-v19-results'/'test_register.json').exists():
  para(d,'V19 is our latest six size local STEP prototype. It adds a parallel disc spring pair, longer pin proposal and second nut. The coupled 3D joint calculation has recorded failed solves and mesh limits. This is a prototype handoff, not a finished product or complete validated simulation phase. Real materials, exact Sony mounting dimensions, acoustics and voluntary wearer feedback remain necessary. Native editable Fusion archives remain V10.')
 elif (P/'engineering-v18-results'/'test_register.json').exists():
  para(d,'V18 is our latest six size local STEP candidate. A passive friction hinge and separate wearing stop replace the loaded sliding pin. Sampled geometry and conditional numerical checks are recorded in the new chapters. Actual torque calibration, complete joint strength, comfort, sound reduction and durability remain unvalidated. Native editable Fusion archives remain V10. No manufacturing release is claimed.')
  if (P/'engineering-v18-results'/'final_available_data_screen.json').exists():para(d,'The final holding screen finds a limited margin: the proposed minimum hinge torque is exhausted at about 1.15 g of equivalent static acceleration in the worst assumed mass case. Handling retention is not established. The final chapters record the material, clearance and saved CAD measurements and the inputs still needed.')
 elif (P/'engineering-v17-results'/'test_register.json').exists():
  para(d,'V16 remains the latest six size local CAD candidate. V17 adds child large and adult small pin entry trials with larger holes and entry cones. The later chapters record their trade-offs and checks. Native editable Fusion archives remain V10. These are local STEP prototype candidates, not a validated finished product.')
  if (P/'engineering-v17-results'/'digital_closeout.json').exists():para(d,'The latest assessment puts the latch on hold for production. The loaded pin and spring comparison exposes a return-force risk. We need actual guide drag, spring and material measurements before treating the joint as reliable. No physical comfort, sound or durability pass exists.')
 elif (P/'engineering-v16-results'/'selected_candidates.json').exists():para(d,'The latest local candidates are V16, with folded-position index holes and recessed rivet retention in six sizes. Child and adult layouts differ. The later chapters record their checks, earlier failures and remaining work. Native editable Fusion archives remain V10; V16 is local STEP work. These are prototype candidates, not a validated finished product.')
 elif (P/'engineering-v12-results'/'cad_report.json').exists():para(d,'Our latest six size local CAD candidate is V14, with a rear service cap after the V13 assembly route failed. V15 adds one adult small knob retention experiment and a child packing search on V14 parts. Their results and remaining problems are described at the end of this report. The picture above is the earlier native V10 assembly; later revisions are local STEP candidates.')
 para(d,'This document explains the user need, selected market options, every development stage and what our tests actually mean. Read it alongside SoftSpace Flex for the replacement-pad project. That separate route now targets the Sony WH-CH720N, chosen by the user. Sony confirms replaceable pads, but mounting measurements and host-specific results are still missing. [17]')
 para(d,'Competing WH-CH720N replacement pads are already listed by Crysendo and Geekria. The companion report records current and older indexed price evidence separately. Our softer glasses zone still needs a measured advantage; it is not enough to offer memory foam or claim local availability. [18, 19]')
 new_page(d,'What autistic people may need')
 para(d,'There is no single headphone preference shared by all autistic people. Some are very sensitive to noise, touch or heat; others enjoy sound or firm pressure. Preferences can change with the environment. Our design choices must come from the people who will wear the product, not only from our calculations. [1]')
 para(d,'Sound sensitivity is not just a rare exception. A 2021 research review estimated current hyperacusis, or reduced tolerance to sound, at about 41% using interviews and questionnaires and 27% using observational or objective measures. The estimates varied a lot. These figures do not describe every autistic person and do not tell us what headphones they prefer. [2]')
 table(d,['What we should ask about','What we are trying to design'],[
  ['Loud or sudden sounds','Useful reduction without added playback, beeps or electronic hiss'],['Pressure and glasses arms','A softer contact area and several adjustable fit choices'],['Heat and sweat','Materials we can test in warm and humid conditions'],['Texture and rubbing sounds','Smooth seams and a cover the wearer can choose or reject'],['Bulk and weight','Enough ear space with as little unnecessary material as possible'],['Control and removal','Easy removal and adjustment; wearing remains the user’s choice'],['Communication','Check whether important voices and everyday cues remain usable']], [2.2,4.7])
 para(d,'These are design questions and hypotheses, not a proven preference ranking. If someone removes the headphones, we should investigate discomfort or their wish for a break. Keeping them on at all costs is not our goal.')
 para(d,'A small 2019 study followed six children aged 8 to 16 using in-ear and over-ear noise-attenuating headphones. It provides early evidence worth exploring, but its small sample cannot establish a universal winner or validate our product. [3]')
 new_page(d,'What the market already offers')
 para(d,'People use child earmuffs, industrial hearing protection, ordinary ANC headphones and earplugs. A product does not need an autism label to be useful. Some are inexpensive; others add electronics, premium materials or specialist fittings.')
 table(d,['Example','Observed price','What the source shows','What is still unknown'],[
 ['Robustt earmuffs [4]','INR 808 for 2\nINR 404 each','Adjustable passive earmuffs; claimed NRR 21','Delivery, fit and sensory comfort; test report not reviewed'],
 ['SYGA child earmuffs [5]','INR 699','Child earmuff listing','Page gives conflicting stock messages; no matched tests'],
 ['Alpine Muffy Kids [6]','Indian delivered price not verified','Child passive defender aimed at focus and hearing protection','Local supply and fit for our users'],
 ['boAt Nirvana 751 ANC [7]','INR 5,099\nINR 3,099 with listed coupon','ANC audio headphone; page says restocking soon','Coupon, stock and comfort for our audience'],
 ['Sony WH CH720N [8,9]','INR 6,990 listing','ANC and music; specified mass 192 g','Local delivery and our matched wearer results'],
 ['Noisefighters Sightlines [11]','USD 60 before shipping and imports','Replacement gel and foam pads with glasses relief','Confirmed Indian stock and total delivered cost'],
 ['Our defender','No verified price yet','Six-size digital passive concept','All physical benefits and production cost']], [1.65,1.15,2.05,2.05])
 para(d,'This is a selected sample from our 29-entry market review, not every product sold. Prices were checked on 13 October 2026 and are not guaranteed checkout prices. We cannot say all existing options are expensive. The opportunity must include a clear benefit beyond price.')
 new_page(d,'Side by side with ordinary headphones')
 picture(d,'market_pictures','Seller photos identify the SYGA and Sony products. Our image is CAD. The photos do not establish a performance comparison.',6.55)
 table(d,['Feature','Passive market earmuffs','Ordinary ANC audio headphones','Our planned defender'],[
 ['Main purpose','Reduce outside sound','Music and calls with electronic noise cancellation','Reduce outside sound for sensory use'],
 ['Battery or charging','Usually unnecessary','Needed for active features','No electronics planned'],
 ['Music playback','Usually absent','Available','Absent in this concept'],
 ['Added sound','No electronic hiss generator; rubbing still possible','Prompts or hiss depend on the model and settings','No electronic prompts planned; rubbing untested'],
 ['Fit choice','Adjustment varies by model','Adjustment and pads vary by model','Six synthetic widths and 30 mm sliders'],
 ['Glasses relief','Depends on the product','ProSpecs exists on selected gaming products [10]','Softer local zone under continuous cover'],
 ['Heat and texture','Depends on materials and wearer','Depends on materials and wearer','We plan material choices and wearer checks'],
 ['Evidence','Some products publish hearing-protection ratings','Specs and tests vary; ANC claims are not NRR','Geometry and limited numerical studies only'],
 ['Is ours better','No matched comparison yet','No matched comparison yet','Not established']], [1.0,1.85,2.05,2.0])
 para(d,'ANC means active noise cancellation. Passive reduction relies on the cup, cushion and seal. ANC does not need white noise playback to work. Our passive route avoids electronics, but it has not been shown to reduce every kind of noise better than ANC.')
 para(d,'NRR and SNR are ratings from different hearing-protection test systems. An advertised ANC dB number or our cavity calculation cannot be compared directly with either. We need the same test setup for every product before ranking sound reduction. [14]')
 new_page(d,'Problems we want to address')
 table(d,['Possible problem','Our proposed change','What would prove it helps'],[
 ['Pads squeeze a glasses arm','Local softer zone under a continuous cover','Pressure mapping plus wearer feedback'],['One fit does not suit the wearer','Several widths and sliding height adjustment','Fit measurements and voluntary trials'],['Hot or sweaty contact','Test cover and foam choices for Indian conditions','Heat and humidity measurements'],['Bulky or tiring assembly','Remove unused parts and measure weight','A weighed prototype and movement trials'],['Poor seal around glasses','Conforming pad without an open groove','Measured isolation with multiple frames'],['High replacement cost','Model-specific replaceable pad and local supply','Supplier quotes and replacement-fit tests']], [1.65,2.45,2.8])
 para(d,'These are problems to investigate, not confirmed defects in every competitor. A softer pad can also compress too far or change the seal. A cooler fabric can let sound through. Every change needs a comparison with the original pad.')
 heading(d,'How to read our tests')
 para(d,'CAD checks look at geometry. Simulations calculate behaviour from assumed inputs. Physical tests measure a made object. Wearer feedback tells us whether someone accepts the feel and sound. These four kinds of evidence answer different questions.')
 para(d,'A mesh is the small pieces used in a numerical calculation. We refine the mesh to see whether the answer settles down. A pass means the selected calculation changed less than our chosen limit; it does not mean the product is safe, comfortable or certified.')
 para(d,'V1 and V2 are the early screening stages described in the saved reports. Their pictures show the available cushion and cover snapshots. They should not be read as a fully tested V1 or V2 manufactured headset.')
 for v in versions:
  code,title,img,cap,change,test,passed,failed,real,evidence=v
  new_page(d,code+' '+title);picture(d,img,cap,5.15)
  label(d,'What changed',change);label(d,'Tests and checks',test);label(d,'What passed',passed);label(d,'What failed or remained open',failed);label(d,'Real world meaning',real)
  p=para(d,'Evidence files: '+evidence);p.runs[0].font.size=Pt(8)
  if code=='V9' and STRUCTURAL and STRUCTURAL['status']=='complete':
   new_page(d,'V9 structural comparison across sizes')
   picture(d,'V9_mesh_comparison','Change between the last two meshes. This does not measure comfort or prove physical strength.',6.4)
   table(d,['Size','Last mesh mm','Stress change','Guide change'],[[c['size'].replace('_',' '),str(c['meshes'][-1]['mesh_max_mm']),format(100*c['stress_relative_mesh_change'],'.2f')+'%',format(100*c['deflection_relative_mesh_change'],'.3f')+'%'] for c in STRUCTURAL['cases']],[2.1,1.4,1.6,1.8])
   para(d,'These comparisons use the actual saved band geometry, an ideal 2 N force per side and an assumed elastic modulus of 2000 MPa. They omit worn-head contact, foam, joint friction and locking. We still need measured materials and prototype tests.')
   if FORCE:
    force_values=[r['force_N'] for r in FORCE['cases']];compression_values=[r['max_compression_mm'] for r in FORCE['cases']]
    para(d,'We also coupled the calculated V9 band stiffness with our simplified pad model for '+str(FORCE['case_count'])+' cases at the middle slider setting. With the chosen head sizes and assumed band moduli, force ranged from '+format(min(force_values),'.2f')+' to '+format(max(force_values),'.2f')+' N per side. Maximum foam compression ranged from '+format(min(compression_values),'.2f')+' to '+format(max(compression_values),'.2f')+' mm across those cases. These values are predictions, not comfort limits.')
    para(d,'This force screen combines a linear 3D band calculation with a scalar pad calculation. It assumes an ideal mounting offset and does not solve the whole worn assembly, scalp contact or slider locking. The earlier V8 force screen covers other extension settings using a different beam model; its numbers are not V9 measurements.')
  if code=='V10' and GAPS10:
   new_page(d,'Why the shortest setting changed')
   picture(d,'V10_clearance_fix','Sections cut from the actual saved V9 and V10 STEP files. Red shows intersecting material. The CAD slices are 0.2 mm thick; these are not physical measurements.',6.6)
   mins={k:min(c['distance_mm'] for r in GAPS10['checks'] for c in r['checks'] if c['pair']==k) for k in ['guide to tongue','guide to pivot pin','knob to fork']}
   para(d,'The minimum calculated nominal distances are '+format(mins['guide to tongue'],'.2f')+' mm from guide to tongue, '+format(mins['guide to pivot pin'],'.2f')+' mm from guide to pivot pin and '+format(mins['knob to fork'],'.2f')+' mm from knob to fork across the saved poses. These are undeformed CAD distances.')
   para(d,'If two matching parts each differ by 0.2 mm in a direction that closes the gap, their combined variation could use 0.4 mm. The approximately '+format(mins['guide to tongue'],'.2f')+' mm minimum gap would then have no guaranteed clearance. This is an example tolerance budget, not a measured factory capability or a proved jam. Roughness, heat, loads and friction still need checks.')
  if code=='V10' and STRUCT10 and STRUCT10['status']=='complete':
   new_page(d,'V10 structural results across sizes')
   table(d,['Size','Final mesh mm','Stress change','Displacement change','Stress check'],[[c['size'].replace('_',' '),str(c['meshes'][-1]['mesh_max_mm']),format(100*c['stress_relative_mesh_change'],'.2f')+'%',format(100*c['deflection_relative_mesh_change'],'.3f')+'%','Pass' if c['stress_gate_5pct'] else 'Not settled'] for c in STRUCT10['cases']],[1.65,1.2,1.2,1.45,1.4])
   para(d,'All six guide-displacement comparisons meet the chosen 5% limit. '+stress10+' '+('Earlier adult-medium comparisons changed by 8.37% and 18%; the final 0.9 to 0.8 mm comparison is recorded in the table. ' if STRUCT10['all_stress_comparisons_pass'] else 'Adult-medium remains unsettled near the upper channel corner. ')+'These are numerical comparisons, not physical strength tests. Saved curved-element coordinates passed an adaptive check for inverted elements.')
   para(d,'The earlier band calculation uses mirror symmetry across its width. The real clamp bore is only on the front wall. Mirroring that half gives the model an extra rear bore. The separate actual-width fixture study below keeps the real single bore, but changes the fixture and loading too. A matched comparison that changes only symmetry is still needed; neither study solves the complete worn assembly.')
   if SLIDER10:
    para(d,'The exposed slider segment was calculated at 0, 15 and 30 mm adjustment. All three displacement comparisons passed 5% after applying the load consistently over its surface. Earlier equal-node-load trials are not used. One finer long-slider trial ran out of memory; the accepted study uses meshes that passed numerical checks and records that failed trial separately.')
   if FORCE10:
    fv=[r['force_N'] for r in FORCE10['cases']];cv=[r['max_compression_mm'] for r in FORCE10['cases']]
    para(d,'The '+str(FORCE10['case_count'])+'-case adjustment screen predicts '+format(min(fv),'.2f')+' to '+format(max(fv),'.2f')+' N per side and maximum foam compression of '+format(min(cv),'.2f')+' to '+format(max(cv),'.2f')+' mm across the selected assumptions. We combine the band and slider stiffness estimates with the simplified pad model. These values are not comfort limits.')
    para(d,'The slider fixture is idealized and the band uses the symmetry approximation explained above. This screen does not solve real clamp friction, pin bearing, guide rotation, scalp contact or the complete worn assembly. It uses the same synthetic head width at each extension, assumed materials and a 35 mm mounting offset per side. Pressure peaks and actual sealing remain unvalidated.')
   if NATIVE10DONE:
    para(d,'Native V10 rebuilding is complete. '+('All 18 native STEP poses independently passed the all-body intersection check and contain 28 solids each.' if NATIVEPOSE10 and NATIVEPOSE10['all_pass'] else 'The independent native STEP audit is still running or has unresolved results.')+' Source hashes remain recorded. Geometry agreement does not remove the quarter-width modelling limitation. '+('All six saved Fusion archives were reopened and their V10 components contain 28 solids each.' if NATIVEARCH10 and NATIVEARCH10['status']=='complete' else 'Fusion archive reopening remains unchecked.'))
   if IDENTITY10 and IDENTITY10['all_match']:para(d,'File hashes also match across '+str(IDENTITY10['unique_CAD_files'])+' current native and local CAD files. This ties the files to the recorded checks; it adds no physical performance result.')
   if LOCKREACH10:para(d,'The clamp tips also reach their sliding tongues in '+str(LOCKREACH10['case_count'])+' checked left and right positions across the intended 0 to 30 mm range. This is geometric contact only. Actual threads, torque, friction, holding force, stop retention and wear remain untested.')
   if FULLWIDTH10 or STRENGTH10:new_page(d,'V10 actual width band results')
   if FULLWIDTH10 and FULLWIDTH10['status']=='complete':
    r=FULLWIDTH10['meshes'][-1]
    para(d,'A separate adult-small calculation keeps the actual full front-to-rear width and its single front clamp bore. Guide compliance is '+format(r['compliance_mm_per_N'],'.3f')+' mm per N; two meshes differ by '+format(100*FULLWIDTH10['compliance_relative_mesh_change'],'.2f')+'%. '+('This meets the chosen 5% displacement comparison.' if FULLWIDTH10['compliance_gate_5pct'] else 'This does not meet the chosen 5% displacement comparison.')+' The earlier finer run exhausted memory; the solver now assembles the same equations in smaller batches, checked against the original solver on the same beam mesh. It uses an ideal crown fixture and uniform surface load, different from the quarter model. This adult-small result is part of the size study below. It is not a worn-assembly validation or an isolated symmetry comparison. The quarter-force screen is retained separately.')
   elif FULLWIDTH10:
    para(d,'A separate adult-small calculation retains the actual full front-to-rear width and single front clamp bore. The 2 mm mesh solved, but the 1.5 mm refinement ran out of memory while assembling its stiffness matrix. No mesh comparison pass is claimed. The coarse result is provisional, uses an ideal crown fixture and uniform load, and does not replace the earlier 54-case screen. Other sizes and actual worn contact remain open.')
   if FULLSIZES10:
    actual_stress_changes=[abs(c['meshes'][-1]['max_von_mises_centroid_MPa']/c['meshes'][-2]['max_von_mises_centroid_MPa']-1) for c in FULLSIZES10['cases']]
    actual_stress_passes=sum(v<.05 for v in actual_stress_changes)
    table(d,['Actual width size','Final mesh mm','Guide compliance mm per N','Compliance change','Sampled stress change'],[[c['size'].replace('_',' '),str(c['meshes'][-1]['mesh_max_mm']),format(c['meshes'][-1]['compliance_mm_per_N'],'.3f'),format(100*c['compliance_relative_mesh_change'],'.3f')+'%',format(100*v,'.2f')+'% / '+('Pass' if v<.05 else 'Open')] for c,v in zip(FULLSIZES10['cases'],actual_stress_changes)],[1.45,1.05,1.85,1.15,1.4])
    para(d,'The sampled peak-stress comparison meets our chosen 5% limit in '+str(actual_stress_passes)+' of '+str(len(actual_stress_changes))+' recorded actual-width sizes. '+('Some peak comparisons remain open until separately refined. ' if actual_stress_passes<len(actual_stress_changes) else 'Earlier larger peak changes remain in history. ')+'Stable guide displacement alone does not establish stable peak stress. Even a final peak comparison pass is not an absolute error bound or physical strength result.')
    para(d,'This fixture study currently covers '+str(len(FULLSIZES10['cases']))+' of the six sizes. '+('All recorded displacement comparisons meet the chosen 5% limit.' if FULLSIZES10['all_compliance_comparisons_pass'] else 'Some recorded displacement comparisons do not meet the chosen 5% limit.')+' It retains the actual front-to-rear band width, but still omits scalp, joint, clamp and worn-head contact. The different fixture and load distribution mean it does not isolate symmetry error against the old quarter model.')
   if (P/'engineering-v10-results'/'child_medium_full_width_prior_memory_failure.json').exists():para(d,'The first child-medium 1.5 mm run also ran out of memory while extracting the constrained matrix. Direct assembly of that matrix and its reaction rows matched the original solver on the same verification beam; the table records the completed runs and later refinements. Resource failures remain in the project history.')
   if FULLFORCE10:
    vals=[r['force_N'] for r in FULLFORCE10['cases']];comp=[r['max_compression_mm'] for r in FULLFORCE10['cases']]
    para(d,'Using the actual-width fixture stiffness in the same reduced series model gives '+str(FULLFORCE10['case_count'])+' assumed-input cases with '+format(min(vals),'.2f')+' to '+format(max(vals),'.2f')+' N per side and maximum pad compression of '+format(min(comp),'.2f')+' to '+format(max(comp),'.2f')+' mm. The older quarter-model screen is kept for comparison. These are different ideal models, not measured forces. Material, cover, head and mounting assumptions remain; guide moments, pin bearing, friction and sensory acceptance are not solved.')
   if FULLSIZES10 and FULLSIZES10['status']=='complete' and (I/'V10_numerical_summary.png').exists():
    plot_sources=json.loads((P/'engineering-v10-results'/'numerical_plot_sources.json').read_text())
    assert all(hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256'] for r in plot_sources['source_files'])
    new_page(d,'What the numerical comparisons show')
    picture(d,'V10_numerical_summary','Saved numerical results. The two band fixtures have different restraints and loading. This is not a measured headphone comparison.',6.55)
    para(d,'The left plot keeps the adult-medium stress history, including changes above our chosen limit before the final smaller change. A final mesh comparison pass does not make the maximum stress exact.')
    para(d,'The right plot compares guide compliance: how far the guide moves for one newton in each ideal fixture. Higher compliance means a more flexible response under that fixture. The values use an assumed elastic modulus of 2000 MPa. They do not rank comfort, real band force or sound reduction.')
   if STRENGTH10:
    new_page(d,'V10 conditional material requirements')
    para(d,'We also scaled the ideal band stress to the predicted nominal-setting force in '+str(STRENGTH10['case_count'])+' cases. Under these assumptions, a material strength of at least '+format(STRENGTH10['minimum_strength_for_margin_3_over_all_nominal_cases_MPa'],'.2f')+' MPa would be needed for a margin of 3 across those cases. This is a conditional requirement for this fixture, not a measured material property or product strength result. Margins of 2 and 3 are illustrative targets, not a claimed product standard.')
    table(d,['Assumed strength MPa','Cases meeting margin 2','Cases meeting margin 3'],[[str(r['assumed_strength_MPa']),str(r['cases_with_margin_at_least_2'])+' of '+str(STRENGTH10['case_count']),str(r['cases_with_margin_at_least_3'])+' of '+str(STRENGTH10['case_count'])] for r in STRENGTH10['strength_option_counts']],[2.3,2.3,2.3])
    para(d,'This screen uses the largest recorded stress sampled at element centres across the accepted meshes. It is not a proven upper bound on the actual maximum stress: earlier mesh changes include an 18% adult-medium change before the final 0.243% comparison. The calculation does not include measured yield strength, fatigue, creep, print defects, pin bearing, clamp torque, drop impacts or full worn contact. We have not chosen a material from this table or proved that a prototype is strong enough. Each fixture retains its own force and modelling assumptions.')
 new_page(d,'Current results in plain English')
 table(d,['Question','Current answer'],[
 ['Can the saved CAD be opened as solids','All 24 V8 and 18 V9 STEP exports passed. '+('V10 has 18 local STEP poses with 28 solids each.' if V10 else '')],['Do the checked parts overlap',('The 18 saved V10 poses pass all-body overlap checks. Earlier V9 shortest-setting clashes are documented.' if POSE10 and POSE10['all_pass'] else 'V9 shortest-setting clashes remain under review.')],['Does the band calculation settle down',(stress10+' V10 guide-displacement comparisons are recorded separately.' if V10 else 'All six V9 stress and guide-displacement comparisons pass 5%.')],['Is the acoustic calculation stable','The improved cavity model is stable at the sampled frequencies. It does not include a measured glasses leak.'],['Have we fixed heat and sweat','No. Earlier model scenarios still reached saturation.'],['Will autistic people like wearing it','Unknown. No participant trials have been done.'],['Is it better than a market headphone','Unknown. No matched physical comparison has been done.'],['Can we sell it as a finished product','The current evidence does not establish that.']], [2.4,4.5])
 para(d,'The earlier V8 CAD mass was estimated at about 166 to 250 g for adults across the size and density assumptions; child mass about 131 to 196 g. These are not measured weights. Sony specifies 192 g for the WH CH720N, so our design is not automatically lighter. Shape and pressure also matter. [9]')
 para(d,('V8 had two stress comparisons above the chosen limit. V9 rounded internal guide corners and its six recorded comparisons passed, but later adjustment checks found clashes. V10 fixes those clashes. '+stress10+' The actual-width fixture result and any remaining refinement limits are recorded in the V10 section. Measured material strength and a full worn-assembly test are still missing.' if V10 else 'V8 stress comparisons pass in four sizes and fail in two. Read the V9 section for the candidate checks.'))
 new_page(d,'How we will compare real products')
 table(d,['Test','Compare under the same conditions','Current status'],[
 ['Outside noise reduction','Our defender, budget earmuff and selected ANC model; with and without glasses','Not performed'],['Pressure and band force','Same measured head sizes, pad compression and extension settings','Simulation only'],['Heat and moisture','Same room conditions, wear duration and cover material measurements','Assumption-based screening only'],['Fit and movement','Same head and ear measurements; walking, bending and easy removal','Not performed'],['Sensory acceptance','Voluntary feedback on texture, pressure, rubbing sound and control','Not performed'],['Retention and durability','Slider pull-out, adjustment cycles, drops, cleaning and pad attachment','Not performed']], [1.6,3.85,1.45])
 para(d,'For acoustic tests, measure levels near the ear under a repeatable sound field across frequencies. Compare models at the same fit, glasses and test settings. Do not rank products using marketing numbers from different test methods.')
 para(d,'We first need measured foam compression and recovery, cover stretch and friction, band stiffness and creep, liner sound properties and shell damping. Those values will make the calculations more realistic. We can then build a bench prototype and compare predictions with measurements.')
 para(d,'The wearer should be free to remove the device and say what feels wrong. Child fit, retention, small parts and pinch points need their own assessment. Success should include useful noise reduction and willingness to wear, not just a high dB number.')
 new_page(d,'Sources and project records')
 sources(d,list(range(1,12))+[14,15,16,17,18,19]);
 para(d,'Detailed market background is in engineering-v6-results/market_sample.csv and MARKET.md. Geometry and simulation evidence are in the V1 screening, V2 shape study and V3 to V10 result folders. EarDefender_V8_Review_and_Simulations.zip retains earlier evidence. EarDefender_V10_Native_CAD_and_Recorded_Checks.zip contains the current native candidates and recorded V10 checks. These packages are not finished product validation.')
 new_page(d,'What we update next')
 para(d,'Next priorities are selecting and measuring real materials, extending the joint and worn-fit model, finishing retention and manufacturing details, and measuring sound reduction with glasses. No comfort or attenuation claim should be added until the relevant evidence exists.')
 table(d,['Update date','Design status','Change to this document'],[[STAMP,REV,'First living Word edition. Added needs, selected market comparisons, CAD pictures, V1 to V9 history and clear evidence limits.']], [1.25,2.0,3.65])
 para(d,'Both project documents share the same evidence date and design status. After a meaningful design or test change, update both: replace obsolete results, add failures as well as passes, refresh pictures and explain the effect on the other product route. Preserve earlier document editions. The documents do not update while no work is being run.')
 from additional_v10_tests import add_section
 add_section(d,P,new_page,para,table,False)
 from v11_study_section import add_v11
 add_v11(d,P,new_page,para,table,picture,link,False)
 from v12_study_section import add_v12
 add_v12(d,P,new_page,para,table,picture,link,False)
 from v14_study_section import add_v14
 add_v14(d,P,new_page,para,table,picture,link,False)
 from v15_study_section import add_v15
 add_v15(d,P,new_page,para,table,picture,link,False)
 from v16_study_section import add_v16
 add_v16(d,P,new_page,para,table,picture,link,False)
 from v17_study_section import add_v17
 add_v17(d,P,new_page,para,table,picture,False,link)
 from v18_study_section import add_v18
 add_v18(d,P,new_page,para,table,picture,link,False)
 from v18_completion_section import add_completion
 add_completion(d,P,new_page,para,table,picture,False)
 from v18_final_screen_section import add_final_screen
 add_final_screen(d,P,new_page,para,table,picture,False)
 from v19_handoff_section import add_v19
 add_v19(d,P,new_page,para,table,picture,link,False)
 from v19_quadratic_section import add_quadratic
 add_quadratic(d,P,new_page,para,table)
 from v19_inward_section import add_inward
 add_inward(d,P,new_page,para,table)
 from v20_preprototype_section import add_v20
 add_v20(d,P,new_page,para,table,picture,link,False)
 from v21_review_section import add_v21
 add_v21(d,P,new_page,para,table,picture)
 return save(d,'Ear_Defender_Project.docx')

def glasses_doc():
 d=setup('SoftSpace Flex','Affordable replacement pads for compatible headphones in India')
 para(d,'Current update on 24 October 2026: the V21 review finds pressure increases when glasses miss the 18 or 32 mm soft zones. No zone is a final winner. The shared headset passes six finer stress checks but still fails both adult fork checks. The V20 pad bodies are unchanged; exact Sony mounting fit, comfort, sealing and sound benefits remain unverified. See the final V21 chapter.')
 para(d,'We want a replacement cushion that presses less on glasses arms while keeping a good seal. The user keeps their headphone and replaces its removable pads. We are developing the contact idea together with our passive ear defender, but this is a separate product route.')
 picture(d,'V20_flex_CAD','V20 uniform control and two soft-zone body candidates. Published aftermarket outside size; assumed opening and cover. The mounting skirt is not yet dimensioned or fit-verified.',6.55)
 label(d,'Current conclusion','The idea is worth investigating. We have not proved less pain, unchanged music, no sound leakage or universal compatibility. The pad needs tests on each supported headphone model.')
 if (P/'engineering-v19-results'/'test_register.json').exists():para(d,'The shared standalone design is now V19. Its revised assembly and conditional joint calculations are recorded in the final chapters, including failed trials and refinement limits. The new V20 pad bodies use a published aftermarket envelope, but exact Sony mounting dimensions are still missing. No fit, comfort or sound benefit is proved.')
 elif (P/'engineering-v18-results'/'test_register.json').exists():para(d,'The shared standalone design is now V18, using a passive folding hinge and wearing stop. The Sony WH CH720N replacement cushion is unchanged and still needs the original mounting measurements. The new hinge checks do not prove a pad benefit. The final chapters explain the shared update.')
 if (P/'engineering-v18-results'/'final_available_data_screen.json').exists():para(d,'The final standalone holding screen identifies a limited torque margin under assumed handling loads. This adds no measured Sony cushion benefit. The last chapters record the finding and the available data screening decision.')
 para(d,'This document covers the market gap, the cushion design, the work completed and the tests still needed. Read SoftSpace Project for the full standalone-headband history.')
 new_page(d,'The glasses problem and our proposed fix')
 para(d,'A glasses arm sits between the cushion and the side of the head. It can concentrate pressure and lift the pad. The amount depends on the frame, the headphone force and the pad. A softer area may help the pad conform, but it can also create a weak seal if it is too soft.')
 picture(d,'glasses_section','Concept drawing only. A softer area should compress around the arm while the cover remains continuous. It is not a measured seal.',6.55)
 para(d,'Our pad has main foam, a local softer zone, a continuous cover and a carrier behind it. The numerical softer-zone ratio is 0.5, meaning half the main foam stress for the chosen compression curve. It is an assumption, not a selected material specification.')
 para(d,'We are trying to avoid an open channel through the seal. However, a continuous cover alone does not prove an airtight seal: folds, seams, arm shape, mounting leaks and uneven force can still cause gaps.')
 para(d,'For replacement pads we do not design the host headband. We still need to measure its force and cup shape because those affect the new cushion. A design that works on one headphone can fail on another.')
 new_page(d,'First target Sony WH CH720N')
 para(d,'We selected Sony WH-CH720N. Sony explains that its pad edge fits into a housing groove, with top and bottom slots and arrows aligned. This confirms replaceable pads; the instructions give no manufacturing dimensions for our replacement. [17]')
 para(d,'Sony specifies an over-ear closed headphone, approximately 192 g, with 30 mm drivers and noise cancellation. [9] Our pad must preserve the mounting edge and avoid vents, microphones and driver clearance. The generic pad CAD is not yet compatible with this model. The user owns the headphone and plans to measure it later.')
 table(d,['What to measure','Why it matters','Current value'],[
 ['Outer pad size, ear opening and depth','Ear space, contact area and cup distance','Not measured'],
 ['Housing groove and pad skirt contour, depth and thickness','Fit and retention without an open leak path','Not measured'],
 ['Top and bottom alignment slots','Correct seating and orientation','Not measured'],
 ['Driver, vent and microphone clearance','Sound response and ANC behaviour','Not measured'],
 ['Host force at worn widths and cup angle','Compression and pressure on glasses','Not measured'],
 ['Glasses arm shape and worn contact path','Softer zone position and width','Not measured']], [2.55,2.9,1.45])
 para(d,'Keep a continuous cover over the softer foam zone. This is a design hypothesis, not proof of zero leakage. Compare the original pad, new uniform pad and new soft-zone pad on this same headphone. Check seating, pressure, incoming noise with ANC off and on, outgoing music and frequency response. All host-specific results are still untested.')
 new_page(d,'WH CH720N replacement pad comparison')
 table(d,['Option','What is advertised or planned','Price evidence','What remains unknown'],[
 ['Crysendo [18]','Indexed seller listing claims protein leather, memory foam and WH-CH720N compatibility','Indexed INR 719 to 756; live price not verified','Glasses pressure, seal, delivery and stock'],
 ['Geekria PRO [19]','Manufacturer claims memory foam, cooling gel, extra thickness and WH-CH720N compatibility','USD 23.99 for two pads; shipping extra','Delivered Indian price, glasses pressure and sound changes'],
 ['Our candidate','Softer glasses zone under a continuous cover; model-specific skirt planned','No supplier or selling price yet','Sony mount fit, pressure, sound, ANC, durability and comfort']], [1.1,2.05,1.55,2.2])
 para(d,'The Crysendo search result comes from an older indexed seller page. Its direct page could not be checked, so this is not a current purchase quote. Geekria’s product page was checked on 13 October 2026; Indian delivery and local stock were not checked. Manufacturer comfort claims are not matched test results. [18, 19]')
 para(d,'Replacement pads already have competing listings. Our proposed advantage must be lower pressure around real glasses while keeping fit and sound acceptable at a useful cost. A memory-foam label or replacement-pad label alone does not establish that advantage. We have not proved our cushion is better.')

 new_page(d,'What already exists and the Indian gap')
 table(d,['Option','What already exists','Price or access','Our possible contribution'],[
 ['Turtle Beach ProSpecs [10]','Adjustable glasses relief with a tab that changes cushion depth; more than ordinary memory foam','Exact Indian model and delivered price not verified','Investigate pads for other removable-pad models'],
 ['Noisefighters Sightlines [11]','Gel and acoustic foam pads with glasses relief cuts and adapters','USD 60 before shipping and imports; no confirmed Indian stock found in our search','Explore cheaper locally supplied compatible pads'],
 ['Brainwavz oval pads [12]','Several pad materials and a fit guide','Indian delivered price and model fit need checking','Add a deliberate glasses contact region and test it'],
 ['Wicked Cushions [13]','Model-specific replacement pads including cooling gel options','Indian delivered price not verified','Explore budget mounts and measured pressure/seal performance'],
 ['Our concept','Softer local zone under a continuous cover','No supplier quote or sale price yet','Test affordable model-specific versions']], [1.35,2.15,1.65,1.75])
 para(d,'We cannot honestly say this feature is absent everywhere in India. Our review did not confirm easy, inexpensive local access to specialist glasses-relief replacement pads for the budget models we want to serve. That is a market hypothesis to check, not proof that no seller exists.')
 para(d,'We should choose a small set of popular removable-pad models, measure their mounts and ask users what they would pay. We should not promise one cushion for every brand or call our pad the cheapest before getting production quotes.')
 new_page(d,'Budget ranges and compatibility')
 picture(d,'market_pictures','Examples of a child earmuff, an ordinary ANC headphone and our CAD. Replacement-pad fit for these market models has not been tested.',6.55)
 table(d,['Headphone price band','What we should check before making a pad'],[
 ['INR 1,000 to 3,000','Is the pad removable without damage? Can an affordable replacement still leave a useful price difference?'],['INR 3,000 to 5,000','Measure mounting lip or clips, cup opening, pad depth and headband force.'],['INR 5,000 to 10,000','Check isolation and bass as well as glasses pressure; choose exact models.'],['INR 10,000 to 20,000','Test ANC behaviour and original-pad comparison on each model.'],['INR 20,000 to 40,000','Compatibility and sound changes still matter; a higher headphone price does not guarantee a better glasses seal.']], [1.9,5.0])
 para(d,'These are target price bands, not confirmed gaps in every band. They describe headphone purchase price, not a planned cushion price. No verified manufacturing or selling price has been calculated.')
 table(d,['Original ordinary cushion','Existing specialist cushion','Our proposed cushion'],[['Fits the model it was designed for','Needs its own supported mount or adapter','Current carrier is only a blank'],['Glasses feel varies with frame and force','Some products already use relief cuts or channels','Local softer region under a continuous cover'],['Known original sound for that headphone','Can still change sound when replacing the original','Must measure bass, response, isolation and leakage'],['Benchmark for our comparison','Benchmark for specialist benefits','Benefits remain unproven']], [2.3,2.3,2.3])
 new_page(d,'Our development so far')
 picture(d,'pad_history','Saved cushion and cover geometry from early stages and V8. Colours are illustrative.',6.55)
 table(d,['Stage','Pad work and evidence','Main limitation'],[
 ['V1','Split a glasses contact region and added simplified frame references; 3,240 spring-contact cases','Independent foam cells; gaps remained; no real sound test'],['V2','Compared 9,216 shapes and made a connected cover surface','Ideal contact was not proof of sealing; cover was not a solid wrap'],['V3','Curved pads, solid cover envelope and scalar cover/foam calculations','No actual fabric, skin, friction, seams or measured materials'],['V4','Cup alignment and coupled force study','Pressure peaks failed refinement; humid cases saturated'],['V5','72 pad comparisons and 6 mm virtual sensor checks','Stable averages, unstable point peaks; physical seal unknown'],['V6','Corrected carrier/cover overlap and verified replacement STEP exports','Still no real headphone mount or acoustic-pad comparison'],['V7 to V8','Pad concept retained while the own-defender band changed; V8 replacement exports checked','V8 acoustic cavity model does not calculate a real glasses leak'],['V9','Standalone-band corner experiment'+(' with native candidates now exported' if NATIVE else ''),'No new replacement-pad or measured leakage evidence'],['V10','Standalone guide clearances corrected; Sony WH-CH720N selected for pad route','Generic pad unchanged; host measurements and leakage results missing']], [0.7,3.65,2.55])
 new_page(d,'Which cushion checks passed and failed')
 table(d,['Check','Recorded outcome','What it tells us'],[
 ['Simple compression and force balance','Passed under assumed inputs','The numerical equations are behaving as expected'],['Continuous V2 cover surface','Connected surface passed','Not a full volumetric cover or tested seam'],['V8 replacement exports','Six STEP files contain four solids each','The saved pad components can be imported'],['V6 and V8 nominal overlap audits','Passed for own-defender assemblies','Not proof of fitting another headphone'],['Average pressure refinement in V5','Under 5% change for two nominal cases','Averaged model pressures are more stable'],['Point pressure refinement','Failed','Do not claim an exact peak pressure or pain reduction'],['Hot and humid moisture cases','Some reached saturation','Heat and sweat are not solved'],['Sound leaking in around glasses','No measured pass','Current contact gap values are not a leakage measurement'],['Music leaking out','Not tested','No zero-leakage claim is justified'],['Bass and sound quality','Not tested','Pad changes need headphone-specific response tests']], [2.05,2.0,2.85])
 para(d,'Early V1 outputs showed lower frame pressure after reducing local stiffness. That reduction was partly built into the assumed model and is not evidence that our actual pad prevents headaches. Later cover models added coupling and revealed unstable point pressures. We should use the latest evidence rather than advertise the early percentage.')
 new_page(d,'Noise getting in and music getting out')
 picture(d,'leak_paths','Two separate questions. Incoming noise and outgoing playback must each be measured. Diagram is conceptual.',6.55)
 para(d,'For our passive defender there is no music driver, so outgoing music leakage is not a current product function. For a replacement pad on music headphones, we must test both directions and also check whether the pad changes bass or ANC performance.')
 para(d,'The current acoustic work solves a hypothetical cup cavity. The improved model checks numerical stability across 48 sampled frequencies from 31.5 Hz to 8 kHz. It does not include a measured three-dimensional slit around a real glasses arm, real cover seams or a real headphone driver. It cannot answer how much music a nearby person will hear.')
 para(d,'Zero leakage is not a result we can promise. Our working goal is to avoid a meaningful loss of isolation or increase in playback leakage compared with the original pad, while improving comfort. We will choose a numerical acceptance limit only after measuring the original pad and agreeing on the use case.')
 new_page(d,'The tests needed on each supported model')
 table(d,['Test','Comparison and method','Status'],[
 ['Mount fit','Original and new pads on the exact headphone; clips, lip, pull-off, cup clearance','Not done'],['Incoming noise','Repeatable external sound field; levels near the ear with no, thin, thick and curved glasses arms','Not done'],['Outgoing playback','Same measured level inside the cup; microphones outside at fixed distances and positions','Not done'],['Music response','Original and new pads on the same fixture; frequency response, especially bass; ANC on and off where available','Not done'],['Pressure and comfort','Pressure mapping plus voluntary feedback at measured clamp forces','Models only'],['Heat and moisture','Same ambient conditions and duration; temperature and humidity measurements','Models only'],['Movement and repeatability','Re-seat pads and glasses repeatedly; turn head and check several users or fixtures','Not done'],['Durability','Cleaning, compression recovery, foam ageing, cover wear, bond and mount retention','Not done']], [1.35,4.25,1.3])
 para(d,'Test an original pad, a uniform new pad without the soft zone, and our soft-zone pad. Where possible, add an existing specialist pad. That separates the effect of changing the whole cushion from the effect of our glasses zone.')
 para(d,'Use the same headphone, frame position, test signal, fixture and inside-cup playback level. Matching only the volume-slider setting may be misleading because pad changes can alter the sound level at the ear. Repeat the fit several times and show the range of results.')
 new_page(d,'What is still missing and what comes next')
 para(d,'We need real foam compression and recovery curves, cover stretch and friction, frame shapes, head geometry and measured forces from the host headphones. We also need a finished seam, bond and mounting design. The continuous cover and softer zone should be checked together, not treated as separate guaranteed fixes.')
 para(d,'Start with the selected Sony WH-CH720N, whose pads can be replaced. Measure its original mount before changing the carrier or skirt. Make original, uniform and softer-zone samples. Check fit and retention first, then measure incoming noise, outgoing playback and frequency response. Improve the geometry using those results before expanding to more models.')
 para(d,'Affordable Indian supply is our intended direction. It becomes a supported business claim only after we confirm a real demand gap, supplier costs, model compatibility and measurable improvement. The standalone autistic-user defender remains the first-priority project; this pad route can share learning and materials.')
 table(d,['Update date','Shared evidence status','Change to this document'],[[STAMP,REV,'First living Word edition. Added CAD pictures, existing competitors, honest Indian availability wording, version history, leakage limits and a model-specific test plan.']], [1.25,1.8,3.85])
 para(d,'Update this document whenever pad geometry, materials, host-model fit or sound results change. Also update SoftSpace Project so both reports stay consistent. Record failures and replace obsolete claims; do not only append good results.')
 if V10:
  new_page(d,'Latest shared CAD and simulation results')
  para(d,'V10 corrects the guide and knob clashes found in the standalone V9 shortest setting. All 18 native V10 STEP poses passed the all-body overlap audit. Six saved Fusion archives reopened with 28 solids in each V10 component. This is geometry evidence; it does not test glasses comfort or sealing.')
  if IDENTITY10 and IDENTITY10['all_match']:para(d,'The '+str(IDENTITY10['unique_CAD_files'])+' current native and local standalone CAD files also match the hashes recorded in their checks. This ties those results to the saved files.')
  para(d,'The quarter-band displacement comparisons pass in all six sizes. '+stress10+' That ideal model mirrors a front clamp bore onto the rear wall. It is not the complete worn assembly.')
  if FULLSIZES10:
   n_actual=len(FULLSIZES10['cases']);n_stress=sum(abs(c['meshes'][-1]['max_von_mises_centroid_MPa']/c['meshes'][-2]['max_von_mises_centroid_MPa']-1)<.05 for c in FULLSIZES10['cases'])
   para(d,'The separate actual-width fixture study covers '+str(n_actual)+' of six sizes. Its recorded guide-compliance comparisons '+('all pass' if FULLSIZES10['all_compliance_comparisons_pass'] else 'do not all pass')+' our chosen 5% limit. Sampled peak-stress comparisons pass in '+str(n_stress)+' of those sizes. Earlier coarse-to-fine peak changes above 5% and memory failures remain in the history. Read the main report for the current refinements. These ideal fixtures still omit real scalp, joint and clamp contact.')
  extra=(' An additional '+str(FULLFORCE10['case_count'])+'-case screen uses the actual-width fixture.' if FULLFORCE10 else '')
  material=(' A conditional material-strength screen uses predicted forces and illustrative margins; it has no measured strength or durability pass.' if STRENGTH10 else '')
  para(d,'The standalone quarter-fixture force screen has 54 cases.'+extra+' The force screens use assumed materials and synthetic heads.'+material+' These calculations do not measure the Sony headband force or prove a replacement pad reduces pressure, incoming noise or outgoing music.')
  para(d,'The generic V8 replacement pad is unchanged and is not claimed to fit Sony WH-CH720N. At the V19 stage its mount had not been measured. The V20 chapter now uses a published aftermarket envelope and keeps the exact skirt and groove dimensions open. Host fit, retention, incoming noise, outgoing playback, frequency response, ANC behaviour and wearer comfort remain untested. Both reports will be updated when those dimensions or results arrive.')
 new_page(d,'Sources and project records')
 sources(d,[5,8,9,10,11,12,13,17,18,19]);para(d,'Primary local evidence: cad_build_report.json; cover_prototype_report.json; shape-study-results/report.md; engineering-v3-results/contact_summary.json; engineering-final-results/REVIEW.md; engineering-v5-results/REVIEW.md; cad_v8_report.json; cad_v8_audit.json; engineering-v8-results/STEP_verification.json; engineering-v7-results/acoustic_p2_summary.json. The named files are saved in EarDefenderProject.')
 from additional_v10_tests import add_section
 add_section(d,P,new_page,para,table,True)
 from v11_study_section import add_v11
 add_v11(d,P,new_page,para,table,picture,link,True)
 from v12_study_section import add_v12
 add_v12(d,P,new_page,para,table,picture,link,True)
 from v14_study_section import add_v14
 add_v14(d,P,new_page,para,table,picture,link,True)
 from v15_study_section import add_v15
 add_v15(d,P,new_page,para,table,picture,link,True)
 from v16_study_section import add_v16
 add_v16(d,P,new_page,para,table,picture,link,True)
 from v17_study_section import add_v17
 add_v17(d,P,new_page,para,table,picture,True,link)
 from v18_study_section import add_v18
 add_v18(d,P,new_page,para,table,picture,link,True)
 from v18_completion_section import add_completion
 add_completion(d,P,new_page,para,table,picture,True)
 from v18_final_screen_section import add_final_screen
 add_final_screen(d,P,new_page,para,table,picture,True)
 from v19_handoff_section import add_v19
 add_v19(d,P,new_page,para,table,picture,link,True)
 from v19_quadratic_section import add_quadratic
 add_quadratic(d,P,new_page,para,table)
 from v19_inward_section import add_inward
 add_inward(d,P,new_page,para,table)
 from v20_preprototype_section import add_v20
 add_v20(d,P,new_page,para,table,picture,link,True)
 from v21_review_section import add_v21
 add_v21(d,P,new_page,para,table,picture)
 return save(d,'Glasses_Friendly_Headphone_Cushions.docx')

if __name__=='__main__':
 old_status=O/'document_status.json'
 if old_status.exists():
  for item in json.loads(old_status.read_text()).get('documents',[]):
   existing=Path(item['path'])
   if existing.exists() and hashlib.sha256(existing.read_bytes()).hexdigest()!=item['sha256']:
    raise RuntimeError('Document changed outside the builder; preserve user edits before rebuilding: '+str(existing))
 paths=[main_doc(),glasses_doc()]
 manifest={'updated':'24 October 2026','design_status':REV,'documents':[{'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for f in paths],'market_checked':'2026-10-13','future_rule':'Update both documents after every meaningful project edit or new result; preserve user edits and history; do not silently regenerate over user edits.'}
 (O/'document_status.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))

