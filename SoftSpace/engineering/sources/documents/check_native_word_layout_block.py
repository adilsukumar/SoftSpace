"""Render native Word PDF exports and record page/layout evidence without changing DOCX."""
from pathlib import Path
import json,hashlib
import pypdfium2 as pdfium
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;Q=P/'qa';status=json.loads((Q/'native_word_status.json').read_text(encoding='utf-8-sig'));records=[]
for item in status['documents']:
 source=P/(item['document']+'.docx');assert hashlib.sha256(source.read_bytes()).hexdigest()==item['source_sha256'];pdf=Path(item['pdf']);assert hashlib.sha256(pdf.read_bytes()).hexdigest()==item['pdf_sha256'];d=pdfium.PdfDocument(str(pdf));assert len(d)==item['native_pages'];folder=Q/('native_block_'+item['document']+'_'+item['source_sha256'][:8]);folder.mkdir(exist_ok=True);pages=[];thumbs=[]
 for i in range(len(d)):
  page=d[i];tp=page.get_textpage();text=tp.get_text_range();bounds=[];count=tp.count_rects()
  for j in range(count):
   l,b,r,t=tp.get_rect(j)
   if l<-.5 or b<-.5 or r>page.get_width()+.5 or t>page.get_height()+.5:bounds.append([l,b,r,t])
  body=[s for s in text.splitlines() if not s.startswith('SOFTSPACE') and not s.startswith('Concept under development') and s.strip()];record=dict(page=i+1,characters=len(text),body_lines=len(body),first_lines=body[:3],last_lines=body[-3:],text_rectangles_outside_physical_page=bounds)
  pages.append(record);im=page.render(scale=1.25).to_pil().convert('RGB');im.save(folder/('page-'+str(i+1)+'.png'));thumb=im.copy();thumb.thumbnail((234,302));canvas=Image.new('RGB',(250,325),'white');canvas.paste(thumb,(8,8));ImageDraw.Draw(canvas).text((8,309),str(i+1),fill='black');thumbs.append(canvas)
 for group in range((len(thumbs)+19)//20):
  sheet=Image.new('RGB',(1250,1300),'#cccccc')
  for j,im in enumerate(thumbs[group*20:(group+1)*20]):sheet.paste(im,((j%5)*250,(j//5)*325))
  sheet.save(folder/('sheet-'+str(group+1)+'.png'))
 rec=dict(document=item['document'],render_folder=str(folder),source_sha256=item['source_sha256'],native_pages=len(d),blank_body_pages=[r['page'] for r in pages if r['body_lines']==0],short_text_pages=[r['page'] for r in pages if r['characters']<250],out_of_page_text_rectangles=sum(len(r['text_rectangles_outside_physical_page']) for r in pages),pages=pages);records.append(rec);print({k:v for k,v in rec.items() if k!='pages'},flush=True)
(Q/'native_block_layout_checks.json').write_text(json.dumps(dict(date='2026-10-26',documents=records,scope='Native Word PDF export, all-page render, text rectangle and blank-page checks. Visual inspection is recorded separately; these automated checks do not verify scientific claims.'),indent=2))
