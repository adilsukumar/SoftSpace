from pathlib import Path
import pypdfium2 as pdfium
P=Path(__file__).parent/'qa'
for name in ['Ear_Defender_Project','Glasses_Friendly_Headphone_Cushions']:
 d=pdfium.PdfDocument(str(P/name/'approximate_layout.pdf'))
 print(name)
 for i in range(len(d)):
  page=d[i];text=page.get_textpage().get_text_range()
  lines=[s.strip() for s in text.splitlines() if s.strip()]
  print(i+1, ' | '.join(lines[1:3]))
